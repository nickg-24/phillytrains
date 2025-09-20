#!/usr/bin/env python3
import requests
from google.transit import gtfs_realtime_pb2
import zipfile, io, csv

# --- Config ---
origin = "Conshohocken"
destination = "Suburban Station"
n = 2
DEBUG = 1   # 0 = clean, 1 = medium, 2 = full debug

# --- Step 1: Next To Arrive (NTA) ---
nta_url = f"https://www3.septa.org/api/NextToArrive/index.php?req1={origin}&req2={destination}&req3={n}"
nta_resp = requests.get(nta_url)
nta_data = nta_resp.json()

if DEBUG >= 2:
    print("=== NTA DATA ===")
    for t in nta_data:
        print(t)
    print()

# --- Step 2: GTFS Trip Updates ---
tu_url = "https://www3.septa.org/gtfsrt/septarail-pa-us/Trip/rtTripUpdates.pb"
resp = requests.get(tu_url)
tu_feed = gtfs_realtime_pb2.FeedMessage()
tu_feed.ParseFromString(resp.content)
if DEBUG >= 2:
    print(f"Trip Updates feed: {len(tu_feed.entity)} entities")

# --- Step 3: GTFS Vehicle Positions ---
vp_url = "https://www3.septa.org/gtfsrt/septarail-pa-us/Vehicle/rtVehiclePosition.pb"
resp = requests.get(vp_url)
vp_feed = gtfs_realtime_pb2.FeedMessage()
vp_feed.ParseFromString(resp.content)
if DEBUG >= 2:
    print(f"Vehicle Positions feed: {len(vp_feed.entity)} entities")

# --- Step 4: Load stop_id → stop_name from google_rail.zip ---
zip_url = "https://www3.septa.org/developer/gtfs_public.zip"
resp = requests.get(zip_url)
outer = zipfile.ZipFile(io.BytesIO(resp.content))
rail_bytes = outer.read("google_rail.zip")
rail_zip = zipfile.ZipFile(io.BytesIO(rail_bytes))

stop_lookup = {}
with rail_zip.open("stops.txt") as f:
    reader = csv.DictReader(io.TextIOWrapper(f, "utf-8"))
    for row in reader:
        stop_lookup[row["stop_id"]] = row["stop_name"]

if DEBUG >= 2:
    print(f"Loaded {len(stop_lookup)} stops from GTFS static\n")

# --- Step 5: Loop through NTA trains ---
for idx, trip in enumerate(nta_data):
    nta_train_id = trip.get("orig_train")
    dep_time = trip.get("orig_departure_time")
    arr_time = trip.get("orig_arrival_time")
    status = trip.get("orig_delay")
    last_station = None

    if DEBUG >= 1:
        print("=" * 40)
        print(f"Checking NTA train {nta_train_id} ({origin} → {destination})")

    # --- Check cancellation in Trip Updates ---
    found_tu = False
    for entity in tu_feed.entity:
        if entity.HasField("trip_update"):
            trip_id = entity.trip_update.trip.trip_id
            if nta_train_id and nta_train_id in trip_id:
                found_tu = True
                if DEBUG >= 1:
                    print(f"Matched TripUpdate trip_id: {trip_id}")
                if entity.trip_update.trip.schedule_relationship == gtfs_realtime_pb2.TripDescriptor.CANCELED:
                    status = "CANCELLED"
                    if DEBUG >= 1:
                        print("Marked as CANCELLED by GTFS-RT")
                break
    if DEBUG >= 2 and not found_tu:
        print("No TripUpdate match found for this train")

    # --- Find vehicle position and stop name (only for first train) ---
    if idx == 0:  # only do "last location" for first train
        found_vp = False
        for entity in vp_feed.entity:
            if entity.HasField("vehicle"):
                trip_id = entity.vehicle.trip.trip_id
                if nta_train_id and nta_train_id in trip_id:
                    found_vp = True
                    vp = entity.vehicle
                    if DEBUG >= 1:
                        print(f"Matched VehiclePosition trip_id: {trip_id}")
                        print(f"Raw stop_id from VP: {vp.stop_id}")
                    if vp.stop_id in stop_lookup:
                        last_station = stop_lookup[vp.stop_id]
                        if DEBUG >= 1:
                            print(f"Translated stop_id → {last_station}")
                    else:
                        if DEBUG >= 1:
                            print("stop_id not in stop_lookup")
                    break
        if DEBUG >= 2 and not found_vp:
            print("No VehiclePosition match found for this train")

    # --- Final summary block ---
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
