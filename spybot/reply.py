from spybot.utils import wrap_strings

TEXT_TYPE            = 'TEXT'
FILE_TYPE            = 'FILE'
LOCATION_TYPE        = 'LOCATION'
CONTACT_TYPE         = 'CONTACT'
KEYBOARD_CHANGE_TYPE = 'CHANGE'
TYPES                = [TEXT_TYPE
                       ,FILE_TYPE
                       ,LOCATION_TYPE
                       ,CONTACT_TYPE
                       ,KEYBOARD_CHANGE_TYPE]

IMAGE_FILE_TYPE        = 'IMAGE'
GIF_FILE_TYPE          = 'GIF'
VIDEO_FILE_TYPE        = 'VIDEO'
PUSH_TO_TALK_FILE_TYPE = 'PUSH_TO_TALK'
ATTACHMENT_FILE_TYPE   = 'ATTACHMENT'
FILE_TYPES             = [IMAGE_FILE_TYPE
                         ,GIF_FILE_TYPE
                         ,VIDEO_FILE_TYPE
                         ,PUSH_TO_TALK_FILE_TYPE
                         ,ATTACHMENT_FILE_TYPE]


def is_reply(reply):
    if type(reply) in (Text
                      ,Gif
                      ,Video
                      ,PushToTalk
                      ,Attachment
                      ,Location
                      ,Contact
                      ,KeyboardChange):
        return True
    return False


class _Reply:

    def __init__(self, to, reply_type, keyboard=None):
        self.reply = {'to': to, 'type': reply_type}
        self.type  = reply_type
        if keyboard != None:
            self.reply['keyboard'] = self._transform_keyboard(keyboard)
        self.string_separator = ', '
        self.string_equal     = ' -> '


    def __str__(self):
        return wrap_strings([('type'     , self.type)
                            ,('to'     , self.reply['to'])]
                           ,separator=self.string_separator
                           ,equal=self.string_equal)
            

    def _transform_keyboard(self, keyboard):
        fixed_keyboard = []
        row_size = len(keyboard)
        row_count = 1
        while row_count <= row_size:
            columns = keyboard[row_count]
            column_size = len(columns)
            column_count = 1
            fixed_column = []
            while column_count <= column_size:
                key = columns[column_count]
                (command, text) = key
                fixed_column.append({'command': command, 'text': text})
                column_count += 1
            fixed_keyboard.append(fixed_column)
            row_count += 1
        return fixed_keyboard


class Text(_Reply):

    def __init__(self, to, body, keyboard=None):
        _Reply.__init__(self, to, TEXT_TYPE, keyboard)
        self.reply['body'] = body


    def __str__(self):
        string  = super().__str__()
        string += self.string_separator + wrap_strings([('body', self.reply['body'])]
                                                      ,separator=self.string_separator
                                                      ,equal=self.string_equal)
        return string


class _File(_Reply):

    def __init__(self
                ,to
                ,name
                ,mediatype
                ,url
                ,size
                ,body=' '
                ,keyboard=None):
        _Reply.__init__(self, to, FILE_TYPE, keyboard)
        self.reply['body']     = body
        self.reply['fileName'] = name
        self.reply['fileType'] = mediatype
        self.reply['fileUrl']  = url
        self.reply['fileSize'] = size


    def __str__(self):
        string   = super().__str__()
        items    = [('media-type', self.reply['fileType'])
                   ,('name', self.reply['fileNme'])
                   ,('size', self.reply['fileSize'], "KB")
                   ,('URL', self.reply['fileUrl'])]
        if self.body and self.body != ' ':
            items.insert(2, ('body', self.file['body']))
        string += self.string_separator + wrap_strings(items
                                                      ,separator=self.string_separator
                                                      ,equal=self.string_equal)
        return string


class Image(_File):

    def __init__(self
                ,to
                ,name
                ,url
                ,size
                ,thumbnail_url
                ,width
                ,height
                ,body=' '
                ,keyboard=None):
        _File.__init__(self
                      ,to
                      ,name
                      ,IMAGE_FILE_TYPE
                      ,url
                      ,size
                      ,body
                      ,keyboard)
        self.reply['thumbnailUrl'] = thumbnail_url
        self.reply['imageWidth']   = width
        self.reply['imageHeight']  = height


    def __str__(self):
        string   = super().__str__()
        items    = [('width', self.reply['imageWidth'])
                   ,('height', self.reply['imageHeight'])
                   ,('thumbnail-URL', self.reply['thumbnailUrl'])]
        string  += self.string_separator + wrap_strings(items
                                                       ,separator=self.string_separator
                                                       ,equal=self.string_equal)
        return string


class Gif(_File):

    def __init__(self
                ,to
                ,name
                ,url
                ,size
                ,thumbnail_url
                ,width
                ,height
                ,body=' '
                ,keyboard=None):
        _File.__init__(self
                      ,to
                      ,name
                      ,GIF_FILE_TYPE
                      ,url
                      ,size
                      ,body
                      ,keyboard)
        self.reply['thumbnailUrl'] = thumbnail_url
        self.reply['imageWidth']   = width
        self.reply['imageHeight']  = height


    def __str__(self):
        string   = super().__str__()
        items    = [('width', self.reply['imageWidth'])
                   ,('height', self.reply['imageHeight'])
                   ,('thumbnail-URL', self.reply['thumbnailUrl'])]
        string  += self.string_separator + wrap_strings(items
                                                       ,separator=self.string_separator
                                                       ,equal=self.string_equal)
        return string


class Video(_File):

    def __init__(self
                ,to
                ,name
                ,url
                ,size
                ,duration
                ,thumbnail_url
                ,width
                ,height
                ,body=' '
                ,keyboard=None):
        _File.__init__(self
                      ,to
                      ,name
                      ,VIDEO_FILE_TYPE
                      ,url
                      ,size
                      ,body
                      ,keyboard)
        self.reply['fileDuration']    = duration
        self.reply['thumbnailUrl']    = thumbnail_url
        self.reply['thumbnailWidth']  = width
        self.reply['thumbnailHeight'] = height


    def __str__(self):
        string   = super().__str__()
        items    = [('duration', self.reply['fileDuration'], 'ms')
                   ,('thumbnail-width', self.reply['thumbnailWidth'])
                   ,('thumbnail-height', self.reply['thumbnailHeight'])
                   ,('thumbnail-URL', self.reply['thumbnailUrl'])]
        string  += self.string_separator + wrap_strings(items
                                                       ,separator=self.string_separator
                                                       ,equal=self.string_equal)
        return string


class PushToTalk(_File):

    def __init__(self
                ,to
                ,name
                ,url
                ,size
                ,duration
                ,body=' '
                ,keyboard=None):
        _File.__init__(self
                      ,to
                      ,name
                      ,PUSH_TO_TALK_FILE_TYPE
                      ,url
                      ,size
                      ,body
                      ,keyboard)
        self.reply['fileDuration'] = duration


    def __str__(self):
        string   = super().__str__()
        items    = [('duration', self.reply['fileDuration'], 'ms')]
        string  += self.string_separator + wrap_strings(items
                                                       ,separator=self.string_separator
                                                       ,equal=self.string_equal)
        return string


class Attachment(_File):

    def __init__(self, to, name, url, size, body=' ', keyboard=None):
        _File.__init__(self
                      ,to
                      ,name
                      ,ATTACHMENT_FILE_TYPE
                      ,url
                      ,size
                      ,body
                      ,keyboard)


class Location(_Reply):

    def __init__(self, to, latitude, longitude, keyboard=None):
        _Reply.__init__(self, to, LOCATION_TYPE, keyboard)
        self.reply['latitude']  = latitude
        self.reply['longitude'] = longitude


    def __str__(self):
        string   = super().__str__()
        items    = [('latitude', self.reply['latitude'])
                   ,('longitude', self.reply['longitude'])]
        string  += self.string_separator + wrap_strings(items
                                                       ,separator=self.string_separator
                                                       ,equal=self.string_equal)
        return string


class Contact(_Reply):

    def __init__(self
                ,to
                ,nickname
                ,avatar_url
                ,phone_number
                ,keyboard=None):
        _Reply.__init__(self, to, CONTACT_TYPE, keyboard)
        self.reply['nickName']  = nickname
        self.reply['avatarUrl'] = avatar_url
        self.reply['phoneNo']   = phone_number


    def __str__(self):
        string   = super().__str__()
        items    = [('nickname', self.reply['nickName'])
                   ,('phone-number', self.reply['phoneNo'])
                   ,('avatar-URL', self.reply['avatarlUrl'])]
        string  += self.string_separator + wrap_strings(items
                                                       ,separator=self.string_separator
                                                       ,equal=self.string_equal)
        return string


class KeyboardChange(_Reply):
    def __init__(self, to, keyboard):
        _Reply.__init__(self, to, KEYBOARD_CHANGE_TYPE, keyboard)
