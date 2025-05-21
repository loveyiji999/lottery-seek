# qimen_engine.py
"""
奇門遁甲飛宮排盤引擎（M3 完整版）

功能：
 1. 確定遁法 (陽/陰) 與遁數 (1~8)
 2. 飛布九星、八門、三奇、六儀、八神至中宮及八方宮
 3. 中宮放置值符與值使，其餘宮位依遁數逆時針飛入

依賴：
 - astronomical_core.solar_longitude

使用：
    from qimen_engine import generate_qimen_chart
    chart = generate_qimen_chart(datetime.now(), longitude=120.0)
"""
from datetime import datetime
from astronomical_core import solar_longitude
import math

# 環宮逆時針（排除中宮5）
PALACES = [1,4,7,8,9,6,3,2]

# 奇門九星
QIMEN_STARS = ['天蓬','天任','天冲','天輔','天英','天芮','天柱','天心','天禽']
# 八門
QIMEN_DOORS = ['休','生','傷','杜','景','死','驚','開']
# 三奇六儀（奇在前）
QIMEN_QI = ['丙','丁','戊']
QIMEN_YI = ['庚','辛','壬','癸','乙','己']
# 八神（不含中宮值符）
QIMEN_GODS = ['勾陳','六合','朱雀','玄武','白虎','青龍','螣蛇','值使']

# 值符星：陽遁用『天蓬』，陰遁用『天任』
VALUE_STAR = {'yang':'天蓬','yin':'天任'}
VALUE_DOOR = '值使'

# 遁法與遁數計算
def determine_dun(dt: datetime):
    # 計算太陽視黃經
    jd = dt.timestamp() / 86400.0 + 2440587.5
    lon = solar_longitude(jd) % 360
    term_idx = int(math.floor(lon / 15.0))  # 0-23
    if term_idx >= 18 or term_idx < 6:
        dun_type = 'yang'
        dun_no = ((term_idx - 18) % 24) // 3 + 1
    else:
        dun_type = 'yin'
        dun_no = ((term_idx - 6) // 3) + 1
    return dun_type, dun_no

# 主盤生成
def generate_qimen_chart(dt: datetime, longitude: float):
    dun_type, dun_no = determine_dun(dt)
    # 計算飛宮起點 index
    start = PALACES.index(dun_no)
    # 旋轉八方宮
    rotated = PALACES[start:] + PALACES[:start]

    # 九星分布：中宮放值符，其餘飛入八宮
    stars = {5: VALUE_STAR[dun_type]}
    # 星列表除去值符
    other_stars = [s for s in QIMEN_STARS if s != VALUE_STAR[dun_type]]
    for palace, star in zip(rotated, other_stars):
        stars[palace] = star

    # 八門分布：八門飛入八宮，中宮空
    doors = {5: None}
    for palace, door in zip(rotated, QIMEN_DOORS):
        doors[palace] = door

    # 三奇六儀分布：九宮含中宮，旋轉後分配
    entities = QIMEN_QI + QIMEN_YI
    pal9 = rotated + [5]
    qi_yi = {p: e for p, e in zip(pal9, entities)}

    # 八神分布：中宮值使，其餘八神飛入八宮
    gods = {5: VALUE_DOOR}
    for palace, god in zip(rotated, QIMEN_GODS):
        gods[palace] = god

    return {
        'dun_type': dun_type,
        'dun_no': dun_no,
        'stars': stars,
        'doors': doors,
        'qi_yi': qi_yi,
        'gods': gods
    }

# 測試
if __name__ == '__main__':
    ch = generate_qimen_chart(datetime.now(), longitude=120.0)
    for key, val in ch.items(): print(key, val)
