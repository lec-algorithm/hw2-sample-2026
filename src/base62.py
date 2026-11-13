"""base62 인코딩: 0 이상의 정수를 0-9, a-z, A-Z 62글자로 쓴다.

일련번호 1, 2, 3, ...을 짧은 코드로 바꾸는 데 쓴다. 62진법이므로 n의 자릿수는
log62(n)에 비례한다. 1억 개를 만들어도 코드는 다섯 글자다.
"""

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)  # 62


def encode(n):
    """0 이상의 정수 n을 base62 문자열로. encode(0)은 "0"이다."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("정수만 인코딩할 수 있습니다")
    if n < 0:
        raise ValueError("음수는 인코딩할 수 없습니다")
    if n == 0:
        return ALPHABET[0]
    digits = []
    while n > 0:
        n, r = divmod(n, BASE)
        digits.append(ALPHABET[r])
    return "".join(reversed(digits))


def decode(s):
    """base62 문자열 s를 정수로. 빈 문자열이나 알파벳 밖 글자는 ValueError."""
    if not isinstance(s, str) or s == "":
        raise ValueError("빈 코드는 디코딩할 수 없습니다")
    n = 0
    for c in s:
        i = ALPHABET.find(c)
        if i < 0:
            raise ValueError(f"base62 글자가 아닙니다: {c!r}")
        n = n * BASE + i
    return n


if __name__ == "__main__":
    for n in (0, 1, 61, 62, 3843, 3844, 100_000_000):
        print(f"{n:>11} -> {encode(n)}")
