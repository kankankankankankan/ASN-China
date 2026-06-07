# ASN 列表生成说明

这个项目可以生成三类列表：

- 中国和美国 ASN 列表，使用原有脚本。
- 服务类 ASN 列表，使用 `config/asn_services.json`。
- 国家或地区 ASN 列表，使用 `config/asn_countries.json`。

## 快速操作

### 只更新现有列表

如果没有新增服务或国家，只想重新拉取最新数据，运行：

```bash
python3 scripts/IP_CN.py
python3 scripts/ASN_CN.py
python3 scripts/ASN_US.py
python3 scripts/ASN_SERVICES.py
python3 scripts/ASN_COUNTRIES.py
```

这些命令会更新：

```text
IP.China.list
IPv4.China.list
IPv6.China.list
ASN.China.list
ASN.US.list
ASN.Telegram.list
ASN.Japan.list
ASN.Korea.list
```

### 新增服务列表

1. 编辑 `config/asn_services.json`。
2. 追加服务配置。
3. 运行 `python3 scripts/ASN_SERVICES.py`。
4. 检查生成的 `ASN.<Service>.list`。
5. 提交配置、脚本生成的列表文件。

### 新增国家或地区列表

1. 编辑 `config/asn_countries.json`。
2. 追加国家或地区配置。
3. 运行 `python3 scripts/ASN_COUNTRIES.py`。
4. 检查生成的 `ASN.<Country>.list`。
5. 提交配置、脚本生成的列表文件。

### 推送后的自动更新

GitHub Actions 已配置定时运行，入口在 `.github/workflows/ci.yml`。

触发方式：

- push 后自动运行。
- 每天按 cron 定时运行。
- 在 GitHub Actions 页面手动运行 `workflow_dispatch`。

手动运行步骤：

1. 打开 GitHub 仓库页面。
2. 进入 `Actions`。
3. 选择 `Update ASN and IP List`。
4. 点击 `Run workflow`。
5. 选择 `target`。
6. 点击绿色的 `Run workflow`。

`target` 可选值：

```text
all: 更新全部列表
ip: 只更新中国 IP 列表
base-asn: 只更新 ASN.China.list 和 ASN.US.list
service-asn: 只更新服务类 ASN，例如 ASN.Telegram.list
country-asn: 只更新国家或地区 ASN，例如 ASN.Japan.list 和 ASN.Korea.list
```

`all` 会执行：

```bash
python scripts/IP_CN.py
python scripts/ASN_CN.py
python scripts/ASN_US.py
python scripts/ASN_SERVICES.py
python scripts/ASN_COUNTRIES.py
```

## 服务类 ASN

服务类 ASN 使用：

```bash
python3 scripts/ASN_SERVICES.py
```

Telegram 已配置为自动发现。脚本每次运行时会查询 RIPE 数据库中 `ORG-TMI4-RIPE` 关联的 `aut-num` 对象。如果 Telegram 以后新增 ASN，并且该 ASN 归属这个 RIPE 组织，生成结果会自动包含新 ASN。

手动填写的 `asns` 用于补充名称和兜底。例如 `44907` 可以显示为 `Telegram Messenger CDN`。

新增普通服务时，在 `config/asn_services.json` 追加：

```json
{
  "name": "Example",
  "output": "ASN.Example.list",
  "description": "ASN Information for Example.",
  "source": "https://bgp.he.net",
  "asns": [
    {
      "number": 64512,
      "name": "Example Network"
    }
  ]
}
```

新增后运行：

```bash
python3 scripts/ASN_SERVICES.py
```

## 国家或地区 ASN

国家或地区 ASN 使用：

```bash
python3 scripts/ASN_COUNTRIES.py
```

当前已配置：

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

新增国家或地区时，在 `config/asn_countries.json` 追加：

```json
{
  "code": "SG",
  "name": "Singapore",
  "output": "ASN.Singapore.list"
}
```

`code` 使用 bgp.he.net 国家代码，例如：

```text
JP: https://bgp.he.net/country/JP
KR: https://bgp.he.net/country/KR
SG: https://bgp.he.net/country/SG
HK: https://bgp.he.net/country/HK
```

文件名统一使用国家或地区英文全名，例如 `ASN.Japan.list`、`ASN.Korea.list`、`ASN.Singapore.list`。

新增后运行：

```bash
python3 scripts/ASN_COUNTRIES.py
```

## 本地检查

修改配置后运行：

```bash
python3 -m json.tool config/asn_services.json
python3 -m json.tool config/asn_countries.json
python3 -m py_compile scripts/ASN_SERVICES.py
python3 -m py_compile scripts/ASN_COUNTRIES.py
python3 scripts/ASN_SERVICES.py
python3 scripts/ASN_COUNTRIES.py
```

GitHub Actions 已配置定时运行这些脚本，推送后会自动更新生成文件。
