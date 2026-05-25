# Progress

## Summary
Data layer and display layer are both complete. All four display panels (`logo`, `rail`, `subway`, `alerts`) are implemented using PIL and render live data correctly. `main.py` is the main slideshow loop. `display/matrix.py` wraps rgbmatrix with a graceful fallback for WSL dev. `preview.py` saves panel PNGs locally for layout iteration. `setup.md` has full fresh-Pi instructions. Remaining step: set up the Pi hardware and run on the matrix.

---

## Session Log

<!-- START_OF_DAY reads the last 3-5 entries below. Older entries are for reference only — they are not loaded into the session. -->

### [2026-05-25]
**Focus:** Display layer implementation and Pi setup
**Done:** All display panels (`logo`, `rail`, `subway`, `alerts`) implemented with PIL; `display/matrix.py` rgbmatrix wrapper with WSL mock mode; `main.py` main slideshow loop; `preview.py` local PNG preview tool; `test_matrix.py` Pi hardware smoke test; `setup.md` fully rewritten for fresh Pi with venv+sudo pattern
**Next:** Flash Pi, follow setup.md, run `test_matrix.py`, then `main.py`; tune layout (font sizes, header labels, departure count) based on what it looks like on hardware
**Notes:** rgbmatrix now pip-installable (Feb 2026 overhaul). Pi pattern: install venv as user, run with `sudo .venv/bin/python3`. Audio driver must be disabled in `/boot/firmware/config.txt` or display will flicker. `preview.py` confirmed working with live data: 2 rail trains, 103/104 subway times, 6 alert pages.

### [2026-05-24]
**Focus:** Scaffolding new multi-line architecture and implementing the full data layer
**Done:** New directory structure (`data/`, `display/panels/`); `data/gtfs.py` (shared GTFS loader with zip cache, shared utilities); `data/rail.py` (multi-line NTA + GTFS fallback, fixes >24h GTFS time handling); `data/subway.py` (BSL scheduled departures, verified live — 103/104 trips per direction); `data/alerts.py` (multi-line GTFS-RT alert aggregation with deduplication); `config.yaml` restructured to `rail_lines` list format; display panel stubs created; full display layer planned
**Next:** Implement `display/panels/` (logo, rail, subway, alerts) and new main loop — requires Pi hardware access to test
**Notes:** BSL route IDs in GTFS are `B1`/`B2`/`B3`, not `"BSL"`. Platform stop IDs confirmed: northbound=32139, southbound=1283. rgbmatrix library API is essentially unchanged; main display work is font migration (BDF→PIL via `pilfont`). Subway slide departure count (2 vs 3) to be tuned on hardware.
