"""
Campus terminology / glossary module for LibreTranslate.

This module powers the "校园术语库" (campus glossary) feature used at
Shenzhen MSU-BIT University (深圳北理莫斯科大学), a Chinese-Russian
cooperative university. The idea: when translating between 中文 (zh) and
русский (ru), known domain terms (course names, majors, administrative
words) should be translated with the *canonical* term from the glossary
instead of whatever the neural engine guesses.

Technique: "mask-and-restore" glossary injection.
  1. Find glossary terms present in the *source* text.
  2. Replace them with private-use-area placeholder tokens so the engine
     does not mangle them.
  3. Translate the masked text.
  4. Restore each placeholder with the canonical *target* term.

This keeps the change decoupled from the underlying translation engine
(Argos / CTranslate2) and requires no retraining.
"""

import json
import os
import re

# Private Use Area range, safe from normal text and most tokenizers.
TOKEN_OPEN = "\ue000"
TOKEN_CLOSE = "\ue001"

# Supported campus languages for the glossary.
CAMPUS_LANGS = ("zh", "ru")


class Term:
    """A single bilingual terminology entry."""

    __slots__ = ("zh", "ru", "category", "note")

    def __init__(self, zh="", ru="", category="", note=""):
        self.zh = (zh or "").strip()
        self.ru = (ru or "").strip()
        self.category = (category or "").strip()
        self.note = (note or "").strip()

    def as_dict(self):
        return {
            "zh": self.zh,
            "ru": self.ru,
            "category": self.category,
            "note": self.note,
        }

    def form(self, lang):
        return self.zh if lang == "zh" else self.ru


class TerminologyDB:
    """In-memory terminology database backed by a JSON file."""

    def __init__(self, path=None):
        self.path = path
        self.terms = []
        if path and os.path.isfile(path):
            self.load(path)

    # ---- persistence -------------------------------------------------
    def load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.terms = [Term(**t) for t in data.get("terms", [])]
        self.path = path
        return self

    def save(self, path=None):
        path = path or self.path
        if not path:
            raise ValueError("No path to save terminology database")
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        data = {"terms": [t.as_dict() for t in self.terms]}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.path = path

    # ---- mutations ---------------------------------------------------
    def add(self, zh, ru, category="", note=""):
        # De-duplicate on exact (zh, ru) pair.
        zh, ru = zh.strip(), ru.strip()
        for t in self.terms:
            if t.zh == zh and t.ru == ru:
                t.category = category or t.category
                t.note = note or t.note
                return t
        t = Term(zh, ru, category, note)
        self.terms.append(t)
        return t

    def remove(self, zh, ru):
        before = len(self.terms)
        self.terms = [t for t in self.terms if not (t.zh == zh and t.ru == ru)]
        return len(self.terms) != before

    def query(self, q=None, lang=None):
        q = (q or "").strip().lower()
        out = []
        for t in self.terms:
            if q:
                if q not in t.zh.lower() and q not in t.ru.lower():
                    continue
            if lang and lang in CAMPUS_LANGS:
                if not t.form(lang):
                    continue
            out.append(t.as_dict())
        return out

    # ---- glossary injection -----------------------------------------
    def _find(self, text, src_lang):
        """Return glossary terms whose source-language form is in `text`."""
        hits = []
        for t in self.terms:
            form = t.form(src_lang)
            if form and form in text:
                hits.append(t)
        # Longest first so nested terms are masked before shorter ones.
        hits.sort(key=lambda t: len(t.form(src_lang)), reverse=True)
        return hits

    def mask(self, text, src_lang):
        """Replace source-language terms with placeholder tokens.

        Returns (masked_text, mapping) where mapping is a list of
        (token, Term) pairs.
        """
        hits = self._find(text, src_lang)
        mapping = []
        for i, t in enumerate(hits):
            token = "%s%d%s" % (TOKEN_OPEN, i, TOKEN_CLOSE)
            text = text.replace(t.form(src_lang), token)
            mapping.append((token, t))
        return text, mapping

    def unmask(self, text, mapping, tgt_lang):
        """Restore placeholder tokens with canonical target-language terms."""
        for token, t in mapping:
            text = text.replace(token, t.form(tgt_lang))
        # Safety net: if any private-use tokens survived translation
        # mangled, drop them rather than leaking garbage to the user.
        text = re.sub(
            "%s[0-9]+%s" % (TOKEN_OPEN, TOKEN_CLOSE), "", text
        )
        return text

    def translate_with_glossary(self, text, src_lang, tgt_lang, translate_fn):
        """Run `translate_fn(masked_text)` then restore glossary terms."""
        masked, mapping = self.mask(text, src_lang)
        translated = translate_fn(masked)
        return self.unmask(translated, mapping, tgt_lang)

    def terms_used(self, text, src_lang):
        """Return glossary entries that appear in `text` (for UI display)."""
        return [t.as_dict() for t in self._find(text, src_lang)]


# Module-level singleton, initialised in app.create_app().
_db = None


def init(path):
    global _db
    if path and os.path.isfile(path):
        _db = TerminologyDB(path)
    else:
        # Fall back to the bundled seed glossary shipped with the fork.
        bundled = os.path.join(os.path.dirname(__file__), "campus_terms.json")
        _db = TerminologyDB(bundled if os.path.isfile(bundled) else None)
    return _db


def get_db():
    return _db
