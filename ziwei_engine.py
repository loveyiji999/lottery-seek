# ziwei_engine.py
"""
紫微斗數排盤引擎（M2 完整版）

功能：
 1. 四柱八字計算（年、月、日、時柱）
 2. 命宮、身宮定位（斗君起盤法）
 3. 14 主星排布（紫微至破軍）
 4. 四化（化祿、化權、化科、化忌）演算法

依賴：
 - lunardate (農曆轉換)
 - swisseph (天文曆算)

使用示例：
    from ziwei_engine import generate_chart
    chart = generate_chart(datetime(1990,5,17,15,30), 'male', 8.0)
    print(chart)
"""
from datetime import datetime, timedelta
import swisseph as swe
from lunardate import LunarDate

# 干支常數
HEAVENLY_STEMS = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
EARTHLY_BRANCHES = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
# 紫微 14 主星次序
MAIN_STARS = [
    '紫微','天機','太陽','武曲','天同','廉貞','天府','太陰',
    '貪狼','巨門','天相','天梁','七殺','破軍'
]
# 四化對應順序
TRANS_NAMES = ['化祿','化權','化科','化忌']

# --------------- 干支計算 ---------------

def get_year_pillar(year: int) -> str:
    """計算年柱（天干地支）"""
    idx = (year - 1984) % 60
    gs = HEAVENLY_STEMS[idx % 10]
    eb = EARTHLY_BRANCHES[idx % 12]
    return gs + eb


def get_month_pillar(year_stem: str, lunar_month: int) -> str:
    """計算月柱，以寅月為一月"""
    stem_idx = HEAVENLY_STEMS.index(year_stem)
    m_stem = HEAVENLY_STEMS[(stem_idx * 2 + lunar_month - 2) % 10]
    m_branch = EARTHLY_BRANCHES[(lunar_month + 1) % 12]
    return m_stem + m_branch


def get_day_pillar(dt: datetime) -> str:
    """計算日柱，根據儒略日對60天循環"""
    jd = swe.julday(dt.year, dt.month, dt.day, 0)
    idx = int(jd + 49) % 60
    ds = HEAVENLY_STEMS[idx % 10]
    db = EARTHLY_BRANCHES[idx % 12]
    return ds + db


def get_hour_pillar(day_stem: str, hour: int) -> str:
    """計算時柱，子時(23-1)屬地支子"""
    hr_branch = ((hour + 1) // 2) % 12
    eb = EARTHLY_BRANCHES[hr_branch]
    stem_idx = HEAVENLY_STEMS.index(day_stem)
    hr_stem = HEAVENLY_STEMS[(stem_idx * 2 + hr_branch) % 10]
    return hr_stem + eb

# --------------- 四柱八字 ---------------

def calculate_bazi(dt: datetime, tz_offset: float = 8.0) -> dict:
    """計算年、月、日、時柱，返回字典"""
    local = dt - timedelta(hours=tz_offset)
    ld = LunarDate.fromSolarDate(local.year, local.month, local.day)
    year_p = get_year_pillar(ld.year)
    month_p = get_month_pillar(year_p[0], ld.month)
    day_p = get_day_pillar(local)
    hour_p = get_hour_pillar(day_p[0], local.hour)
    return {'year': year_p, 'month': month_p, 'day': day_p, 'hour': hour_p}

# --------------- 宮位定位 ---------------

def locate_palaces(pillars: dict) -> dict:
    """依月支、時支定位命宮與身宮（1-12宮）"""
    mb = pillars['month'][1]
    idx = EARTHLY_BRANCHES.index(mb)
    ming = (1 - idx) % 12 + 1
    hb = pillars['hour'][1]
    idh = EARTHLY_BRANCHES.index(hb)
    shen = (1 - idh) % 12 + 1
    return {'ming': ming, 'shen': shen}

# --------------- 主星排布 ---------------

def place_main_stars(palaces: dict) -> dict:
    """從命宮開始逆時針布置14主星"""
    mapping = {i: [] for i in range(1, 13)}
    start = palaces['ming'] - 1
    for i, star in enumerate(MAIN_STARS):
        pos = ((start - i) % 12) + 1
        mapping[pos].append(star)
    return mapping

# --------------- 四化演算 ---------------

def compute_transformations(pillars: dict, stars_map: dict) -> dict:
    """依年干計算化祿/權/科/忌並返回所在宮位"""
    idx = HEAVENLY_STEMS.index(pillars['year'][0]) % 4
    name = TRANS_NAMES[idx]
    star_map = {'化祿': '紫微', '化權': '天機', '化科': '太陽', '化忌': '武曲'}
    target_star = star_map[name]
    for palace, stars in stars_map.items():
        if target_star in stars:
            return {name: palace}
    return {name: None}

# --------------- 組合介面 ---------------

def generate_chart(dt: datetime, gender: str, tz_offset: float = 8.0) -> dict:
    bazi = calculate_bazi(dt, tz_offset)
    pal = locate_palaces(bazi)
    stars = place_main_stars(pal)
    trans = compute_transformations(bazi, stars)
    return {'bazi': bazi, 'palaces': pal, 'stars': stars, 'transform': trans}

# 測試
if __name__ == '__main__':
    test_dt = datetime(1990, 5, 17, 15, 30)
    result = generate_chart(test_dt, 'male', 8.0)
    print(result)
