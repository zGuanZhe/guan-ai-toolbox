@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 观的 AI 工具箱 - Web 控制台 (5050)

echo ==============================================================================
echo       观的 AI 工具箱 · 全功能可视化 Web 控制台 (http://127.0.0.1:5050)
echo       [会话恢复 / 账号池与自动注册 / 插件市场 / 破限中枢 / 路由归因]
echo ==============================================================================
echo.

set "PY_CMD="
python --version >nul 2>&1
if not errorlevel 1 set "PY_CMD=python"
if "%PY_CMD%"=="" (
    py -3 --version >nul 2>&1
    if not errorlevel 1 set "PY_CMD=py -3"
)
if "%PY_CMD%"=="" if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if "%PY_CMD%"=="" if exist "C:\Python314\python.exe" set "PY_CMD=C:\Python314\python.exe"
if "%PY_CMD%"=="" (
    echo [错误] 未在系统中检测到 Python，请先安装 Python 3.10+ 并勾选 Add to PATH。
    pause
    exit /b 1
)

echo [*] 使用 Python: %PY_CMD%

%PY_CMD% -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [*] 正在安装 Flask 依赖...
    %PY_CMD% -m pip install flask
    if errorlevel 1 (
        echo [错误] 安装 Flask 失败，请检查网络后重试。
        pause
        exit /b 1
    )
)

echo [*] 检查并清理端口 5050 占用...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5050" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%p >nul 2>&1
)

echo [*] 正在启动后台浏览器自动唤醒监听...
start "" %PY_CMD% -c "import time, webbrowser; time.sleep(1.2); webbrowser.open('http://127.0.0.1:5050')"

echo [*] 正在启动 Web 控制台服务 (http://127.0.0.1:5050)...
echo.
echo ==============================================================================
echo 控制台地址: http://127.0.0.1:5050
echo 服务运行中，按 Ctrl+C 可停止服务，关闭此终端窗口即可退出
echo ==============================================================================
echo.

%PY_CMD% "web\server.py"

if not errorlevel 1 goto END
echo.
echo [提示] Web 控制台已退出，退出码: %errorlevel%
pause
:END