# AI 使用说明（该项目使用了哪些 AI 工具、生成了哪些部分、改了什么）

## 使用的 AI 工具
- **WorkBuddy（AI 助手）**：用于需求拆解、仓库分析、代码生成与改写、文档与演示文稿撰写。
- 代码运行/测试环境：Python 3.13，用于执行 `py_compile` 与单元测试（验证改动可运行）。

## AI 生成 / 改写的各部分

### 1. 仓库代码改动（fork 后的「校园模式」）
全部由 AI 在理解 LibreTranslate 源码结构后生成，并经过单元测试验证：

| 文件 | 说明 |
| --- | --- |
| `libretranslate/terminology.py` | 术语库（mask-and-restore 注入）、术语增删查 |
| `libretranslate/name_translit.py` | 中俄人名音译（规则 + 覆盖表） |
| `libretranslate/scenario_templates.py` | 场景模板引擎（通知/邮件/课件标题/会议邀请） |
| `libretranslate/campus_terms.json` | 种子术语库（课程/专业/行政/通用） |
| `libretranslate/campus_templates.json` | 场景模板定义 |
| `libretranslate/campus_names.json` | 已知师生姓名音译对照 |
| `libretranslate/templates/campus.html` | 校园模式前端页面 |
| `libretranslate/app.py` | 新增 6 个端点并将术语库接入 `/translate` |
| `libretranslate/main.py`、`default_values.py` | 新增 `--campus-mode` 等命令行参数 |
| `libretranslate/tests/test_campus.py` | 单元测试用例（已通过） |
| `README.md` | 新增 Campus Mode 章节 |

### 2. 项目策划书（Word/PDF）
由 AI 基于题目要点撰写，含：为什么值得做、与商业翻译服务的差异、术语库建设方案、
可推广院校、AGPL-3.0 合规处理。

### 3. 双创大赛 PPT
由 AI 根据策划书结构生成，共 16 页，覆盖痛点/方案/技术/模式/推广/合规。

## 人工复核与诚实声明
- **俄语术语准确性**：种子术语库中的俄文词条由 AI 根据公开知识生成，**建议由俄语母语者/外方
  教师复核**后再正式投入使用；系统已支持通过 UI/API 随时补充与修正。
- **人名音译为启发式**：`name_translit.py` 为拼音/字母的近似音译，覆盖表（campus_names.json）
  用于保证已知姓名准确；未收录姓名仅供近似参考，不应作为正式证件拼写依据。
- 所有 AI 生成代码均通过本地语法检查与单元测试；完整服务运行还需安装依赖并下载
  Argos 翻译模型（zh↔ru），这部分按 LibreTranslate 官方文档进行。
