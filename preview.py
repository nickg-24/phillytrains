#!/usr/bin/env python3
"""
Renders each display panel with live data and saves PNGs to preview_output/.
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
    rail.render(data).save(OUT / f"rail_{line['name'].lower()}.png")
    print(f"rail_{line['name'].lower()}.png  ({len(data['trains'])} train(s))")

sub = fetch_subway(cfg.get("subway", {}))
subway.render(sub, "northbound").save(OUT / "subway_nb.png")
subway.render(sub, "southbound").save(OUT / "subway_sb.png")
print(f"subway_nb.png  ({len(sub['northbound'])} times today)")
print(f"subway_sb.png  ({len(sub['southbound'])} times today)")

alert_list = fetch_alerts(cfg.get("rail_lines", []))
if alert_list:
    pages = alerts.render(alert_list)
    for i, img in enumerate(pages):
        img.save(OUT / f"alert_{i}.png")
    print(f"{len(pages)} alert page(s) saved")
else:
    print("No active alerts")

print(f"\nSaved to {OUT}/")
