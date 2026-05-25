# PhillyTrains – SEPTA LED Matrix Display

A Raspberry Pi project that shows live SEPTA transit data on a 64×64 RGB LED matrix. Displays upcoming Regional Rail departures, Broad Street Line times, and service alerts in a rotating slideshow — starts automatically on boot, no interaction required.

---

## Preview

<p align="center">
  <img src="images/slide1.jpg" width="200" alt="SEPTA Logo slide">
  <img src="images/slide2.jpg" width="200" alt="Train departure slide">
  <img src="images/slide3.jpg" width="200" alt="Train departure slide">
  <img src="images/slide4.jpg" width="200" alt="Alert slide">
</p>

---

## Hardware

| Part | Link |
|------|------|
| Raspberry Pi 3 Model B+ | — |
| Adafruit RGB Matrix Bonnet | [adafruit.com/product/3211](https://www.adafruit.com/product/3211) |
| 64×64 RGB LED Matrix (3mm pitch) | [adafruit.com/product/4732](https://www.adafruit.com/product/4732) |
| 5V 4A power supply | [adafruit.com/product/1466](https://www.adafruit.com/product/1466) |

Adafruit's [RGB Matrix Bonnet guide](https://learn.adafruit.com/adafruit-rgb-matrix-bonnet-for-raspberry-pi/overview) covers wiring and physical setup.

---

## What it shows

- **Regional Rail** — next departures between your configured stations, with train number, departure time, arrival time, and on-time status
- **Broad Street Line** — next northbound and southbound departures from your stop
- **Service alerts** — filtered to your configured routes, paginated across the display

Everything is configured in `config.yaml` — no code changes needed to track different stations or lines.

---

## Setup

See **[setup.md](./setup.md)** for full instructions. The short version:

1. Flash Raspberry Pi OS Lite (64-bit) with Wi-Fi and SSH configured
2. Clone the repo and edit `config.yaml` for your stops
3. Run `bash setup.sh`
4. Reboot, verify hardware with `test_matrix.py`, then start the service

---

## How it works

- `main.py` — main loop: fetches data, builds slides, drives the display at ~30 fps
- `data/` — fetches from SEPTA's Next To Arrive API, GTFS Realtime alerts feed, and static GTFS schedule (fallback when live data is unavailable)
- `display/panels/` — renders each slide type (rail, subway, alerts, logo) as a PIL image
- `display/matrix.py` — thin wrapper around `rpi-rgb-led-matrix`; falls back to a no-op when running without hardware (useful for development)
- `config.yaml` — all user configuration: stations, routes, display timing, matrix settings

---

## Data sources

All data is from SEPTA's open developer program:

- [Next To Arrive API](https://www3.septa.org/api/NextToArrive/)
- [GTFS Realtime Service Alerts](https://www3.septa.org/gtfsrt/septarail-pa-us/Service/rtServiceAlerts.pb)
- [Static GTFS Schedule](https://www3.septa.org/developer/gtfs_public.zip)

---

## Credits

- [hzeller/rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) for LED matrix control
- [SEPTA Developer Program](https://www3.septa.org/developer/) for transit data

---

This project was revamped using [loopdehoot](https://github.com/nickg-24/loopdehoot), an AI-assisted development tool I'm working on. Not sure it's any more effective than just using Claude Code directly, but it was fun to put together.
