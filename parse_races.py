"""Parse Taipei Marathon contest page into structured JSON."""
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

html = Path("/tmp/contest.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")

table = soup.find("table", id="GridView1")
races = []
for tr in table.find_all("tr"):
    tds = tr.find_all("td")
    if len(tds) < 7:
        continue
    classes = " ".join(tr.get("class") or [])
    is_old = "oldactivity" in classes
    month_tag = tds[0].find(id="monthtag")
    is_new = bool(tds[0].find("img"))
    name_a = tds[1].find("a")
    name = name_a.get_text(strip=True) if name_a else tds[1].get_text(strip=True)
    link = name_a["href"] if name_a and name_a.has_attr("href") else ""
    date_text = tds[3].get_text(" ", strip=True)
    location = tds[4].get_text(" ", strip=True)
    distances = []
    for btn in tds[5].find_all("button"):
        title = btn.get("title", "")
        label = btn.get_text(strip=True)
        fee_m = re.search(r"費用[：: ]*\s*(\d+)", title)
        limit_m = re.search(r"限額[：: ]*\s*(\d+)", title)
        distances.append({
            "label": label,
            "fee": int(fee_m.group(1)) if fee_m else None,
            "limit": int(limit_m.group(1)) if limit_m else None,
        })
    organizer = tds[6].get_text(" ", strip=True)
    status = tds[7].get_text(" ", strip=True) if len(tds) > 7 else ""

    # Parse date: "05/03 日 05:00" or "12/21 日 06:00"
    md_m = re.match(r"(\d{2})/(\d{2})\s*([一二三四五六日])\s*([\d:]+)?", date_text)
    month = int(md_m.group(1)) if md_m else None
    day = int(md_m.group(2)) if md_m else None
    weekday = md_m.group(3) if md_m else None
    start_time = md_m.group(4) if md_m and md_m.group(4) else ""

    # Region from location prefix (first 3 chars usually county/city)
    region_m = re.match(r"(臺北市|新北市|基隆市|桃園市|新竹市|新竹縣|苗栗縣|臺中市|彰化縣|南投縣|雲林縣|嘉義市|嘉義縣|臺南市|高雄市|屏東縣|宜蘭縣|花蓮縣|臺東縣|澎湖縣|金門縣|連江縣)", location)
    region = region_m.group(1) if region_m else "其他"

    # Status normalization → reg_state: closed | open | upcoming | unknown
    today = (5, 3)  # 2026-05-03
    s = status.strip()
    norm_status = s

    def parse_md(token):
        m = re.match(r"\s*(\d+)月(\d+)日", token)
        return (int(m.group(1)), int(m.group(2))) if m else None

    if s == "" or s == "未開放":
        reg_state = "upcoming"
    elif "截止" in s:
        reg_state = "closed"
    else:
        # patterns: "X月X日 ~ Y月Y日" | "X月X日 ~" | "~ Y月Y日" | "~ Y月Y日 (最後三天)"
        parts = [p.strip() for p in s.split("~")]
        start_md = parse_md(parts[0]) if parts and parts[0] else None
        end_md = parse_md(parts[1]) if len(parts) > 1 and parts[1] else None
        started = start_md is None or today >= start_md
        ended = end_md is not None and today > end_md
        if not started:
            reg_state = "upcoming"
        elif ended:
            reg_state = "closed"
        else:
            reg_state = "open"

    # Max distance (numeric, for distance category filtering)
    max_km = 0
    cats = set()
    for d in distances:
        m = re.search(r"([\d.]+)\s*K", d["label"], re.IGNORECASE)
        if m:
            km = float(m.group(1))
            max_km = max(max_km, km)
            if km >= 42:
                cats.add("全馬")
            elif km >= 21:
                cats.add("半馬")
            elif km >= 10:
                cats.add("10K+")
            else:
                cats.add("休閒")
        else:
            # 88樓 (vertical), 鐵人 etc.
            cats.add("特殊")

    races.append({
        "name": name,
        "link": link,
        "date_raw": date_text,
        "month": month,
        "day": day,
        "weekday": weekday,
        "start_time": start_time,
        "location": location,
        "region": region,
        "distances": distances,
        "categories": sorted(cats),
        "max_km": max_km,
        "organizer": organizer,
        "status": norm_status,
        "status_raw": status,
        "reg_state": reg_state,
        "is_past": is_old,
        "is_new": is_new,
        "month_tag": month_tag.get_text(strip=True) if month_tag else "",
    })

# Assign year by walking source order. Source is chronological; when the
# month *decreases* between consecutive races, we crossed into the next year.
# We anchor at "today's year" for the first non-past race.
TODAY_YEAR = 2026
TODAY_MONTH = 5
year = TODAY_YEAR
prev_month = None
for r in races:
    m = r["month"]
    if m is None:
        r["year"] = None
        continue
    if r["is_past"]:
        # past races appear at the very top (already-happened in current year)
        r["year"] = TODAY_YEAR
        prev_month = m
        continue
    if prev_month is not None and m < prev_month:
        # Month went backwards — we rolled into the next year
        year += 1
    r["year"] = year
    prev_month = m

print(f"Parsed {len(races)} races")
years = sorted({r['year'] for r in races if r['year']})
print("Years detected:", years)
for y in years:
    cnt = sum(1 for r in races if r['year']==y)
    print(f"  {y}: {cnt} races")
Path("/Volumes/myData-2T/Code/my-dev/sports/races.json").write_text(
    json.dumps(races, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("Categories:", sorted({c for r in races for c in r["categories"]}))
print("Regions:", sorted({r["region"] for r in races}))
print("Statuses:", sorted({r["status"] for r in races}))
print("Sample:", json.dumps(races[3], ensure_ascii=False, indent=2))
