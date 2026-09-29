@echo off
chcp 65001 >nul
echo ===================================================
echo  深圳北理莫斯科大学 中俄双语校园翻译 - 一键发布脚本
echo  仓库: Jenny123456-bit/LibreTranslate  (campus-mode)
echo ===================================================
echo.
echo  [前置] 请先确认：
echo    1) 已安装 Git (https://git-scm.com) 与 GitHub CLI (https://cli.github.com)
echo    2) 已执行过:  gh auth login   （浏览器里登录你的 GitHub 账号）
echo    3) 已在 github.com 网页上 Fork 了 LibreTranslate 到你账号
echo       （打开 https://github.com/LibreTranslate/LibreTranslate 点右上角 Fork）
echo.
pause

echo  [1/3] 配置 git 使用 gh 的凭据（若已安装 gh）...
where gh >nul 2>nul && gh auth setup-git

echo  [2/3] 设置远程地址为你的 fork ...
git remote remove origin 2>nul
git remote add origin https://github.com/Jenny123456-bit/LibreTranslate.git

echo  [3/3] 推送 campus-mode 分支 ...
git push -u origin campus-mode

echo.
if errorlevel 1 (
  echo  推送失败。常见原因：
  echo   - 还没在网页 Fork，或 fork 用户名不是 Jenny123456-bit
  echo   - 未执行 gh auth login / 凭据失效（重新 gh auth login）
  echo   - 用密码 push 被拒：GitHub 仅支持 Personal Access Token (PAT) 作为密码
) else (
  echo  成功！你的链接现在应可访问：
  echo  https://github.com/Jenny123456-bit/LibreTranslate/tree/campus-mode
)
echo.
pause
