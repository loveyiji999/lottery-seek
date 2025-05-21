# main.py

import requests
import re
import pandas as pd
import time
from bs4 import BeautifulSoup

BASE_URL = "http://www.pilio.idv.tw/ltobig/list.asp"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}

def fetch_html(page: int) -> str:
    resp = requests.get(
        BASE_URL,
        params={"indexpage": page, "orderby": "new"},
        headers=HEADERS,
        timeout=10
    )
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}，無法取得第 {page} 頁資料")
    resp.encoding = "big5"
    html = resp.text
    if len(html) < 300:
        raise RuntimeError(f"第 {page} 頁回傳內容過短，可能已無更多資料")
    return html

def parse_draws(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n").replace("\xa0", " ")
    pattern = re.compile(
        r"(\d{4}/\d{2}/\d{2})\s*\([^\)]*\)\s*"
        r"([0-9]{2}(?:,\s*[0-9]{2}){5})\s*([0-9]{2})",
        re.S
    )
    results = []
    for date, reds_str, special in pattern.findall(text):
        reds = [n.strip() for n in reds_str.split(",")]
        entry = {"date": date}
        for i, r in enumerate(reds, start=1):
            entry[f"red{i}"] = r
        entry["special"] = special
        results.append(entry)
    return results

def scrape_all() -> list[dict]:
    all_data = []
    seen_dates = set()
    page = 1
    MAX_PAGE = 20000  # 安全上限，避免意外無限迴圈
    while True:
        print(f"正在抓取第 {page} 頁…")
        try:
            html = fetch_html(page)
        except RuntimeError as e:
            print("❌ 抓取中斷：", e)
            break

        page_data = parse_draws(html)
        if not page_data:
            print("已無更多資料，結束抓取。")
            break

        current_dates = {item["date"] for item in page_data}
        # 檢測重複：若本頁日期與先前已抓到的交集不為空，代表到了尾頁
        if seen_dates & current_dates:
            print("偵測到重複期數，結束抓取。")
            break

        seen_dates |= current_dates
        all_data.extend(page_data)

        page += 1
        if page > MAX_PAGE:
            print(f"已超過最大頁數 {MAX_PAGE}，強制結束。")
            break

        time.sleep(0.5)
    return all_data

def main():
    data = scrape_all()
    if not data:
        print("❌ 未抓到任何資料，程式結束。")
        return

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"], format="%Y/%m/%d", errors="coerce")
    df.dropna(subset=["date"], inplace=True)
    df.sort_values("date", ascending=False, inplace=True)

    output_file = "lottery_results.xlsx"
    df.to_excel(output_file, index=False)
    print(f"✅ 共抓取 {len(df)} 筆資料，已存為 {output_file}")

if __name__ == "__main__":
    main()
