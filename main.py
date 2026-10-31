#!/usr/bin/env python3
import os
import threading
import time
import traceback
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

# Latest slide list, replaced by the refresh thread. The display loop only reads it.
_slides = None


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


def _fetch_all(config, previous):
    """Fetch each source on its own. A failed source keeps its last good data."""
    lines     = config.get("rail_lines", [])
    route_ids = config.get("alerts", {}).get("route_ids", [])
    data = dict(previous)

    try:
        data["rail"] = [fetch_rail(line) for line in lines]
    except Exception as e:
        print(f"[refresh] rail failed, keeping last data: {e}", flush=True)

    try:
        data["subway"] = fetch_subway(config.get("subway", {}))
    except Exception as e:
        print(f"[refresh] subway failed, keeping last data: {e}", flush=True)

    try:
        data["alerts"] = fetch_alerts(route_ids)
    except Exception as e:
        print(f"[refresh] alerts failed, keeping last data: {e}", flush=True)

    return data


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


def _refresh_forever(config, interval):
    """Runs in a background thread so network waits never freeze the display."""
    global _slides
    data = {"rail": [], "subway": {}, "alerts": []}
    while True:
        try:
            data = _fetch_all(config, data)
            _slides = _build_slides(config, data)
        except Exception:
            print("[refresh] unexpected error, will retry:", flush=True)
            traceback.print_exc()
        time.sleep(interval)


def main():
    config = yaml.safe_load(open("config.yaml"))
    display = MatrixDisplay(config.get("matrix", {}))
    refresh_interval = config.get("refresh_interval", 60)

    t_logo    = config.get("display", {}).get("logo", 5)
    logo_only = [([logo.render()], t_logo)]

    hw_cfg      = config.get("halloween", {})
    hw_frames   = halloween.load_images(hw_cfg.get("dir", "images/halloween"))
    hw_duration = hw_cfg.get("duration", 3)
    hw_every    = max(1, hw_cfg.get("every", 4))
    hw_index    = 0
    shown       = 0

    threading.Thread(
        target=_refresh_forever, args=(config, refresh_interval), daemon=True
    ).start()

    try:
        while True:
            # Until the first fetch finishes (or if the network is down at boot),
            # the logo keeps the display alive.
            for frames, duration in (_slides or logo_only):
                _show_slide(display, frames, duration)
                shown += 1

                if hw_frames and shown % hw_every == 0 and _halloween_on():
                    _show_slide(display, [hw_frames[hw_index % len(hw_frames)]], hw_duration)
                    hw_index += 1

    except KeyboardInterrupt:
        print("Stopping.")


if __name__ == "__main__":
    main()
