import requests
from google.transit import gtfs_realtime_pb2

ALERTS_URL = "https://www3.septa.org/gtfsrt/septarail-pa-us/Service/rtServiceAlerts.pb"


def fetch_alerts(route_ids):
    """
    route_ids: list of route ID strings to filter alerts for (e.g. ["NOR", "B1"])
    Returns: deduplicated list of alert strings relevant to any configured route
    """
    route_ids = set(route_ids or [])

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
            if ie.route_id and ie.route_id in route_ids:
                if desc not in seen:
                    seen.add(desc)
                    alerts.append(desc)
                break

    return alerts


if __name__ == "__main__":
    import json
    import yaml

    cfg = yaml.safe_load(open("config.yaml"))
    route_ids = cfg.get("alerts", {}).get("route_ids", [])
    result = fetch_alerts(route_ids)
    print(json.dumps(result, indent=2))
