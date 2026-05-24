import datetime
from data.gtfs import load_subway, format_gtfs_time, service_active


def _departures_for_stop(gtfs, stop_id, date):
    result = []
    for trip_id, dep_time in gtfs["stop_times"].get(stop_id, []):
        svc_id = gtfs["trip_service"].get(trip_id)
        if not svc_id or not service_active(gtfs, svc_id, date):
            continue
        h, m, s = map(int, dep_time.split(":"))
        result.append((h * 3600 + m * 60 + s, format_gtfs_time(dep_time, date)))
    result.sort(key=lambda x: x[0])
    return [t for _, t in result]


def fetch_subway(config):
    """
    config: {station, route_id, stops: {northbound: stop_id, southbound: stop_id}}
    Returns: {station, northbound: [times], southbound: [times]}
    """
    nb_stop = str(config["stops"]["northbound"])
    sb_stop = str(config["stops"]["southbound"])

    gtfs = load_subway({nb_stop, sb_stop})
    today = datetime.date.today()

    return {
        "station": config["station"],
        "northbound": _departures_for_stop(gtfs, nb_stop, today),
        "southbound": _departures_for_stop(gtfs, sb_stop, today),
    }


if __name__ == "__main__":
    import json
    import yaml

    cfg = yaml.safe_load(open("config.yaml"))
    result = fetch_subway(cfg.get("subway", {}))
    print(json.dumps({
        "station": result["station"],
        "northbound_count": len(result["northbound"]),
        "southbound_count": len(result["southbound"]),
        "northbound_sample": result["northbound"][:5],
        "southbound_sample": result["southbound"][:5],
    }, indent=2))
