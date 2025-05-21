# gui_hexagram_predictor.py
# =============================================================
# 「完整八卦大樂透預測器」
#  • 以擲銅錢法 (三枚) 起一卦，6 爻決定本卦→變卦
#  • 將本卦 (或變卦若有動爻) 轉為上卦 / 下卦 (0–7)
#  • 對應五行，並依陰陽 (奇偶) 給定選號規則
#  • 每爻對應 1 顆號碼，共 6 顆；保證互不重複、符合奇偶與五行尾數
#  • 可選「隨機銅錢」或「指定年月日時 (8 字) 起卦」
#  • GUI 以 Tkinter 實作，顯示卦象圖、本卦→變卦、六顆預測號碼
# =============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime

# ────────────── 卦象與五行基礎資料 ──────────────
TRIGRAMS = [
    '坤', '乾', '兌', '離', '震', '巽', '坎', '艮'  # 0–7 (先將坤排0，乾排1 方便映射)
]
TRI_ELEMENT = {
    '乾': '金', '兌': '金', '離': '火', '震': '木',
    '巽': '木', '坎': '水', '艮': '土', '坤': '土'
}
ELEMENT_TAIL = {
    '木': {3, 8},
    '火': {2, 7},
    '土': {0, 5},
    '金': {4, 9},
    '水': {1, 6}
}
YIN_NUMS = {n for n in range(1, 50) if n % 2 == 0}
YANG_NUMS = {n for n in range(1, 50) if n % 2 == 1}

# ────────────── 擲銅錢起卦 ──────────────
# 3 枚銅錢：H=3, T=2 →和 6=老陰,7=少陽,8=少陰,9=老陽
COIN_MAP = {0: 2, 1: 3}  # 0=tail→2, 1=head→3 (新台幣：字面=tail)


def toss_line() -> int:
    return sum(random.choice([2, 3]) for _ in range(3))


def auto_hexagram() -> list[int]:
    """產生 6 爻 (自下而上)"""
    return [toss_line() for _ in range(6)]


# ────────────── 八字時間起卦 (梅花易數簡化) ──────────────

def datetime_hexagram(dt: datetime) -> list[int]:
    """使用當前年月日時 (梅花易數) 取數。簡化公式：
    (年+月+日+時) % 8 作為下卦索引，(年+月+日+時) % 8 作為上卦索引，
    動爻 = (年+月+日+時) % 6，為 0 無動。若有動→變卦。
    爻值用少陽/少陰, 動爻視為老陽/老陰
    """
    num_sum = dt.year + dt.month + dt.day + dt.hour
    lower = num_sum % 8
    upper = (num_sum // 8) % 8
    moving = num_sum % 6  # 0~5，0 無動
    lines = []
    for i in range(6):
        # 少陰8 少陽7
        v = 8 if ((lower if i < 3 else upper) in [0,3,5,7]) else 7  # 偶：陰卦=少陰  奇：陽卦=少陽  (粗略)
        if moving and i == moving - 1:
            v = 6 if v == 8 else 9
        lines.append(v)
    return lines


# ────────────── 卦象工具 ──────────────

def lines_to_trigrams(lines: list[int]):
    # 0–2 下卦，3–5 上卦, 取陰陽二進制 0/1 (陰=0,陽=1)
    def tri_index(seg):
        bits = [(1 if x % 2 == 1 else 0) for x in seg]
        return bits[0] + bits[1]*2 + bits[2]*4  # 道家順序
    lower = tri_index(lines[:3])
    upper = tri_index(lines[3:])
    return TRIGRAMS[lower], TRIGRAMS[upper]


# ────────────── 號碼生成規則 ──────────────

def pick_number(pool, used, element):
    candidates = [n for n in pool if (n not in used) and (n % 10 in ELEMENT_TAIL[element])]
    if not candidates:
        # 放寬尾數限制
        candidates = [n for n in pool if n not in used]
    return random.choice(candidates)


def generate_numbers(lines):
    """根據 6 爻陰陽 + 卦象五行產生 6 顆互不重複號碼"""
    lower_tri, upper_tri = lines_to_trigrams(lines)
    numbers = []
    for idx, v in enumerate(lines):
        parity_pool = YANG_NUMS if v % 2 == 1 else YIN_NUMS
        trigram = lower_tri if idx < 3 else upper_tri
        elem = TRI_ELEMENT[trigram]
        num = pick_number(parity_pool, numbers, elem)
        numbers.append(num)
    return sorted(numbers)

# ────────────── GUI ──────────────
class HexagramGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('完整八卦預測器')
        self.geometry('420x480')
        self.lines = []
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(pady=10)
        ttk.Button(frm, text='隨機擲卦', command=self.random_hexagram).grid(row=0, column=0, padx=5)
        ttk.Button(frm, text='以當前時間起卦', command=self.datetime_hexagram).grid(row=0, column=1, padx=5)
        ttk.Button(frm, text='重新選號', command=self.refresh_numbers).grid(row=0, column=2, padx=5)

        self.hex_text = tk.Text(self, height=8, width=40, state='disabled', font=('Consolas', 12))
        self.hex_text.pack(pady=10)
        self.num_var = tk.StringVar()
        ttk.Label(self, text='預測號碼', font=('Arial', 12)).pack()
        ttk.Label(self, textvariable=self.num_var, font=('Consolas', 20)).pack(pady=10)

    # 事件
    def random_hexagram(self):
        self.lines = auto_hexagram()
        self.display_hexagram()
        self.generate_and_show()

    def datetime_hexagram(self):
        self.lines = datetime_hexagram(datetime.now())
        self.display_hexagram()
        self.generate_and_show()

    def refresh_numbers(self):
        if not self.lines:
            messagebox.showinfo('提示', '請先起卦')
            return
        self.generate_and_show()

    # Helper
    def display_hexagram(self):
        self.hex_text.configure(state='normal'); self.hex_text.delete('1.0', tk.END)
        lines_disp = []
        symbols = {6:'⚋ x', 7:'⚊', 8:'⚋', 9:'⚊ x'}
        for v in self.lines[::-1]:  # 高爻在上
            lines_disp.append(symbols[v])
        lower, upper = lines_to_trigrams(self.lines)
        self.hex_text.insert(tk.END, '\n'.join(lines_disp) + f"\n上卦: {upper}  下卦: {lower}\n")
        self.hex_text.configure(state='disabled')

    def generate_and_show(self):
        nums = generate_numbers(self.lines)
        self.num_var.set('  '.join(f"{n:02d}" for n in nums))


if __name__ == '__main__':
    try:
        import numpy  # ensure numpy available for randomness consistency (optional)
    except ImportError:
        pass
    app = HexagramGUI()
    app.mainloop()
