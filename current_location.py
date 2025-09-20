#!/usr/bin/env python3
import requests
from google.transit import gtfs_realtime_pb2
import zipfile, io, csv

# --- Step 1: Load GTFS static (for stop_id → name lookup) ---
zip_url = "https://www3.septa.org/developer/gtfs_public.zip"
resp = requests.get(zip_url)
outer = zipfile.ZipFile(io.BytesIO(resp.content))
rail_bytes = outer.read("google_rail.zip")
rail_zip = zipfile.ZipFile(io.BytesIO(rail_bytes))

stop_lookup = {}
with rail_zip.open("stops.txt") as f:
    import io as sysio
    reader = csv.DictReader(sysio.TextIOWrapper(f, "utf-8"))
    for row in reader:
        stop_lookup[row["stop_id"]] = row["stop_name"]

# --- Step 2: Get Vehicle Positions feed ---
vp_url = "https://www3.septa.org/gtfsrt/septarail-pa-us/Vehicle/rtVehiclePosition.pb"
resp = requests.get(vp_url)
vp_feed = gtfs_realtime_pb2.FeedMessage()
vp_feed.ParseFromString(resp.content)

print("=== Norristown Line Active Trains ===")
for entity in vp_feed.entity:
    if entity.HasField("vehicle"):
        trip_id = entity.vehicle.trip.trip_id
        if trip_id.startswith("NOR"):   # only Norristown line
            sid = entity.vehicle.stop_id
            stop_name = stop_lookup.get(sid, sid)
            print(f"Trip: {trip_id}, StopID: {sid}, StopName: {stop_name}, Status={entity.vehicle.current_status}")
