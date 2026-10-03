"""Exercise dependency selection, hard limits, failures, and timeout cleanup."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "harness", Path(__file__).resolve().parents[1] / "scripts/check_module_codegen.py"
)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


class ManifestTests(unittest.TestCase):
    def test_diamond_closure_and_valid_manifest(self):
        modules = {
            "base": {"schemas": ["a.xsd"]},
            "a": {"schemas": ["b.xsd"], "depends_on": ["base"]},
            "b": {"schemas": ["c.xsd"], "depends_on": ["base"]},
            "root": {"schemas": ["d.xsd"], "depends_on": ["a", "b"]},
        }
        names = harness.closure(modules, "root")
        self.assertEqual(names, ["base", "a", "b", "root"])
        manifest = harness.tomllib.loads(harness.manifest(modules, names, "python"))
        self.assertEqual(list(manifest["modules"]), names)
        self.assertEqual(manifest["modules"]["root"], modules["root"])

    def test_dependency_cycle_fails(self):
        with self.assertRaisesRegex(ValueError, "cyclic"):
            harness.closure(
                {"a": {"depends_on": ["b"]}, "b": {"depends_on": ["a"]}}, "a"
            )


class CgroupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.system = os.environ.get("CORPUS_TEST_SYSTEM") == "1"
        result = subprocess.run(
            (["sudo", "-n"] if cls.system else [])
            + [
                "systemd-run",
                *([] if cls.system else ["--user"]),
                "--scope",
                "--quiet",
                "-p",
                "MemoryMax=64M",
                "--",
                "true",
            ],
            capture_output=True,
            check=False,
        )
        if result.returncode and cls.system:
            raise RuntimeError("system cgroup manager required in CI")
        if result.returncode:
            raise unittest.SkipTest("user systemd cgroup manager required")

    def test_limits_are_kernel_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            runner = harness.BoundedRunner(output, 64, 10, self.system)
            script = 'from pathlib import Path; c=Path("/sys/fs/cgroup")/Path("/proc/self/cgroup").read_text().strip().split("::")[1].lstrip("/"); assert (c/"memory.max").read_text().strip()==str(64*1024*1024); assert (c/"memory.swap.max").read_text().strip()=="0"'
            runner.run([sys.executable, "-c", script], output, "limits")
            self.assertEqual(
                json.loads((output / "results.json").read_text())[0]["exit_code"], 0
            )

    def test_compile_failure_is_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "bad.py").write_text("def broken(:\n")
            runner = harness.BoundedRunner(output, 64, 10, self.system)
            with self.assertRaises(RuntimeError):
                runner.run(
                    [sys.executable, "-m", "py_compile", str(output / "bad.py")],
                    output,
                    "compile",
                )
            self.assertIn("SyntaxError", (output / "compile.log").read_text())
            self.assertNotEqual(
                json.loads((output / "results.json").read_text())[0]["exit_code"], 0
            )

    def test_timeout_kills_descendants(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            runner = harness.BoundedRunner(output, 64, 1, self.system)
            script = 'import subprocess,time; from pathlib import Path; p=subprocess.Popen(["sleep","60"]); Path("child.pid").write_text(str(p.pid)); time.sleep(60)'
            with self.assertRaises(RuntimeError):
                runner.run([sys.executable, "-c", script], output, "timeout")
            pid = (output / "child.pid").read_text()
            process = Path("/proc") / pid / "stat"
            self.assertTrue(
                not process.exists() or process.read_text().split()[2] == "Z"
            )
            self.assertEqual(
                json.loads((output / "results.json").read_text())[0]["exit_code"], 124
            )


if __name__ == "__main__":
    unittest.main()
