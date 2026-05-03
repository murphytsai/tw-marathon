# 台灣路跑賽事篩選器 · TW Marathon Filter

A standalone, single-file filter for road races listed on
[taipeimarathon.org.tw](http://www.taipeimarathon.org.tw/contest.aspx).

**Live**: https://murphytsai.github.io/tw-marathon/

## Features

- Filter by distance category (全馬 / 半馬 / 10K+ / 休閒 / 特殊), month, region, and registration state
- Keyword search on race name, location, organizer
- Star races to build a personal shortlist (saved in `localStorage`)
- Click a distance chip on a card to mark which option you'll run — neon outline + ✓
- "🖨 列印 PDF" — clean print layout that preserves card colors
- Month section dividers
- Fully offline-capable: no external CSS/JS/fonts, all 169 races embedded in `index.html`

## Refresh data

```bash
curl -sL -A "Mozilla/5.0" http://www.taipeimarathon.org.tw/contest.aspx -o /tmp/contest.html
uv run python parse_races.py
uv run python build_html.py
```

`index.html` is the only file you need to ship.
