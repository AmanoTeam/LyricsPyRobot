import inspect
import json
import os.path
from functools import partial, wraps
from glob import glob

import db

enabled_locales = [
    "en-US",  # English
    "pt-BR",  # Portuguese (Brazil)
    "he-IL",  # Hebrew
    "es-ES",  # Spanish
    "pt-BR2",  # Protugês zoeiro
    "en-HT",  # English HiperTranslate
]

default_language = "en-US"


def cache_localizations(files: list[str]) -> dict[str, dict[str, dict[str, str]]]:
    ldict = {lang: {} for lang in enabled_locales}
    for file in files:
        _, lname, pname = file.split(os.path.sep)
        pname = pname.split(".")[0]
        dic = json.load(open(file, encoding="utf-8"))
        dic.update(ldict[lname].get(pname, {}))
        ldict[lname][pname] = dic
    return ldict


jsons: list[str] = []

for locale in enabled_locales:
    jsons += glob(os.path.join("locales", locale, "*.json"))

langdict = cache_localizations(jsons)


def get_locale_string(
    dic: dict, language: str, default_context: str, key: str, context: str = None
) -> str:
    if context:
        default_context = context
        dic = langdict[language].get(context, langdict[default_language][context])
    res: str = (
        dic.get(key) or langdict[default_language][default_context].get(key) or key
    )
    return res


def get_lang(cid) -> str:
    lang = db.db_get_lang(cid)

    lang = lang[0] if lang and lang[0] else default_language

    if len(lang.split("-")) == 1:
        # Try to find a language that starts with the provided language_code
        for locale_ in enabled_locales:
            if locale_.startswith(lang):
                lang = locale_
    elif lang.split("-")[1].islower():
        lang = lang.split("-")
        lang[1] = lang[1].upper()
        lang = "-".join(lang)
    return lang if lang in enabled_locales else default_language


def use_chat_lang(context=None):
    if not context:
        frame = inspect.stack()[1]
        context = frame[0].f_code.co_filename.split(os.path.sep)[-1].split(".")[0]

    def decorator(func):
        @wraps(func)
        async def wrapper(client, message):
            cid = message.from_user.id
            lang = get_lang(cid)

            dic = langdict.get(lang, langdict[default_language])

            lfunc = partial(get_locale_string, dic.get(context, {}), lang, context)
            return await func(client, message, lfunc)

        return wrapper

    return decorator


def use_user_lang(cid, context=None):
    lang = get_lang(cid)

    if not context:
        frame = inspect.stack()[1]
        context = frame[0].f_code.co_filename.split(os.path.sep)[-1].split(".")[0]

    dic = langdict.get(lang, langdict[default_language])
    return partial(get_locale_string, dic.get(context, {}), lang, context)
