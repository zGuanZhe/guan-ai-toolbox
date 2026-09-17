@echo off
chcp 65001 >nul
title 观的 AI 工具箱 - 通用总控制台
:MENU
cls
echo ==============================================================================
echo                 观的 AI 工具箱 (Guan's AI Toolbox) - 通用总控中心
echo      [WorkBuddy / Trae / Qoder / ZCode / ClaudeCode / Antigravity / OpenAI]
echo ==============================================================================
echo.
echo   [1] 跨工具会话记录管理与一键恢复中心 (restore-histry)
echo       - 分工具隔离管理: WorkBuddy, Trae, ZCode, Claude, Antigravity, ChatGPT
echo.
echo   [2] 多厂家自动注册与智能账号池一键切换中枢 (register)
echo       - 参考 any-auto-register 与 Antigravity-Manager
echo       - 集成 Camoufox 指纹反爬浏览器: WorkBuddy, Qoder, OpenAI, Tavily, Grok
echo.
echo   [3] 通用 Skills 与 MCP 协议扩展库 (skills/mcp)
echo       - 14 款核心生产级 MCP 服务与全端同步 (CC-Switch, Claude, Codex, WorkBuddy)
echo       - 74+ 国际顶级品牌设计系统 (getdesign.md) 与 CCSwitch 状态机
echo.
echo   [4] 通用 Instruct 提示词与指令工程体系 (instruct)
echo       - 认知编译器体系: Antigravity, Claude Code, OpenAI Codex
echo.
echo   [5] 扩展工具与前沿实验室 (others - ModelTrace 等)
echo       - 模型路由检测与主动归因 (ModelTrace): 识别假冒套壳模型、测中转真实性
echo.
echo   [6] 启动全功能可视化 Web 控制台 (Letters.app 风格现代化仪表盘)
echo       - 整合会话恢复、账号池、14款MCP全端强刷、指令工程与在线测谎
echo.
echo   [0] 退出
echo.
echo ==============================================================================
set /p opt="请输入功能序号 [0-6]: "

if "%opt%"=="1" goto RESTORE
if "%opt%"=="2" goto REGISTER
if "%opt%"=="3" goto MCP
if "%opt%"=="4" goto INSTRUCT
if "%opt%"=="5" goto OTHERS
if "%opt%"=="6" goto WEB
if "%opt%"=="0" goto EXIT
goto MENU

:RESTORE
cls
cd /d "%~dp0restore-histry"
call "启动会话恢复中心.bat"
cd /d "%~dp0"
goto MENU

:REGISTER
cls
cd /d "%~dp0register"
call "启动账号与注册中心.bat"
cd /d "%~dp0"
goto MENU

:MCP
cls
echo ==============================================================================
echo       Skills 技能库、设计系统与 MCP 协议中枢 (CCSwitch 状态机管理模式)
echo ==============================================================================
echo.
echo   [1] 查看本地精选技能清单 (Curated Skills Hub)
echo   [2] 宿主状态诊断 (CCSwitch 模式: Active / Inactive 状态机)
echo   [3] 激活/启用指定技能 (CCSwitch Enable -> 载入活体上下文)
echo   [4] 停用/休眠指定技能 (CCSwitch Disable -> 移出活体上下文)
echo   [5] 一键切换工作流预设 (CCSwitch Profiles: fullstack, python, frontend 等)
echo   [6] 查看全网 AI Agent 技能与 MCP 生态平台大全 (NETWORK_PLATFORMS)
echo   [7] 查看与注入 74+ 国际顶级品牌设计系统 (getdesign.md)
echo   [8] 从网络 Git 仓库导入新技能至本地池
echo   [9] 查看 14 款核心生产级 MCP 服务清单 (Curated 14 MCP Hub)
echo   [10] 巡检 14 款 MCP 全端同步状态 (CC-Switch / Claude / Codex / WorkBuddy)
echo   [11] 一键同步 14 款 MCP 至全端客户端 (Sync All Clients)
echo   [12] 查看 14 款 MCP 详细使用手册与 OAuth 认证指南 (14_MCPS_GUIDE.md)
echo   [0] 返回主菜单
echo.
echo ==============================================================================
set /p sopt="请选择操作 [0-12]: "
if "%sopt%"=="1" (
    python "%~dp0skills\tools\skill_manager.py" --list
    pause
    goto MCP
)
if "%sopt%"=="2" (
    python "%~dp0skills\tools\skill_manager.py" --status
    pause
    goto MCP
)
if "%sopt%"=="3" (
    set /p skname="请输入要激活的技能名称 (如 tdd-workflow, frontend-design): "
    python "%~dp0skills\tools\skill_manager.py" --enable "%skname%" --target "%~dp0"
    pause
    goto MCP
)
if "%sopt%"=="4" (
    set /p skname="请输入要停用的技能名称: "
    python "%~dp0skills\tools\skill_manager.py" --disable "%skname%" --target "%~dp0"
    pause
    goto MCP
)
if "%sopt%"=="5" (
    python "%~dp0skills\tools\skill_manager.py" --profiles
    set /p prof="请输入要应用的 Profile 名称 (如 fullstack, frontend, python-dev, office-docs): "
    python "%~dp0skills\tools\skill_manager.py" --profile "%prof%" --target "%~dp0"
    pause
    goto MCP
)
if "%sopt%"=="6" (
    python "%~dp0skills\tools\skill_manager.py" --platforms
    pause
    goto MCP
)
if "%sopt%"=="7" (
    python "%~dp0skills\tools\skill_manager.py" --brands
    echo.
    set /p bname="请输入要复制注入的品牌名称 (直接回车跳过): "
    if not "%bname%"=="" (
        python "%~dp0skills\tools\skill_manager.py" --copy-design "%bname%" --target "%~dp0"
    )
    pause
    goto MCP
)
if "%sopt%"=="8" (
    set /p gurl="请输入网络 Git 技能仓库 URL: "
    python "%~dp0skills\tools\skill_manager.py" --import-git "%gurl%"
    pause
    goto MCP
)
if "%sopt%"=="9" (
    python "%~dp0skills\tools\skill_manager.py" --mcp-list
    pause
    goto MCP
)
if "%sopt%"=="10" (
    python "%~dp0skills\tools\skill_manager.py" --mcp-status
    pause
    goto MCP
)
if "%sopt%"=="11" (
    python "%~dp0skills\tools\skill_manager.py" --mcp-sync all
    pause
    goto MCP
)
if "%sopt%"=="12" (
    type "%~dp0skills\mcp\14_MCPS_GUIDE.md"
    pause
    goto MCP
)
goto MENU

:INSTRUCT
cls
echo ==============================================================================
echo            Instruct 提示词与指令体系 (instruct)
echo ==============================================================================
echo.
echo   [1] Google Antigravity / Gemini CLI 指令框架 (antigravity-instruct)
echo   [2] Anthropic Claude Code 确定性指令系统 (claude-instruct)
echo   [3] OpenAI Codex / GPT CLI 免杀高精契约 (gpt-instruct v2)
echo   [4] 查看完整开发与操作手册 (README.md)
echo   [0] 返回主菜单
echo.
echo ==============================================================================
set /p iopt="请选择指令系统 [0-4]: "
if "%iopt%"=="1" (
    cd /d "%~dp0instruct\antigravity-instruct"
    python agy-instruct.py --status
    pause
    goto INSTRUCT
)
if "%iopt%"=="2" (
    cd /d "%~dp0instruct\claude-instruct"
    python claude-instruct.py --status
    pause
    goto INSTRUCT
)
if "%iopt%"=="3" (
    cd /d "%~dp0instruct\gpt-instruct"
    python codex-instruct-v2.py --status
    pause
    goto INSTRUCT
)
if "%iopt%"=="4" (
    type "%~dp0instruct\README.md"
    pause
    goto INSTRUCT
)
goto MENU

:OTHERS
cls
echo ==============================================================================
echo       观的 AI 工具箱 · 扩展工具与前沿实验中枢 (others)
echo       当前收录: ModelTrace (模型路由检测与主动指纹归因系统)
echo ==============================================================================
echo.
echo   [1] 启动 ModelTrace 网页交互端 (自动打开 http://127.0.0.1:7860)
echo   [2] 运行 ModelTrace 运行环境与 13 款模型指纹库诊断
echo   [3] 查看 ModelTrace 指纹库收录模型全景清单
echo   [4] 查看 ModelTrace 核心使用手册与归因算法原理
echo   [5] 查看 Codex 监控插件说明 (ModelTrace Guard)
echo   [6] 打开自动化邮箱 API (https://email.manageh.shop/)
echo   [7] 打开 Outlook 快速取件平台 (https://mail.chatai.codes/)
echo   [8] 打开 ChatGPT Session 转 sub2api 工具 (https://convert.13916454.xyz/)
echo   [9] 打开实用云端工具导航 (打开实用云端工具.bat)
echo   [0] 返回主菜单
echo.
echo ==============================================================================
set /p oopt="请选择功能序号 [0-9]: "
if "%oopt%"=="1" (
    cd /d "%~dp0others"
    call "启动模型路由检测.bat"
    cd /d "%~dp0"
    goto OTHERS
)
if "%oopt%"=="2" (
    python "%~dp0others\modeltrace_cli.py" --status
    pause
    goto OTHERS
)
if "%oopt%"=="3" (
    python "%~dp0others\modeltrace_cli.py" --models
    pause
    goto OTHERS
)
if "%oopt%"=="4" (
    type "%~dp0others\ModelTrace\README.md"
    pause
    goto OTHERS
)
if "%oopt%"=="5" (
    type "%~dp0others\ModelTrace\codex-plugin\modeltrace-guard\README.md"
    pause
    goto OTHERS
)
if "%oopt%"=="6" (
    start "" "https://email.manageh.shop/"
    goto OTHERS
)
if "%oopt%"=="7" (
    start "" "https://mail.chatai.codes/"
    goto OTHERS
)
if "%oopt%"=="8" (
    start "" "https://convert.13916454.xyz/"
    goto OTHERS
)
if "%oopt%"=="9" (
    cd /d "%~dp0others"
    call "打开实用云端工具.bat"
    cd /d "%~dp0"
    goto OTHERS
)
goto MENU

:WEB
cls
call "%~dp0启动工具箱Web控制台.bat"
goto MENU

:EXIT
exit
