# mapping_engine.py
"""
M4 號碼映射與權重合成模組

功能：
 1. 將奇門遁甲盤局權重映射到 1-49 號碼
 2. 將紫微斗數盤局權重映射到 1-49 號碼
 3. 合併兩者權重並輸出 Top-k 與隨機抽樣號碼

依賴：
 - numpy
 - ziwei_engine.generate_chart
 - qimen_engine.generate_qimen_chart
"""
import numpy as np
from qimen_engine import generate_qimen_chart
from ziwei_engine import generate_chart
from datetime import datetime

# Lo Shu 九宮 → 號碼對應
LOSHU_TO_NUMBERS = {
    1: [1,10,19,28,37],
    2: [2,11,20,29,38],
    3: [3,12,21,30,39],
    4: [4,13,22,31,40],
    5: [5,14,23,32,41,46,47,48,49],
    6: [6,15,24,33,42],
    7: [7,16,25,34,43],
    8: [8,17,26,35,44],
    9: [9,18,27,36,45],
}

# 紫微 12 宮 → 號碼對應
def palace_to_numbers_ziwei(pal: int):
    base = (pal - 1) * 4 + 1
    nums = list(range(base, min(base + 4, 50)))
    return nums

# 奇門盤權重映射

def qimen_number_weights(dt: datetime, longitude: float):
    chart = generate_qimen_chart(dt, longitude)
    # 初始數組
    w = np.zeros(49, dtype=float)
    # 盤局內容
    stars = chart['stars']      # palace->star
    doors = chart['doors']      # palace->door
    dun_type = chart['dun_type']
    # 迴圈 1-9 宮
    for pal in range(1,10):
        weight = 1.0
        # 值符星
        value_star = '天蓬' if dun_type=='yang' else '天任'
        if stars.get(pal)== value_star:
            weight *= 3
        # 八門權重
        door = doors.get(pal)
        if door == '開':        weight *= 3
        elif door in ('休','生'): weight *= 2
        elif door in ('死','驚'): weight *= 0.5
        # 映射到號碼
        nums = LOSHU_TO_NUMBERS.get(pal, [])
        for n in nums:
            w[n-1] += weight
    # 正規化
    return w / w.sum()

# 紫微盤權重映射

def ziwei_number_weights(birth_dt: datetime, tz_offset: float=8.0):
    chart = generate_chart(birth_dt, 'male', tz_offset)
    pal = chart['palaces']      # dict with 'ming','shen'
    trans = chart['transform']   # dict of transformation name->palace
    # 初始數組
    w = np.zeros(49, dtype=float)
    # 設定基礎權重
    palace_weights = {i:1.0 for i in range(1,13)}
    # 命宮
    palace_weights[ pal['ming'] ] *= 3
    # 四化
    factors = {'化祿':3.0, '化權':2.0, '化科':1.5, '化忌':0.5}
    for name, p in trans.items():
        factor = factors.get(name, 1.0)
        if p:
            palace_weights[p] *= factor
    # 對每宮映射號碼
    for palace, weight in palace_weights.items():
        nums = palace_to_numbers_ziwei(palace)
        for n in nums:
            w[n-1] += weight
    # 正規化
    return w / w.sum()

# 合併權重

def combine_weights(w_qm: np.ndarray, w_zw: np.ndarray, alpha: float=0.5):
    # alpha: 奇門比重, (1-alpha): 紫微
    comb = alpha * w_qm + (1-alpha) * w_zw
    return comb / comb.sum()

# 生成號碼

def predict_top(weights: np.ndarray, k: int=6):
    idx = np.argsort(weights)[-k:][::-1]
    return [i+1 for i in idx]


def predict_random(weights: np.ndarray, k: int=6):
    probs = weights / weights.sum()
    return list(np.random.choice(np.arange(1,50), size=k, replace=False, p=probs))

# 測試
if __name__ == '__main__':
    now = datetime.now()
    w_qm = qimen_number_weights(now, 120.0)
    w_zw = ziwei_number_weights(datetime(1990,5,17,15,30), 8.0)
    comb = combine_weights(w_qm, w_zw, 0.6)
    print('Top6:', predict_top(comb))
    print('Rand6:', predict_random(comb))
