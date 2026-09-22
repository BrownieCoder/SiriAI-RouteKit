# Clash Meta / Mihomo：本地规则 provider

核验于 2026-09-22，使用当前 [Mihomo provider 文档](https://wiki.metacubex.one/config/rule-providers/)、[内容格式](https://wiki.metacubex.one/config/rule-providers/content/)与[路由语法](https://wiki.metacubex.one/config/rules/)。Clash Meta 是 Mihomo 的旧称，图形客户端的按钮和覆写机制各不相同。

## 先认识三个词

- **rule-provider：** 一个规则文件，本项目是 5 条 `DOMAIN` 精确匹配。
- **policy / 策略组：** 选用哪个已有节点或出口。
- **first-match：** 按规则顺序匹配，前面命中后就可能不再到后面。因此 SiriAI 必须在宽泛 Apple/China/Global 前面。

## 在当前配置副本添加

1. 使用客户端的配置复制/备份功能保留原配置。若配置会随订阅更新覆盖，请使用该客户端支持的覆写/合并功能，不直接改临时下载文件。
2. 找到内核的配置目录（HomeDir），把 [rules/clash-meta.yaml](../rules/clash-meta.yaml)放到该目录下 `rules/clash-meta.yaml`。路径按内核 HomeDir 解释，并不一定是你打开示例文件所在目录。不要为方便而扩大 `SAFE_PATHS`。
3. 在现有 `rule-providers:` 下增加以下项。文件已有这个顶层键时，添加子项，不能重复顶层键：

```yaml
rule-providers:
  SiriAI:
    type: file
    behavior: classical
    format: yaml
    path: ./rules/clash-meta.yaml
```

4. 优先使用已存在且有可用节点的 AI 策略组。在 `rules:` 的安全规则之后、宽泛 Apple/China/Global/CDN 规则之前添加一行。以下 `AI` 必须换成你配置里真实存在的组名：

```yaml
rules:
  - RULE-SET,SiriAI,AI
```

这只是插入片段，不是替换全部 rules。原有 `MATCH` 及其它业务规则继续保留。现有 proxy-rulesets 模板实际复用 `🤖 AI 服务`，不新建 Siri 组；上面的 `AI` 是需要替换成自己已有组名的示例。

5. 若确需独立组，可添加下列 `select` 组，再把上一行最后一段改为 `SiriAI`。组内 `AI` 仍然引用自己已有的组：

```yaml
proxy-groups:
  - name: SiriAI
    type: select
    proxies:
      - AI
```

6. 保存、使用该副本并重载配置。检查 provider 列表：`SiriAI` 应成功加载 5 条。选中实际可用的出口，不能停在 REJECT 或不存在的占位组。
7. 在客户端连接列表/日志中，发起一次不含私人内容的请求，核对域名、命中 `RULE-SET,SiriAI`、最终策略和实际出口。留意是 TCP 还是 UDP。示例和脚本的静态通过不能替代这一步。

## 无节点示例怎样使用？

[examples/clash-meta.yaml](../examples/clash-meta.yaml)是能供结构解析的独立演示。它用 `REJECT` 显式阻断尚未配置出口的目标流量，其他流量 `MATCH,DIRECT`。需要先把已有节点或组并入配置再替换该选择，不能把示例当作现成联网服务。日常配置采用上面的插入步骤，避免覆盖原来代理其他流量的规则。

如果本机已安装 Mihomo，可在本项目根目录用独立路径做语法检查：

```sh
mihomo -t -d . -f examples/clash-meta.yaml
```

这检查公开示例与本地 provider，不读取个人配置。不需要启动监听端口。图形客户端会有不同入口；若没有 CLI，使用它自己的配置检查，不要把本项目脚本称为 Mihomo 官方解析器。

## 顺序和 UDP 的细节

`guzzoni.apple.com` 可能先被 Apple 直连规则命中；其他 Relay 域可能先被宽泛 CDN/Global 命中。新增一条精确 provider 引用在其之前即可，无需重新排序全部规则。保留安全拦截优先和既有游戏规则的相对次序。

Mihomo 官方文档另有 UDP 例外：请求是 UDP 而代理不支持 UDP 时，会继续向下匹配。PCC/扩展主机官方列 TCP 与 UDP/443，所以要核对最终连接的策略和节点 UDP 能力。不要把静态 first-match 模拟称为所有协议的真实转发证明。[Mihomo 优先级](https://wiki.metacubex.one/config/rules/)、[Apple 端口说明](https://support.apple.com/en-us/101555)

遇到 provider 未加载，先查目录/格式/缩进；命中 Apple DIRECT，先查次序；命中 SiriAI 仍失败，再查节点、协议、DNS 和资格。完整顺序见[排障指南](排障指南.md)。
