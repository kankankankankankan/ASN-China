'''
Generate ASN rule lists from config/asn_services.json.
'''
from datetime import datetime, timezone
import json
from pathlib import Path

import requests


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "config" / "asn_services.json"
REQUEST_TIMEOUT = 30


def load_services():
    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def validate_service(service):
    required_fields = ("name", "output")
    missing_fields = [field for field in required_fields if field not in service]
    if missing_fields:
        raise ValueError(
            "{} is missing required field(s): {}".format(
                service.get("name", "<unknown>"),
                ", ".join(missing_fields),
            )
        )

    if "asns" not in service and "discoveries" not in service:
        raise ValueError(
            "{} must define asns or discoveries".format(service["name"])
        )

    for asn in service.get("asns", []):
        if "number" not in asn or "name" not in asn:
            raise ValueError(
                "{} has an ASN entry without number or name".format(service["name"])
            )

    for discovery in service.get("discoveries", []):
        if discovery.get("type") == "ripe_org" and "org" not in discovery:
            raise ValueError(
                "{} has a ripe_org discovery without org".format(service["name"])
            )


def get_attribute(obj, name):
    attributes = obj.get("attributes", {}).get("attribute", [])
    for attribute in attributes:
        if attribute.get("name") == name:
            return attribute.get("value")
    return None


def parse_ripe_aut_nums(data, default_name=None):
    asns = []
    objects = data.get("objects", {}).get("object", [])
    for obj in objects:
        aut_num = get_attribute(obj, "aut-num")
        if not aut_num or not aut_num.upper().startswith("AS"):
            continue

        as_name = get_attribute(obj, "as-name")
        name = default_name or as_name or "Unknown"
        asns.append(
            {
                "number": int(aut_num[2:]),
                "name": name.replace("_", " "),
            }
        )
    return asns


def fetch_ripe_org_asns(discovery):
    url = "https://rest.db.ripe.net/search.json"
    params = {
        "source": "RIPE",
        "query-string": discovery["org"],
        "inverse-attribute": "org",
        "type-filter": "aut-num",
    }
    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return parse_ripe_aut_nums(
        response.json(),
        default_name=discovery.get("default_name"),
    )


def discover_asns(service):
    discovered_asns = []
    for discovery in service.get("discoveries", []):
        discovery_type = discovery.get("type")
        if discovery_type == "ripe_org":
            try:
                discovered_asns.extend(fetch_ripe_org_asns(discovery))
            except requests.RequestException as error:
                if discovery.get("required", True):
                    raise RuntimeError(
                        "Failed to discover ASN for {} from RIPE org {}: {}".format(
                            service["name"],
                            discovery["org"],
                            error,
                        )
                    )
                print(
                    "Warning: skipped RIPE discovery for {} org {}".format(
                        service["name"],
                        discovery["org"],
                    )
                )
        else:
            raise ValueError(
                "{} has unsupported discovery type {}".format(
                    service["name"],
                    discovery_type,
                )
            )
    return discovered_asns


def collect_asns(service):
    asns_by_number = {}
    for asn in discover_asns(service):
        asns_by_number[int(asn["number"])] = asn["name"]

    for asn in service.get("asns", []):
        asns_by_number[int(asn["number"])] = asn["name"]

    if not asns_by_number:
        raise ValueError("{} did not produce any ASN".format(service["name"]))

    return [
        {"number": number, "name": name}
        for number, name in sorted(asns_by_number.items())
    ]


def write_service(service):
    validate_service(service)
    asns = collect_asns(service)

    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    output_path = ROOT_DIR / service["output"]
    description = service.get(
        "description",
        "ASN Information for {}.".format(service["name"]),
    )
    source = service.get("source", "https://github.com/missuo/ASN-China")

    lines = [
        "// {} ({})".format(description, source),
        "// Last Updated: UTC {}".format(updated_at),
        "// Generated from config/asn_services.json",
        "",
    ]

    for asn in asns:
        lines.append("IP-ASN,{} // {}".format(asn["number"], asn["name"]))

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    for service in load_services():
        write_service(service)


if __name__ == "__main__":
    main()
