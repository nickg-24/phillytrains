import requests
from google.transit import gtfs_realtime_pb2
from data.gtfs import load_rail

ALERTS_URL = "https://www3.septa.org/gtfsrt/septarail-pa-us/Service/rtServiceAlerts.pb"


def fetch_alerts(lines):
    """
    lines: list of {name, origin, destination, route_id}
    Returns: deduplicated list of alert strings relevant to any configured line
    """
    route_ids = {line["route_id"] for line in lines if line.get("route_id")}
    stop_names = set()
    for line in lines:
        stop_names.add(line["origin"])
        stop_names.add(line["destination"])

    gtfs = load_rail()
    stop_lookup = gtfs["stop_lookup"]

    try:
        resp = requests.get(ALERTS_URL, timeout=10)
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(resp.content)
    except Exception:
        return []

    seen = set()
    alerts = []

    for entity in feed.entity:
        if not entity.HasField("alert"):
            continue
        if not entity.alert.description_text.translation:
            continue
        desc = entity.alert.description_text.translation[0].text

        if not entity.alert.informed_entity:
            if desc not in seen:
                seen.add(desc)
                alerts.append(desc)
            continue

        for ie in entity.alert.informed_entity:
            if (ie.route_id and ie.route_id in route_ids) or (
                ie.stop_id and stop_lookup.get(ie.stop_id) in stop_names
            ):
                if desc not in seen:
                    seen.add(desc)
                    alerts.append(desc)
                break

    return alerts


if __name__ == "__main__":
    import json
    import yaml

    cfg = yaml.safe_load(open("config.yaml"))
    lines = cfg.get("rail_lines", [])
    alerts = fetch_alerts(lines)
    print(json.dumps(alerts, indent=2))
