import requests
import zipfile
import io
import csv
import datetime

GTFS_URL = "https://www3.septa.org/developer/gtfs_public.zip"

_outer_bytes = None
_rail_data = None
_subway_data = None


def _get_outer_zip():
    global _outer_bytes
    if _outer_bytes is None:
        resp = requests.get(GTFS_URL, timeout=30)
        _outer_bytes = resp.content
    return zipfile.ZipFile(io.BytesIO(_outer_bytes))


def format_gtfs_time(timestr, service_date):
    h, m, s = map(int, timestr.split(":"))
    day_offset = h // 24
    h = h % 24
    dt = datetime.datetime.combine(service_date, datetime.time(h, m, s))
    if day_offset:
        dt += datetime.timedelta(days=day_offset)
    return dt.strftime("%I:%M %p")


def service_active(gtfs, service_id, date):
    date_str = date.strftime("%Y%m%d")
    cd = gtfs["calendar_dates"]
    if service_id in cd and date_str in cd[service_id]:
        return cd[service_id][date_str] == "1"
    cal = gtfs["calendar"]
    if service_id not in cal:
        return False
    row = cal[service_id]
    start = datetime.datetime.strptime(row["start_date"], "%Y%m%d").date()
    end = datetime.datetime.strptime(row["end_date"], "%Y%m%d").date()
    if not (start <= date <= end):
        return False
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    return row[weekdays[date.weekday()]] == "1"


def load_rail():
    global _rail_data
    if _rail_data is not None:
        return _rail_data

    rail_zip = zipfile.ZipFile(io.BytesIO(_get_outer_zip().read("google_rail.zip")))

    stop_lookup = {}
    with rail_zip.open("stops.txt") as f:
        for row in csv.DictReader(io.TextIOWrapper(f, "utf-8")):
            stop_lookup[row["stop_id"]] = row["stop_name"]

    trip_stops = {}
    with rail_zip.open("stop_times.txt") as f:
        for row in csv.DictReader(io.TextIOWrapper(f, "utf-8")):
            tid = row["trip_id"]
            trip_stops.setdefault(tid, []).append(
                (int(row["stop_sequence"]), row["stop_id"], row["departure_time"])
            )
    for tid in trip_stops:
        trip_stops[tid].sort(key=lambda x: x[0])

    trip_service = {}
    with rail_zip.open("trips.txt") as f:
        for row in csv.DictReader(io.TextIOWrapper(f, "utf-8")):
            trip_service[row["trip_id"]] = row["service_id"]

    calendar = {}
    with rail_zip.open("calendar.txt") as f:
        for row in csv.DictReader(io.TextIOWrapper(f, "utf-8")):
            calendar[row["service_id"]] = row

    calendar_dates = {}
    with rail_zip.open("calendar_dates.txt") as f:
        for row in csv.DictReader(io.TextIOWrapper(f, "utf-8")):
            calendar_dates.setdefault(row["service_id"], {})[row["date"]] = row["exception_type"]

    _rail_data = {
        "stop_lookup": stop_lookup,
        "trip_stops": trip_stops,
        "trip_service": trip_service,
        "calendar": calendar,
        "calendar_dates": calendar_dates,
    }
    return _rail_data


def load_subway(stop_ids):
    """Load bus GTFS, filtering stop_times to the given stop_ids set."""
    global _subway_data
    if _subway_data is not None:
        return _subway_data

    stop_ids = set(stop_ids)
    bus_zip = zipfile.ZipFile(io.BytesIO(_get_outer_zip().read("google_bus.zip")))

    stop_times = {}
    with bus_zip.open("stop_times.txt") as f:
        for row in csv.DictReader(io.TextIOWrapper(f, "utf-8")):
            if row["stop_id"] in stop_ids:
                stop_times.setdefault(row["stop_id"], []).append(
                    (row["trip_id"], row["departure_time"])
                )

    trip_service = {}
    with bus_zip.open("trips.txt") as f:
        for row in csv.DictReader(io.TextIOWrapper(f, "utf-8")):
            trip_service[row["trip_id"]] = row["service_id"]

    calendar = {}
    with bus_zip.open("calendar.txt") as f:
        for row in csv.DictReader(io.TextIOWrapper(f, "utf-8")):
            calendar[row["service_id"]] = row

    calendar_dates = {}
    with bus_zip.open("calendar_dates.txt") as f:
        for row in csv.DictReader(io.TextIOWrapper(f, "utf-8")):
            calendar_dates.setdefault(row["service_id"], {})[row["date"]] = row["exception_type"]

    _subway_data = {
        "stop_times": stop_times,
        "trip_service": trip_service,
        "calendar": calendar,
        "calendar_dates": calendar_dates,
    }
    return _subway_data
