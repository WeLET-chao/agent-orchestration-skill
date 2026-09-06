"""Exercise the real PTY wrapper with a fake CLI; no provider calls are made."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


WRAPPER = Path(__file__).with_name("run_agy_print.sh")


class WrapperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agy-wrapper-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work = self.root / "work tree"
        self.work.mkdir()
        self.fake = self.root / "fake agy"
        self.fake.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, sys, time\n"
            "from pathlib import Path\n"
            "Path('invocation.json').write_text(json.dumps({"
            "'args': sys.argv[1:], 'cwd': os.getcwd(), 'tty': os.isatty(1)}))\n"
            "print('FAKE_OUTPUT', flush=True)\n"
            "print('FAKE_DIAGNOSTIC', file=sys.stderr, flush=True)\n"
            "time.sleep(float(os.environ.get('FAKE_DELAY', '0')))\n"
            "sys.exit(int(os.environ.get('FAKE_EXIT', '0')))\n"
        )
        self.fake.chmod(0o755)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith('AGY_')}
        self.env["AGY_BIN"] = str(self.fake)

    def run_wrapper(self, *args, **env):
        return subprocess.run(
            ["bash", str(WRAPPER), "--workdir", str(self.work), *args],
            cwd=self.root, env=self.env | env, capture_output=True,
            text=True, timeout=10,
        )

    def test_paths_prompt_and_arguments(self):
        prompt = 'quotes " \' $HOME `id`\nsecond line'
        (self.work / "prompt.txt").write_text(prompt)
        result = self.run_wrapper(
            "-f", "prompt.txt", "--out", "artifacts/out.txt", "--log", "logs/run.tty",
            "--model", "selected-model", "--effort", "high", "--dir", "extra dir",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        invocation = json.loads((self.work / "invocation.json").read_text())
        self.assertTrue(invocation["tty"])
        self.assertEqual(invocation["cwd"], str(self.work))
        self.assertEqual(invocation["args"], [
            "--dangerously-skip-permissions", "--model", "selected-model",
            "--print-timeout", "8m", "--effort", "high", "--add-dir", "extra dir",
            "--print=" + prompt,
        ])
        self.assertIn("FAKE_OUTPUT", (self.work / "artifacts/out.txt").read_text())
        self.assertIn("FAKE_DIAGNOSTIC", (self.work / "logs/run.tty").read_text())

    def test_prompt_sources_are_exclusive(self):
        prompt = self.root / "prompt.txt"
        prompt.write_text("file prompt")
        result = self.run_wrapper("-p", "inline prompt", "-f", str(prompt))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse((self.work / "invocation.json").exists())

    def test_existing_outputs_are_preserved(self):
        for option in ("--out", "--log"):
            with self.subTest(option=option):
                target = self.work / "existing.txt"
                target.write_text("KEEP")
                result = self.run_wrapper("-p", "hello", option, str(target))
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(target.read_text(), "KEEP")
                self.assertFalse((self.work / "invocation.json").exists())

    def test_output_and_log_cannot_alias(self):
        target = self.work / "same.txt"
        result = self.run_wrapper("-p", "hello", "--out", str(target), "--log", str(target))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.work / "invocation.json").exists())

    def test_failure_preserves_exit_code_and_log_location(self):
        result = self.run_wrapper("-p", "hello", "--log", "failed.tty", FAKE_EXIT="7")
        self.assertEqual(result.returncode, 7)
        self.assertIn("agy transcript:", result.stderr)
        self.assertIn("FAKE_OUTPUT", (self.work / "failed.tty").read_text())

    def test_timeout_preserves_log(self):
        result = self.run_wrapper(
            "-p", "hello", "--timeout", "0.2s", "--log", "timeout.tty", FAKE_DELAY="3",
        )
        self.assertEqual(result.returncode, 124)
        self.assertIn("agy transcript:", result.stderr)
        self.assertIn("FAKE_OUTPUT", (self.work / "timeout.tty").read_text())

    def test_defaults_and_unique_logs(self):
        for _ in range(2):
            result = self.run_wrapper("-p", "hello")
            self.assertEqual(result.returncode, 0, result.stderr)
        args = json.loads((self.work / "invocation.json").read_text())["args"]
        self.assertIn("gemini-3.8-flash-high", args)
        self.assertIn("--dangerously-skip-permissions", args)
        self.assertEqual(len(list((self.work / ".scratch/agent_logs/agy").glob("*.tty"))), 2)


if __name__ == "__main__":
    unittest.main()
