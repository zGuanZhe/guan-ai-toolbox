# -*- coding: utf-8 -*-
"""
Guan's AI Toolbox - Register & Account Manager Interactive UI
多厂家自动注册流水线与账号池一键切换中枢。
"""

import os
import sys
from switchers.workbuddy_switcher import WorkBuddyAccountSwitcher
from switchers.trae_switcher import TraeAccountSwitcher
from switchers.antigravity_switcher import AntigravityAccountSwitcher
from engines import get_registered_engines
from core.browser_camoufox import CamoufoxBrowser

class RegisterUI:
    def __init__(self):
        self.wb_switcher = WorkBuddyAccountSwitcher()
        self.trae_switcher = TraeAccountSwitcher()
        self.agy_switcher = AntigravityAccountSwitcher()
        self.engines = {e.provider: e for e in get_registered_engines()}
        self.browser = CamoufoxBrowser()

    def run(self):
        while True:
            print("\n" + "=" * 80)
            print("        观的 AI 工具箱 · 多厂家自动注册与智能账号池中枢")
            print("   [集成 Camoufox 指纹浏览器 · 参考 any-auto-register & Antigravity-Manager]")
            print("=" * 80)
            
            # 读取当前 WorkBuddy 活跃状态
            wb_accs = self.wb_switcher.list_accounts()
            cur_wb = next((a for a in wb_accs if a.is_active), None)
            cur_wb_str = f"{cur_wb.email} (UID: {cur_wb.uid[:10]}...)" if cur_wb else "未检测到活跃账号"

            print(f"【当前宿主工具登录态快报】")
            print(f"  • WorkBuddy: {cur_wb_str}")
            print(f"  • 指纹浏览器: {'✅ 正常就绪 (' + self.browser.exe_path + ')' if self.browser.is_available() else '❌ 未找到'}")
            print("-" * 80)

            print("【第一部分：多厂家账号池管理与一键切换 (参考 Antigravity-Manager)】")
            print(f"  [1] WorkBuddy 账号池管理与一键切换 (已存 {len(wb_accs)} 个账号)")
            print(f"  [2] Trae / Trae CN 账号池管理与一键切换")
            print(f"  [3] Antigravity / Gemini 账号池与快速轮换")
            print("\n【第二部分：多厂家自动化注册流水线 (参考 any-auto-register)】")
            print("  [4] WorkBuddy 一键自动化注册 (拉起 Camoufox 并自动入池)")
            print("  [5] Qoder 自动化注册流水线 (Camoufox 指纹驱动)")
            print("  [6] OpenAI / ChatGPT 自动化批量注册")
            print("  [7] Tavily 搜索 API 批量开户流水线")
            print("  [8] xAI Grok 自动化批量注册流水线 (带 YesCaptcha & SSO Token)")
            print("\n【系统检测与工具】")
            print("  [9] 测试启动 Camoufox 指纹反检测浏览器")
            print("  [0] 退出")
            print("=" * 80)

            choice = input("请选择功能序号 [0-9]: ").strip()
            if choice == "0":
                print("[*] 退出账号与注册中心。")
                break
            elif choice == "1":
                self._handle_workbuddy_switcher()
            elif choice == "2":
                self._handle_trae_switcher()
            elif choice == "3":
                self._handle_antigravity_switcher()
            elif choice == "4":
                self._run_engine("workbuddy")
            elif choice == "5":
                self._run_engine("qoder")
            elif choice == "6":
                self._run_engine("openai")
            elif choice == "7":
                self._run_engine("tavily")
            elif choice == "8":
                self._run_engine("grok")
            elif choice == "9":
                self._test_camoufox()
            else:
                print("[!] 序号无效，请重新输入。")

    def _handle_workbuddy_switcher(self):
        while True:
            print("\n>>> 【WorkBuddy 账号池管理与一键切换】")
            accs = self.wb_switcher.list_accounts()
            print(f"{'序号':^4} | {'账号 / 邮箱':<30} | {'UID':<36} | {'状态'}")
            print("-" * 85)
            for idx, a in enumerate(accs, 1):
                stat = "🟢 当前激活" if a.is_active else "⚪ 备选"
                print(f"{idx:^4} | {a.email:<30} | {a.uid:<36} | {stat}")
            print("-" * 85)
            print("操作选项:")
            print("  [S] 输入序号一键切换至该账号")
            print("  [A] 手动添加新账号至账号池")
            print("  [0] 返回上级菜单")
            opt = input("请输入选择 [默认 S]: ").strip().upper()
            if opt == "0":
                break
            elif opt == "A":
                uid = input("请输入新账号 UID: ").strip()
                email = input("请输入新账号 邮箱/备注: ").strip()
                if uid and email:
                    self.wb_switcher.add_account(uid, email)
                    print(f"[✓] 账号 {email} 已成功加入 WorkBuddy 账号池！")
            else:
                idx_str = input("请输入要切换到的账号序号: ").strip()
                if idx_str.isdigit():
                    num = int(idx_str)
                    if 1 <= num <= len(accs):
                        target = accs[num - 1]
                        restart_wb = input("是否同时自动优雅重启 WorkBuddy 客户端生效？[Y/n]: ").strip().lower() != 'n'
                        ok = self.wb_switcher.switch_to(target.uid, restart_client=restart_wb)
                        if ok:
                            print(f"[🎉] 成功一键切换至 WorkBuddy 账号: {target.email}！")
                        else:
                            print("[❌] 切换失败，请检查文件权限。")
                    else:
                        print("[!] 无效序号。")

    def _handle_trae_switcher(self):
        print("\n>>> 【Trae / Trae CN 账号池管理】")
        accs = self.trae_switcher.list_accounts()
        if not accs:
            print("[*] 账号池当前为空。如需添加，请输入: ")
            email = input("Trae 账号邮箱 (回车跳过): ").strip()
            if email:
                uid = input("Trae UID: ").strip()
                self.trae_switcher.add_account(uid, email)
                print(f"[✓] Trae 账号 {email} 已保存。")
        else:
            for idx, a in enumerate(accs, 1):
                print(f"  [{idx}] {a.email} ({a.uid})")

    def _handle_antigravity_switcher(self):
        print("\n>>> 【Antigravity / Gemini 账号池】")
        accs = self.agy_switcher.list_accounts()
        for idx, a in enumerate(accs, 1):
            stat = "🟢 当前" if a.is_active else "⚪ 备选"
            print(f"  [{idx}] {a.email} ({stat})")

    def _run_engine(self, provider: str):
        engine = self.engines.get(provider)
        if not engine:
            print(f"[!] 未找到注册引擎: {provider}")
            return
        print(f"\n>>> 正在启动【{engine.name}】自动化注册流程...")
        res = engine.register_one()
        if res.get("success"):
            print(f"[✓] 执行就绪: {res.get('message', '操作成功')}")
        else:
            print(f"[❌] 启动失败: {res.get('error', '未知原因')}")

    def _test_camoufox(self):
        print("\n>>> 正在启动 Camoufox 指纹浏览器测试 (无痕反爬环境)...")
        res = self.browser.launch(url="https://bot.sannysoft.com", headless=False)
        if res.get("success"):
            print("[✓] Camoufox 指纹浏览器启动成功，正在进行反机器人环境自检。")
        else:
            print(f"[❌] 启动失败: {res.get('error')}")
