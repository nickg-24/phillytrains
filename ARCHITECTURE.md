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
| config.yaml | Multi-line rail config, subway platform stop IDs and direction config, matrix and display timing |

## Key Decisions
| Decision | Rationale | Date |
|----------|-----------|------|
| `data/gtfs.py` as shared GTFS loader with outer zip cache | Both rail and subway need GTFS; caching avoids downloading the zip twice at boot | 2026-05-24 |
| `route_id` specified explicitly in config | Inferring route_id from NTA response text was fragile; explicit config is reliable | 2026-05-24 |
| Pure PIL rendering for all display panels | Decouples rendering from rgbmatrix library; `graphics` module dropped entirely | 2026-05-24 |
| BSL platform stop IDs: northbound=32139, southbound=1283 | Two distinct stop_ids in google_bus.zip confirmed from GTFS stop_times | 2026-05-24 |
| BDF fonts converted to PIL format via `pilfont` | PIL cannot load .bdf directly; one-time conversion step added to setup.md | 2026-05-24 |

## Open Questions
- Whether 3 subway departures fits comfortably on a slide, or if 2 reads better at actual viewing distance
- Whether subway slide header needs abbreviation ("BSL ↑ Fern Rock" may be too long for 64px width)
