@echo off
chcp 65001 >nul
title 观的 AI 工具箱 - 实用云端效率与接码工具导航 (Others)
:MENU
cls
echo ==============================================================================
echo       观的 AI 工具箱 · 实用云端效率与接码工具导航 (others)
echo ==============================================================================
echo.
echo   [1] 自动化邮箱 API (https://email.manageh.shop/)
echo       - Edu/Gmail/iCloud/Outlook 接码与批量开户 API 服务
echo.
echo   [2] Outlook 快速取件平台 (https://mail.chatai.codes/)
echo       - IMAP OAuth2 + Graph API 双协议并行取件与令牌刷新
echo.
echo   [3] ChatGPT Session -> sub2api / Codex 格式转换 (https://convert.13916454.xyz/)
echo       - 将 ChatGPT 会话凭据一键转为 sub2api, CPA, Cockpit, Codex 格式
echo.
echo   [4] 一键在默认浏览器中打开全部 3 个网站
echo.
echo   [0] 退出
echo.
echo ==============================================================================
set /p opt="请选择操作 [0-4]: "

if "%opt%"=="1" (
    start "" "https://email.manageh.shop/"
    goto MENU
)
if "%opt%"=="2" (
    start "" "https://mail.chatai.codes/"
    goto MENU
)
if "%opt%"=="3" (
    start "" "https://convert.13916454.xyz/"
    goto MENU
)
if "%opt%"=="4" (
    start "" "https://email.manageh.shop/"
    start "" "https://mail.chatai.codes/"
    start "" "https://convert.13916454.xyz/"
    goto MENU
)
if "%opt%"=="0" exit
goto MENU
