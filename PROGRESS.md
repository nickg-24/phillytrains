# Progress

## Summary
Data layer is complete and tested. `data/gtfs.py` provides a shared GTFS loader (rail + subway) with a zip cache. `data/rail.py`, `data/subway.py`, and `data/alerts.py` are all implemented and runnable standalone. `config.yaml` has been restructured for multi-line rail and BSL subway with confirmed platform stop IDs. Display panels are stubbed with planned interfaces; implementation is deferred until Pi hardware access.

---

## Session Log

<!-- START_OF_DAY reads the last 3-5 entries below. Older entries are for reference only — they are not loaded into the session. -->

### [2026-05-24]
**Focus:** Scaffolding new multi-line architecture and implementing the full data layer
**Done:** New directory structure (`data/`, `display/panels/`); `data/gtfs.py` (shared GTFS loader with zip cache, shared utilities); `data/rail.py` (multi-line NTA + GTFS fallback, fixes >24h GTFS time handling); `data/subway.py` (BSL scheduled departures, verified live — 103/104 trips per direction); `data/alerts.py` (multi-line GTFS-RT alert aggregation with deduplication); `config.yaml` restructured to `rail_lines` list format; display panel stubs created; full display layer planned
**Next:** Implement `display/panels/` (logo, rail, subway, alerts) and new main loop — requires Pi hardware access to test
**Notes:** BSL route IDs in GTFS are `B1`/`B2`/`B3`, not `"BSL"`. Platform stop IDs confirmed: northbound=32139, southbound=1283. rgbmatrix library API is essentially unchanged; main display work is font migration (BDF→PIL via `pilfont`). Subway slide departure count (2 vs 3) to be tuned on hardware.
