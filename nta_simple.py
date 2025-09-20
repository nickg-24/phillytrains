#!/usr/bin/env python3
import requests

origin = "Conshohocken"
destination = "Suburban Station"
n = 3  # how many trains to ask for

url = f"https://www3.septa.org/api/NextToArrive/index.php?req1={origin}&req2={destination}&req3={n}"
resp = requests.get(url)
data = resp.json()

# NTA returns a list of trips; iterate and print
for i in range(len(data)):
    trip = data[i]

    dep_time = trip.get("orig_departure_time")
    arr_time = trip.get("orig_arrival_time")
    status = trip.get("orig_delay")

    print("=" * 40)
    print(f"{origin} > {destination}")
    print(f"Departs: {dep_time}")
    print(f"Arrives: {arr_time}")
    print(f"Status:  {status}")
    print("=" * 40)
    print()