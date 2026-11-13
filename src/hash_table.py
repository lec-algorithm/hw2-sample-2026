"""선형 탐지 해시 테이블: 주제 08의 것을 문자열 키 전용으로 다시 만든 것.

Python의 dict, set, 내장 hash()를 쓰지 않는다. 키와 값은 리스트 두 개에
나란히 둔다. hash()를 쓰지 않는 이유는 실행할 때마다 문자열 해시값이 바뀌어
실험을 다시 돌리면 다른 숫자가 나오기 때문이다.
"""

R = 31  # 호너 방식의 가중치. 주제 08과 같다.


def horner_hash(key, m):
    """h <- (R * h + code(c)) mod M. 글자마다 나머지를 취해 h가 M보다 커지지 않는다."""
    h = 0
    for c in key:
        h = (R * h + ord(c)) % m
    return h


class HashTable:
    def __init__(self, capacity=16, max_load=0.5):
        if capacity < 1:
            raise ValueError("capacity는 1 이상이어야 합니다")
        self._m = capacity
        self._n = 0
        self._max_load = max_load      # None이면 크기를 바꾸지 않는다
        self._keys = [None] * capacity  # None이면 빈칸
        self._values = [None] * capacity

    def __len__(self):
        return self._n

    def __contains__(self, key):
        return self._slot(key)[0] is not None

    @property
    def capacity(self):
        return self._m

    @property
    def load_factor(self):
        return self._n / self._m

    def _slot(self, key):
        """(key가 있는 칸 또는 None, 넣을 수 있는 빈칸 또는 None, 들여다본 칸 수)"""
        i = horner_hash(key, self._m)
        for probes in range(1, self._m + 1):
            k = self._keys[i]
            if k is None:
                return None, i, probes
            if k == key:
                return i, None, probes
            i = (i + 1) % self._m  # 끝에 닿으면 0번 칸으로
        return None, None, self._m  # 한 바퀴를 돌았다: 가득 찼고 키는 없다

    def find(self, key):
        """(값 또는 None, 들여다본 칸 수)"""
        found, _, probes = self._slot(key)
        if found is None:
            return None, probes
        return self._values[found], probes

    def get(self, key):
        return self.find(key)[0]

    def put(self, key, value):
        found, empty, _ = self._slot(key)
        if found is not None:
            self._values[found] = value
            return
        if empty is None:
            raise OverflowError("테이블이 가득 찼습니다")
        self._keys[empty] = key
        self._values[empty] = value
        self._n += 1
        if self._max_load is not None and self.load_factor > self._max_load:
            self._resize(2 * self._m)

    def _resize(self, new_m):
        old = zip(self._keys, self._values)
        self._m = new_m
        self._n = 0
        self._keys = [None] * new_m
        self._values = [None] * new_m
        for k, v in old:
            if k is not None:
                self.put(k, v)
