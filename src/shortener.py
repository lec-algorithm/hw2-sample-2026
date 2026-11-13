"""URL 단축기: 일련번호를 base62로 바꿔 코드로 쓴다.

코드를 URL의 해시값으로 만들지 않는다. 그러면 서로 다른 URL이 같은 코드를
받을 수 있다. 일련번호는 겹치지 않는다. 해시 테이블은 저장에만 쓴다.
"""

from base62 import decode, encode
from hash_table import HashTable

MAX_URL_LENGTH = 2048


def validate(url):
    """앞뒤 공백을 지운 URL. 받을 수 없는 URL이면 ValueError"""
    url = url.strip()
    if len(url) > MAX_URL_LENGTH:
        raise ValueError(f"URL이 {MAX_URL_LENGTH}자를 넘습니다")
    for scheme in ("http://", "https://"):
        if url.startswith(scheme):
            rest = url[len(scheme):]
            break
    else:
        raise ValueError("http:// 또는 https://로 시작해야 합니다")
    if rest == "":
        raise ValueError("주소가 비어 있습니다")
    if any(c.isspace() for c in url):
        raise ValueError("URL 안에 공백이 있습니다")
    return url


class Shortener:
    def __init__(self):
        self._next = 1
        self._code_of = HashTable()  # URL -> 코드
        self._url_of = HashTable()   # 코드 -> URL

    def __len__(self):
        return len(self._url_of)

    def shorten(self, url):
        url = validate(url)
        code = self._code_of.get(url)
        if code is not None:
            return code
        code = encode(self._next)
        self._next += 1
        self._code_of.put(url, code)
        self._url_of.put(code, url)
        return code

    def expand(self, code):
        try:
            decode(code)
        except ValueError:
            return None
        return self._url_of.get(code)
