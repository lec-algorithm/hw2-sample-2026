"""URL 단축기 웹 서버. 표준 모듈 http.server만 쓴다.

  GET  /          URL을 넣는 폼
  POST /shorten   짧은 링크를 만들어 보여 준다
  GET  /<코드>    원래 URL로 302 이동

실행: make serve  (Codespaces에서는 아래 '포트' 탭에 8000이 뜬다)
저장은 메모리에만 한다. 서버를 끄면 링크가 사라진다.
"""

import argparse
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from shortener import Shortener

store = Shortener()

PAGE = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>URL 단축기</title>
<style>
 body {{ font-family: sans-serif; max-width: 36rem; margin: 3rem auto; padding: 0 1rem; line-height: 1.6; }}
 input[type=url] {{ width: 100%; padding: .6rem; font-size: 1rem; box-sizing: border-box; }}
 button {{ margin-top: .6rem; padding: .6rem 1.2rem; font-size: 1rem; }}
 .short {{ font-size: 1.4rem; word-break: break-all; }}
 .error {{ color: #b3261e; }}
</style></head><body>
<h1>URL 단축기</h1>
{body}
<form method="post" action="/shorten">
 <input type="url" name="url" placeholder="https://..." required>
 <button>줄이기</button>
</form>
<p>저장된 링크 {count}개</p>
</body></html>
"""


class Handler(BaseHTTPRequestHandler):
    def base_url(self):
        # Codespaces는 프록시 뒤에 있다. Host만 보면 localhost:8000이 찍힌다.
        host = self.headers.get("X-Forwarded-Host") or self.headers.get("Host", "localhost")
        proto = self.headers.get("X-Forwarded-Proto", "http")
        return f"{proto}://{host}"

    def send_page(self, status, body):
        data = PAGE.format(body=body, count=len(store)).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self.send_page(200, "")
            return
        code = self.path.lstrip("/")
        url = store.expand(code)
        if url is None:
            self.send_page(404, f'<p class="error">없는 코드입니다: {html.escape(code)}</p>')
            return
        self.send_response(302)
        self.send_header("Location", url)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        if self.path != "/shorten":
            self.send_page(404, '<p class="error">없는 주소입니다</p>')
            return
        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        url = form.get("url", [""])[0]
        try:
            code = store.shorten(url)
        except ValueError as e:
            self.send_page(400, f'<p class="error">{html.escape(str(e))}</p>')
            return
        short = f"{self.base_url()}/{code}"
        self.send_page(200, f'<p class="short"><a href="{html.escape(short)}">{html.escape(short)}</a></p>'
                            f'<p>{html.escape(url.strip())}</p>')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    port = parser.parse_args().port
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"http://localhost:{port} 에서 듣는 중. 끄려면 Ctrl+C")
    server.serve_forever()


if __name__ == "__main__":
    main()
