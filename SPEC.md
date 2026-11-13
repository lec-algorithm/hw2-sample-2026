# 명세: URL 단축기

## 1. 무엇을 만드는가

긴 URL을 넣으면 짧은 코드를 돌려주고, 그 코드로 접속하면 원래 URL로 보내 주는
서비스. 코드와 URL의 대응은 **직접 구현한 해시 테이블**에 저장한다.

## 2. base62 인코딩 (`src/base62.py`)

- `encode(n)`: 0 이상의 정수를 글자 `0-9`, `a-z`, `A-Z` 순서의 62진법 문자열로
  바꾼다. `encode(0)`은 `"0"`, `encode(61)`은 `"Z"`, `encode(62)`는 `"10"`
- 음수는 `ValueError`, 정수가 아니면(`bool` 포함) `TypeError`
- `decode(s)`: 역변환. 빈 문자열이나 62글자 밖의 글자는 `ValueError`
- 대소문자를 구분한다. `"a"`와 `"A"`는 다른 수다.

## 3. 해시 테이블 (`src/hash_table.py`)

- 충돌은 **선형 탐지**로 푼다. 차 있으면 다음 칸, 끝에 닿으면 0번 칸
- 키는 문자열. 해시는 주제 08의 **호너 방식**: `h = (31 * h + ord(c)) % M`
- Python의 `dict`, `set`, 내장 `hash()`는 쓰지 않는다. 저장은 리스트로만 한다.
  - `hash()`는 실행할 때마다 문자열 해시값이 바뀌어 실험을 재현할 수 없다.
- `HashTable(capacity=16, max_load=0.5)`
  - 넣은 뒤 적재율 N/M이 `max_load`를 넘으면 크기를 두 배로 늘리고 모든 키를 다시 넣는다.
  - `max_load=None`이면 크기를 바꾸지 않는다(실험용). 이때 가득 차면 `OverflowError`
- `put(key, value)`: 새 키면 넣고, 있던 키면 값을 바꾼다.
- `get(key)`: 값, 없으면 `None`
- `find(key)`: `(값 또는 None, 들여다본 칸 수)`. 처음 들여다본 칸도 1로 센다.
- `len(t)`, `key in t`, `t.capacity`, `t.load_factor`
- 삭제는 만들지 않는다. 단축기는 지우지 않는다.

## 4. 단축기 (`src/shortener.py`)

- `Shortener()`의 `shorten(url)`은 코드를, `expand(code)`는 URL을 돌려준다.
- 코드는 일련번호 1, 2, 3, ...을 base62로 바꾼 것. 첫 URL은 `"1"`
- 같은 URL을 다시 넣으면 **새 번호를 쓰지 않고** 처음 코드를 돌려준다.
- URL 앞뒤의 공백은 지우고 저장한다. 그 밖에는 바꾸지 않는다.
- `http://` 또는 `https://`로 시작하지 않거나, 그 뒤가 비었거나, 공백이 들어 있거나,
  2048자를 넘으면 `ValueError`
- 없는 코드나 base62가 아닌 코드는 `expand`가 `None`을 돌려준다(예외 아님).
- URL→코드, 코드→URL 두 방향 모두 직접 만든 `HashTable`에 저장한다.

## 5. 웹 서버 (`src/server.py`)

- 표준 모듈 `http.server`만 쓴다. 기본 포트 8000, `--port`로 바꿀 수 있다.
- `GET /` → URL을 넣는 폼
- `POST /shorten` (폼 필드 `url`) → 짧은 링크를 보여 주는 페이지.
  잘못된 URL이면 400과 이유
- `GET /<코드>` → `302`, `Location`에 원래 URL. 없는 코드면 404
- 짧은 링크의 주소는 요청의 `X-Forwarded-Host`(없으면 `Host`)와
  `X-Forwarded-Proto`(없으면 `http`)로 만든다. Codespaces는 프록시 뒤에 있어서
  `Host`만 보면 `localhost:8000`이 찍힌다.
- 결과 페이지에 넣는 URL은 HTML 이스케이프한다.

## 6. 경계 사례

- `encode(0)`, `encode(61)`, `encode(62)`, 아주 큰 수의 왕복
- `decode("")`, `decode("-")`, 한글이 섞인 코드
- 해시: `"stop"`과 `"spot"`, `"post"`를 M=97에 넣으면 9, 49, 49 (주제 08 표와 같아야 한다)
- 크기를 늘린 뒤에도 모든 키를 찾는다.
- 같은 칸에 몰린 키를 모두 찾는다(충돌).
- `max_load=None`인 테이블을 가득 채우면 `OverflowError`
- 같은 URL을 두 번 → 같은 코드, 번호는 하나만 쓴다.
- 앞뒤 공백만 다른 URL은 같은 URL
- `ftp://...`, `http://`, `https://a b`, 2049자 URL → `ValueError`
- 없는 코드, `"!!"` 같은 코드 → `None`
