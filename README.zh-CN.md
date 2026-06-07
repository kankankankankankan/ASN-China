# ASN 列表 GitHub Actions 操作说明

这个项目通过 GitHub Actions 更新 ASN 和 IP 列表。

当前支持三类列表：

1. 中国 IP、中国 ASN、美国 ASN，使用原有脚本。
2. 服务类 ASN，配置文件是 `config/asn_services.json`。
3. 国家或地区 ASN，配置文件是 `config/asn_countries.json`。

## 手动运行 GitHub Actions

1. 打开 GitHub 仓库页面。
2. 进入 `Actions`。
3. 选择 `Update ASN and IP List`。
4. 点击 `Run workflow`。
5. 选择 `target`。
6. 点击绿色的 `Run workflow`。
7. 等待任务完成，Actions 会自动提交生成结果。

`target` 可选值：

```text
all: 更新全部列表
ip: 只更新中国 IP 列表
base-asn: 只更新 ASN.China.list 和 ASN.US.list
service-asn: 只更新服务类 ASN，例如 ASN.Telegram.list
country-asn: 只更新国家或地区 ASN，例如 ASN.Japan.list 和 ASN.Korea.list
```

## 自动更新

`.github/workflows/ci.yml` 已配置自动更新。

触发方式：

1. 推送代码后自动运行。
2. 按 cron 定时运行。
3. 在 GitHub Actions 页面手动运行。

定时和 push 默认使用 `all`，会更新全部列表。

## 后期新增服务

适用场景：

1. Telegram、Netflix 这类服务。
2. 需要生成 `ASN.<Service>.list` 的列表。

操作步骤：

1. 在 GitHub 仓库里打开 `config/asn_services.json`。
2. 点击编辑。
3. 把服务 key 加到 `enabled`。
4. 提交改动。
5. 进入 `Actions`。
6. 运行 `Update ASN and IP List`。
7. `target` 选择 `service-asn`。
8. 等待 Actions 自动生成并提交新列表。

例如启用 Netflix，只需要把：

```json
{
  "enabled": [
    "telegram"
  ]
}
```

改成：

```json
{
  "enabled": [
    "telegram",
    "netflix"
  ]
}
```

然后在 Actions 里选择 `service-asn`，会生成 `ASN.Netflix.list`。

当前服务目录 `config/asn_service_catalog.json` 已内置：

```text
telegram
netflix
```

服务目录里已经写好自动发现规则，普通使用时不用填写 ASN。

如果服务不在目录里，再编辑 `config/asn_service_catalog.json` 追加完整配置：

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

Telegram 当前使用 RIPE 自动发现，并配置了 `ORG-TMI4-RIPE` 和 `ORG-TMI5-RIPE`。

含义：

1. Actions 每次运行时查询 RIPE。
2. 查询 `ORG-TMI4-RIPE` 和 `ORG-TMI5-RIPE` 关联的 `aut-num`。
3. Telegram 后期新增 ASN 时，只要 RIPE 里归属这些组织，生成结果会自动包含新 ASN。

Telegram 不需要手动填写 ASN。Actions 会根据 RIPE 返回结果生成 `ASN.Telegram.list`。

Netflix 使用 bgp.he.net 的 AS-SET 自动发现：

```json
{
  "type": "bgp_he_as_set",
  "as_set": "as-nflx",
  "default_name": "Netflix"
}
```

Netflix 不需要手动填写 ASN。Actions 会根据 `as-nflx` AS-SET 返回结果生成 `ASN.Netflix.list`。

## 后期新增国家或地区

适用场景：

1. Japan、Korea、Singapore、Hong Kong 这类国家或地区。
2. 需要生成 `ASN.<Country>.list` 的列表。

操作步骤：

1. 在 GitHub 仓库里打开 `config/asn_countries.json`。
2. 点击编辑。
3. 追加国家或地区配置。
4. 提交改动。
5. 进入 `Actions`。
6. 运行 `Update ASN and IP List`。
7. `target` 选择 `country-asn`。
8. 等待 Actions 自动生成并提交新列表。

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

新增 Singapore 示例：

```json
{
  "code": "SG",
  "name": "Singapore",
  "output": "ASN.Singapore.list"
}
```

`code` 使用 bgp.he.net 国家代码：

```text
JP: https://bgp.he.net/country/JP
KR: https://bgp.he.net/country/KR
SG: https://bgp.he.net/country/SG
HK: https://bgp.he.net/country/HK
```

文件名统一使用英文全名，例如：

```text
ASN.Japan.list
ASN.Korea.list
ASN.Singapore.list
ASN.HongKong.list
```

## 提交后检查

Actions 完成后检查这些内容：

1. Actions 任务状态是成功。
2. 仓库出现新的 `.list` 文件。
3. 自动提交里包含配置文件和生成文件。
4. 生成文件格式类似 `IP-ASN,62041 // Telegram Messenger Inc`。
