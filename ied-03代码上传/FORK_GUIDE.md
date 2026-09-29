# Fork 发布指南与仓库核验（深圳北理莫斯科大学 · 中俄双语校园模式）

本项目是 [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate) 的一个 fork，
新增了面向中俄合作办学院校的「校园模式」。

> 说明：本仓库的**全部代码改动已在本地完成并通过测试**。由于提交环境（WorkBuddy 沙箱）
> 未登录 GitHub，无法代为执行 `git push`。请按下方步骤 **1 分钟** 即可把改动发布到你自己的
> GitHub fork，得到题目要求的「fork 后的仓库链接」。

---

## 一、发布到你自己的 fork（得到提交链接）

### 方式 A：用 GitHub CLI（推荐，一条命令）
```bash
# 1) 登录你的 GitHub（浏览器里完成授权）
gh auth login

# 2) 创建你自己的 fork（会自动添加为 origin）
gh repo fork LibreTranslate/LibreTranslate --clone=false

# 3) 在当前本地仓库里指向你的 fork 并推送
git remote rename origin upstream        # 把上游保留为 upstream
git remote add origin https://github.com/Jenny123456-bit/LibreTranslate.git
git push -u origin campus-mode

# 4) 提交链接即为：
#    https://github.com/Jenny123456-bit/LibreTranslate/tree/campus-mode
```

### 方式 B：网页手动 fork
1. 打开 https://github.com/LibreTranslate/LibreTranslate ，点击右上角 **Fork**。
2. 在本地产出目录执行：
   ```bash
   git remote rename origin upstream
   git remote add origin https://github.com/Jenny123456-bit/LibreTranslate.git
   git push -u origin campus-mode
   ```

> 分支名为 `campus-mode`，所有改动都在该分支；`main` 保持与上游一致，方便后续回馈上游。

---

## 二、仓库核验清单（可对照检查）

- [ ] 分支 `campus-mode` 已推送到你的 fork
- [ ] `libretranslate/terminology.py` 存在（术语库核心）
- [ ] `libretranslate/name_translit.py` 存在（人名音译）
- [ ] `libretranslate/scenario_templates.py` 存在（场景模板）
- [ ] `libretranslate/campus_terms.json` / `campus_templates.json` / `campus_names.json` 存在（种子数据）
- [ ] `libretranslate/templates/campus.html` 存在（校园模式页面）
- [ ] `libretranslate/app.py` 含 `/terminology`、`/campus/templates`、`/campus/render`、
      `/campus/transliterate`、`/bilingual`、`/campus` 端点
- [ ] `README.md` 含「Campus Mode」章节
- [ ] 测试通过：`python libretranslate/tests/test_campus.py`（无需翻译模型，10 项全过）

本地快速核验命令：
```bash
python -m py_compile libretranslate/app.py libretranslate/main.py \
  libretranslate/default_values.py libretranslate/terminology.py \
  libretranslate/name_translit.py libretranslate/scenario_templates.py
python libretranslate/tests/test_campus.py
```

---

## 三、AGPL-3.0 传染性约束的处理方式

LibreTranslate 采用 **AGPL-3.0**（最强传染性 copyleft）。核心约束：
**只要你把修改后的程序作为网络服务提供给他人，就必须向这些用户提供修改后的完整源码。**

本项目采取的组合策略：

1. **校内非商业使用**：本工具定位为「单所大学内部的非商业辅助工具」，部署在校园内网 /
   校园账号体系内，面向本校师生，不对外公开运营、不收费。
2. **源码始终公开、可获取**：所有改动自托管在本 fork 中，任何人（包括通过校园网访问服务
   的用户）都能获得对应源码（本仓库即源码）。
3. **回馈上游**：将改动以 PR 形式提交回 LibreTranslate 上游，使社区共同受益，也避免长期
   维护私有分支。
4. **合规提示**：若未来要对外开放服务或商业化，需另行与校方/法务确认，并继续履行 AGPL 的
   源码提供义务；本 fork 不授予任何超出 AGPL-3.0 的额外许可。

> 商标提示：LibreTranslate 名称与 Logo 受 [TRADEMARK.md](TRADEMARK.md) 约束，校内非商业
> 使用一般不受影响，但对外宣传时请留意。
