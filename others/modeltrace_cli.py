#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ModelTrace CLI - 观的 AI 工具箱 · 模型路由检测与主动归因管理命令行
"""

from __future__ import annotations
import sys
import os
import json
import argparse
from pathlib import Path

# 确保 Windows 下控制台 UTF-8 输出无乱码与异常
if sys.platform == "win32":
    try:
        if sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr.encoding.lower() != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
MODELTRACE_DIR = BASE_DIR / "ModelTrace"
DATA_DIR = MODELTRACE_DIR / "data"

def check_dependencies() -> dict[str, bool]:
    deps = {}
    for mod in ["flask", "numpy", "click"]:
        try:
            __import__(mod)
            deps[mod] = True
        except ImportError:
            deps[mod] = False
    return deps

def inspect_banks() -> dict[str, any]:
    results = {}
    if not DATA_DIR.exists():
        return results
    
    for bank_file in DATA_DIR.glob("*_bank.json"):
        try:
            data = json.loads(bank_file.read_text(encoding="utf-8"))
            models_data = data.get("models", [])
            if isinstance(models_data, list):
                models = [m.get("display_name", m.get("id", str(m))) for m in models_data if isinstance(m, dict)]
            elif isinstance(models_data, dict):
                models = list(models_data.keys())
            else:
                models = []
            results[bank_file.name] = {
                "count": len(models),
                "models": models,
                "size_kb": round(bank_file.stat().st_size / 1024, 1)
            }
        except Exception as e:
            results[bank_file.name] = {"error": str(e)}
    return results

def print_status():
    print("=" * 78)
    print("       观的 AI 工具箱 · ModelTrace 模型路由检测与指纹归因系统诊断")
    print("=" * 78)
    
    # 依赖检查
    deps = check_dependencies()
    print("[*] Python 运行环境依赖:")
    all_ok = True
    for mod, ok in deps.items():
        state = "[+ 已安装]" if ok else "[- 未安装]"
        print(f"  • {mod:<10}: {state}")
        if not ok:
            all_ok = False
            
    print("\n[*] 指纹库 (Fingerprint Banks) 状态:")
    banks = inspect_banks()
    if not banks:
        print("  [!] 未检测到指纹库文件，请确认 data/ 目录完整性。")
    else:
        for name, info in banks.items():
            if "error" in info:
                print(f"  • {name:<20}: [加载失败] {info['error']}")
            else:
                print(f"  • {name:<20}: [{info['count']} 款模型] ({info['size_kb']} KB)")
                
    print("\n[+] Web 服务端点: http://127.0.0.1:7860")
    print("[+] Codex 监控插件: others/ModelTrace/codex-plugin/modeltrace-guard")
    print("=" * 78)
    if all_ok:
        print("[√] 状态: 运行环境与指纹库完全就绪，可随时双击 '启动模型路由检测.bat' 开启！")
    else:
        print("[!] 提示: 存在缺失依赖，请运行 'pip install -r ModelTrace/requirements.txt' 进行安装。")
    print("=" * 78)

def list_models():
    banks = inspect_banks()
    print("=" * 78)
    print("                   ModelTrace 当前收录模型全景清单")
    print("=" * 78)
    unified = banks.get("unified_bank.json")
    if unified and "models" in unified:
        models = unified["models"]
        print(f"共计收录 {len(models)} 款生产级大模型指纹特征：\n")
        claude_models = [m for m in models if "claude" in m.lower()]
        gpt_models = [m for m in models if "gpt" in m.lower()]
        other_models = [m for m in models if m not in claude_models and m not in gpt_models]
        
        if claude_models:
            print("【Anthropic Claude 家族】:")
            for m in claude_models:
                print(f"  - {m}")
        if gpt_models:
            print("\n【OpenAI GPT 家族】:")
            for m in gpt_models:
                print(f"  - {m}")
        if other_models:
            print("\n【其他扩展家族】:")
            for m in other_models:
                print(f"  - {m}")
    else:
        print("未在 unified_bank.json 中找到模型数据。")
    print("=" * 78)

def start_server():
    import subprocess
    start_script = MODELTRACE_DIR / "start.py"
    if not start_script.exists():
        print(f"[!] 找不到启动脚本: {start_script}")
        sys.exit(1)
    print(">>> 正在拉起 ModelTrace 本地 Web 服务 (http://127.0.0.1:7860)...")
    subprocess.run([sys.executable, str(start_script)], cwd=str(MODELTRACE_DIR))

def main():
    parser = argparse.ArgumentParser(description="ModelTrace CLI - 模型路由检测中枢")
    parser.add_argument("--status", action="store_true", help="诊断 Python 依赖与指纹库就绪状态")
    parser.add_argument("--models", action="store_true", help="列出当前指纹库收录的所有模型名")
    parser.add_argument("--start", action="store_true", help="启动 Web 服务并打开浏览器")
    
    args = parser.parse_args()
    if args.status:
        print_status()
    elif args.models:
        list_models()
    elif args.start:
        start_server()
    else:
        print_status()

if __name__ == "__main__":
    main()
