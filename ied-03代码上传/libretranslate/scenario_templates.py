"""
Scenario templates for the campus translation tool.

Many campus messages follow fixed patterns: 通知 (notices), 邮件 (emails),
课件标题 (courseware titles), 会议邀请 (meeting invites). Instead of
translating free text every time, users pick a template, fill in a few
fields, and get a ready-made 中文 / русский bilingual pair.

Templates use Python str.format-style placeholders, e.g. {date}, {course},
{name}. Each template stores both the zh and ru skeletons.
"""

import json
import os


DEFAULT_TEMPLATES = [
    {
        "id": "notice",
        "category": "通知",
        "fields": ["date", "title", "body", "contact"],
        "zh": "【通知】{date}\n主题：{title}\n{body}\n联系人：{contact}",
        "ru": "[Уведомление] {date}\nТема: {title}\n{body}\nКонтакт: {contact}",
    },
    {
        "id": "email",
        "category": "邮件",
        "fields": ["to", "subject", "greeting", "body", "sign"],
        "zh": "收件人：{to}\n主题：{subject}\n{greeting}\n{body}\n{sign}",
        "ru": "Кому: {to}\nТема: {subject}\n{greeting}\n{body}\n{sign}",
    },
    {
        "id": "courseware_title",
        "category": "课件标题",
        "fields": ["course", "lesson", "teacher"],
        "zh": "《{course}》第{lesson}讲 — 主讲：{teacher}",
        "ru": "«{course}», занятие {lesson} — преподаватель: {teacher}",
    },
    {
        "id": "meeting_invite",
        "category": "会议邀请",
        "fields": ["date", "time", "place", "topic", "host"],
        "zh": "会议邀请\n时间：{date} {time}\n地点：{place}\n议题：{topic}\n主持人：{host}",
        "ru": "Приглашение на собрание\nВремя: {date} {time}\nМесто: {place}\nПовестка: {topic}\nВедущий: {host}",
    },
]


class TemplateEngine:
    def __init__(self, path=None):
        self.path = path
        if path and os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                self.templates = json.load(f).get("templates", DEFAULT_TEMPLATES)
        else:
            self.templates = DEFAULT_TEMPLATES

    def list(self):
        return [
            {"id": t["id"], "category": t.get("category", ""), "fields": t["fields"]}
            for t in self.templates
        ]

    def get(self, template_id):
        for t in self.templates:
            if t["id"] == template_id:
                return t
        return None

    def render(self, template_id, lang, fields):
        t = self.get(template_id)
        if t is None:
            raise KeyError("Unknown template: %s" % template_id)
        skeleton = t["zh"] if lang == "zh" else t["ru"]
        # Fill only the placeholders that exist; leave others as-is.
        try:
            return skeleton.format(**fields)
        except (KeyError, IndexError):
            # Fall back to safe substitution of provided fields.
            out = skeleton
            for k, v in fields.items():
                out = out.replace("{%s}" % k, str(v))
            return out

    def render_bilingual(self, template_id, fields):
        return {
            "zh": self.render(template_id, "zh", fields),
            "ru": self.render(template_id, "ru", fields),
        }


_engine = None


def init(path):
    global _engine
    _engine = TemplateEngine(path)
    return _engine


def get_engine():
    return _engine
