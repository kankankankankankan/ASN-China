'''
Generate country ASN rule lists from config/asn_countries.json.
'''
from datetime import datetime, timezone
import json
from pathlib import Path

import requests
from lxml import etree


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "config" / "asn_countries.json"
REQUEST_TIMEOUT = 30
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/107.0.0.0 Safari/537.36"
    )
}


def load_countries():
    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def validate_country(country):
    required_fields = ("code", "name", "output")
    missing_fields = [field for field in required_fields if field not in country]
    if missing_fields:
        raise ValueError(
            "{} is missing required field(s): {}".format(
                country.get("code", "<unknown>"),
                ", ".join(missing_fields),
            )
        )


def fetch_country_asns(country):
    url = "https://bgp.he.net/country/{}".format(country["code"])
    response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    tree = etree.HTML(response.text)
    rows = tree.xpath('//*[@id="asns"]/tbody/tr')
    asns = []
    for row in rows:
        number_nodes = row.xpath("td[1]/a")
        name_nodes = row.xpath("td[2]")
        if not number_nodes or not name_nodes:
            continue

        asn_number = number_nodes[0].text.replace("AS", "")
        asn_name = name_nodes[0].text
        if asn_name:
            asns.append(
                {
                    "number": int(asn_number),
                    "name": asn_name,
                }
            )

    if not asns:
        raise ValueError("No ASN found for {}".format(country["code"]))

    return sorted(asns, key=lambda asn: asn["number"])


def write_country(country):
    validate_country(country)
    asns = fetch_country_asns(country)

    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    output_path = ROOT_DIR / country["output"]
    source = "https://bgp.he.net/country/{}".format(country["code"])

    lines = [
        "// ASN Information in {}. ({})".format(country["name"], source),
        "// Last Updated: UTC {}".format(updated_at),
        "// Generated from config/asn_countries.json",
        "",
    ]

    for asn in asns:
        lines.append("IP-ASN,{} // {}".format(asn["number"], asn["name"]))

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    for country in load_countries():
        write_country(country)


if __name__ == "__main__":
    main()
