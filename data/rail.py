import requests
import datetime
from data.gtfs import load_rail, format_gtfs_time, service_active

NTA_URL = "https://www3.septa.org/api/NextToArrive/index.php"


def _find_next_service(gtfs, origin_name, dest_name, from_date):
    stop_lookup = gtfs["stop_lookup"]
    trip_stops = gtfs["trip_stops"]
    trip_service = gtfs["trip_service"]

    origin_ids = {sid for sid, name in stop_lookup.items() if name == origin_name}
    dest_ids = {sid for sid, name in stop_lookup.items() if name == dest_name}

    d = from_date + datetime.timedelta(days=1)
    for _ in range(14):
        best_trip = None
        best_secs = None
        for trip_id, stops in trip_stops.items():
            svc_id = trip_service.get(trip_id)
            if not svc_id or not service_active(gtfs, svc_id, d):
                continue
            o = dest = None
            for seq, stop_id, dep in stops:
                if stop_id in origin_ids and o is None:
                    o = (seq, dep)
                if stop_id in dest_ids and o and seq > o[0] and dest is None:
                    dest = (seq, dep)
            if o and dest:
                h, m, s = map(int, o[1].split(":"))
                dep_secs = h * 3600 + m * 60 + s
                if best_secs is None or dep_secs < best_secs:
                    best_secs = dep_secs
                    best_trip = (format_gtfs_time(o[1], d), format_gtfs_time(dest[1], d), d)
        if best_trip:
            return best_trip
        d += datetime.timedelta(days=1)
    return None


def fetch_rail(line):
    """
    line: {name, origin, destination, route_id, n}
    Returns: {name, origin, destination, trains: [{train_no, depart, arrive, status}]}
    """
    origin = line["origin"]
    destination = line["destination"]
    n = line.get("n", 2)

    try:
        resp = requests.get(
            NTA_URL,
            params={"req1": origin, "req2": destination, "req3": n},
            timeout=10,
        )
        nta_data = resp.json()
    except Exception:
        nta_data = []

    trains = []
    if nta_data:
        for trip in nta_data:
            trains.append({
                "train_no": trip.get("orig_train"),
                "depart": trip.get("orig_departure_time"),
                "arrive": trip.get("orig_arrival_time"),
                "status": trip.get("orig_delay"),
            })
    else:
        gtfs = load_rail()
        result = _find_next_service(gtfs, origin, destination, datetime.date.today())
        if result:
            dep, arr, service_date = result
            trains.append({
                "train_no": None,
                "depart": dep,
                "arrive": arr,
                "status": f"Next service {service_date.strftime('%A, %B %d')}",
            })

    return {
        "name": line["name"],
        "origin": origin,
        "destination": destination,
        "trains": trains,
    }


if __name__ == "__main__":
    import json
    import sys
    import yaml

    cfg = yaml.safe_load(open("config.yaml"))
    lines = cfg.get("rail_lines", [])
    if not lines:
        print("No rail_lines in config.yaml")
        sys.exit(1)
    for line in lines:
        print(json.dumps(fetch_rail(line), indent=2))
