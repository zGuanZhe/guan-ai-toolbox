#!/usr/bin/env python3
"""
Unit tests for claude-instruct.
"""

import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "claude-instruct.py"
spec = importlib.util.spec_from_file_location("claude_instruct", MODULE_PATH)
ci = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = ci
spec.loader.exec_module(ci)


class TestClaudeInstruct(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="claude_instruct_test_"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_manifest_loads_and_contains_valid_packages(self):
        manifest = ci.load_manifest()
        self.assertIn("claude-v1-standard", manifest)
        self.assertIn("claude-v2-hyperdrive", manifest)
        for pkg_name, info in manifest.items():
            self.assertTrue((ci.PACKAGES_DIR / info["markdown_file"]).exists())
            actual_sha = ci.sha256_file(ci.PACKAGES_DIR / info["markdown_file"])
            self.assertEqual(actual_sha, info["markdown_sha256"])

    def test_apply_and_reset_in_temp_project(self):
        # 1. Apply to temporary project
        ret = ci.apply_instruct(
            version="claude-v1-standard",
            scope="project",
            project_dir=self.temp_dir,
            dry_run=False,
        )
        self.assertEqual(ret, 0)

        claude_md = self.temp_dir / "CLAUDE.md"
        self.assertTrue(claude_md.exists())
        content = claude_md.read_text(encoding="utf-8")
        self.assertIn("<!-- claude-instruct:start name=claude-v1-standard -->", content)
        self.assertIn("@.claude/instruct/claude-v1-standard.md", content)

        instruct_file = self.temp_dir / ".claude" / "instruct" / "claude-v1-standard.md"
        self.assertTrue(instruct_file.exists())
        self.assertIn("DETERMINISTIC_EXECUTION", instruct_file.read_text(encoding="utf-8"))

        # 2. Reset
        ret_reset = ci.reset_instruct(scope="project", project_dir=self.temp_dir, dry_run=False)
        self.assertEqual(ret_reset, 0)
        content_after = claude_md.read_text(encoding="utf-8")
        self.assertNotIn("<!-- claude-instruct:start", content_after)

    def test_dry_run_does_not_modify_disk(self):
        claude_md = self.temp_dir / "CLAUDE.md"
        ret = ci.apply_instruct(
            version="claude-v2-hyperdrive",
            scope="project",
            project_dir=self.temp_dir,
            dry_run=True,
        )
        self.assertEqual(ret, 0)
        self.assertFalse(claude_md.exists())


if __name__ == "__main__":
    unittest.main()
