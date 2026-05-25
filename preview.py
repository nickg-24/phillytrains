#!/usr/bin/env python3
"""
Renders each display panel with live data and saves PNGs to preview_output/.
For animated slides (rail), saves the first frame and the middle frame.
Run from repo root: python3 preview.py
"""
from pathlib import Path
import yaml
from data.rail import fetch_rail
from data.subway import fetch_subway
from data.alerts import fetch_alerts
from display.panels import logo, rail, subway, alerts

OUT = Path("preview_output")
OUT.mkdir(exist_ok=True)

cfg = yaml.safe_load(open("config.yaml"))

logo.render().save(OUT / "logo.png")
print("logo.png")

for line in cfg.get("rail_lines", []):
    data = fetch_rail(line)
    trains = data.get("trains", [])
    if not trains:
        frames = rail.render(line["name"], None)
        frames[0].save(OUT / f"rail_{line['name'].lower()}_no_service.png")
        print(f"rail_{line['name'].lower()}_no_service.png")
    else:
        for i, train in enumerate(trains):
            frames = rail.render(line["name"], train)
            frames[0].save(OUT / f"rail_{line['name'].lower()}_{i}_frame0.png")
            frames[len(frames)//2].save(OUT / f"rail_{line['name'].lower()}_{i}_mid.png")
            print(f"rail_{line['name'].lower()} train {i}: {len(frames)} frames")

sub = fetch_subway(cfg.get("subway", {}))
subway.render(sub, "northbound").save(OUT / "subway_nb.png")
subway.render(sub, "southbound").save(OUT / "subway_sb.png")
print(f"subway_nb.png, subway_sb.png")

alert_list = fetch_alerts(cfg.get("rail_lines", []))
if alert_list:
    pages = alerts.render(alert_list)
    for i, img in enumerate(pages):
        img.save(OUT / f"alert_{i}.png")
    print(f"{len(pages)} alert page(s)")
else:
    print("No active alerts")

print(f"\nSaved to {OUT}/")
