# gui_predictor.py
# tkinter GUI 整合奇門遁甲 + 紫微斗數 + 權重合成樂透預測器

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mapping_engine

class LotteryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('玄學大樂透預測器')
        self.geometry('500x600')
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(padx=10, pady=10, fill='x')

        # 紫微生日
        ttk.Label(frm, text='出生日期 (YYYY-MM-DD HH:MM):').pack(anchor='w')
        self.birth_var = tk.StringVar(value='1990-05-17 15:30')
        ttk.Entry(frm, textvariable=self.birth_var).pack(fill='x')

        # 時區偏移
        ttk.Label(frm, text='時區偏移 (例: 8.0):').pack(anchor='w', pady=(10,0))
        self.tz_var = tk.DoubleVar(value=8.0)
        ttk.Entry(frm, textvariable=self.tz_var).pack(fill='x')

        # 奇門經度
        ttk.Label(frm, text='當地經度 (度, East +):').pack(anchor='w', pady=(10,0))
        self.lon_var = tk.DoubleVar(value=120.0)
        ttk.Entry(frm, textvariable=self.lon_var).pack(fill='x')

        # 權重比重
        ttk.Label(frm, text='奇門比重 α (0.0～1.0):').pack(anchor='w', pady=(10,0))
        self.alpha_var = tk.DoubleVar(value=0.5)
        ttk.Scale(frm, from_=0.0, to=1.0, variable=self.alpha_var, orient='horizontal').pack(fill='x')

        # 策略: Top 或 隨機
        ttk.Label(frm, text='選號策略:').pack(anchor='w', pady=(10,0))
        self.method_var = tk.StringVar(value='top')
        ttk.Radiobutton(frm, text='Top-k', variable=self.method_var, value='top').pack(anchor='w')
        ttk.Radiobutton(frm, text='隨機抽取', variable=self.method_var, value='random').pack(anchor='w')

        # K 值
        kfrm = ttk.Frame(frm)
        kfrm.pack(anchor='w', pady=(10,0))
        ttk.Label(kfrm, text='K 值 (選取號碼數):').pack(side='left')
        self.k_var = tk.IntVar(value=6)
        ttk.Spinbox(kfrm, from_=1, to=49, textvariable=self.k_var, width=5).pack(side='left')

        # 按鈕
        ttk.Button(frm, text='生成預測號碼', command=self.on_generate).pack(pady=20)

        # 結果輸出
        self.output = tk.Text(self, height=10, font=('Consolas', 14))
        self.output.pack(padx=10, pady=10, fill='both', expand=True)

    def on_generate(self):
        try:
            dt = datetime.strptime(self.birth_var.get(), '%Y-%m-%d %H:%M')
        except Exception:
            messagebox.showerror('錯誤', '請輸入正確的出生日期與時間格式')
            return
        tz = self.tz_var.get()
        lon = self.lon_var.get()
        alpha = self.alpha_var.get()
        k = self.k_var.get()

        # 計算權重
        try:
            w_qm = mapping_engine.qimen_number_weights(datetime.now(), longitude=lon)
            w_zw = mapping_engine.ziwei_number_weights(dt, tz_offset=tz)
        except Exception as e:
            messagebox.showerror('運算錯誤', str(e))
            return
        w_comb = mapping_engine.combine_weights(w_qm, w_zw, alpha)

        # 預測
        if self.method_var.get() == 'top':
            nums = mapping_engine.predict_top(w_comb, k)
            label = f'Top {k} 號碼:'
        else:
            nums = mapping_engine.predict_random(w_comb, k)
            label = f'Random {k} 號碼:'

        # 顯示
        self.output.delete('1.0', tk.END)
        self.output.insert(tk.END, f'奇門權重 α = {alpha:.2f}\n')
        self.output.insert(tk.END, f'紫微權重 (1-α) = {1-alpha:.2f}\n')
        self.output.insert(tk.END, f'{label} ' + ' '.join(f'{n:02d}' for n in nums))

if __name__ == '__main__':
    app = LotteryApp()
    app.mainloop()
