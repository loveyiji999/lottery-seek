# astronomical_core.py
"""
天文曆算核心模組（M1）

功能：
 1. 公曆 ⇄ 農曆轉換（天文算法 + lunardate）
 2. 真太陽時計算
 3. 24 節氣精確時刻計算
依賴：pyswisseph, lunardate
"""
import swisseph as swe
import math
from datetime import datetime, timedelta
from lunardate import LunarDate

# 設定瑞士曆書檔案路徑
# swe.set_ephe_path('/path/to/ephe')

# --------- 儒略日與天文計算 ---------

def julian_day(dt: datetime) -> float:
    """計算 UTC 時間的儒略日 (JD)"""
    year, month, day = dt.year, dt.month, dt.day
    hr = dt.hour + dt.minute/60 + dt.second/3600
    return swe.julday(year, month, day, hr)


def true_solar_time(dt: datetime, lon: float) -> float:
    """計算真太陽時 (Local True Solar Time, 小時)
    lon: 東經正數, 西經負數 (度)
    dt: naive datetime 當作本地時
    """
    # 轉換為 UTC
    # 如果 dt 為本地時，請先轉 UTC
    jd = julian_day(dt)
    # 太陽視黃經
    sun_lon = swe.calc_ut(jd, swe.SUN)[0][0]
    # 果酬天下太陽時 = (sun_lon + 180) /15 mod24
    # 考慮經度修正
    utc_decimal = dt.hour + dt.minute/60 + dt.second/3600
    lst = (utc_decimal + lon/15) % 24
    tse = (sun_lon/15 - lst + 24) % 24
    return tse


def solar_longitude(jd: float) -> float:
    """返回太陽視黃經 (度)"""
    return swe.calc_ut(jd, swe.SUN)[0][0]


def lunar_longitude(jd: float) -> float:
    """返回月亮視黃經 (度)"""
    return swe.calc_ut(jd, swe.MOON)[0][0]

# --------- 24 節氣計算 ---------

def compute_solar_terms(year: int) -> dict:
    """計算該年 24 節氣時間，回傳 {節氣名: datetime}"""
    terms = {}
    solar_terms = [i * 15.0 for i in range(24)]
    names = [
        '春分','清明','穀雨','立夏','小滿','芒種','夏至','小暑','大暑','立秋',
        '處暑','白露','秋分','寒露','霜降','立冬','小雪','大雪','冬至','小寒',
        '大寒','立春','雨水','驚蟄'
    ]
    # 二分搜尋求節氣時刻
    dt_start = datetime(year, 1, 1)
    dt_end = datetime(year+1, 1, 1)
    jd_start = julian_day(dt_start)
    jd_end = julian_day(dt_end)
    for angle, name in zip(solar_terms, names):
        low, high = jd_start, jd_end
        for _ in range(40):
            mid = (low + high)/2
            diff = ((solar_longitude(mid) - angle + 180) % 360) - 180
            if diff > 0:
                high = mid
            else:
                low = mid
        dt_term = datetime.utcfromtimestamp((low - 2440587.5)*86400)
        terms[name] = dt_term
    return terms

# --------- 農曆轉換 ---------

def solar_to_lunar(dt: datetime) -> LunarDate:
    """公曆轉農曆，包含閏月標記"""
    return LunarDate.fromSolarDate(dt.year, dt.month, dt.day)


def lunar_to_solar(ld: LunarDate) -> datetime:
    """農曆轉公曆"""
    dt = ld.toSolarDate()
    return datetime(dt.year, dt.month, dt.day)

# --------- 測試區 ---------
if __name__ == '__main__':
    now = datetime.utcnow()
    print('JD:', julian_day(now))
    print('True Solar Time (@120E):', true_solar_time(now,120))
    terms = compute_solar_terms(now.year)
    for k,v in terms.items(): print(k, v)
    # 農曆測試
    ld = solar_to_lunar(now)
    print('Lunar:', ld.year, ld.month, ld.day, 'leap' if ld.isLeapMonth else '')
    dt_back = lunar_to_solar(ld)
    print('Back to Solar:', dt_back)
