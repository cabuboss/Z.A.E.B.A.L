"""Five offline smoke checks, shared by native Windows and Linux."""

import concurrent.futures
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core"))
sys.path.insert(0, str(ROOT / "scripts"))
import install_codex_hook as installer
import zaebal


class TestCrossPlatform(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="zaebal-smoke-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "Проверка & user's folder"
        self.root.mkdir()
        self.config = self.root / "codex" / "hooks.json"
        self.dest = self.root / "runtime"
        self.state = self.root / "state"
        self.state.mkdir()
        (self.state / "config.json").write_text(
            json.dumps({"audit_levels": []}), encoding="utf-8")
        self.env = {**os.environ, "ZAEBAL_STATE_DIR": str(self.state), "PYTHONUTF8": "1"}
        self.env.pop("ZAEBAL_INTERNAL", None)

    def invoke(self, prompt, session="smoke", command=None):
        payload = json.dumps({"session_id": session, "prompt": prompt}, ensure_ascii=False)
        args = command or [sys.executable, "-X", "utf8", str(ROOT / "core" / "zaebal.py"),
                           "--host", "codex"]
        if command and os.name == "nt":
            args = shlex.split(command)  # fixed PowerShell flags + base64, no shell expansion
        result = subprocess.run(args, shell=command is not None and os.name != "nt", input=payload,
                                capture_output=True, encoding="utf-8", env=self.env,
                                cwd=self.root, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_registered_command_install_update_remove_and_unicode(self):
        other = {"type": "command", "command": "echo untouched"}
        installer.write_json(self.config, {"description": "keep", "hooks": {
            "UserPromptSubmit": [{"hooks": [other]}], "Stop": [{"hooks": []}],
        }})
        first = installer.install(self.config, self.dest)
        second = installer.install(self.config, self.dest)
        self.assertNotEqual(first["backup"], second["backup"])
        data = json.loads(self.config.read_text(encoding="utf-8"))
        groups = data["hooks"]["UserPromptSubmit"]
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0]["hooks"], [other])
        command = groups[1]["hooks"][0]["command"]
        self.assertEqual(self.invoke("Привет", command=command), "")
        for level in (1, 2, 2, 3):
            self.assertIn(f'<zaebal level="{level}">',
                          self.invoke("ты меня заебал", command=command))
        ack = self.invoke("продолжай", command=command)
        self.assertNotIn("not persisted", ack)
        self.assertIn('<zaebal level="1">', self.invoke("ты меня заебал", command=command))
        installer.install(self.config, self.dest, remove=True)
        remaining = json.loads(self.config.read_text(encoding="utf-8"))
        self.assertEqual(remaining["hooks"]["UserPromptSubmit"], [{"hooks": [other]}])
        self.assertEqual(remaining["hooks"]["Stop"], [{"hooks": []}])
        self.assertEqual(remaining["description"], "keep")
        self.assertTrue((self.dest / "core" / "zaebal.py").exists())

    def test_parallel_processes_keep_every_trigger(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.invoke("ты меня заебал", "parallel"), range(8)))
        self.assertTrue(all('<zaebal level=' in out for out in results))
        state = json.loads((self.state / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(len(state["parallel"]["stamps"]), 8)

    def test_dismiss_command_is_executable_and_replay_is_noop(self):
        out = self.invoke("ты меня заебал")
        if os.name == "nt":
            command = re.search(r"powershell\.exe -NoProfile -NonInteractive -EncodedCommand [A-Za-z0-9+/=]+", out).group()
        else:
            # POSIX command appears on one line in the injected protocol.
            command = next(line.strip().strip("`") for line in out.splitlines()
                           if "--dismiss-trigger=" in line)
        for _ in range(2):
            result = subprocess.run(shlex.split(command) if os.name == "nt" else command,
                                    shell=os.name != "nt", env=self.env, capture_output=True,
                                    encoding="utf-8", timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('<zaebal level="1">', self.invoke("ты меня заебал"))

    def test_invalid_config_is_preserved_before_copy(self):
        self.config.parent.mkdir()
        self.config.write_text("{broken", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            installer.install(self.config, self.dest)
        self.assertEqual(self.config.read_text(encoding="utf-8"), "{broken")
        self.assertFalse(self.dest.exists())

    def test_custom_auditor_argv_preserves_unicode_and_arguments(self):
        # A local stand-in exercises the process boundary without calling a model.
        verdict = "\n".join(label + ": " + ("UNVERIFIED" if label == "STATUS" else "данные")
                            for label in zaebal.AUDIT_SECTION_LABELS)
        script = ("import os,sys; assert os.environ['ZAEBAL_INTERNAL']=='1'; "
                  "assert sys.argv[1]=='Привет & $()'; print(" + repr(verdict) + ")")
        cfg = zaebal.validate_config({"auditor_command": [sys.executable, "-X", "utf8", "-c", script]})
        actual, error = zaebal.run_auditor("codex", "Привет & $()", cfg)
        self.assertIsNone(error)
        self.assertEqual(actual, verdict)


if __name__ == "__main__":
    unittest.main()
