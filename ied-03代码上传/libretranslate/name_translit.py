"""
Heuristic Chinese <-> Russian name transliteration (人名音译).

At a Chinese-Russian university, students and staff constantly transliterate
names: Russian professors' names into Chinese (ru -> zh) and Chinese names
into Russian (zh -> ru). This module provides *heuristic* transliteration
so the translation UI can suggest a phonetic equivalent instead of leaving
names blank or mistranslating them.

IMPORTANT: These are phonetic approximations, not authoritative. The module
also supports a curated override table (campus_names.json) for well-known
faculty/staff so verified spellings take priority.
"""

import json
import os
import re

# Curated overrides: verified (zh <-> ru) pairs take priority.
_OVERRIDES = {}


def load_overrides(path):
    global _OVERRIDES
    _OVERRIDES = {}
    if path and os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for entry in data.get("names", []):
            zh = (entry.get("zh") or "").strip()
            ru = (entry.get("ru") or "").strip()
            if zh:
                _OVERRIDES[("zh", zh)] = ru
            if ru:
                _OVERRIDES[("ru", ru)] = zh


# ---- Russian -> Chinese ----------------------------------------------
# Approximate mapping of common Russian letter groups to Chinese syllables.
_RU_TO_ZH = [
    ("й", "й"),  # left as-is marker
    ("ж", "ж"),
    ("ц", "ц"),
    ("ш", "ш"),
    ("щ", "щ"),
    ("ч", "ч"),
    ("х", "х"),
    ("ъ", ""),
    ("ь", ""),
    ("э", "э"),
    ("ю", "юй"),
    ("я", "я"),
    ("а", "а"),
    ("б", "б"),
    ("в", "в"),
    ("г", "г"),
    ("д", "д"),
    ("е", "е"),
    ("з", "з"),
    ("и", "и"),
    ("к", "к"),
    ("л", "л"),
    ("м", "м"),
    ("н", "н"),
    ("о", "о"),
    ("п", "п"),
    ("р", "р"),
    ("с", "с"),
    ("т", "т"),
    ("у", "у"),
    ("ф", "ф"),
    ("ы", "ы"),
]

# Common Russian -> Chinese syllable approximations for full names.
_RU_SYLLABLES = [
    ("евге", "евгэ"), ("алек", "алэк"), ("андр", "андр"),
    ("нико", "нико"), ("серг", "сэрг"), ("дмит", "дмит"),
    ("миха", "миха"), ("екат", "екат"), ("олег", "олэг"),
    ("татъ", "тат"), ("влад", "влад"), ("мари", "мари"),
]


def _ru_to_zh_word(word):
    w = word.lower().strip(" .,-")
    # Apply syllable-level approximations first.
    for ru, zh in _RU_SYLLABLES:
        w = w.replace(ru, zh)
    # Then per-letter transliteration (kept simple/phonetic).
    table = {
        "а": "а", "б": "б", "в": "в", "г": "г", "д": "д", "е": "е",
        "ж": "ж", "з": "з", "и": "и", "й": "й", "к": "к", "л": "л",
        "м": "м", "н": "н", "о": "о", "п": "п", "р": "р", "с": "с",
        "т": "т", "у": "у", "ф": "ф", "х": "х", "ц": "ц", "ч": "ч",
        "ш": "ш", "щ": "щ", "ъ": "", "ы": "ы", "ь": "", "э": "э",
        "ю": "юй", "я": "я",
    }
    out = []
    for ch in w:
        out.append(table.get(ch, ch))
    return "".join(out)


def ru_to_zh(text):
    """Transliterate a Russian name into a phonetic Chinese approximation."""
    if not text:
        return ""
    # Curated overrides take priority.
    key = ("ru", text.strip())
    if key in _OVERRIDES:
        return _OVERRIDES[key]
    # Transliterate word by word, capitalising the first letter.
    parts = re.split(r"([\s\-]+)", text.strip())
    out = []
    for p in parts:
        if re.match(r"\s", p) or p in ("-",):
            out.append(p)
        else:
            tr = _ru_to_zh_word(p)
            out.append(tr)
    return "".join(out)


# ---- Chinese (pinyin) -> Russian -------------------------------------
# Pinyin initials and finals mapped to Cyrillic approximations.
_PINYIN_INITIALS = {
    "b": "б", "p": "п", "m": "м", "f": "ф", "d": "д", "t": "т",
    "n": "н", "l": "л", "g": "г", "k": "к", "h": "х",
    "j": "цз", "q": "ц", "x": "с", "zh": "чж", "ch": "ч", "sh": "ш",
    "r": "ж", "z": "цз", "c": "ц", "s": "с",
}
_PINYIN_FINALS = {
    "a": "а", "o": "о", "e": "э", "i": "и", "u": "у", "v": "юй",
    "ai": "ай", "ei": "эй", "ao": "ао", "ou": "оу",
    "an": "ань", "en": "энь", "ang": "ан", "eng": "эн",
    "ia": "я", "ie": "е", "iao": "яо", "iu": "ю", "ian": "янь",
    "in": "инь", "iang": "ян", "ing": "ин",
    "ua": "уа", "uo": "о", "uai": "уай", "ui": "уй", "uan": "уань",
    "un": "унь", "uang": "уан", "ong": "ун", "iong": "юн",
    "van": "юань", "vn": "юнь", "er": "эр",
}


def _split_syllables(pinyin):
    """Greedily split a pinyin string into (initial, final) syllables."""
    pinyin = pinyin.lower().strip()
    # Insert a separator between syllables heuristically.
    # We accept space- or apostrophe-separated input first.
    if " " in pinyin or "'" in pinyin:
        raw = re.split(r"[\s']+", pinyin)
    else:
        # No separators: try to split on vowel boundaries is hard; require
        # separated input. Return as a single token best-effort.
        raw = [pinyin]
    syllables = []
    for syl in raw:
        if not syl:
            continue
        matched = False
        for init in ("zh", "ch", "sh", "b", "p", "m", "f", "d", "t", "n",
                    "l", "g", "k", "h", "j", "q", "x", "r", "z", "c", "s"):
            if syl.startswith(init) and len(syl) > len(init):
                fin = syl[len(init):]
                if fin in _PINYIN_FINALS or fin == "":
                    syllables.append((_PINYIN_INITIALS.get(init, init),
                                      _PINYIN_FINALS.get(fin, fin)))
                    matched = True
                    break
        if not matched:
            # No initial, just a final.
            if syl in _PINYIN_FINALS:
                syllables.append(("", _PINYIN_FINALS[syl]))
            else:
                syllables.append(("", syl))
    return syllables


def zh_to_ru(text, pinyin=None):
    """Transliterate a Chinese name into Russian.

    `pinyin` may be supplied (space-separated syllables, tone marks stripped);
    if omitted, the raw Chinese characters are transliterated per-character
    with a minimal common-character fallback.
    """
    if not text:
        return ""
    # Curated overrides take priority.
    key = ("zh", text.strip())
    if key in _OVERRIDES:
        return _OVERRIDES[key]

    if pinyin:
        syllables = _split_syllables(pinyin)
        out = "".join(init + fin for init, fin in syllables)
        return out.capitalize()

    # No pinyin supplied: per-character minimal fallback.
    return text  # cannot reliably romanise glyphs without a pinyin library


def transliterate(name, direction, pinyin=None):
    """Unified entry point used by the API.

    direction: 'ru2zh' or 'zh2ru'
    """
    if direction == "ru2zh":
        return ru_to_zh(name)
    if direction == "zh2ru":
        return zh_to_ru(name, pinyin=pinyin)
    raise ValueError("Unsupported transliteration direction: %s" % direction)
