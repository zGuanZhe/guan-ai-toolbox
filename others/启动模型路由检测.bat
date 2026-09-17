@echo off
chcp 65001 >nul
title 观的 AI 工具箱 - 模型路由检测与指纹归因中心 (ModelTrace)
cd /d "%~dp0ModelTrace"

echo ==============================================================================
echo       观的 AI 工具箱 · 模型路由检测与主动指纹归因 (ModelTrace)
echo       [识别假冒模型 / 测中转API路由真实性 / 13 款主流模型指纹校验]
echo ==============================================================================
echo.
echo 正在检查 Python 依赖运行环境...
python -c "import flask, numpy, click" 2>nul
if %errorlevel% neq 0 (
    echo [!] 检测到部分 Python 依赖未安装，正在自动为您安装...
    python -m pip install -r requirements.txt
)

echo [✓] 依赖环境就绪！
echo.
echo 正在启动 ModelTrace 本地服务 (默认端口 7860)...
echo 服务启动后，系统将自动在浏览器中打开: http://127.0.0.1:7860
echo 若浏览器未自动弹出，请手动复制上述链接至浏览器访问。
echo.
echo 按 Ctrl+C 可停止当前服务。
echo ==============================================================================
echo.

python start.py

pause
