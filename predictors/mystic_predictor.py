# gui_mystic_predictor.py
# 玄學大樂透預測器：陰陽 + 五行 + 吉/忌 平衡
# -------------------------------------------------
# • 載入 lottery_results.xlsx 作為歷史資料
# • 生成符合玄學規則的 6 顆號碼組合
#   - 陰陽平衡：3 陽 3 陰 或 4 陽 2 陰
#   - 五行旺木水：至少各含 1 顆木、水尾數；金尾不得超過 2
#   - 吉/忌：最多 1 顆忌數 (4,14,24,44)，若出現忌數則必含吉數 6 或 8
#   - 不得與歷史開獎完全重複
# • Tkinter GUI：顯示生成組合，可按鈕刷新

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import random

# ---------------- 玄學映射 ----------------
YIN = {n for n in range(1, 50) if n % 2 == 0}  # 偶數
YANG = {n for n in range(1, 50) if n % 2 == 1}

TAIL_ELEMENT = {
    1: '水', 6: '水',
    2: '火', 7: '火',
    3: '木', 8: '木',
    4: '金', 9: '金',
    0: '土', 5: '土'
}

LUCKY = {6, 8, 9}
UNLUCKY = {4, 14, 24, 44}

# ---------------- 載入歷史組合 ----------------

def load_history(path: str = 'lottery_results.xlsx') -> set[str]:
    df = pd.read_excel(path)
    combos = df[[f'red{i}' for i in range(1, 7)]].astype(int)
    combo_set = {
        '-'.join(f"{n:02d}" for n in sorted(row))
        for row in combos.values.tolist()
    }
    return combo_set

HISTORY = load_history()

# ---------------- 規則檢查 ----------------

def check_rules(nums: list[int]) -> bool:
    # 1. 不得重複歷史
    key = '-'.join(f"{n:02d}" for n in sorted(nums))
    if key in HISTORY:
        return False
    # 2. 陰陽
    yang_cnt = sum(1 for n in nums if n in YANG)
    yin_cnt = 6 - yang_cnt
    if not ((yang_cnt == 3 and yin_cnt == 3) or (yang_cnt == 4 and yin_cnt == 2)):
        return False
    # 3. 五行
    elements = [TAIL_ELEMENT[n % 10] for n in nums]
    if elements.count('木') < 1 or elements.count('水') < 1:
        return False
    if elements.count('金') > 2:
        return False
    # 4. 吉/忌
    unlucky_present = any(n in UNLUCKY for n in nums)
    lucky_present = any(n in LUCKY for n in nums)
    if unlucky_present and not lucky_present:
        return False
    if sum(1 for n in nums if n in UNLUCKY) > 1:
        return False
    return True

# ---------------- 組合產生器 ----------------

def generate_combo(max_attempts: int = 10000) -> list[int] | None:
    attempts = 0
    while attempts < max_attempts:
        nums = random.sample(range(1, 50), 6)
        if check_rules(nums):
            return sorted(nums)
        attempts += 1
    return None

# ---------------- GUI ----------------
class MysticGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("玄學大樂透預測器")
        self.geometry("340x260")
        ttk.Label(self, text="符合陰陽‧五行‧吉/忌規則的號碼：", font=("Arial", 12)).pack(pady=10)
        self.num_var = tk.StringVar(value="點擊『生成』取得號碼")
        lbl = ttk.Label(self, textvariable=self.num_var, font=("Consolas", 18))
        lbl.pack(pady=10)
        btn = ttk.Button(self, text="生成號碼", command=self.on_generate)
        btn.pack(pady=10)
        self.status_var = tk.StringVar()
        ttk.Label(self, textvariable=self.status_var, foreground="gray").pack(pady=5)

    def on_generate(self):
        combo = generate_combo()
        if combo:
            self.num_var.set('  '.join(f"{n:02d}" for n in combo))
            self.status_var.set("成功生成！祝好運 ✨")
        else:
            messagebox.showwarning("生成失敗", "在上限嘗試次數內無法找到符合規則的組合，請稍後再試。")


if __name__ == '__main__':
    app = MysticGUI()
    app.mainloop()
