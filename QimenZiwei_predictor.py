# gui_qimen_ziwei_predictor.py
# =============================================================
# 彩券玄學加強版：奇門遁甲 + 紫微斗數
# -------------------------------------------------------------
#   ★ 奇門遁甲（簡化）：
#     - 以公曆年月日時計算地盤 (九宮 1~9)
#     - 值符落宮、開門落宮 → 視為最旺
#     - 各宮對應號碼池 (1–49)，先映射 1~9 ×5 →45，再以洛書順序補 46~49
#     - 權重：旺宮 3x，休生門 2x，其餘 1x
#   ★ 紫微斗數（簡化）：
#     - 需輸入出生年月日（時可略）
#     - 以年支排斗君宮 → 命宮索引 (1~12)
#     - 化祿、化權、化科、化忌（以年份 modulo 4 簡化）
#     - 命宮 + 化祿宮視為大旺，權/科次之，忌為略衰 → 權重 3,2,1,0.5
#   ★ 綜合：
#     - 用使用者勾選之比重 α_QM, α_ZW → combine(weights)
#     - 提供 Top-k 與 權重隨機抽法
# =============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import numpy as np
import random

# ------------------ 映射工具 ------------------
LOSHU_TO_NUMBERS = {
    1: [1,10,19,28,37],
    2: [2,11,20,29,38],
    3: [3,12,21,30,39],
    4: [4,13,22,31,40],
    5: [5,14,23,32,41],
    6: [6,15,24,33,42],
    7: [7,16,25,34,43],
    8: [8,17,26,35,44],
    9: [9,18,27,36,45],
}
# 補 46~49 到中宮 5
LOSHU_TO_NUMBERS[5] += [46,47,48,49]

# ------------------ 奇門遁甲簡化 ------------------

QIMEN_DOORS = ['休','生','傷','杜','景','死','驚','開','']  # 開門最吉


def qimen_weights(dt: datetime) -> np.ndarray:
    """簡化：
      • 地盤宮 = (年+月+日+時) % 9 +1  (洛書1~9)
      • 值符 = 宮
      • 開門 = (宮+7) %9 +1  (僅示例)
      • 開/值符 3x, 休/生 2x, 其餘 1x
    """
    num_sum = dt.year + dt.month + dt.day + dt.hour
    palace = num_sum % 9 + 1
    open_palace = (palace + 7) % 9 + 1
    # 簡化休門、生門：palace+1, palace+2
    rest_palace = (palace + 1) % 9 + 1
    growth_palace = (palace + 2) % 9 + 1
    weights = np.ones(49)
    def boost(p, factor):
        for n in LOSHU_TO_NUMBERS[p]:
            weights[n-1] *= factor
    boost(palace, 3)
    boost(open_palace, 3)
    boost(rest_palace, 2)
    boost(growth_palace, 2)
    return weights / weights.sum()

# ------------------ 紫微斗數簡化 ------------------

ZHI_IDX = {'子':1,'丑':2,'寅':3,'卯':4,'辰':5,'巳':6,'午':7,'未':8,'申':9,'酉':10,'戌':11,'亥':12}
GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'

def year_ganzhi(year:int):
    diff = year - 1984  # 1984甲子
    gan = GAN[diff%10]
    zhi = ZHI[diff%12]
    return gan+zhi


def ziwei_weights(birth: datetime) -> np.ndarray:
    """
    極簡：
      • 命宮 = (月 + 日) %12 (1~12)
      • 年干 mod4 -> 化祿宮 = 命宮+mod
      • 權=+1, 科=+2, 忌=+3 (示例)  ，但只做權重
    """
    pal_idx = (birth.month + birth.day) % 12 + 1
    transform = (birth.year % 4)  # 0=祿,1=權,2=科,3=忌
    weights = np.ones(49)
    # 宮→候選號碼池 (宮index-1)*4+1 作示例
    def palace_nums(p):
        base = (p-1)*4+1
        return list(range(base, min(base+4,50)))
    # 加權
    for n in palace_nums(pal_idx):
        weights[n-1] *= 3  # 命宮最旺
    if transform <3:
        for n in palace_nums((pal_idx+transform)%12 or 12):
            weights[n-1] *= 2  # 祿權科次旺
    else:
        for n in palace_nums((pal_idx+transform)%12 or 12):
            weights[n-1] *= 0.5  # 忌宮減半
    return weights / weights.sum()

# ------------------ 號碼生成 ------------------

def pick_numbers(prob, k=6):
    nums = np.random.choice(np.arange(1,50), size=k, replace=False, p=prob)
    return sorted(nums)

# ------------------ GUI ------------------
class PredictorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('奇門遁甲 + 紫微斗數 預測器')
        self.geometry('480x380')
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(pady=8)
        # 紫微生日輸入
        ttk.Label(frm, text='出生年月日 (YYYY-MM-DD):').grid(row=0,column=0,sticky='e')
        self.birth_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.birth_var,width=12).grid(row=0,column=1)
        # 比重
        ttk.Label(frm, text='奇門 (0~1):').grid(row=1,column=0,sticky='e')
        self.qm_var = tk.DoubleVar(value=0.5)
        ttk.Entry(frm, textvariable=self.qm_var,width=6).grid(row=1,column=1,sticky='w')
        ttk.Label(frm, text='紫微 (補足):').grid(row=1,column=2,sticky='e')
        # 按鈕
        ttk.Button(self, text='生成號碼', command=self.on_generate).pack(pady=15)
        self.output = tk.Text(self,height=10,state='disabled',font=('Consolas',12))
        self.output.pack(fill='both',expand=True,padx=10)

    def on_generate(self):
        try:
            birth = datetime.strptime(self.birth_var.get().strip(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror('格式錯誤','請輸入 YYYY-MM-DD 格式生日'); return
        alpha = min(max(self.qm_var.get(),0),1)
        qm_w = qimen_weights(datetime.now())
        zw_w = ziwei_weights(birth)
        combined = qm_w*alpha + zw_w*(1-alpha)
        combined /= combined.sum()
        nums_top = np.argsort(combined)[-6:][::-1]+1
        nums_rand = pick_numbers(combined,6)
        self.output.configure(state='normal'); self.output.delete('1.0',tk.END)
        self.output.insert(tk.END, f"奇門權重: {alpha:.2f}\n紫微權重: {1-alpha:.2f}\n")
        self.output.insert(tk.END, f"Top6: {' '.join(f'{n:02d}' for n in nums_top)}\n")
        self.output.insert(tk.END, f"隨機6: {' '.join(f'{n:02d}' for n in nums_rand)}\n")
        self.output.configure(state='disabled')

if __name__ == '__main__':
    import numpy as np
    PredictorGUI().mainloop()
