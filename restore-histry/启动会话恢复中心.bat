@echo off
chcp 65001 >nul
title 观的 AI 工具箱 - 历史会话管理与恢复中心
python "%~dp0main.py"
if errorlevel 1 pause
