# Clash / Mihomo：先分清“导入示例”和“添加规则”

**这些客户端的快捷链接导入的是一份完整配置，不会自动把 Siri AI 规则合并进你的订阅。** 本项目不提供节点。要保留日常路由，请使用下方的配置副本方式；独立示例只适合查看结构，不能当作直接可用的网络配置。

安装页和新版远程示例尚未上线。下面的文件可以本地下载；稳定 HTTPS 地址目前仅供发布检查，不能把尚未发布的地址当作可用订阅：

```text
https://raw.githubusercontent.com/BrownieCoder/SiriAI-RouteKit/main/examples/clash-remote.yaml
```

[下载自包含示例](../examples/clash-remote.yaml)。它显式使用空节点列表、SiriAI 组中的 `REJECT` 和最后的 `MATCH,DIRECT`：启用后 Siri AI 的 5 个目标被阻断，其余流量直连。没有外部文件依赖，不会读取你已有的节点。导入机制依据官方文档与发布源码，真机 GUI 导入尚未测试。[客户端能力与来源](客户端导入能力.md)。

## ClashX.Meta

macOS 客户端；已核验 v1.4.45 的远程配置导入。

**上线后入口：导入 SiriAI 示例配置。确认后会自动切换到它。** 原配置通常保留，但同名项可能被更新；不要沿用日常配置的名字，遇到同名提示请取消或另取名称。示例会阻断这 5 个目标，并使其他流量直连。

无法自动打开时：

1. 复制安装页的完整示例 URL。
2. 在“配置 → 托管配置 → 管理”添加 URL，使用一个尚未使用的配置名称。以所装版本实际菜单为准。
3. 确认会导入并切换。演示后从配置列表切回原配置；日常分流请继续下方“在当前配置副本添加”。

预留安装页：`https://browniecoder.github.io/SiriAI-RouteKit/install/clashx-meta.html`。未上线前不作为可用按钮。

## Clash Verge Rev

已核验 v2.5.5；源码注册 Windows、macOS、Linux 的导入协议。macOS 官方文档要求 2.0 及以后；浏览器或系统关联问题可能阻止打开，复制地址即可，不必为此修改注册表或权限。

**上线后入口：导入 SiriAI 示例配置。** 已有当前配置时，新示例追加到列表；首次导入可能自动启用。它不是规则覆写文件，不会自动合并。启用示例会阻断这 5 个目标，并使其他流量直连。

无法自动打开时：

1. 复制安装页的完整示例 URL。
2. 打开“订阅”，粘贴 URL 并点“导入”。
3. 保持原配置启用；首次导入时不要把无节点示例当日常配置。需要日常分流时，按下面步骤关联现有出口。

预留安装页：`https://browniecoder.github.io/SiriAI-RouteKit/install/clash-verge-rev.html`。未上线前不作为可用按钮。

## 其他 Mihomo 客户端

只使用该 App 明确提供的“从 URL 导入”或文件导入入口，先确认是否会自动切换或覆盖。没有入口时使用[现有配置副本](#在当前配置副本添加)。未专门验证 Mihomo Party 等其他 GUI，不为它们构造一键链接。

## 一键导入失败：先复制地址

先检查完整 HTTPS 地址能否打开，再检查客户端是否安装。浏览器阻止唤起时，直接复制 URL 到上面的导入入口；离线时下载示例文件。**不要将 `rules/clash-meta.yaml` 当完整订阅导入**，它只有规则列表。

以下为高级手动备用路径。Mihomo 会从上往下找第一条匹配规则，所以 Siri AI 规则必须在宽泛 Apple 规则前面，安全拦截仍优先。[内核路由文档](https://wiki.metacubex.one/config/rules/)。

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
