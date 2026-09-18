@echo off
title 观的 AI 工具箱 - Web 控制台
cd /d "%~dp0"

echo ==============================================================================
echo       观的 AI 工具箱 · 全功能可视化 Web 控制台 (Letters.app 风格)
echo       [会话恢复 / 账号池 / 14款MCP全端强刷 / 破限工程 / ModelTrace 测谎]
echo ==============================================================================
echo.

:: 1. 自动定位可用 Python 解释器
set "PY_CMD="
where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_CMD=python"
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set "PY_CMD=py"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    ) else if exist "C:\Python314\python.exe" (
        set "PY_CMD=C:\Python314\python.exe"
    ) else (
        echo [错误] 未能在系统中检测到有效 Python 解释器！
        echo 请先安装 Python 3.10+ 并勾选 Add to PATH。
        echo.
        pause
        exit /b 1
    )
)

echo [*] 正在使用 Python: %PY_CMD%

:: 2. 检查并安装 Flask 依赖
echo [*] 正在检查 Flask 运行环境...
%PY_CMD% -c "import flask" >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] 检测到 Flask 未安装，正在自动为您安装...
    %PY_CMD% -m pip install flask
    if %errorlevel% neq 0 (
        echo [错误] 安装 Flask 失败，请检查网络连接后重试。
        pause
        exit /b 1
    )
)
echo [*] 依赖环境检测通过！

:: 3. 端口占用检查与自动释放
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5050" ^| findstr "LISTENING"') do (
    echo [!] 端口 5050 已被旧进程 (PID: %%p) 占用，正在释放...
    taskkill /F /PID %%p >nul 2>nul
)

:: 4. 自动唤起浏览器
echo [*] 正在唤起默认浏览器: http://127.0.0.1:5050 ...
start "" "http://127.0.0.1:5050"

:: 5. 启动 Web 服务
echo [*] 正在启动 Web 控制台服务 (127.0.0.1:5050)...
echo.
echo ==============================================================================
echo Web 控制台运行中: http://127.0.0.1:5050
echo 按 Ctrl+C 可停止服务，关闭此窗口即可退出。
echo ==============================================================================
echo.

%PY_CMD% "web/server.py"

if %errorlevel% neq 0 (
    echo.
    echo [提示] Web 控制台服务已退出 (Exit code: %errorlevel%)。
)
pause
