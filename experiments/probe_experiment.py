"""적재율에 따른 평균 탐지 횟수 실험.

크기를 고정한 테이블(max_load=None)에 무작위 URL을 적재율 α까지 넣고,
  - 성공 탐색: 넣은 키를 모두 한 번씩 찾을 때 들여다본 칸 수의 평균
  - 실패 탐색: 넣지 않은 키를 찾을 때 들여다본 칸 수의 평균
을 잰다. 주제 08의 크누스 근삿값과 나란히 놓는다.

실행: make experiment  →  experiments/results.csv, experiments/probes.svg
"""

import csv
import random
import string
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from hash_table import HashTable  # noqa: E402

M = 4093            # 소수. 주제 08 "M은 소수로"
MISSES = 2000       # 실패 탐색에 쓰는 없는 키 수
SEED = 2026         # 같은 숫자가 다시 나오도록 고정
ALPHAS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9]


def random_url(rng):
    path = "".join(rng.choices(string.ascii_letters + string.digits, k=10))
    return f"https://example.com/{path}"


def theory(alpha):
    return 0.5 * (1 + 1 / (1 - alpha)), 0.5 * (1 + 1 / (1 - alpha) ** 2)


def measure(alpha, rng):
    n = int(alpha * M)
    t = HashTable(capacity=M, max_load=None)
    keys = []
    while len(keys) < n:
        url = random_url(rng)
        if url not in t:
            t.put(url, True)
            keys.append(url)
    hit = sum(t.find(k)[1] for k in keys) / n
    missing = 0
    total = 0
    while missing < MISSES:
        url = random_url(rng)
        if url in t:
            continue
        total += t.find(url)[1]
        missing += 1
    return hit, total / MISSES


def main():
    rng = random.Random(SEED)
    rows = []
    print(f"M = {M}, 실패 탐색 {MISSES}회")
    print(f"{'α':>5} {'성공(실험)':>10} {'성공(이론)':>10} {'실패(실험)':>10} {'실패(이론)':>10}")
    for a in ALPHAS:
        hit, miss = measure(a, rng)
        th, tm = theory(a)
        rows.append((a, hit, th, miss, tm))
        print(f"{a:>5} {hit:>10.2f} {th:>10.2f} {miss:>10.2f} {tm:>10.2f}")

    with open(HERE / "results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["alpha", "hit_measured", "hit_theory", "miss_measured", "miss_theory"])
        for r in rows:
            w.writerow([r[0]] + [f"{x:.3f}" for x in r[1:]])

    (HERE / "probes.svg").write_text(chart(rows), encoding="utf-8")
    print("저장: experiments/results.csv, experiments/probes.svg")


def chart(rows):
    """표준 모듈만으로 SVG 선 그래프를 그린다. 왼쪽 위가 (0, 0)이다."""
    w, h = 640, 400
    left, right, top, bottom = 56, 160, 28, 48
    pw, ph = w - left - right, h - top - bottom
    ymax = 70

    def x(a):
        return left + a * pw

    def y(v):
        return top + ph - min(v, ymax) / ymax * ph

    series = [  # (이름, 열 번호, 색, 점선)
        ("실패 · 이론", 4, "#D55E00", "6 4"),
        ("실패 · 실험", 3, "#D55E00", ""),
        ("성공 · 이론", 2, "#0072B2", "6 4"),
        ("성공 · 실험", 1, "#0072B2", ""),
    ]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
           f'font-family="sans-serif" font-size="12">',
           f'<rect width="{w}" height="{h}" fill="#fbfbf9"/>']
    for v in range(0, ymax + 1, 10):
        out.append(f'<line x1="{left}" x2="{left + pw}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#dfe1e4"/>')
        out.append(f'<text x="{left - 8}" y="{y(v) + 4:.1f}" text-anchor="end" fill="#6e7781">{v}</text>')
    for a in (0, 0.25, 0.5, 0.75, 1):
        out.append(f'<text x="{x(a):.1f}" y="{top + ph + 18}" text-anchor="middle" fill="#6e7781">{a}</text>')
    out.append(f'<text x="{left + pw / 2}" y="{h - 10}" text-anchor="middle" fill="#24292f">적재율 α</text>')
    out.append(f'<text x="14" y="{top + ph / 2}" text-anchor="middle" fill="#24292f" '
               f'transform="rotate(-90 14 {top + ph / 2})">평균 탐지 칸 수</text>')
    for i, (name, col, color, dash) in enumerate(series):
        pts = " ".join(f"{x(r[0]):.1f},{y(r[col]):.1f}" for r in rows)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"{dash_attr}/>')
        if not dash:
            for r in rows:
                out.append(f'<circle cx="{x(r[0]):.1f}" cy="{y(r[col]):.1f}" r="3" fill="{color}"/>')
        ly = top + 10 + i * 20
        out.append(f'<line x1="{left + pw + 16}" x2="{left + pw + 40}" y1="{ly}" y2="{ly}" '
                   f'stroke="{color}" stroke-width="2"{dash_attr}/>')
        out.append(f'<text x="{left + pw + 46}" y="{ly + 4}" fill="#24292f">{name}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    main()
