# Planning Document : Pi-Powered SEPTA Regional Rail LED Sign

## Objective

Build a Raspberry Pi–driven LED “station board” that cycles through configured **SCHEDULING** views (origin → destination pairs) and displays:

* Next train time
* Live status (On-Time / X min late / Cancelled)
* Last location (last station passed or current stop)
* Optional alert banner relevant to the displayed view

---

## Display Contract (per “SCHEDULING” page)

**Header**

* `ORIGIN → DESTINATION  •  Next at {TIME}`

**Status line**

* `Status: {On-Time | X min late | CANCELLED}`

**Progress line**

* `Last location: {station name}`

**Optional alerts (marquee)**

* Single-line scrolling banner when relevant alerts exist

---

## Data Sources (Regional Rail–first)

### 1) Rider-facing JSON (“Hackathon” endpoints)

* **Next To Arrive (NTA)**: point-to-point upcoming trips used for:

  * Next train time
  * Rider-friendly status text (“On-Time” or “X min late”)

* **TrainView** (development sanity check only):

  * Snapshot of active Regional Rail trains; useful for cross-checking behavior during development

### 2) GTFS family (standardized)

* **GTFS-Realtime Trip Updates (RR)**:

  * Canonical indicator of **cancellations** (`schedule_relationship = CANCELED`)
  * Per-stop predicted times and delay (seconds) if custom logic is ever needed

* **GTFS-Realtime Vehicle Positions (RR)**:

  * Current position, `current_stop_sequence`, and `stop_id` for deriving **last location**

* **GTFS-Realtime Alerts**:

  * Service advisories for the optional alert banner

* **GTFS Static** (lookup ZIP: `stops.txt`, `routes.txt`, `trips.txt`, etc.):

  * Local dictionaries for ID ↔ name mapping (stations, routes), colors, and shapes if ever needed

**Recommended usage pattern (to avoid over-engineering):**

* Use **NTA** for time and “minutes late” status.
* Use **GTFS-RT Trip Updates** only to override with **CANCELLED** when applicable.
* Use **GTFS-RT Vehicle Positions** + **GTFS Static** to compute **last location**.

---

## Architecture

### Modules

* `nta_client`
  Fetch NTA results for each configured origin→destination.

* `gtfsrt_client`
  Lightweight readers for:

  * Trip Updates (detect cancellations)
  * Vehicle Positions (derive last location)
  * Alerts (optional, route-filtered)

* `gtfs_static`
  On boot, parse GTFS static files into in-memory maps:

  * `stop_id → stop_name`
  * `route_id → {route_short_name, long_name, color}`
  * (Optional) `trip_id → route_id` if future logic needs it

* `model`
  Normalize feed outputs to a simple view model:

  ```json
  {
    "origin": "Conshohocken",
    "destination": "Jefferson Station",
    "next_time": "HH:MM",
    "status_text": "On-Time" | "5 min late" | "CANCELLED",
    "last_location": "Miquon",
    "alert": "Short text or null",
    "updated_at": "ISO-8601"
  }
  ```

* `scheduler`
  Polling cadence, rotation timing, caching, stale markers, and backoff.

* `renderer` (data → LED rows)
  Produces 2–3 crisp text rows per page for an LED matrix library (e.g., HUB75).

* `config`
  YAML/JSON configuration with A→B pages and timing.

### Configuration (example)

```yaml
pages:
  - origin: "Conshohocken"
    destination: "Jefferson Station"
    results: 3
  - origin: "Jefferson Station"
    destination: "Conshohocken"
    results: 3

polling:
  nta_seconds: 45
  gtfsrt_trip_seconds: 30
  gtfsrt_vehicle_seconds: 20
  alerts_seconds: 60

rotation:
  page_seconds: 8
  dwell_on_alert_seconds: 12
  dwell_on_cancel_seconds: 12
```

---

## Implementation Plan

### Phase 0 — Bootstrapping

* Parse **GTFS Static** once on startup → dictionaries in memory.
* Implement minimal logging (fetch success/failure, entity counts, last update times).
* Add health indicators in the view model (`updated_at`, `is_stale`).

### Phase 1 — Core SCHEDULING View

1. **NTA fetch**

   * For each configured A→B page, request top N results.
   * Select the first upcoming trip; store:

     * `next_time` (scheduled/predicted display time)
     * `status_text` (e.g., “On-Time”, “8 min late”)

2. **Trip cancellation check**

   * Poll **GTFS-RT Trip Updates** for Regional Rail.
   * Match on route/line, direction, and time window near the origin departure.
   * If a matching entity is `CANCELED`, set `status_text = "CANCELLED"`.

3. **Last location**

   * Poll **GTFS-RT Vehicle Positions** for Regional Rail.
   * For the matched trip, read `current_stop_sequence` and `stop_id`.
   * Use **GTFS Static** to map to a station name.

     * If `STOPPED_AT`, display that stop as last location.
     * Otherwise, display the previous stop in sequence.

4. **Render**

   * Produce three lines:

     * `ORIGIN → DESTINATION  •  Next at HH:MM`
     * `Status: On-Time / X min late / CANCELLED`
     * `Last location: {station}`

### Phase 2 — Rotation, Caching, Robustness

* **Rotation**: advance page every `page_seconds`; extend dwell on alert/cancel pages.
* **Caching**: keep “last good” payloads; on fetch failure, continue displaying with a **STALE** badge and a visible `updated_at`.
* **Rate limiting**: cap polling intervals to avoid hammering endpoints; apply exponential backoff on repeated failures.
* **Time handling**: normalize to local time; display “in Xm” only if provided by NTA; avoid recomputing delays unless needed.

### Phase 3 — Alerts (wire after core APIs are stable)

* **Source**: **GTFS-RT Alerts** for Regional Rail.
* **Relevance filter**:

  * Match alert’s affected routes/lines to the currently displayed page.
  * Optionally filter by affected stops within the page’s A→B corridor.
* **UI rules**:

  * Show banner only when at least one relevant alert exists.
  * Include brief text (title or short description); truncate or scroll as a marquee.
  * Respect alert active windows (start/end); hide automatically when expired.

### Phase 4 — LED Matrix Integration (post-API)

* Connect renderer to `rpi-rgb-led-matrix` (or equivalent).
* Use a fixed-width font for alignment.
* Keep transitions brief (slide/fade) so updates remain visible.
* Add brightness schedule (optional) or PIR-based dimming.

---

## Joining Logic (NTA ↔ GTFS-RT)

* **Match key**:

  * Route/line and direction, plus a small time window around origin departure.
  * Maintain a short-lived “sticky” association to reduce flicker as feeds update.
* **Conflict resolution**:

  * Status precedence: `CANCELLED` (Trip Updates) overrides NTA text; otherwise, keep NTA status as authoritative for “minutes late.”
* **Graceful degradation**:

  * If GTFS-RT vehicle data is missing, suppress “Last location” and keep other lines.
  * If all feeds fail, show a single line: `Data temporarily unavailable` with `updated_at`.

---

## Error Handling & Observability

* Structured logs with timestamps and feed names.
* Counters for successful/failed polls.
* Optional local `/status` page showing:

  * Last poll times per feed
  * Entity counts (Trip Updates, Vehicle Positions, Alerts)
  * Current page index and rotation timer

---

## Security & Maintainability

* No secrets required (public endpoints).
* Wrap HTTP calls with timeouts and retries.
* Encapsulate each feed in its own adapter to allow future bus/trolley expansion with minimal changes.

---

## Testing & Validation

* **Unit tests**:

  * Parsing of NTA responses
  * GTFS-RT cancellation detection
  * Last-location derivation from `current_stop_sequence`
* **Golden samples**:

  * Store a few JSON/protobuf snapshots to test rendering deterministically.
* **Manual checks**:

  * Compare against official web views during peak and off-peak.
  * Verify behavior in known “dark territory” segments (data may be estimated).

---

## Future Enhancements (deferred)

* Web configuration UI for pages (edit origin/destination without SSH).
* Multi-line system board using TrainView-style snapshots.
* Presence-aware brightness and night mode.
* Per-stop ETA smoothing using GTFS-RT delays (only if needed).
* Multi-mode expansion (bus/trolley) via the same GTFS-RT adapters.

---

## Milestones

1. **Core data pipeline (API-only)**

   * GTFS static loaded; NTA page renders time + status; cancellation override; last location derived

2. **Rotation & resilience**

   * Page cycling, caching, stale indicator, backoff

3. **Alerts**

   * Route-filtered alert banner

4. **Hardware integration**

   * LED renderer connected; fonts and transitions finalized

5. **Polish**

   * Config file finalized; basic `/status` page; logs tidy

---

## Acceptance Criteria (Core)

* For each configured A→B:

  * Next train time is displayed from NTA.
  * Status shows “On-Time” or “X min late” from NTA, **or** “CANCELLED” if Trip Updates indicate cancellation.
  * Last location shows a valid station name derived from Vehicle Positions + GTFS Static.
  * “Last updated” timestamp is visible; stale state is indicated on fetch failures.
* System cycles through all configured pages on the LED matrix with clear, legible text.
