"""해시 테이블 테스트. 실행: make test"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hash_table import HashTable, horner_hash  # noqa: E402


class TestHornerHash(unittest.TestCase):
    def test_matches_topic_08(self):
        # 주제 08 "문자열 해싱"의 표와 같은 값이어야 한다.
        self.assertEqual(horner_hash("stop", 97), 9)
        self.assertEqual(horner_hash("spot", 97), 49)
        self.assertEqual(horner_hash("post", 97), 49)

    def test_same_every_run(self):
        # 내장 hash()와 달리 실행할 때마다 같아야 한다.
        self.assertEqual(horner_hash("https://www.yonsei.ac.kr", 1000003),
                         horner_hash("https://www.yonsei.ac.kr", 1000003))

    def test_range(self):
        for key in ["", "a", "https://example.com/" + "x" * 500]:
            self.assertTrue(0 <= horner_hash(key, 13) < 13)


class TestHashTable(unittest.TestCase):
    def test_put_get(self):
        t = HashTable()
        t.put("a", 1)
        t.put("b", 2)
        self.assertEqual(t.get("a"), 1)
        self.assertEqual(t.get("b"), 2)
        self.assertIsNone(t.get("c"))
        self.assertEqual(len(t), 2)

    def test_update_does_not_grow(self):
        t = HashTable()
        t.put("a", 1)
        t.put("a", 9)
        self.assertEqual(t.get("a"), 9)
        self.assertEqual(len(t), 1)

    def test_contains(self):
        t = HashTable()
        t.put("a", 1)
        self.assertIn("a", t)
        self.assertNotIn("b", t)

    def test_collisions(self):
        # spot과 post는 M=97에서 같은 칸(49)이다. 둘 다 찾아야 한다.
        t = HashTable(capacity=97, max_load=None)
        t.put("spot", 1)
        t.put("post", 2)
        self.assertEqual(t.find("spot"), (1, 1))
        self.assertEqual(t.find("post"), (2, 2))

    def test_wrap_around(self):
        # 마지막 칸에서 충돌하면 0번 칸으로 넘어간다.
        m = 7
        keys = [k for k in (chr(c) for c in range(33, 127)) if horner_hash(k, m) == m - 1][:2]
        t = HashTable(capacity=m, max_load=None)
        for i, k in enumerate(keys):
            t.put(k, i)
        self.assertEqual(t.find(keys[1]), (1, 2))

    def test_resize_keeps_all_keys(self):
        t = HashTable(capacity=4, max_load=0.5)
        for i in range(1000):
            t.put(f"key{i}", i)
        self.assertEqual(len(t), 1000)
        self.assertLessEqual(t.load_factor, 0.5)
        for i in range(1000):
            self.assertEqual(t.get(f"key{i}"), i)

    def test_fixed_table_overflows(self):
        t = HashTable(capacity=3, max_load=None)
        for k in "abc":
            t.put(k, 0)
        self.assertEqual(t.load_factor, 1.0)
        with self.assertRaises(OverflowError):
            t.put("d", 0)
        t.put("a", 1)  # 있던 키는 가득 차도 바꿀 수 있다
        self.assertEqual(t.get("a"), 1)

    def test_missing_key_in_full_table_stops(self):
        t = HashTable(capacity=3, max_load=None)
        for k in "abc":
            t.put(k, 0)
        value, probes = t.find("zz")
        self.assertIsNone(value)
        self.assertEqual(probes, 3)


if __name__ == "__main__":
    unittest.main()
