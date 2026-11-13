"""단축기 테스트. 실행: make test"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shortener import Shortener  # noqa: E402


class TestShortener(unittest.TestCase):
    def setUp(self):
        self.s = Shortener()

    def test_first_code_is_1(self):
        self.assertEqual(self.s.shorten("https://www.yonsei.ac.kr"), "1")

    def test_round_trip(self):
        urls = [f"https://example.com/{i}" for i in range(200)]
        codes = [self.s.shorten(u) for u in urls]
        self.assertEqual(len(set(codes)), 200)
        for u, c in zip(urls, codes):
            self.assertEqual(self.s.expand(c), u)

    def test_same_url_same_code(self):
        a = self.s.shorten("https://a.com")
        b = self.s.shorten("https://a.com")
        c = self.s.shorten("https://b.com")
        self.assertEqual(a, b)
        self.assertEqual(c, "2")  # 번호를 하나만 썼다

    def test_strip_spaces(self):
        a = self.s.shorten("https://a.com")
        self.assertEqual(self.s.shorten("  https://a.com\n"), a)
        self.assertEqual(self.s.expand(a), "https://a.com")

    def test_invalid_urls(self):
        for bad in ["ftp://a.com", "www.a.com", "http://", "https://a b",
                    "https://" + "a" * 2041, ""]:
            with self.assertRaises(ValueError, msg=bad):
                self.s.shorten(bad)

    def test_long_url_limit(self):
        ok = "https://" + "a" * 2040  # 정확히 2048자
        self.assertEqual(len(ok), 2048)
        self.assertEqual(self.s.expand(self.s.shorten(ok)), ok)

    def test_unknown_code(self):
        self.s.shorten("https://a.com")
        self.assertIsNone(self.s.expand("zzz"))
        self.assertIsNone(self.s.expand("!!"))
        self.assertIsNone(self.s.expand(""))


if __name__ == "__main__":
    unittest.main()
