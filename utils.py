from locales import langdict

def gen_lang_keyboard():
    langs = list(langdict)
    keyb = []
    while langs:
        lang = langdict[langs[0]]["main"]
        a = [
            (f"{lang['language_flag']} {lang['language_name']}",
              "set_lang " + langs[0],)
        ]
        langs.pop(0)
        if langs:
            lang = langdict[langs[0]]["main"]
            a.append((f"{lang['language_flag']} {lang['language_name']}",
                   "set_lang " + langs[0],))
            langs.pop(0)
        keyb.append(a)
    return keyb
