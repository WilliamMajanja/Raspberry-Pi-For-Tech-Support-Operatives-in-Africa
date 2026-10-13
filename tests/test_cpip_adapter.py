import base64
import hashlib
import hmac
import json
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from portal.cpip_adapter import CPIPAdapter


TEST_KEY = "test-cpip-key-that-is-long-enough-for-local-tests"


class MockCPIPHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        ts, supplied = self.headers.get("X-CPIP-HMAC", ":").split(":", 1)
        expected = hmac.new(TEST_KEY.encode(), f"{ts}:POST:{self.path}".encode(), hashlib.sha256).hexdigest()
        if abs(time.time() - int(ts)) > 300 or not hmac.compare_digest(supplied, expected):
            self.send_response(401)
            self.end_headers()
            return
        if self.path.endswith("/encode"):
            cipher = base64.urlsafe_b64encode(body["message"].encode()).decode()
            result = {"status": "encoded", "accept_additions_header": "milk;variety=" + cipher}
        elif self.path.endswith("/decode"):
            cipher = body["accept_additions"].split("=", 1)[1]
            result = {"status": "decoded", "message": base64.urlsafe_b64decode(cipher.encode()).decode()}
        else:
            self.send_response(404)
            self.end_headers()
            return
        data = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class CPIPAdapterTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), MockCPIPHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        origin = f"http://127.0.0.1:{self.server.server_port}"
        self.adapter = CPIPAdapter(origin, TEST_KEY)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def test_cpip_encode_decode_roundtrip(self):
        cipher = self.adapter.encode_token("a" * 24, "opaque-random-token")
        self.assertNotIn("opaque-random-token", cipher)
        self.assertEqual(self.adapter.decode_token(cipher), ("a" * 24, "opaque-random-token"))

    def test_rejects_public_backend_and_invalid_edition(self):
        with self.assertRaises(Exception):
            CPIPAdapter("http://example.org:4180", TEST_KEY)
        with self.assertRaises(Exception):
            self.adapter.encode_token("../unsafe", "token")


if __name__ == "__main__":
    unittest.main()
