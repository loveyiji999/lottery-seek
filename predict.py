# gui_lottery_predictor.py
# GUI 版進階大樂透預測器：科學 + 玄學 權重組合並可選 top/random 策略

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from datetime import datetime
from math import exp
import random

# ---------- 權重計算函數 ----------
def load_history(filename="lottery_results.xlsx") -> pd.DataFrame:
    df = pd.read_excel(filename)
    reds = df[[f"red{i}" for i in range(1,7)]].astype(int)
    return reds

def frequency_weights(reds: pd.DataFrame) -> np.ndarray:
    counts = reds.values.flatten()
    freq = pd.Series(counts).value_counts().sort_index().values.astype(float)
    return (freq - freq.min()) / (freq.max() - freq.min())

def recency_weights(reds: pd.DataFrame, half_life: float = 50.0) -> np.ndarray:
    N = len(reds)
    weights = np.zeros(49)
    for idx, row in reds.iterrows():
        age = N - idx
        w = exp(-age / half_life)
        for num in row:
            weights[num-1] += w
    return (weights - weights.min()) / (weights.max() - weights.min())

def numerology_weights(sigma: float = 8.0) -> np.ndarray:
    today = datetime.today().strftime("%Y%m%d")
    s = sum(int(d) for d in today)
    center = (s % 49) + 1
    w = np.array([exp(-((i-center)**2) / (2*sigma**2)) for i in range(1,50)])
    return (w - w.min()) / (w.max() - w.min())

def fibonacci_weights() -> np.ndarray:
    fib = [1,1]
    while len(fib) < 49:
        fib.append(fib[-1] + fib[-2])
    weights = np.array([f % 49 for f in fib[:49]], dtype=float)
    return (weights - weights.min()) / (weights.max() - weights.min())

def combine(weights_list, alphas) -> np.ndarray:
    combined = np.zeros_like(weights_list[0])
    for w, a in zip(weights_list, alphas):
        combined += w * a
    return combined

def predict(weights: np.ndarray, method: str = 'top', k: int = 6) -> list[int]:
    if method == 'top':
        idx = np.argsort(weights)[-k:][::-1]
        return [i + 1 for i in idx]
    elif method == 'random':
        p = weights / weights.sum()
        return list(np.random.choice(np.arange(1,50), size=k, replace=False, p=p))
    else:
        raise ValueError("Invalid method")

# ---------- GUI ----------
class LotteryGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("大樂透預測器 (科學+玄學)")
        self.geometry("400x500")
        # 加載歷史資料並生成各權重
        self.reds = load_history()
        self.weights_funcs = {
            '頻率': frequency_weights,
            '時序': recency_weights,
            '數字學': numerology_weights,
            'Fibonacci': fibonacci_weights,
        }
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10, fill='x')
        # 科學方法
        sci_label = ttk.Label(frame, text="科學方法：")
        sci_label.pack(anchor='w')
        self.sci_vars = {}
        for name in ['頻率', '時序']:
            var = tk.BooleanVar(value=True)
            chk = ttk.Checkbutton(frame, text=name, variable=var)
            chk.pack(anchor='w')
            self.sci_vars[name] = var
        # 玄學方法
        myst_label = ttk.Label(frame, text="玄學方法：")
        myst_label.pack(anchor='w', pady=(10,0))
        self.myst_vars = {}
        for name in ['數字學', 'Fibonacci']:
            var = tk.BooleanVar(value=True)
            chk = ttk.Checkbutton(frame, text=name, variable=var)
            chk.pack(anchor='w')
            self.myst_vars[name] = var
        # 策略選擇
        strat_label = ttk.Label(frame, text="預測策略：")
        strat_label.pack(anchor='w', pady=(10,0))
        self.method_var = tk.StringVar(value='top')
        ttk.Radiobutton(frame, text='Top K', variable=self.method_var, value='top').pack(anchor='w')
        ttk.Radiobutton(frame, text='隨機', variable=self.method_var, value='random').pack(anchor='w')
        # K 值
        k_frame = ttk.Frame(frame)
        k_frame.pack(anchor='w', pady=(10,0))
        ttk.Label(k_frame, text='選取數量 K:').pack(side='left')
        self.k_var = tk.IntVar(value=6)
        ttk.Spinbox(k_frame, from_=1, to=49, textvariable=self.k_var, width=5).pack(side='left')
        # 預測按鈕
        btn = ttk.Button(frame, text='預測號碼', command=self.on_predict)
        btn.pack(pady=(20,0))
        # 結果顯示
        self.result_text = tk.Text(self, height=10)
        self.result_text.pack(padx=10, pady=10, fill='both', expand=True)

    def on_predict(self):
        methods = []
        weights = []
        # 科學
        for name, var in self.sci_vars.items():
            if var.get():
                w = self.weights_funcs[name](self.reds)
                methods.append(name)
                weights.append(w)
        # 玄學
        for name, var in self.myst_vars.items():
            if var.get():
                if name == '數字學':
                    w = numerology_weights()
                else:
                    w = fibonacci_weights()
                methods.append(name)
                weights.append(w)
        if not weights:
            messagebox.showwarning("錯誤", "請至少選擇一種方法！")
            return
        alphas = [1/len(weights)] * len(weights)
        comb = combine(weights, alphas)
        k = self.k_var.get()
        top_nums = predict(comb, 'top', k)
        rand_nums = predict(comb, 'random', k)
        # 顯示
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, f"方法：{', '.join(methods)}\n")
        self.result_text.insert(tk.END, f"Top {k} 號碼：{top_nums}\n")
        self.result_text.insert(tk.END, f"隨機 {k} 號碼：{rand_nums}\n")

if __name__ == '__main__':
    app = LotteryGUI()
    app.mainloop()
