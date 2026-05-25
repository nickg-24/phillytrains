# Architecture

## Overview
PhillyTrains is a Raspberry Pi-powered RGB LED matrix display board that shows live and scheduled SEPTA transit information. It runs headlessly on boot and cycles through a continuous slideshow: SEPTA logo → one slide per configured Regional Rail line → one BSL subway slide per direction → an alerts slide (only when relevant alerts exist for any tracked line). Regional Rail uses the SEPTA Next To Arrive API with a GTFS static fallback. Subway (BSL, Lombard-South station) shows scheduled northbound and southbound departures for the day pulled from GTFS static data. Alerts are aggregated across all configured lines and shown together at the end of the loop. All slide rendering uses PIL image composition pushed to the matrix via a thin rgbmatrix wrapper, decoupling rendering from the matrix library. Hardware: Raspberry Pi 3B+, Adafruit RGB Matrix Bonnet, 64x64 RGB LED Matrix.

## Components
| Component | Responsibility |
|-----------|----------------|
| data/gtfs.py | Lazy-loaded GTFS static data singleton (rail + subway); shared `format_gtfs_time` and `service_active` utilities; caches outer zip to avoid duplicate download |
| data/rail.py | Per-line NTA API fetch with GTFS static fallback; returns structured train list |
| data/subway.py | BSL scheduled departures by direction from GTFS static |
| data/alerts.py | GTFS-RT service alert aggregation across all configured lines |
| display/panels/ | PIL-based slide renderers: logo, rail, subway, alerts — each returns a 64×64 PIL.Image |
| display/matrix.py | Thin rgbmatrix wrapper; gracefully no-ops when rgbmatrix is not installed (WSL dev mode) |
| main.py | Main slideshow loop: fetches all data, builds slide list, pushes frames at configured intervals |
| config.yaml | Multi-line rail config, subway platform stop IDs and direction config, matrix and display timing |

## Key Decisions
| Decision | Rationale | Date |
|----------|-----------|------|
| `data/gtfs.py` as shared GTFS loader with outer zip cache | Both rail and subway need GTFS; caching avoids downloading the zip twice at boot | 2026-05-24 |
| `route_id` specified explicitly in config | Inferring route_id from NTA response text was fragile; explicit config is reliable | 2026-05-24 |
| Pure PIL rendering for all display panels | Decouples rendering from rgbmatrix library; `graphics` module dropped entirely | 2026-05-24 |
| BSL platform stop IDs: northbound=32139, southbound=1283 | Two distinct stop_ids in google_bus.zip confirmed from GTFS stop_times | 2026-05-24 |
| BDF fonts converted to PIL format via `pilfont` | PIL cannot load .bdf directly; one-time conversion step added to setup.md | 2026-05-24 |
| `ImageFont.load_default(size=N)` for all text | No font files needed; built into Pillow 9.2+; eliminates pilfont conversion step | 2026-05-25 |
| venv + `sudo .venv/bin/python3` on Pi | rgbmatrix needs GPIO (sudo) at runtime but not at install; venv installed as user, run as sudo | 2026-05-25 |
| rgbmatrix installed via pip (not make) | Feb 2026 overhaul made it pip-installable; `pip install git+https://github.com/hzeller/rpi-rgb-led-matrix` | 2026-05-25 |

## Open Questions
- Whether 3 subway departures fits comfortably on a slide (currently implemented as 3; tune on hardware)
- Subway header "↑ Fern Rock" / "↓ AT&T Stn" auto-falls back to "BSL NB"/"BSL SB" if too wide; verify preferred label on hardware
