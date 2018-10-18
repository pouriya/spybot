import requests
import json
import logging
from inspect import getfullargspec
from os.path import join
from os import getcwd

from spybot.reply import is_reply
from spybot.event import parse

logger = logging.getLogger(__name__)

class Bot:

    BASE_URL = "https://bot.sapp.ir"

    def __init__(self
                ,token
                ,request_timeout      = 0
                ,warn_not_implemented = False
                ,get_retry_max        = 0
                ,send_retry_max       = 0
                ,event_handler        = None):
        self.token                = token
        self.request_timeout      = request_timeout
        self.warn_not_implemented = warn_not_implemented
        self.get_retry_max        = get_retry_max
        self.get_retry_count      = 0
        self.send_retry_max       = send_retry_max
        self.send_retry_count     = 0
        self.event_handler        = event_handler


    def _handle_get_retry(self, exception):
        if not self.get_retry_max:
            raise exception
        elif self.get_retry_max == self.get_retry_count:
            logger.debug('reached max \'get\' retry')
            raise exception
        elif self.get_retry_max > 0:
            self.get_retry_count += 1


    def run(self):
        while True:
            self.get_messages(self.event_handler)


    def get_messages(self, event_handler):
        URI = "{}/{}/getMessage".format(self.BASE_URL, self.token)
        try:
            if self.request_timeout:
                req = requests.get(URI, stream=True, timeout=self.request_timeout)
            else:
                req = requests.get(URI, stream=True)
        except Exception as error:
            logger.error('could not make HTTP request to {!r}'.format(self.BASE_URL))
            self._handle_get_retry(error)
            return
        if req.status_code == 200:
            try:
                for chunk in req.iter_content(chunk_size=None):
                    chunk = chunk.decode()
                    logger.debug('got new chunk {!r}'.format(chunk))
                    if chunk.startswith('{'):
                        self._handle_event(chunk, event_handler)
                        continue
                    logger.debug('skipping chunk')
            except requests.exceptions.ConnectionError as error:
                logger.error('could not read stream chunks')
                req.close()
                self._handle_get_retry(error)
                return
        else:
            logger.error('got HTTP status code {!r}'.format(req.status_code))
            req.close()
            self._handle_get_retry(error)
            return


    def _handle_event(self, event, event_handler):
        try:
            event = json.loads(event)
        except json.decoder.JSONDecodeError:
            raise ValueError('could not decode chunk')
        logger.debug('decoded chunk successfully')

        try:
            event = parse(event)
        except NotImplementedError as error:
            if self.warn_not_implemented:
                logger.warning('got unknown event {!r}, skipping'.format(event))
                return
            raise error
        logger.info('got new event {}'.format(event))
        
        if event.is_file:
            event = self._add_download_method(event)

        logger.debug('running event handler function {}'.format(event_handler))
        if not event_handler:
            result = self.handle_event(event)
        else:
            argument_count = len(getfullargspec(event_handler).args)
            if argument_count == 1:
                result = event_handler(event)
            elif argument_count == 2:
                result = event_handler(self, event)
            else:
                raise ValueError('event handler function {!r} MUST accept one or two argument(s)'.format(event_handler))

        if result == None:
            logger.debug('event handler function does not yield anything')
            return
        if type(result) == list:
            for item in result:
                if is_reply(item):
                    logger.info('event handler function yielded reply with {}'.format(item))
                    self._handle_reply(item)
                else:
                    raise ValueError("unknown reply item {!r}".format(item))
            return
        if is_reply(result):
            logger.info('event handler function yielded reply with {}'.format(result))
            self._handle_reply(result)
            return
        raise ValueError('event handler function {} does not yield valid return value'.format(event_handler))


    def _add_download_method(self, event):
        URL  = self.get_download_url(event.url)
        name = event.name
        def download(path=None):
            try:
                req = requests.get(URL)
            except requests.exceptions.ConnectionError as error:
                logger.error('could not get file {!r}'.format(name))
                req.close()
                self._handle_get_retry(error)
                return False
            if path == None:
                path = getcwd()
            filename = join(path, name)
            try:
                fd = open(filename, 'wb')
                fd.write(req.content)
                logger.error('file {!r} downloaded successfully and saved to {}'.format(name, path))
                return True
            except Exception as error:
                logger.error('could not write file contents to {!r}'.format(filename))
                raise
        event.download = download
        return event


    def get_download_url(self, event_url):
        URL = "{}/{}/downloadFile/{}".format(self.BASE_URL, self.token, event_url) 
        return URL

    def _handle_reply(self, reply):
        reply = reply.reply
        try:
            reply = json.dumps(reply)
        except TypeError:
            raise ValueError("could not encode reply value {!r} to JSON".format(reply))
        logger.debug('wraped reply successfully')
        self._send_message(reply)


    def _send_message(self, data):
        while True:
            try:
                result = self.send_message(data)
                return result
            except Exception as error:
                self._handle_send_retry(error)


    def _handle_send_retry(self, exception):
        if not self.send_retry_max:
            raise exception
        elif self.send_retry_max == self.send_retry_count:
            logger.debug('reached max \'send\' retry')
            raise exception
        elif self.send_retry_max > 0:
            self.send_retry_count += 1


    def send_message(self, data):
        URI = "{}/{}/sendMessage".format(self.BASE_URL, self.token)
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        if self.request_timeout:
            req = requests.post(URI, headers=headers, timeout=self.request_timeout, data=data)
        else:
            req = requests.post(URI, headers=headers, data=data)
        if req.status_code == 200:
            response = req.text
            logger.debug('got send response {!r}'.format(response))
            req.close()
            if response.startswith('{'):
                try:
                    response = json.loads(response)
                    status_code = response['resultCode']
                    if status_code == 200:
                        logger.info('sent message successfully')
                        return (True, 200, None)
                    message = response['resultMessage']
                    logger.error('could not send message because {!r}'.format(message))
                    return (False, staus_code, message)
                except KeyError or json.decoder.JSONDecodeError:
                    logger.error('got error {!r} for send operation'.format(req.text))
                    return (False, req.status_code, 'unknown response {!r}'.format(req.text))
        else:
            logger.error('got HTTP status code {!r} for send operation'.format(req.status_code))
            return (False, req.status_code, 'unknown response {!r}'.format(req.text))


    def handle_event(self, event):
        pass
