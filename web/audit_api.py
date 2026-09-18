# -*- coding: utf-8 -*-
import re
import json
from pathlib import Path

def audit():
    html_path = Path(r"D:\Test\Sub2\观的ai工具箱\web\index.html")
    server_path = Path(r"D:\Test\Sub2\观的ai工具箱\web\server.py")

    html = html_path.read_text(encoding="utf-8")
    server = server_path.read_text(encoding="utf-8")

    # 1. 提取所有前端向后端调用的 API
    frontend_apis = sorted(list(set(re.findall(r'fetch\([\'"`](/api/[^\'"`?]+)', html))))
    
    # 2. 提取后端定义的所有 API
    backend_apis = sorted(list(set(re.findall(r'@app\.route\([\'"`](/api/[^\'"`]+)', server))))

    print("=== 前端调用的 API 列表 ===")
    for api in frontend_apis:
        has_backend = any(api == b or api.startswith(b.split('<')[0]) for b in backend_apis)
        print(f"  {api} -> {'[已对接]' if has_backend else '[未找到后端路由]'}")

    print("\n=== 后端提供的 API 列表 ===")
    for api in backend_apis:
        called = any(api.split('<')[0] in f for f in frontend_apis)
        print(f"  {api} -> {'[前端有调用]' if called else '[前端未调用/隐藏/旧接口]'}")

if __name__ == "__main__":
    audit()
