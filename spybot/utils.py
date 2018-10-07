

def wrap_strings(objects, separator=" ", equal=':'):
        strings   = []
        for item in objects:
            if type(item) == str:
                strings.append(item)
                continue
            if len(item) == 3:
                (pre, value, post) = item
                strings.append("{}{}{}{}".format(pre, equal, value, post))
                continue
            (pre, value) = item
            strings.append("{}{}{}".format(pre, equal, value))
        return separator.join(strings)
