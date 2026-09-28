# 中俄双语校园翻译工具 · Campus Mode for LibreTranslate

基于 [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate)（AGPL-3.0，可自托管、离线运行、数据不出本地）的校园定制分支。面向**深圳北理莫斯科大学**等中俄合作办学场景的中俄双语翻译 / 术语工具。

**本项目 fork 地址：** `https://github.com/Jenny123456-bit/LibreTranslate`

---

## 一、为什么要做这个

深圳北理莫斯科大学是中俄合作办学，校内存在大量俄语 / 中文双语场景：课程术语、教材、通知、与外方老师的邮件沟通。通用商业翻译（如 Google 翻译、百度翻译）存在三个问题：

- **术语不准**：「数据结构」这类专业词常被翻错，且每次结果不一致；
- **数据出境**：学生作业、内部通知传到境外服务器，存在合规风险；
- **场景缺失**：没有面向「通知 / 邮件 / 课件标题」的模板，也没有处理缩写、课程编号、人名音译的能力。

本项目在 LibreTranslate 之上增加「校园模式」，让翻译优先采用自建术语库、保护校园特有信息、并一键产出中俄对照。

---

## 二、核心功能

- **术语库优先翻译**：课程 / 专业 / 行政词汇中俄双向（如「数据结构」→ *структура данных*）。翻译前注入、翻译后还原，保证术语一致。入口：`/translate` 自动启用、`/terminology` 管理。
- **场景模板**：通知、邮件、课件标题、会议邀请的中俄对照一键生成。入口：`/campus/templates`、`/campus/render`。
- **人名音译**：中俄人名启发式音译 + 已知教师覆盖表，避免音译出错。入口：`/campus/transliterate`。
- **一键对照排版**：返回原文、术语感知译文、命中术语三栏，便于双列排版。入口：`/bilingual`。

---

## 三、快速开始

```bash
# 安装依赖后，启用校园模式启动
libretranslate --campus-mode

# 可选：指定你自己的数据文件
libretranslate --campus-mode \
  --terminology-file /path/to/terms.json \
  --campus-names-file /path/to/names.json \
  --campus-templates-file /path/to/templates.json
```

启动后在 Web UI 打开 `/campus` 即可使用校园模式界面。未启用 `--campus-mode` 时，校园端点返回 `403`，`/translate` 退化为普通翻译（忽略术语库）。

完整服务运行还需按官方文档安装依赖并下载 Argos 翻译模型（zh↔ru）。详见上游 [Quickstart](https://docs.libretranslate.com/)。

---

## 四、关键文件

```
libretranslate/
├── terminology.py          # 术语库：mask-and-restore 注入与还原
├── name_translit.py        # 中俄人名音译 + 覆盖表
├── scenario_templates.py   # 场景模板引擎
├── campus_terms.json       # 种子术语库（中俄）
├── campus_templates.json   # 场景模板（通知/邮件/课件/会议）
├── campus_names.json       # 已知教师人名覆盖表
├── templates/campus.html   # 校园模式网页界面
└── tests/test_campus.py    # 单元测试（无需翻译模型即可运行）
```

新增 API 端点（均在 `app.py`，由 `--campus-mode` 控制）：`GET/POST /terminology`、`GET /campus/templates`、`POST /campus/render`、`POST /campus/transliterate`、`POST /bilingual`、`GET /campus`。

---

## 五、术语库怎么建

1. **种子**：由项目预置 `campus_terms.json`（课程 / 专业 / 行政词，含俄文）；
2. **众包**：师生通过 UI 或 API 提交新词、纠错；
3. **母语复核**：由俄语母语者 / 外方教师审核（种子俄文为 AI 初稿，正式使用前需复核）；
4. **结构化**：统一为 `{zh, ru, domain}` 格式，按课程 / 学院分组；
5. **共建**：可导出 JSON 与其它中外合办院校共享。

---

## 六、与商业翻译服务的差异

- **数据**：本项目自托管、不出本地、离线可用；商业 API 需上传至境外服务器。
- **术语**：本项目自建库优先、结果一致；商业翻译不保证专业词准确。
- **场景**：本项目内置通知 / 邮件 / 课件模板；商业翻译通用、无校园模板。
- **合规**：本项目 AGPL 开源可审计；商业翻译闭源、条款不可控。
- **成本**：本项目校内非商业免费；商业翻译按量计费。

---

## 七、许可与合规（AGPL-3.0）

LibreTranslate 采用 **AGPL-3.0**——若你将修改后的服务通过网络对外提供，必须公开相应源码。本分支的处理策略：

- **用途**：校内非商业使用，单校范围；
- **源码公开**：本仓库即改动后的完整源码，始终可获取；
- **回馈上游**：改动以独立模块实现，便于合并回上游；
- **对外服务时**：履行源码提供义务，不闭源。

---

## 八、可推广院校

同类型中俄 / 中外合作办学均可复用本框架，例如：深圳北理莫斯科大学、江苏师范大学圣彼得堡彼尔姆大学联合学院、各类「俄语 + 专业」合作项目，以及其它需要自建术语库 + 数据本地化的小语种校园场景。

---

##

翻译引擎由 [Argos Translate](https://github.com/argosopentech/argos-translate) 提供；上游项目 [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate) 采用 AGPL-3.0 许可。

本分支继承自 LibreTranslate，沿用 [GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html)。
