<!--
 * @Author: Vincent Young
 * @Date: 2022-11-17 02:07:33
 * @LastEditors: Vincent Young
 * @LastEditTime: 2022-11-17 03:33:16
 * @FilePath: /ASN-China/README.md
 * @Telegram: https://t.me/missuo
 * 
 * Copyright © 2022 by Vincent, All Rights Reserved. 
-->
# ASN-China
Real-time updated Chinese ASN and IP database.

中文说明: [README.zh-CN.md](./README.zh-CN.md)

## Features
- Automatic daily updates
- Reliable and accurate source

## Use in proxy app
### Surge
```
[Rule]
# > China ASN List
RULE-SET, https://raw.githubusercontent.com/missuo/ASN-China/main/ASN.China.list, Direct
```

### Quantumult X
```
[filter_remote]
# China ASN List
https://raw.githubusercontent.com/missuo/ASN-China/main/ASN.China.list, tag=ChinaASN, force-policy=direct, update-interval=86400, opt-parser=true, enabled=true
```

### Telegram ASN List
```
RULE-SET, https://raw.githubusercontent.com/missuo/ASN-China/main/ASN.Telegram.list, Proxy
```

## Custom service ASN
Service ASN lists are generated from `config/asn_services.json`.

### Add a service list
To enable a catalog service, add its key to `enabled` in `config/asn_services.json`.

Example, enable Netflix:

```json
{
  "enabled": [
    "telegram",
    "netflix"
  ]
}
```

Services can use two ASN sources:

- `discoveries`: ASN entries discovered at runtime from an external registry.

Telegram uses RIPE organisation discovery for `ORG-TMI4-RIPE` and `ORG-TMI5-RIPE`.
Netflix uses the bgp.he.net AS-SET `as-nflx`.
Disney uses the bgp.he.net AS-SET `AS-DSTL-2`.

Built-in service definitions live in `config/asn_service_catalog.json`.
For services that are not in the catalog, add a new catalog entry.

```json
"example": {
  "name": "Example",
  "output": "ASN.Example.list",
  "description": "ASN Information for Example.",
  "source": "https://bgp.he.net",
  "discoveries": [
    {
      "type": "bgp_he_as_set",
      "as_set": "as-example",
      "default_name": "Example",
      "required": true
    }
  ]
}
```

After editing the config, run the `Update ASN and IP List` workflow in GitHub Actions and choose `service-asn`.
The workflow will generate the file defined by `output`, for example `ASN.Netflix.list`.

### Add a country or region list
Country and region ASN lists are generated from `config/asn_countries.json`.
They use bgp.he.net country pages.

Examples:

```text
CN: https://bgp.he.net/country/CN
US: https://bgp.he.net/country/US
JP: https://bgp.he.net/country/JP
KR: https://bgp.he.net/country/KR
HK: https://bgp.he.net/country/HK
SG: https://bgp.he.net/country/SG
```

Japan and Korea are already configured:

```json
[
  {
    "code": "JP",
    "name": "Japan",
    "output": "ASN.Japan.list"
  },
  {
    "code": "KR",
    "name": "Korea",
    "output": "ASN.Korea.list"
  }
]
```

To add another country or region, append an item:

```json
{
  "code": "SG",
  "name": "Singapore",
  "output": "ASN.Singapore.list"
}
```

Then run the `Update ASN and IP List` workflow in GitHub Actions and choose `country-asn`.

### GitHub Actions

Manual workflow targets:

```text
all: update all lists
ip: update China IP lists
base-asn: update ASN.China.list and ASN.US.list
service-asn: update service ASN lists
country-asn: update country or region ASN lists
```

## Data Source
### ASN Information
- [bgp.he.net](https://bgp.he.net/country/CN)
- [Telegram ASN entries](https://bgp.he.net/AS62041)
- [Netflix AS-SET](https://bgp.he.net/irr/as-set/as-nflx)

### IP Information
- [cbuijs/ipasn](https://github.com/cbuijs/ipasn)

## Author's ASN
**[AS206729](https://bgp.he.net/AS206729)**

The ASN name has been officially changed in the Jan 20, 2022 UTC [Commit](https://github.com/missuo/ASN-China/commit/4345acd8e146c99d56792977d88ed1d6417c9e22).

## Author

**ASN-China** © [Vincent Young](https://github.com/missuo), Released under the [MIT](./LICENSE) License.<br>
