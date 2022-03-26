import re


def clean_key(k):
    replace_re = re.compile(r"[. ]")
    new_key = replace_re.sub("_", k).lower()
    return new_key
