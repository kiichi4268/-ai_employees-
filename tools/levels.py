"""⭐（星）× LV の計算（上限なし・2026-11-11 加藤さん「ゲームみたいに上限をつけたくない」）。

- 1つの星の中で LV1 → LV100。LV100 を超えたら星が1つ上がり、LV1 から（⭐1 LV100 → ⭐2 LV1）。星に上限はない。
- 星が上がるほど1レベルに要る EXP が増える（⭐1 は100、⭐2 は200、⭐s は 100×s）。上に行くほど「日々の学び」を積まないと上がらない。
- 星 s を終えるまでに要る合計 EXP = 100 × 100 × (1+2+…+s) = 5,000 × s × (s+1)。

使い方:
  python3 tools/levels.py 1234          → ⭐1 LV13（次のLVまで 66 EXP）
  python3 tools/levels.py --self-test
シートの「AI社員のレベル」タブも同じ式で自動計算している（E列の EXP を入れるだけ）。
"""
import math, sys


def star_lv(exp):
    """EXP の合計から (星, LV, 次のLVまでのEXP, 今の星での1LVに要るEXP) を返す。"""
    exp = max(0, int(exp))
    s = int((-1 + math.sqrt(1 + 8 * exp / 10000)) // 2) + 1  # exp < 5000 s(s+1) となる最小の s
    while exp >= 5000 * s * (s + 1): s += 1
    while s > 1 and exp < 5000 * (s - 1) * s: s -= 1
    rem = exp - 5000 * (s - 1) * s
    per = 100 * s
    return s, rem // per + 1, per - rem % per, per


def label(exp):
    s, lv, nxt, _ = star_lv(exp)
    return f"⭐{s} LV{lv}（次のLVまで {nxt} EXP）"


def self_test():
    assert star_lv(0)[:2] == (1, 1)
    assert star_lv(99)[:2] == (1, 1) and star_lv(100)[:2] == (1, 2)
    assert star_lv(9999)[:2] == (1, 100)
    assert star_lv(10000)[:2] == (2, 1)          # ⭐1 LV100 の次は ⭐2 LV1
    assert star_lv(10199)[:2] == (2, 1) and star_lv(10200)[:2] == (2, 2)  # ⭐2 は 200 EXP で1LV
    assert star_lv(29999)[:2] == (2, 100) and star_lv(30000)[:2] == (3, 1)
    assert star_lv(5000 * 50 * 51)[:2] == (51, 1)  # 星に上限はない
    print("self-test: ⭐1 LV1 → ⭐1 LV100 → ⭐2 LV1 …（上限なし）すべて想定どおり")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]: self_test()
    elif sys.argv[1:]: print(label(sys.argv[1]))
    else: print(__doc__)
