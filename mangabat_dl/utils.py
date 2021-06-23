import re
from typing import Any

class ContextVar:
    """
    like tkinter.StringVar,
    but with get() and set() only

    you can store any type in this thing

    """
    def __init__(self, context=None):
        self._ctx = context

    def set(self, context: Any=None):
        self._ctx = context

    def get(self):
        return self._ctx

class StringVar:
    """
    adapted from tkinter.StringVar()
    with set() and get() only
    """
    def __init__(self, initial_value: str=None):
        self._value = initial_value or ''

    def set(self, value: str):
        self._value = value

    def get(self):
        return self._value

# This is taken from https://m.mangabat.com/themes/hm/js/custom.js?v=02102021
# This will be re-create into python function
# function change_alias(alias) {
#     var str = alias;
#     str = str.toLowerCase();
#     str = str.replace(/à|á|ạ|ả|ã|â|ầ|ấ|ậ|ẩ|ẫ|ă|ằ|ắ|ặ|ẳ|ẵ/g, "a");
#     str = str.replace(/è|é|ẹ|ẻ|ẽ|ê|ề|ế|ệ|ể|ễ/g, "e");
#     str = str.replace(/ì|í|ị|ỉ|ĩ/g, "i");
#     str = str.replace(/ò|ó|ọ|ỏ|õ|ô|ồ|ố|ộ|ổ|ỗ|ơ|ờ|ớ|ợ|ở|ỡ/g, "o");
#     str = str.replace(/ù|ú|ụ|ủ|ũ|ư|ừ|ứ|ự|ử|ữ/g, "u");
#     str = str.replace(/ỳ|ý|ỵ|ỷ|ỹ/g, "y");
#     str = str.replace(/đ/g, "d");
#     str = str.replace(/ /g, "_");
#     str = str.replace(/[^0-9a-z\s]/gi, '_');
#     str = str.replace(/_+_/g, "_");
#     str = str.replace(/^\_+|\_+$/g, "");
#     return str;
# }
def convert_query_search(query_search: str):
    """
    Convert query search into readable alias
    based on mangabat Javascript `change_alias()` function
    """
    string = query_search.lower()
    REGEXS_CONVERT_ALIAS = [
        [
            re.compile(r'à|á|ạ|ả|ã|â|ầ|ấ|ậ|ẩ|ẫ|ă|ằ|ắ|ặ|ẳ|ẵ'),
            "a"
        ],
        [
            re.compile(r'è|é|ẹ|ẻ|ẽ|ê|ề|ế|ệ|ể|ễ'),
            "e"
        ],
        [
            re.compile(r'ì|í|ị|ỉ|ĩ'),
            "i"
        ],
        [
            re.compile(r'ò|ó|ọ|ỏ|õ|ô|ồ|ố|ộ|ổ|ỗ|ơ|ờ|ớ|ợ|ở|ỡ'),
            "o"
        ],
        [
            re.compile(r'ù|ú|ụ|ủ|ũ|ư|ừ|ứ|ự|ử|ữ'),
            "u"
        ],
        [
            re.compile(r'ỳ|ý|ỵ|ỷ|ỹ'),
            "y"
        ],
        [
            re.compile(r'đ'),
            "d"
        ],
        [
            re.compile(r' '),
            "_"
        ],
        [
            re.compile(r'[^0-9a-z\s]', re.IGNORECASE),
            '_'
        ],
        [
            re.compile(r'_+_'),
            '_'
        ],
        [
            re.compile(r'^\_+|\_+$'),
            ''
        ]
    ]
    alias = ContextVar(string)
    for context in REGEXS_CONVERT_ALIAS:
        regex = context[0]
        replacer = context[1]
        result = regex.sub(replacer, alias.get())
        alias.set(result)
    return alias.get()

# Adapted from
# https://github.com/mansuf/mangadex-downloader/blob/v0.0.5/mangadex_downloader/constants.py#L129
def filter_forbidden_names(string: str):
    """Filter symbol names to prevent error when creating folder or file"""
    result = ''
    UNIX_FORBIDDEN_NAMES = ['/']
    MAC_OS_FORBIDDEN_NAMES = [':']
    WINDOWS_FORBIDDEN_NAMES = ['<', '>', ':', '\"', '/', '\\', '|', '?', '*']
    for word in string:
        if word in UNIX_FORBIDDEN_NAMES:
            continue
        elif word in MAC_OS_FORBIDDEN_NAMES:
            continue
        elif word in WINDOWS_FORBIDDEN_NAMES:
            continue
        else:
            result += word
    final = StringVar(result)
    # remove dot or space in ends words
    # to prevent error when writing file or folder in windows
    while True:
        ctx = final.get()
        if ctx[len(ctx) - 1] == '.' or ctx[len(ctx) - 1] == ' ':
            r = ctx[0:len(ctx) - 1]
            final.set(r)
        else:
            break
    return final.get()