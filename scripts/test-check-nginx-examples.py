#!/usr/bin/env python3

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def check_config(config: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="nginx-checker-") as temporary_directory:
        checkout = Path(temporary_directory) / "checkout"
        shutil.copytree(ROOT, checkout, ignore=shutil.ignore_patterns(".git", ".review", "__pycache__"))
        baseline = subprocess.run(
            ["python3", str(checkout / "scripts/check-nginx-examples.py")],
            capture_output=True,
            text=True,
        )
        if baseline.returncode != 0:
            raise AssertionError("unmodified checker baseline failed:\n" + baseline.stdout + baseline.stderr)
        config_path = checkout / "sample_tornado_nginx.conf"
        config_path.write_text(config, encoding="utf-8")
        return subprocess.run(
            ["python3", str(checkout / "scripts/check-nginx-examples.py")],
            capture_output=True,
            text=True,
        )


def check_mutation(old: str, new: str) -> subprocess.CompletedProcess[str]:
    config_path = ROOT / "sample_tornado_nginx.conf"
    config = config_path.read_text(encoding="utf-8")
    if old not in config:
        raise AssertionError(f"mutation source missing: {old!r}")
    return check_config(config.replace(old, new, 1))


class CheckerMutationTests(unittest.TestCase):
    def assertRejected(self, old: str, new: str) -> None:
        result = check_mutation(old, new)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_upgrade_map_without_connection_gate_is_rejected(self) -> None:
        config = (ROOT / "sample_tornado_nginx.conf").read_text(encoding="utf-8")
        gated_maps = """    map $http_connection $connection_has_upgrade {
        default 0;
        ~*(^|,)\\s*upgrade\\s*(,|$) 1;
    }

    map \"$connection_has_upgrade:$http_upgrade\" $upstream_upgrade {
        default '';
        ~*^1:websocket$ websocket;
    }
"""
        vulnerable_map = """    map $http_upgrade $upstream_upgrade {
        default '';
        ~*^websocket$ websocket;
    }
"""
        self.assertIn(gated_maps, config)
        result = check_config(config.replace(gated_maps, vulnerable_map, 1))
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_forwarded_port_normalization_is_rejected(self) -> None:
        self.assertRejected(
            "            proxy_set_header X-Forwarded-Port $server_port;\n",
            "",
        )

    def test_client_selected_forwarded_port_is_rejected(self) -> None:
        self.assertRejected(
            "            proxy_set_header X-Forwarded-Port $server_port;",
            "            proxy_set_header X-Forwarded-Port $http_x_forwarded_port;",
        )

    def test_arbitrary_upgrade_passthrough_is_rejected(self) -> None:
        self.assertRejected(
            "            proxy_set_header Upgrade $upstream_upgrade;",
            "            proxy_set_header Upgrade $http_upgrade;",
        )

    def test_nonempty_upgrade_map_is_rejected(self) -> None:
        self.assertRejected(
            "        ~*^1:websocket$ websocket;",
            "        default $http_upgrade;",
        )

    def test_connection_token_substring_match_is_rejected(self) -> None:
        self.assertRejected(
            "        ~*(^|,)\\s*upgrade\\s*(,|$) 1;",
            "        ~*upgrade 1;",
        )

    def test_connection_gate_default_open_is_rejected(self) -> None:
        self.assertRejected("        default 0;", "        default 1;")

    def test_upgrade_map_without_combined_key_is_rejected(self) -> None:
        self.assertRejected(
            '    map "$connection_has_upgrade:$http_upgrade" $upstream_upgrade {',
            "    map $http_upgrade $upstream_upgrade {",
        )

    def test_websocket_combined_state_substring_match_is_rejected(self) -> None:
        self.assertRejected(
            "        ~*^1:websocket$ websocket;",
            "        ~*websocket websocket;",
        )

    def test_commented_host_override_is_rejected(self) -> None:
        self.assertRejected(
            "            proxy_set_header Host $server_name;",
            "            # proxy_set_header Host $server_name;",
        )

    def test_commented_server_tokens_is_rejected(self) -> None:
        self.assertRejected("    server_tokens off;", "    # server_tokens off;")

    def test_proxy_pass_uri_suffix_is_rejected(self) -> None:
        self.assertRejected(
            "            proxy_pass http://frontends;",
            "            proxy_pass http://frontends/;",
        )


if __name__ == "__main__":
    unittest.main()
