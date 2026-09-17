#!/usr/bin/env python3
"""
Unit tests for codex-instruct-v2 (Keysmith Edition).
"""

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "codex-instruct-v2.py"
spec = importlib.util.spec_from_file_location("codex_instruct_v2", MODULE_PATH)
ci2 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ci2
spec.loader.exec_module(ci2)


class TestCodexInstructV2(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="codex_instruct_v2_test_"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_manifest_loads_properly(self):
        manifest = ci2.load_manifest()
        self.assertIn("contract", manifest)
        self.assertIn("astra", manifest)
        for name, info in manifest.items():
            f = ci2.PACKAGES_DIR / info["markdown_file"]
            self.assertTrue(f.exists())
            self.assertEqual(ci2.sha256_file(f), info["markdown_sha256"])

    def test_apply_and_reset_in_temp_codex_home(self):
        # 1. Apply contract preset
        ret = ci2.apply_codex_instruct(
            version="contract",
            codex_dir=self.temp_dir,
            dry_run=False,
            isolate_hooks=False,
        )
        self.assertEqual(ret, 0)

        contract_md = self.temp_dir / "contract.md"
        config_toml = self.temp_dir / "config.toml"
        self.assertTrue(contract_md.exists())
        self.assertTrue(config_toml.exists())

        toml_text = config_toml.read_text(encoding="utf-8")
        self.assertIn('model_instructions_file = "./contract.md"', toml_text)

        # 2. Reset
        ret_reset = ci2.reset_codex_instruct(codex_dir=self.temp_dir, dry_run=False)
        self.assertEqual(ret_reset, 0)
        toml_after = config_toml.read_text(encoding="utf-8")
        self.assertNotIn("model_instructions_file", toml_after)

    def test_hooks_isolation_and_restoration(self):
        hooks_file = self.temp_dir / "hooks.json"
        hooks_file.write_text('{"dummy": true}', encoding="utf-8")

        isolated = ci2.isolate_hooks_if_needed(self.temp_dir, dry_run=False)
        self.assertIsNotNone(isolated)
        self.assertFalse(hooks_file.exists())
        self.assertTrue(isolated.exists())

        # Restore
        ret = ci2.restore_hooks(self.temp_dir)
        self.assertEqual(ret, 0)
        self.assertTrue(hooks_file.exists())


if __name__ == "__main__":
    unittest.main()
