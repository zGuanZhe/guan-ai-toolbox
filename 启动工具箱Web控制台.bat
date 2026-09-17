@echo off
chcp 65001 >nul
title 观的 AI 工具箱 - 全功能可视化 Web 控制台 (Letters.app 风格)
cd /d "%~dp0"

echo ==============================================================================
echo       观的 AI 工具箱 · 全功能可视化 Web 控制台 (Letters.app 风格)
echo       [会话恢复 / 账号池 / 14款MCP全端强刷 / 认知编译器 / ModelTrace 测谎]
echo ==============================================================================
echo.
echo 正在检查 Web 服务运行环境...
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo [!] 检测到 Flask 未安装，正在自动为您安装...
    python -m pip install flask
)

echo [✓] 依赖环境就绪！
echo.
echo 正在启动本地 Web 控制台服务 (端口: 5050)...
echo 服务启动后，系统将自动在默认浏览器中打开: http://127.0.0.1:5050
echo 若浏览器未自动弹出，请手动在浏览器地址栏输入上述链接。
echo.
echo 按 Ctrl+C 可停止当前服务。
echo ==============================================================================
echo.

python "web/server.py"

pause
