"""웹 서버 테스트. 실제로 서버를 띄우고 요청을 보낸다. 실행: make test"""

import http.client
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import server  # noqa: E402


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        conn.request(method, path, body=body, headers=headers or {})
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        conn.close()
        return res, data

    def shorten(self, url, headers=None):
        h = {"Content-Type": "application/x-www-form-urlencoded"}
        h.update(headers or {})
        return self.request("POST", "/shorten", urlencode({"url": url}), h)

    def test_form(self):
        res, data = self.request("GET", "/")
        self.assertEqual(res.status, 200)
        self.assertIn("<form", data)

    def test_shorten_and_redirect(self):
        res, data = self.shorten("https://www.yonsei.ac.kr/sc/")
        self.assertEqual(res.status, 200)
        code = server.store.shorten("https://www.yonsei.ac.kr/sc/")
        self.assertIn(f"/{code}", data)
        res, _ = self.request("GET", f"/{code}")
        self.assertEqual(res.status, 302)
        self.assertEqual(res.getheader("Location"), "https://www.yonsei.ac.kr/sc/")

    def test_forwarded_host(self):
        _, data = self.shorten("https://a.com/x", {"X-Forwarded-Host": "abc-8000.app.github.dev",
                                                   "X-Forwarded-Proto": "https"})
        self.assertIn("https://abc-8000.app.github.dev/", data)

    def test_bad_url(self):
        res, _ = self.shorten("ftp://a.com")
        self.assertEqual(res.status, 400)

    def test_unknown_code(self):
        res, _ = self.request("GET", "/nope123")
        self.assertEqual(res.status, 404)

    def test_escape(self):
        res, data = self.request("GET", "/<script>")
        self.assertEqual(res.status, 404)
        self.assertNotIn("<script>", data)


if __name__ == "__main__":
    unittest.main()
