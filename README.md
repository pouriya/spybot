# `SPyBot`
Python wrapper around [Soroush messenger Bot API](https://soroush-app.ir/developer.html). Note that repository is still under development.  


# Build
```sh
/projects $ git clone --depth 1 https://github.com/Pouriya-Jahanbakhsh/spybot && cd spybot
...
/projects/spybot $ sudo python3.5 setup.py install
...
```

# Quick example:
```python

import spybot
import logging

# set up logging (optional):
logging.basicConfig(level=logging.INFO)

def my_event_handler(event):
    if event.is_text:
        replies = []
        for char in event.body:
            reply = spybot.reply.Text(event.sender, char)
            replies.append(reply)
        return replies

bot = spybot.Bot("MY_TOKEN", event_handler=my_event_handler)
bot.run()
```
Place your token in above example and save it in a file named `echobot.py`, then run:  
```sh
/path/to/your/echobot $ python3.5 echobot.py
INFO:requests.packages.urllib3.connectionpool:Starting new HTTPS connection (1): bot.sapp.ir
INFO:spybot.api:got new event type -> TEXT, from -> LC00qzKjtwPTJe352hS..., timestamp -> 1538918596120, body -> Hello😍👍

INFO:spybot.api:event handler function yielded reply with type -> TEXT, to -> LC00qzKjtwPTJe352hS..., body -> H
INFO:requests.packages.urllib3.connectionpool:Starting new HTTPS connection (1): bot.sapp.ir
INFO:spybot.api:sent message successfully

INFO:spybot.api:event handler function yielded reply with type -> TEXT, to -> LC00qzKjtwPTJe352hS..., body -> e
INFO:requests.packages.urllib3.connectionpool:Starting new HTTPS connection (1): bot.sapp.ir
INFO:spybot.api:sent message successfully

INFO:spybot.api:event handler function yielded reply with type -> TEXT, to -> LC00qzKjtwPTJe352hS..., body -> l
INFO:requests.packages.urllib3.connectionpool:Starting new HTTPS connection (1): bot.sapp.ir
INFO:spybot.api:sent message successfully

INFO:spybot.api:event handler function yielded reply with type -> TEXT, to -> LC00qzKjtwPTJe352hS..., body -> l
INFO:requests.packages.urllib3.connectionpool:Starting new HTTPS connection (1): bot.sapp.ir
INFO:spybot.api:sent message successfully

INFO:spybot.api:event handler function yielded reply with type -> TEXT, to -> LC00qzKjtwPTJe352hS..., body -> o
INFO:requests.packages.urllib3.connectionpool:Starting new HTTPS connection (1): bot.sapp.ir
INFO:spybot.api:sent message successfully

INFO:spybot.api:event handler function yielded reply with type -> TEXT, to -> LC00qzKjtwPTJe352hS..., body -> 😍
INFO:requests.packages.urllib3.connectionpool:Starting new HTTPS connection (1): bot.sapp.ir
INFO:spybot.api:sent message successfully

INFO:spybot.api:event handler function yielded reply with type -> TEXT, to -> LC00qzKjtwPTJe352hS..., body -> 👍
INFO:requests.packages.urllib3.connectionpool:Starting new HTTPS connection (1): bot.sapp.ir
INFO:spybot.api:sent message successfully

```

For more information see [Wiki]().  
For contribution see [contribution guide]().
