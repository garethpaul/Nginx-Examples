#!/usr/bin/env python3
import os
from pathlib import Path
import subprocess
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


if __name__ == "__main__":
    unittest.main()
