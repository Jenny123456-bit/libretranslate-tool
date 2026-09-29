"""Tests for the campus-mode modules (run without the translation model)."""

import json
import os
import sys
import unittest

# Import the standalone campus modules directly (without triggering the
# libretranslate package __init__, which requires argostranslate).
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
if PKG not in sys.path:
    sys.path.insert(0, PKG)

import terminology  # noqa: E402
import name_translit  # noqa: E402
import scenario_templates  # noqa: E402


class TestTerminology(unittest.TestCase):
    def setUp(self):
        self.db = terminology.TerminologyDB()
        self.db.add("数据结构", "структуры данных", "课程")
        self.db.add("操作系统", "операционная система", "课程")

    def test_mask_unmask_roundtrip(self):
        text = "今天学习数据结构，明天考操作系统。"
        masked, mapping = self.db.mask(text, "zh")
        self.assertNotIn("数据结构", masked)
        restored = self.db.unmask(masked, mapping, "ru")
        self.assertIn("структуры данных", restored)
        self.assertIn("операционная система", restored)

    def test_terms_used(self):
        hits = self.db.terms_used("数据结构很重要", "zh")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["ru"], "структуры данных")

    def test_add_dedup(self):
        before = len(self.db.terms)
        self.db.add("数据结构", "структуры данных")
        self.assertEqual(len(self.db.terms), before)

    def test_glossary_wrapper(self):
        # A fake translator that simply appends a marker, to prove the
        # placeholder survives and the canonical term is restored.
        def fake_translate(text):
            # Simulate an engine that keeps the private-use token verbatim.
            return text.replace("__KEEP__", "")  # no-op; tokens preserved

        masked, mapping = self.db.mask("数据结构", "zh")
        translated = fake_translate(masked)
        out = self.db.unmask(translated, mapping, "ru")
        self.assertEqual(out, "структуры данных")


class TestNameTranslit(unittest.TestCase):
    def setUp(self):
        name_translit.load_overrides(
            os.path.join(PKG, "campus_names.json"))

    def test_override_ru2zh(self):
        # Override table should return the Chinese form.
        self.assertEqual(name_translit.transliterate("Чжан Вэй", "ru2zh"), "张伟")

    def test_override_zh2ru(self):
        self.assertEqual(name_translit.transliterate("张伟", "zh2ru"), "Чжан Вэй")

    def test_heuristic_ru2zh(self):
        # No override -> phonetic approximation, non-empty.
        out = name_translit.ru_to_zh("Петров")
        self.assertTrue(len(out) > 0)


class TestTemplates(unittest.TestCase):
    def setUp(self):
        self.eng = scenario_templates.TemplateEngine(
            os.path.join(PKG, "campus_templates.json"))

    def test_list(self):
        ids = [t["id"] for t in self.eng.list()]
        self.assertIn("notice", ids)
        self.assertIn("courseware_title", ids)

    def test_render_bilingual(self):
        out = self.eng.render_bilingual("courseware_title", {
            "course": "数据结构", "lesson": "3", "teacher": "Иванов"})
        self.assertIn("数据结构", out["zh"])
        # The Russian skeleton should keep its structure and insert the fields.
        self.assertIn("занятие", out["ru"])
        self.assertIn("преподаватель", out["ru"])
        self.assertIn("Иванов", out["ru"])

    def test_render_single(self):
        out = self.eng.render("notice", "ru", {
            "date": "2026-09-27", "title": "Собрание", "body": "Текст", "contact": "Деканат"})
        self.assertIn("Уведомление", out)


if __name__ == "__main__":
    unittest.main()
