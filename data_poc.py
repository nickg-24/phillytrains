#!/usr/bin/env python3
import requests
from google.transit import gtfs_realtime_pb2
import zipfile, io, csv
import datetime

# --- Config ---
origin = "Conshohocken"
destination = "Suburban Station"
n = 2
DEBUG = 1  # 0 = clean, 1 = medium, 2 = verbose

# GTFS-RT VehiclePosition status map
STATUS_MAP = {
    0: "IN_TRANSIT_TO",
    1: "STOPPED_AT",
    2: "INCOMING_AT"
}

# --- Helper: format GTFS HH:MM:SS into AM/PM ---
def format_gtfs_time(timestr, service_date):
    h, m, s = map(int, timestr.split(":"))
    day_offset = h // 24
    h = h % 24
    dt = datetime.datetime.combine(service_date, datetime.time(h, m, s))
    if day_offset:
        dt += datetime.timedelta(days=day_offset)
    return dt.strftime("%I:%M %p")

# --- Step 1: NTA call ---
nta_url = f"https://www3.septa.org/api/NextToArrive/index.php?req1={origin}&req2={destination}&req3={n}"
nta_resp = requests.get(nta_url)
nta_data = nta_resp.json()

# --- Step 2: Trip Updates feed ---
tu_url = "https://www3.septa.org/gtfsrt/septarail-pa-us/Trip/rtTripUpdates.pb"
resp = requests.get(tu_url)
tu_feed = gtfs_realtime_pb2.FeedMessage()
tu_feed.ParseFromString(resp.content)

# --- Step 3: Vehicle Positions feed ---
vp_url = "https://www3.septa.org/gtfsrt/septarail-pa-us/Vehicle/rtVehiclePosition.pb"
resp = requests.get(vp_url)
vp_feed = gtfs_realtime_pb2.FeedMessage()
vp_feed.ParseFromString(resp.content)

# --- Step 4: Load GTFS static (rail) ---
zip_url = "https://www3.septa.org/developer/gtfs_public.zip"
resp = requests.get(zip_url)
outer = zipfile.ZipFile(io.BytesIO(resp.content))
rail_bytes = outer.read("google_rail.zip")
rail_zip = zipfile.ZipFile(io.BytesIO(rail_bytes))

# stops.txt lookup
stop_lookup = {}
with rail_zip.open("stops.txt") as f:
    reader = csv.DictReader(io.TextIOWrapper(f, "utf-8"))
    for row in reader:
        stop_lookup[row["stop_id"]] = row["stop_name"]

# stop_times.txt lookup
trip_stops = {}
with rail_zip.open("stop_times.txt") as f:
    reader = csv.DictReader(io.TextIOWrapper(f, "utf-8"))
    for row in reader:
        tid = row["trip_id"]
        seq = int(row["stop_sequence"])
        sid = row["stop_id"]
        dep = row["departure_time"]
        if tid not in trip_stops:
            trip_stops[tid] = []
        trip_stops[tid].append((seq, sid, dep))
for tid in trip_stops:
    trip_stops[tid].sort(key=lambda x: x[0])

# trips.txt → service_id + route_id
trip_service = {}
trip_route = {}
with rail_zip.open("trips.txt") as f:
    reader = csv.DictReader(io.TextIOWrapper(f, "utf-8"))
    for row in reader:
        trip_service[row["trip_id"]] = row["service_id"]
        trip_route[row["trip_id"]] = row["route_id"]

# calendar.txt
calendar = {}
with rail_zip.open("calendar.txt") as f:
    reader = csv.DictReader(io.TextIOWrapper(f, "utf-8"))
    for row in reader:
        service_id = row["service_id"]
        calendar[service_id] = row

# calendar_dates.txt
calendar_dates = {}
with rail_zip.open("calendar_dates.txt") as f:
    reader = csv.DictReader(io.TextIOWrapper(f, "utf-8"))
    for row in reader:
        service_id = row["service_id"]
        date = row["date"]
        exception = row["exception_type"]
        if service_id not in calendar_dates:
            calendar_dates[service_id] = {}
        calendar_dates[service_id][date] = exception

# --- Step 5: Service Alerts feed ---
alerts_url = "https://www3.septa.org/gtfsrt/septarail-pa-us/Service/rtServiceAlerts.pb"
resp = requests.get(alerts_url)
alerts_feed = gtfs_realtime_pb2.FeedMessage()
alerts_feed.ParseFromString(resp.content)

# --- Determine stop_ids for origin/destination ---
origin_stop_ids = [sid for sid, name in stop_lookup.items() if name == origin]
dest_stop_ids = [sid for sid, name in stop_lookup.items() if name == destination]

# --- Dynamically infer route_id ---
nta_route_id = None
for trip_id, stops in trip_stops.items():
    o = d = None
    for seq, sid, dep in stops:
        if sid in origin_stop_ids and o is None:
            o = (seq, sid)
        if sid in dest_stop_ids and o and seq > o[0] and d is None:
            d = (seq, sid)
    if o and d:
        nta_route_id = trip_route.get(trip_id)
        if nta_route_id:
            break

if DEBUG >= 1:
    print(f"[DEBUG] Origin stops: {origin_stop_ids}, Dest stops: {dest_stop_ids}")
    print(f"[DEBUG] Inferred route_id: {nta_route_id}")

# --- Filter alerts relevant to this route/stops ---
alerts_list = []
for entity in alerts_feed.entity:
    if entity.HasField("alert"):
        alert = entity.alert
        applies = False
        for ie in alert.informed_entity:
            if nta_route_id and ie.route_id == nta_route_id:
                applies = True
            if ie.stop_id in origin_stop_ids or ie.stop_id in dest_stop_ids:
                applies = True
        if not alert.informed_entity:  # global
            applies = True
        if applies and alert.description_text.translation:
            desc = alert.description_text.translation[0].text
            alerts_list.append(desc)

if DEBUG >= 1:
    print(f"[DEBUG] Loaded {len(alerts_list)} filtered alerts")

# --- Helper: check if service runs on date ---
def service_active(service_id, date):
    date_str = date.strftime("%Y%m%d")
    if service_id in calendar_dates and date_str in calendar_dates[service_id]:
        exc = calendar_dates[service_id][date_str]
        return exc == "1"
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

# --- Helper: find first trip after midnight ---
def find_first_trip_after(date, origin_name, dest_name):
    origin_ids = [sid for sid, name in stop_lookup.items() if name == origin_name]
    dest_ids = [sid for sid, name in stop_lookup.items() if name == dest_name]
    best_time = None
    best_trip = None
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

# --- MAIN ---
if not nta_data:
    today = datetime.date.today()
    d = today + datetime.timedelta(days=1)
    while True:
        trip = find_first_trip_after(d, origin, destination)
        if trip:
            tid, dep, arr = trip
            print("=" * 40)
            print(f"{origin} > {destination}")
            print(f"No more trains today.")
            print(f"Next service: Departing {dep}, Arriving {arr}, on {d.strftime('%A, %B %d')}")
            print("=" * 40)
            break
        d += datetime.timedelta(days=1)
else:
    for idx, trip in enumerate(nta_data):
        nta_train_id = trip.get("orig_train")
        dep_time = trip.get("orig_departure_time")
        arr_time = trip.get("orig_arrival_time")
        status = trip.get("orig_delay")
        last_station = None

        # check cancellation
        for entity in tu_feed.entity:
            if entity.HasField("trip_update"):
                trip_id = entity.trip_update.trip.trip_id
                if nta_train_id and nta_train_id in trip_id:
                    if entity.trip_update.trip.schedule_relationship == gtfs_realtime_pb2.TripDescriptor.CANCELED:
                        status = "CANCELLED"
                    break

        # only compute last station for first train
        if idx == 0:
            for entity in vp_feed.entity:
                if entity.HasField("vehicle"):
                    trip_id = entity.vehicle.trip.trip_id
                    if nta_train_id and nta_train_id in trip_id:
                        vp = entity.vehicle
                        cs = vp.current_stop_sequence
                        st = vp.current_status
                        sid = vp.stop_id
                        if st == 1:  # STOPPED_AT
                            last_station = stop_lookup.get(sid, sid)
                        elif st == 0:  # IN_TRANSIT_TO
                            if trip_id in trip_stops:
                                prev_seq = cs - 1
                                prev_stop = next((s for (seq, s, dep) in trip_stops[trip_id] if seq == prev_seq), None)
                                if prev_stop:
                                    last_station = stop_lookup.get(prev_stop, prev_stop)
                            if not last_station:
                                last_station = stop_lookup.get(sid, sid)
                        break

        print("=" * 40)
        print(f"{origin} > {destination}")
        print(f"Train #: {nta_train_id}")
        print(f"Departs: {dep_time}")
        print(f"Arrives: {arr_time}")
        print(f"Status:  {status}")
        if last_station:
            print(f"Last location: {last_station}")
        print("=" * 40)
        print()

# --- Global alerts shown once per cycle ---
if alerts_list:
    print("=== Alerts ===")
    for a in alerts_list:
        print(f"* {a}")
    print("=" * 40)
