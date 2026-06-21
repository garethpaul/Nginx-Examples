#!/usr/bin/env python3
import os
from pathlib import Path
import shlex
import shutil
import stat
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class MakefileRootTests(unittest.TestCase):
    def run_make(
        self,
        *arguments: str,
        extra_environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        environment = {"PATH": os.environ.get("PATH", "")}
        if extra_environment:
            environment.update(extra_environment)
        return subprocess.run(
            ["make", "-n", "-f", str(ROOT / "Makefile"), *arguments],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            env=environment,
        )

    def assert_root_not_redirected(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn(str(ROOT / "scripts" / "check-nginx-examples.py"), result.stdout)
        self.assertNotIn("/tmp/untrusted", result.stdout)

    def test_root_command_line_override_is_ignored(self) -> None:
        self.assert_root_not_redirected(
            self.run_make("ROOT=/tmp/untrusted", "static-check")
        )

    def test_root_environment_override_is_ignored(self) -> None:
        self.assert_root_not_redirected(
            self.run_make(
                "-e",
                "static-check",
                extra_environment={"ROOT": "/tmp/untrusted"},
            )
        )

    def test_makefile_list_command_line_override_fails_closed(self) -> None:
        result = self.run_make("MAKEFILE_LIST=/tmp/untrusted", "test")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stdout)

    def test_makefile_list_environment_override_fails_closed(self) -> None:
        result = self.run_make(
            "-e",
            "test",
            extra_environment={"MAKEFILE_LIST": "/tmp/untrusted"},
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stdout)

    def test_all_aliases_preserve_spaced_quoted_absolute_path(self) -> None:
        alias_scripts = {
            "build": ("check-nginx-examples.py",),
            "check": (
                "check-nginx-examples.py",
                "test-check-nginx-examples.py",
                "test-nginx-proxy.py",
                "test-makefile-root.py",
            ),
            "checker-test": ("test-check-nginx-examples.py",),
            "lint": ("check-nginx-examples.py",),
            "proxy-test": ("test-nginx-proxy.py",),
            "root-test": ("test-makefile-root.py",),
            "static-check": ("check-nginx-examples.py",),
            "test": (
                "test-check-nginx-examples.py",
                "test-nginx-proxy.py",
                "test-makefile-root.py",
            ),
            "verify": (
                "check-nginx-examples.py",
                "test-check-nginx-examples.py",
                "test-nginx-proxy.py",
                "test-makefile-root.py",
            ),
        }
        with tempfile.TemporaryDirectory(prefix="nginx-spaced-root-") as directory:
            parent = Path(directory)
            checkout = parent / "Nginx [examples] \"' gate"
            makefile = checkout / "Makefile"
            checkout.mkdir()
            shutil.copyfile(ROOT / "Makefile", makefile)
            for alias, scripts in alias_scripts.items():
                for variable in (None, "ROOT", "SHELL_ROOT"):
                    with self.subTest(alias=alias, variable=variable):
                        arguments = ["make", "--no-print-directory", "-n", "-f", str(makefile)]
                        if variable:
                            arguments.append(f"{variable}=/tmp/untrusted")
                        arguments.append(alias)
                        result = subprocess.run(
                            arguments,
                            cwd=parent,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            check=False,
                            env={"PATH": os.environ.get("PATH", "")},
                        )
                        self.assertEqual(result.returncode, 0, result.stdout)
                        self.assertNotIn("/tmp/untrusted", result.stdout)
                        for script in scripts:
                            expected = shlex.quote(str(checkout / "scripts" / script))
                            self.assertIn(expected, result.stdout)

    def test_checkout_name_cannot_execute_command_substitution(self) -> None:
        with tempfile.TemporaryDirectory(prefix="nginx-shell-root-") as directory:
            parent = Path(directory)
            tools = parent / "bin"
            tools.mkdir()
            marker = parent / "executed"
            helper = tools / "touch_marker"
            helper.write_text(f"#!/bin/sh\n: > '{marker}'\n", encoding="utf-8")
            helper.chmod(helper.stat().st_mode | stat.S_IXUSR)
            checkout = parent / "Nginx`touch_marker`"
            shutil.copytree(
                ROOT,
                checkout,
                ignore=shutil.ignore_patterns(".git", ".review", "__pycache__"),
            )
            result = subprocess.run(
                ["make", "-f", str(checkout / "Makefile"), "static-check"],
                cwd=parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
                env={"PATH": f"{tools}:{os.environ.get('PATH', '')}"},
            )
            self.assertFalse(marker.exists(), result.stdout)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_spaced_quoted_checkout_runs_owned_leaf_gates(self) -> None:
        with tempfile.TemporaryDirectory(prefix="nginx-live-root-") as directory:
            parent = Path(directory)
            checkout = parent / "Nginx [examples] \"' gate"
            shutil.copytree(
                ROOT,
                checkout,
                ignore=shutil.ignore_patterns(".git", ".review", "__pycache__"),
            )
            result = subprocess.run(
                [
                    "make",
                    "-f",
                    str(checkout / "Makefile"),
                    "static-check",
                    "checker-test",
                    "proxy-test",
                ],
                cwd=parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
                env={"PATH": os.environ.get("PATH", "")},
            )
            self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
