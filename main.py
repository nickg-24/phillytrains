#!/usr/bin/env python3
import os
import time
from pathlib import Path
import yaml

# Use the OS cert store instead of certifi — avoids issues when running under sudo in a venv.
os.environ.setdefault("REQUESTS_CA_BUNDLE", "/etc/ssl/certs/ca-certificates.crt")

from data.rail import fetch_rail
from data.subway import fetch_subway
from data.alerts import fetch_alerts
from display.matrix import MatrixDisplay
from display.panels import logo, rail, subway, alerts, halloween

_FRAME_DELAY = 0.033  # ~30 fps

# Create this file to turn Halloween images on, delete it to turn them off.
# Checked after every slide, so no restart is needed. See tools/halloween.sh.
_HALLOWEEN_FLAG = Path(__file__).resolve().parent / "halloween.on"


def _halloween_on():
    return _HALLOWEEN_FLAG.exists()


def _show_slide(display, frames, duration):
    """Show a slide for `duration` seconds, looping through frames if animated."""
    end = time.time() + duration
    i = 0
    while time.time() < end:
        display.show(frames[i % len(frames)])
        time.sleep(_FRAME_DELAY)
        i += 1


def _fetch_all(config):
    lines     = config.get("rail_lines", [])
    route_ids = config.get("alerts", {}).get("route_ids", [])
    return {
        "rail":   [fetch_rail(line) for line in lines],
        "subway": fetch_subway(config.get("subway", {})),
        "alerts": fetch_alerts(route_ids),
    }


def _build_slides(config, data):
    t = config.get("display", {})
    t_logo  = t.get("logo", 5)
    t_train = t.get("train", 10)
    t_alert = t.get("alert", 10)

    slides = [([logo.render()], t_logo)]

    for line_data in data["rail"]:
        origin = line_data.get("origin", line_data["name"])
        dest   = line_data.get("destination", "")
        header = f"{origin} > {dest}" if dest else origin
        trains = line_data.get("trains", [])
        if not trains:
            slides.append((rail.render(header, None), t_train))
        else:
            for train in trains:
                slides.append((rail.render(header, train), t_train))

    sub = data["subway"]
    if sub.get("northbound"):
        slides.append(([subway.render(sub, "northbound")], t_train))
    if sub.get("southbound"):
        slides.append(([subway.render(sub, "southbound")], t_train))

    for img in alerts.render(data["alerts"]):
        slides.append(([img], t_alert))

    return slides


def main():
    config = yaml.safe_load(open("config.yaml"))
    display = MatrixDisplay(config.get("matrix", {}))
    refresh_interval = config.get("refresh_interval", 60)

    hw_cfg      = config.get("halloween", {})
    hw_frames   = halloween.load_images(hw_cfg.get("dir", "images/halloween"))
    hw_duration = hw_cfg.get("duration", 3)
    hw_index    = 0

    data = _fetch_all(config)
    slides = _build_slides(config, data)
    last_refresh = time.time()

    try:
        while True:
            if time.time() - last_refresh >= refresh_interval:
                data = _fetch_all(config)
                slides = _build_slides(config, data)
                last_refresh = time.time()

            for frames, duration in slides:
                _show_slide(display, frames, duration)

                if hw_frames and _halloween_on():
                    _show_slide(display, [hw_frames[hw_index % len(hw_frames)]], hw_duration)
                    hw_index += 1

    except KeyboardInterrupt:
        print("Stopping.")


if __name__ == "__main__":
    main()
