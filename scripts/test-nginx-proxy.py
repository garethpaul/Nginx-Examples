#!/usr/bin/env python3

import contextlib
import http.client
import http.server
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
NGINX = (
    os.environ.get("NGINX")
    or shutil.which("nginx")
    or "/opt/homebrew/opt/nginx/bin/nginx"
)
MIME_TYPES = next(
    (
        path
        for path in [Path("/opt/homebrew/etc/nginx/mime.types"), Path("/etc/nginx/mime.types")]
        if path.is_file()
    ),
    None,
)


def unused_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


class EchoHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        payload = json.dumps(
            {
                "path": self.path,
                "headers": {name.lower(): value for name, value in self.headers.items()},
            },
            sort_keys=True,
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self) -> None:
        self.do_GET()

    def log_message(self, format: str, *args: object) -> None:
        return


class ThreadingServer(http.server.ThreadingHTTPServer):
    daemon_threads = True


@contextlib.contextmanager
def running_proxy():
    nginx_path = Path(NGINX)
    if not nginx_path.is_file():
        raise unittest.SkipTest(f"Nginx is unavailable at {nginx_path}")
    if MIME_TYPES is None:
        raise unittest.SkipTest("Nginx mime.types is unavailable")

    backend_port = unused_port()
    proxy_port = unused_port()
    backend = ThreadingServer(("127.0.0.1", backend_port), EchoHandler)
    backend_thread = threading.Thread(target=backend.serve_forever, daemon=True)
    backend_thread.start()

    with tempfile.TemporaryDirectory(prefix="nginx-examples-") as temporary_directory:
        temporary = Path(temporary_directory)
        config = (ROOT / "sample_tornado_nginx.conf").read_text(encoding="utf-8")
        config = config.replace("    use epoll;\n", "")
        config = config.replace("/var/log/nginx/error.log", str(temporary / "error.log"))
        config = config.replace("/var/run/nginx.pid", str(temporary / "nginx.pid"))
        config = config.replace("/var/log/nginx/access.log", str(temporary / "access.log"))
        config = config.replace(
            "    upstream frontends {\n"
            "        server 127.0.0.1:8000;\n"
            "        server 127.0.0.1:8001;\n"
            "        server 127.0.0.1:8002;\n"
            "        server 127.0.0.1:8003;\n"
            "    }",
            "    upstream frontends {\n"
            f"        server 127.0.0.1:{backend_port};\n"
            "    }",
        )
        config = config.replace("    include mime.types;", f"    include {MIME_TYPES};")
        config = config.replace("        listen 80;", f"        listen 127.0.0.1:{proxy_port};")
        config = config.replace("root /srv/example-app;", f"root {temporary / 'static'};")
        config_path = temporary / "nginx.conf"
        config_path.write_text(config, encoding="utf-8")

        subprocess.run(
            [str(nginx_path), "-t", "-p", str(temporary), "-c", str(config_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        process = subprocess.Popen(
            [str(nginx_path), "-p", str(temporary), "-c", str(config_path), "-g", "daemon off;"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                try:
                    with socket.create_connection(("127.0.0.1", proxy_port), timeout=0.1):
                        break
                except OSError:
                    if process.poll() is not None:
                        raise RuntimeError("Nginx exited before accepting connections")
                    time.sleep(0.05)
            else:
                raise RuntimeError("Nginx did not start within five seconds")
            yield proxy_port
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            backend.shutdown()
            backend.server_close()


def request(proxy_port: int, path: str, headers: dict[str, str]) -> dict[str, object]:
    connection = http.client.HTTPConnection("127.0.0.1", proxy_port, timeout=5)
    try:
        connection.request("GET", path, headers=headers)
        response = connection.getresponse()
        body = response.read()
        if response.status != 200:
            raise AssertionError(f"unexpected proxy response {response.status}: {body!r}")
        return json.loads(body)
    finally:
        connection.close()


class ProxyBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proxy = running_proxy()
        cls.proxy_port = cls.proxy.__enter__()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.proxy.__exit__(None, None, None)

    def test_spoofed_forwarding_headers_are_replaced_or_removed(self) -> None:
        result = request(
            self.proxy_port,
            "/identity?next=%2Fadmin",
            {
                "Host": "attacker.example:9443",
                "X-Real-IP": "203.0.113.8",
                "X-Forwarded-Host": "attacker.example",
                "X-Forwarded-For": "203.0.113.9, 198.51.100.4",
                "X-Forwarded-Proto": "https",
                "X-Forwarded-Port": "443",
                "Forwarded": "for=203.0.113.10;host=attacker.example;proto=https",
                "Proxy": "http://attacker.example",
            },
        )
        headers = result["headers"]
        self.assertEqual(headers["host"], "example.local")
        self.assertEqual(headers["x-forwarded-host"], "example.local")
        self.assertEqual(headers["x-real-ip"], "127.0.0.1")
        self.assertEqual(headers["x-forwarded-for"], "127.0.0.1")
        self.assertEqual(headers["x-forwarded-proto"], "http")
        self.assertEqual(headers["x-forwarded-port"], str(self.proxy_port))
        self.assertNotIn("forwarded", headers)
        self.assertNotIn("proxy", headers)
        self.assertEqual(result["path"], "/identity?next=%2Fadmin")

    def test_non_websocket_upgrade_is_not_forwarded(self) -> None:
        result = request(
            self.proxy_port,
            "/upgrade",
            {"Host": "example.local", "Connection": "upgrade", "Upgrade": "h2c"},
        )
        headers = result["headers"]
        self.assertNotIn("upgrade", headers)
        self.assertEqual(headers["connection"], "close")

    def test_websocket_upgrade_is_forwarded_case_insensitively(self) -> None:
        result = request(
            self.proxy_port,
            "/socket?token=opaque",
            {"Host": "example.local", "Connection": "upgrade", "Upgrade": "WebSocket"},
        )
        headers = result["headers"]
        self.assertEqual(headers["upgrade"], "websocket")
        self.assertEqual(headers["connection"], "upgrade")
        self.assertEqual(result["path"], "/socket?token=opaque")

    def test_proxy_pass_preserves_encoded_path_and_repeated_query(self) -> None:
        result = request(
            self.proxy_port,
            "/api/a%2Fb?item=one&item=two",
            {"Host": "example.local"},
        )
        self.assertEqual(result["path"], "/api/a%2Fb?item=one&item=two")

    def test_request_body_limit_is_enforced_before_upstream(self) -> None:
        connection = http.client.HTTPConnection("127.0.0.1", self.proxy_port, timeout=5)
        try:
            connection.request(
                "POST",
                "/upload",
                body=b"x" * (1024 * 1024 + 1),
                headers={"Host": "example.local", "Content-Type": "application/octet-stream"},
            )
            response = connection.getresponse()
            response.read()
            self.assertEqual(response.status, 413)
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
