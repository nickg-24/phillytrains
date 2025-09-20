#!/usr/bin/env python3
import requests
from google.transit import gtfs_realtime_pb2

url = "https://www3.septa.org/gtfsrt/septarail-pa-us/Trip/rtTripUpdates.pb"

resp = requests.get(url)
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(resp.content)

print("Cancelled trains:")
for entity in feed.entity:
    print(entity)
    if entity.HasField("trip_update"):
        trip = entity.trip_update.trip
        if trip.schedule_relationship == gtfs_realtime_pb2.TripDescriptor.CANCELED:
            print(f"- Trip ID: {trip.trip_id}, Route: {trip.route_id}")
