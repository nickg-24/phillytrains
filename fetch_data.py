#!/usr/bin/env python3
import requests
from google.transit import gtfs_realtime_pb2
import zipfile, io, csv
import datetime
import yaml
import os

# --- Load Config ---
def load_config(path="config.yaml"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

origin = config.get("origin", "Conshohocken")
destination = config.get("destination", "Suburban Station")
n = config.get("n", 2)
DEBUG = config.get("debug", 0)

# --- Helper: format GTFS HH:MM:SS into AM/PM ---
def format_gtfs_time(timestr, service_date):
    h, m, s = map(int, timestr.split(":"))
    day_offset = h // 24
    h = h % 24
    dt = datetime.datetime.combine(service_date, datetime.time(h, m, s))
    if day_offset:
        dt += datetime.timedelta(days=day_offset)
    return dt.strftime("%I:%M %p")

# --- Load GTFS static (rail only, once) ---
zip_url = "https://www3.septa.org/developer/gtfs_public.zip"
resp = requests.get(zip_url)
outer = zipfile.ZipFile(io.BytesIO(resp.content))
rail_bytes = outer.read("google_rail.zip")
rail_zip = zipfile.ZipFile(io.BytesIO(rail_bytes))

# stops.txt
stop_lookup = {}
with rail_zip.open("stops.txt") as f:
    reader = csv.DictReader(io.TextIOWrapper(f, "utf-8"))
    for row in reader:
        stop_lookup[row["stop_id"]] = row["stop_name"]

# stop_times.txt
trip_stops = {}
with rail_zip.open("stop_times.txt") as f:
    reader = csv.DictReader(io.TextIOWrapper(f, "utf-8"))
    for row in reader:
        tid = row["trip_id"]
        seq = int(row["stop_sequence"])
        sid = row["stop_id"]
        dep = row["departure_time"]
        trip_stops.setdefault(tid, []).append((seq, sid, dep))
for tid in trip_stops:
    trip_stops[tid].sort(key=lambda x: x[0])

# trips.txt > service_id
trip_service = {}
with rail_zip.open("trips.txt") as f:
    reader = csv.DictReader(io.TextIOWrapper(f, "utf-8"))
    for row in reader:
        trip_service[row["trip_id"]] = row["service_id"]

# calendar.txt
calendar = {}
with rail_zip.open("calendar.txt") as f:
    reader = csv.DictReader(io.TextIOWrapper(f, "utf-8"))
    for row in reader:
        calendar[row["service_id"]] = row

# calendar_dates.txt
calendar_dates = {}
with rail_zip.open("calendar_dates.txt") as f:
    reader = csv.DictReader(io.TextIOWrapper(f, "utf-8"))
    for row in reader:
        calendar_dates.setdefault(row["service_id"], {})[row["date"]] = row["exception_type"]

# --- Service active check ---
def service_active(service_id, date):
    date_str = date.strftime("%Y%m%d")
    if service_id in calendar_dates and date_str in calendar_dates[service_id]:
        return calendar_dates[service_id][date_str] == "1"
    if service_id not in calendar:
        return False
    row = calendar[service_id]
    start = datetime.datetime.strptime(row["start_date"], "%Y%m%d").date()
    end = datetime.datetime.strptime(row["end_date"], "%Y%m%d").date()
    if not (start <= date <= end):
        return False
    weekday = date.weekday()
    weekdays = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    return row[weekdays[weekday]] == "1"

# --- Find first trip after midnight for origin>destination ---
def find_first_trip_after(date, origin_name, dest_name):
    origin_ids = [sid for sid, name in stop_lookup.items() if name == origin_name]
    dest_ids = [sid for sid, name in stop_lookup.items() if name == dest_name]
    best_trip = None
    best_time = None
    for trip_id, stops in trip_stops.items():
        sid = trip_service.get(trip_id)
        if not sid or not service_active(sid, date):
            continue
        o = d = None
        for seq, stop_id, dep in stops:
            if stop_id in origin_ids and o is None:
                o = (seq, dep)
            if stop_id in dest_ids and o and seq > o[0] and d is None:
                d = (seq, dep)
        if o and d:
            dep_time = datetime.datetime.strptime(o[1], "%H:%M:%S").time()
            if best_time is None or dep_time < best_time:
                best_time = dep_time
                dep_fmt = format_gtfs_time(o[1], date)
                arr_fmt = format_gtfs_time(d[1], date)
                best_trip = (trip_id, dep_fmt, arr_fmt)
    return best_trip

# --- One refresh cycle ---
def run_once():
    # Step 1: NTA call
    nta_url = f"https://www3.septa.org/api/NextToArrive/index.php?req1={origin}&req2={destination}&req3={n}"
    nta_resp = requests.get(nta_url)
    nta_data = nta_resp.json()
    if DEBUG >= 1:
        print(f"[DEBUG] Pulled {len(nta_data)} trips from NTA API")

    # Step 2: Service Alerts
    alerts_url = "https://www3.septa.org/gtfsrt/septarail-pa-us/Service/rtServiceAlerts.pb"
    resp = requests.get(alerts_url)
    alerts_feed = gtfs_realtime_pb2.FeedMessage()
    alerts_feed.ParseFromString(resp.content)
    if DEBUG >= 1:
        print(f"[DEBUG] Loaded {len(alerts_feed.entity)} service alerts")

    # Infer route_id for filtering (basic)
    route_id = None
    if nta_data:
        if "Norristown" in nta_data[0].get("orig_line", ""):
            route_id = "NOR"
    if DEBUG >= 1:
        print(f"[DEBUG] Inferred route_id: {route_id}")

    trains = []
    alerts_list = []

    if not nta_data:
        today = datetime.date.today()
        d = today + datetime.timedelta(days=1)
        while True:
            trip = find_first_trip_after(d, origin, destination)
            if trip:
                _, dep, arr = trip
                trains.append({
                    "train_no": None,
                    "depart": dep,
                    "arrive": arr,
                    "status": f"Next service on {d.strftime('%A, %B %d')}"
                })
                break
            d += datetime.timedelta(days=1)
    else:
        for trip in nta_data:
            trains.append({
                "train_no": trip.get("orig_train"),
                "depart": trip.get("orig_departure_time"),
                "arrive": trip.get("orig_arrival_time"),
                "status": trip.get("orig_delay"),
            })

    for entity in alerts_feed.entity:
        if entity.HasField("alert") and entity.alert.description_text.translation:
            desc = entity.alert.description_text.translation[0].text
            relevant = False
            for ie in entity.alert.informed_entity:
                if route_id and ie.route_id == route_id:
                    relevant = True
                if ie.stop_id in stop_lookup and stop_lookup[ie.stop_id] in (origin, destination):
                    relevant = True
            if not entity.alert.informed_entity:  # global
                relevant = True
            if relevant:
                if DEBUG >= 1:
                    print(f"[DEBUG] Including alert: {desc[:50]}...")
                alerts_list.append(desc)

    return {
        "origin": origin,
        "destination": destination,
        "trains": trains,
        "alerts": alerts_list,
        "last_updated": datetime.datetime.now().isoformat()
    }

# Allow testing standalone
if __name__ == "__main__":
    import json
    data = run_once()
    print(json.dumps(data, indent=2))

