'''
Generate ASN rule lists from config/asn_services.json.
'''
from datetime import datetime, timezone
import json
from pathlib import Path

import requests


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "config" / "asn_services.json"
CATALOG_PATH = ROOT_DIR / "config" / "asn_service_catalog.json"
REQUEST_TIMEOUT = 30


def load_json(path):
    with path.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def load_services():
    config = load_json(CONFIG_PATH)

    if isinstance(config, list):
        return config

    enabled = config.get("enabled", [])
    catalog = config.get("catalog", load_json(CATALOG_PATH))
    services = []
    normalized_catalog = {
        str(service_key).lower(): service
        for service_key, service in catalog.items()
    }
    for service_key in enabled:
        normalized_key = str(service_key).strip().lower()
        if normalized_key not in normalized_catalog:
            raise ValueError(
                "Enabled service {} is not defined in catalog".format(service_key)
            )
        services.append(normalized_catalog[normalized_key])
    return services


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
        if discovery.get("type") == "bgp_he_as_set" and "as_set" not in discovery:
            raise ValueError(
                "{} has a bgp_he_as_set discovery without as_set".format(
                    service["name"]
                )
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


def fetch_bgp_he_as_set_asns(discovery):
    as_set = discovery["as_set"]
    url = "https://bgp.he.net/irr/as-set/{}".format(as_set)
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    asns = []
    for line in response.text.splitlines():
        stripped = line.strip()
        if "members:" not in stripped:
            continue

        member = stripped.split("members:", 1)[1].strip()
        if not member.upper().startswith("AS"):
            continue

        asn_digits = "".join(char for char in member[2:] if char.isdigit())
        if asn_digits:
            asns.append(
                {
                    "number": int(asn_digits),
                    "name": discovery.get("default_name", "Unknown"),
                }
            )
    return asns


def lookup_bgp_he_asn_name(asn_number, default_name):
    url = "https://bgp.he.net/AS{}".format(asn_number)
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    marker = "<title>AS{} ".format(asn_number)
    if marker not in response.text:
        return default_name

    title = response.text.split(marker, 1)[1].split(" - bgp.he.net</title>", 1)[0]
    return title.strip() or default_name


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
        elif discovery_type == "bgp_he_as_set":
            try:
                discovered_asns.extend(fetch_bgp_he_as_set_asns(discovery))
            except requests.RequestException as error:
                if discovery.get("required", False):
                    raise RuntimeError(
                        "Failed to discover ASN for {} from AS-SET {}: {}".format(
                            service["name"],
                            discovery["as_set"],
                            error,
                        )
                    )
                print(
                    "Warning: skipped AS-SET discovery for {} {}".format(
                        service["name"],
                        discovery["as_set"],
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

    if service.get("resolve_names"):
        for number, name in list(asns_by_number.items()):
            asns_by_number[number] = lookup_bgp_he_asn_name(number, name)

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
