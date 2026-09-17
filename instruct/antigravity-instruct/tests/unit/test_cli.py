import unittest
import shutil
import tempfile
import zipfile
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import importlib
agy_instruct = importlib.import_module("agy-instruct")
sync_archives = importlib.import_module("sync-archives")


class TestAgyInstructCLI(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_state_persistence(self):
        sample_state = {"version": "agy-v1-standard", "managed_files": ["a.txt"]}
        agy_instruct.save_state(self.test_dir, sample_state)
        loaded = agy_instruct.load_state(self.test_dir)
        self.assertEqual(loaded.get("version"), "agy-v1-standard")
        self.assertEqual(loaded.get("managed_files"), ["a.txt"])
        self.assertEqual(loaded.get("state_version"), agy_instruct.STATE_VERSION)

    def test_dry_run_apply(self):
        p_info = agy_instruct.AVAILABLE_VERSIONS["agy-v1-standard"]
        res = agy_instruct.deploy_package(Path(p_info["md"]), self.test_dir, dry_run=True)
        self.assertTrue(res)
        # Verify no files actually created
        self.assertFalse((self.test_dir / "GEMINI.md").exists())
        self.assertFalse((self.test_dir / ".agy-instruct-state.json").exists())

    def test_live_apply_and_reset(self):
        p_info = agy_instruct.AVAILABLE_VERSIONS["agy-v1-standard"]
        # Apply
        apply_res = agy_instruct.deploy_package(Path(p_info["md"]), self.test_dir, dry_run=False)
        self.assertTrue(apply_res)
        self.assertTrue((self.test_dir / "GEMINI.md").exists())
        self.assertTrue((self.test_dir / ".agents" / "rules" / "00-model-instructions.md").exists())
        self.assertTrue((self.test_dir / ".agy-instruct-state.json").exists())

        # Reset
        reset_res = agy_instruct.reset_deployment(self.test_dir, dry_run=False)
        self.assertTrue(reset_res)
        self.assertFalse((self.test_dir / "GEMINI.md").exists())
        self.assertFalse((self.test_dir / ".agy-instruct-state.json").exists())

    def test_deploy_custom_zip(self):
        # Create a mock custom prompt zip
        custom_md = self.test_dir / "my-custom-prompt.md"
        custom_md.write_text("# Custom Prompt Content", encoding="utf-8")
        custom_zip = self.test_dir / "my-custom-prompt.zip"
        with zipfile.ZipFile(custom_zip, "w") as zf:
            zf.write(custom_md, arcname="my-custom-prompt.md")

        deploy_target = self.test_dir / "target_ws"
        deploy_target.mkdir()

        res = agy_instruct.deploy_package(custom_zip, deploy_target, version_label="my-custom-prompt")
        self.assertTrue(res)
        installed_prompt = deploy_target / ".agents" / "rules" / "00-model-instructions.md"
        self.assertTrue(installed_prompt.exists())
        self.assertIn("Custom Prompt Content", installed_prompt.read_text(encoding="utf-8"))

    def test_archive_sync_and_verify(self):
        verify_res = sync_archives.verify_archives()
        self.assertTrue(verify_res)

    def test_banner_and_display_width(self):
        banner = agy_instruct.section_banner("测试 Test")
        self.assertTrue(len(banner) > 10)
        self.assertEqual(agy_instruct.display_width("测试"), 4)
        self.assertEqual(agy_instruct.display_width("test"), 4)


if __name__ == "__main__":
    unittest.main()
