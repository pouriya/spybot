from spybot.utils import wrap_strings

TEXT_TYPE            = 'TEXT'
FILE_TYPE            = 'FILE'
LOCATION_TYPE        = 'LOCATION'
START_TYPE           = 'START'
STOP_TYPE            = 'STOP'
KEYBOARD_CHANGE_TYPE = 'KEYBOARD_CHANGE'
TYPES                = [TEXT_TYPE
                       ,FILE_TYPE
                       ,START_TYPE
                       ,STOP_TYPE
                       ,LOCATION_TYPE
                       ,KEYBOARD_CHANGE_TYPE]

IMAGE_FILE_TYPE        = 'IMAGE'
GIF_FILE_TYPE          = 'GIF'
VIDEO_FILE_TYPE        = 'VIDEO'
PUSH_TO_TALK_FILE_TYPE = 'PUSH_TO_TALK'
CONTACT_FILE_TYPE      = 'CONTACT'
ATTACHMENT_FILE_TYPE   = 'ATTACHMENT'
FILE_TYPES             = [IMAGE_FILE_TYPE
                         ,GIF_FILE_TYPE
                         ,VIDEO_FILE_TYPE
                         ,PUSH_TO_TALK_FILE_TYPE
                         ,CONTACT_FILE_TYPE
                         ,ATTACHMENT_FILE_TYPE]


def parse(event):
    try:
        (error, result) = (False, event['type'])
    except KeyError:
        (error, result) = (True, 'could not found \'type\' in {!r}'.format(event))
    if error:
        raise LookupError(result)
    event_type = result

    if event_type == TEXT_TYPE:
        parsed_event = Text(event)
    elif event_type == FILE_TYPE:
        try:
            (error, result) = (False, event['fileType'])
        except KeyError:
            (error, result) = (False, ATTACHMENT_FILE_TYPE)
        file_type = result

        if file_type == IMAGE_FILE_TYPE:
            parsed_event = Image(event)
        elif file_type == GIF_FILE_TYPE:
            parsed_event = Gif(event)
        elif file_type == VIDEO_FILE_TYPE:
            parsed_event = Video(event)
        elif file_type == PUSH_TO_TALK_FILE_TYPE:
            parsed_event = PushToTalk(event)
#        elif file_type == CONTACT_FILE_TYPE:
#            parsed_event = Contact(event)
        elif file_type == ATTACHMENT_FILE_TYPE:
            parsed_event = Attachment(event)
        else:
            raise NotImplementedError('unknown file type {!r} in {!r}'.format(file_type, event))

    elif event_type == START_TYPE:
        parsed_event = Start(event)
    elif event_type == STOP_TYPE:
        parsed_event = Stop(event)
    elif event_type == LOCATION_TYPE:
        parsed_event = Location(event)
#	elif event_type == KEYBOARD_CHANGE_TYPE:
#		parsed_event = KeyBoardChange(event)
    else:
        raise NotImplementedError('unknown type {!r} in {!r}'.format(event_type, event))
    return parsed_event


class _Event:

    def __init__(self, event, event_type):
        self.type             = event_type
        self.sender           = self._read_sender(event)
        self.time             = self._read_time(event)
        self.is_text          = False
        self.is_file          = False
        self.is_image         = False
        self.is_gif           = False
        self.is_video         = False
        self.is_attachment    = False
        self.is_push_to_talk  = False
        self.is_location      = False
        self.is_start         = False
        self.is_stop          = False
        self.string_separator = ', '
        self.string_equal     = ' -> '


    def __str__(self):
        return wrap_strings([('type'     , self.type)
                            ,('from'     , self.sender)
                            ,('timestamp', self.time)]
                           ,separator=self.string_separator
                           ,equal=self.string_equal)


    def _read_sender(self, event):
        return self._read(event, 'from')


    def _read_time(self, event):
        def filter_function(value, event):
            try:
                value = int(value)
                return value
            except ValueError:
                pass
            raise ValueError('could not convert time {!r} to integer in {!r}'.format(time, event))
        return self._read(event, 'time', filter_function)


    def _read(self, event, key, filter_function=None, default=None):
        try:
            (error, result) = (False, event[key])
        except KeyError as exception:
            (error, result) = (True, exception)
        if error:
            if default:
                return default[0]
            raise LookupError('could not found {!r} in {!r}'.format(key, event))
        if filter_function:
            result = filter_function(result, event)
        return result


class Text(_Event):

    def __init__(self, event):
        _Event.__init__(self, event, TEXT_TYPE)
        self.body    = self._read_body(event)
        self.is_text = True


    def __str__(self):
        string  = super().__str__()
        string += self.string_separator + wrap_strings([('body', self.body)]
                                                      ,separator=self.string_separator
                                                      ,equal=self.string_equal)
        return string

    def _read_body(self, event):
        return self._read(event, 'body')


class _File(_Event):

    def __init__(self, event, mediatype):
        _Event.__init__(self, event, FILE_TYPE)
        self.body      = self._read_body(event)
        self.url       = self._read_url(event)
        self.name      = self._read_name(event)
        self.size      = self._read_size(event)
        self.mediatype = mediatype
        self.is_file   = True


    def __str__(self):
        string   = super().__str__()
        items    = [('media-type', self.mediatype)
                   ,('name', self.name)
                   ,('size', self.size, "KB")
                   ,('URL', self.url)]
        if self.body and self.body != ' ':
            items.insert(2, ('body', self.body))
        string += self.string_separator + wrap_strings(items
                                                      ,separator=self.string_separator
                                                      ,equal=self.string_equal)
        return string


    def _read_body(self, event):
        return self._read(event, 'body', default=(None,))


    def _read_url(self, event):
        return self._read(event, 'fileUrl')


    def _read_id(self, event):
        return self._read(event, 'fileId', default=(None,))


    def _read_name(self, event):
        return self._read(event, 'fileName')


    def _read_size(self, event):
        return self._read(event, 'fileSize')


class Image(_File):

    def __init__(self, event):
        _File.__init__(self, event, IMAGE_FILE_TYPE)
        self.thumbnail_url = self._read_thumbnail_url(event)
        self.width         = self._read_image_width(event)
        self.height        = self._read_image_height(event)
        self.is_image      = True


    def __str__(self):
        string   = super().__str__()
        items    = [('width', self.width)
                   ,('height', self.height)
                   ,('thumbnail-URL', self.thumbnail_url)]
        string  += self.string_separator + wrap_strings(items
                                                       ,separator=self.string_separator
                                                       ,equal=self.string_equal)
        return string


    def _read_thumbnail_url(self, event):
        return self._read(event, 'thumbnailUrl')


    def _read_image_width(self, event):
        return self._read(event, 'imageWidth')


    def _read_image_height(self, event):
        return self._read(event, 'imageHeight')


class Gif(_File):

    def __init__(self, event):
        _File.__init__(self, event, GIF_FILE_TYPE)
        self.thumbnail_url = self._read_thumbnail_url(event)
        self.image_width   = self._read_image_width(event)
        self.image_height  = self._read_image_height(event)
        self.is_gif        = True


    def __str__(self):
        string   = super().__str__()
        items    = [('width', self.width)
                   ,('height', self.height)
                   ,('thumbnail-URL', self.thumbnail_url)]
        string  += self.string_separator + wrap_strings(items
                                                       ,separator=self.string_separator
                                                       ,equal=self.string_equal)
        return string


    def _read_thumbnail_url(self, event):
        return self._read(event, 'thumbnailUrl')


    def _read_image_width(self, event):
        return self._read(event, 'imageWidth')


    def _read_image_height(self, event):
        return self._read(event, 'imageHeight')


class Video(_File):

    def __init__(self, event):
        _File.__init__(self, event, VIDEO_FILE_TYPE)
        self.duration         = self._read_duration(event)
        self.thumbnail_url    = self._read_thumbnail_url(event)
        self.thumbnail_width  = self._read_thumbnail_width(event)
        self.thumbnail_height = self._read_thumbnail_height(event)
        self.is_video         = True


    def __str__(self):
        string   = super().__str__()
        items    = [('duration', self.duration, 'ms')
                   ,('thumbnail-width', self.thumbnail_width)
                   ,('thumbnail-height', self.thumbnail_height)
                   ,('thumbnail-URL', self.thumbnail_url)]
        string  += self.string_separator + wrap_strings(items
                                                       ,separator=self.string_separator
                                                       ,equal=self.string_equal)
        return string


    def _read_duration(self, event):
        return self._read(event, 'fileDuration')


    def _read_thumbnail_url(self, event):
        return self._read(event, 'thumbnailUrl')


    def _read_thumbnail_width(self, event):
        return self._read(event, 'thumbnailWidth')


    def _read_thumbnail_height(self, event):
        return self._read(event, 'thumbnailHeight')


class PushToTalk(_File):

    def __init__(self, event):
        _File.__init__(self, event, PUSH_TO_TALK_FILE_TYPE)
        self.duration        = self._read_duration(event)
        self.is_push_to_talk = True


    def __str__(self):
        string   = super().__str__()
        items    = [('duration', self.duration, 'ms')]
        string  += self.string_separator + wrap_strings(items
                                                       ,separator=self.string_separator
                                                       ,equal=self.string_equal)
        return string


    def _read_duration(self, event):
        return self._read(event, 'fileDuration')


class Attachment(_File):

    def __init__(self, event):
        _File.__init__(self, event, ATTACHMENT_FILE_TYPE)
        self.is_attachment = True


class Location(_Event):

    def __init__(self, event):
        _Event.__init__(self, event, LOCATION_TYPE)
        self.latitude    = self._read_latitude(event)
        self.longitude   = self._read_longitude(event)
        self.is_location = True


    def __str__(self):
        string   = super().__str__()
        items    = [('latitude', self.latitude)
                   ,('longitude', self.longitude)]
        string  += self.string_separator + wrap_strings(items
                                                       ,separator=self.string_separator
                                                       ,equal=self.string_equal)
        return string


    def _read_latitude(self, event):
        return self._read(event, 'latitude')


    def _read_longitude(self, event):
        return self._read(event, 'longitude')


class Start(_Event):

    def __init__(self, event):
        _Event.__init__(self, event, START_TYPE)
        self.is_start = True


class Stop(_Event):

    def __init__(self, event):
        _Event.__init__(self, event, STOP_TYPE)
        self.is_stop = True
