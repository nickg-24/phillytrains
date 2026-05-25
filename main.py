#!/usr/bin/env python3
import os
import time
import yaml

# Use the OS cert store instead of certifi — avoids issues when running under sudo in a venv.
os.environ.setdefault("REQUESTS_CA_BUNDLE", "/etc/ssl/certs/ca-certificates.crt")
from data.rail import fetch_rail
from data.subway import fetch_subway
from data.alerts import fetch_alerts
from display.matrix import MatrixDisplay
from display.panels import logo, rail, subway, alerts


def _fetch_all(config):
    lines = config.get("rail_lines", [])
    return {
        "rail": [fetch_rail(line) for line in lines],
        "subway": fetch_subway(config.get("subway", {})),
        "alerts": fetch_alerts(lines),
    }


def _build_slides(config, data):
    t = config.get("display", {})
    slides = [(logo.render(), t.get("logo", 5))]

    for line_data in data["rail"]:
        slides.append((rail.render(line_data), t.get("train", 10)))

    sub = data["subway"]
    if sub.get("northbound"):
        slides.append((subway.render(sub, "northbound"), t.get("train", 10)))
    if sub.get("southbound"):
        slides.append((subway.render(sub, "southbound"), t.get("train", 10)))

    for img in alerts.render(data["alerts"]):
        slides.append((img, t.get("alert", 10)))

    return slides


def main():
    config = yaml.safe_load(open("config.yaml"))
    display = MatrixDisplay(config.get("matrix", {}))
    refresh_interval = config.get("refresh_interval", 60)

    data = _fetch_all(config)
    slides = _build_slides(config, data)
    last_refresh = time.time()

    try:
        while True:
            if time.time() - last_refresh >= refresh_interval:
                data = _fetch_all(config)
                slides = _build_slides(config, data)
                last_refresh = time.time()

            for image, duration in slides:
                display.show(image)
                time.sleep(duration)

    except KeyboardInterrupt:
        print("Stopping.")


if __name__ == "__main__":
    main()
