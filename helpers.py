def replace_all(text, d):
    for key, value in d.items():
        text = text.replace('${' + key + '}', value)

    return text
