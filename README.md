# 🍎 SiriAI-RouteKit

Siri AI / Apple Intelligence 中国大陆网络分流规则与中文小白教程，支持 Shadowrocket、Clash Meta / Mihomo。

**本项目与 Apple Inc. 无关联，为社区维护项目。规则只决定网络出口，不保证获得功能资格。** 当前为本地准备版本，尚未发布在线规则订阅地址。

## 30 秒判断：我到底能不能用？

- [ ] 设备型号支持我需要的功能。
- [ ] 系统版本符合对应功能要求。
- [ ] 设备销售地区符合官方条件。
- [ ] 当前所在地及 Apple 账户国家/地区符合要求。
- [ ] 设备语言与 Siri 语言符合对应功能要求。
- [ ] 本机有足够空间，模型已下载并完成初始化。
- [ ] 如果目标是 Siri AI（Beta），已获得该 Beta 的使用资格。
- [ ] 最后才检查：规则确实命中，策略选择及网络出口正常。

前面的设备、账号、地区、系统或语言条件不满足时，换节点通常不能解决。

## 先分清自己要用什么

**Apple 官方确认，核验于 2026-09-22：** 当前 Siri AI（Beta）与一般 Apple Intelligence 是两个不同的核对对象。Siri AI Beta 要求 27 系列系统及匹配的英语设备/Siri 语言；不能把一般 Apple Intelligence 对简体中文的支持套用到它。[Siri AI 官方要求](https://support.apple.com/zh-cn/148218)、[Apple Intelligence 官方说明](https://support.apple.com/zh-cn/121115)

中国大陆销售设备当前仍受 Apple Intelligence 限制。境外销售设备也要核对所在地和 Apple 账户地区。美国节点、修改设备地区、切换 App Store 账户均不是官方承诺的解锁方法。[设备与账号要求](docs/设备与账号要求.md)

## 选一个入口开始

1. 先读[设备与账号要求](docs/设备与账号要求.md)：机型、系统、语言、国行/外版、账户和模型空间。
2. 使用小火箭：按 [Shadowrocket 教程](docs/Shadowrocket教程.md)把精确规则加入当前配置副本。
3. 使用 Mihomo 内核：按 [Clash Meta / Mihomo 教程](docs/Clash-Meta教程.md)添加本地 provider 并复用现有策略组。
4. 不成功：按[排障指南](docs/排障指南.md)逐层检查；术语参见[技术原理](docs/技术原理.md)。

没有代理节点的用户需要自行准备可用的网络服务。本项目只提供规则，不提供节点、订阅或账号。

## 这 5 个精确域名做什么？

规则覆盖 Apple 官方列明的 Siri/听写、Private Cloud Compute（私有云计算，PCC）与 Apple Intelligence 扩展入口。传统 Siri 和听写使用 `guzzoni.apple.com`，也会随之改变出口。它不是全量 Apple 服务或完整模型下载依赖清单。[Apple 网络主机说明](https://support.apple.com/en-us/101555)

- [唯一源导入的域名清单](rules/domains.txt)与[逐域来源](rules/provenance.json)。
- [Shadowrocket 规则集](rules/shadowrocket.list)与[无节点配置示例](examples/shadowrocket.conf)。
- [Mihomo classical provider](rules/clash-meta.yaml)与[无节点配置示例](examples/clash-meta.yaml)。
- [18 条截图规则完整审计](research/domain-audit.json)：5 条接纳、5 条待验证、8 条不进入默认规则；没有添加断网 REJECT 规则来“拒绝”候选。

本项目不把 iCloud Private Relay、商店下载、地图整族域名或 `siri` 关键字当作 Siri AI 专属流量。不能把截图中的 18 条全部照抄进日常配置。

## 证据怎么读？

| 标记 | 含义 |
|---|---|
| Apple 官方确认 | 资格、服务用途有 Apple 直达来源和核验日期。 |
| 本项目验证 | 脚本已检查规则、来源锁、生成一致性和示例引用；这不是设备联网实测。 |
| 社区经验 | Shadowrocket 详细界面和配置写法参考社区维护手册，明确为非官方资料。 |
| 尚待验证 | 候选域名、真实设备功能、实际出口及客户端导入结果。 |

**尚未进行 Shadowrocket 真机导入、Apple 设备功能或真实网络请求实测。** 静态验证通过不能证明 Siri AI 可用。Mihomo 示例默认以 `REJECT` 显式阻断目标流量，需先按教程关联自己已有的出口。两个独立示例的其他流量均直连；优先把所需部分合入当前配置副本，保留原有兜底规则。

## 安全与隐私

不需要 MITM，不需要安装未知 CA，不需要解密 Siri 流量，也不需要向本项目提供 Apple 账户密码或代理订阅。不要公开密码、2FA 验证码、节点用户名密码、API token、订阅 URL、账号邮箱或完整私人配置。排障只记录脱敏后的机型/版本、域名、规则、时间和错误类别。[反馈模板](.github/ISSUE_TEMPLATE/问题反馈.md)

## 维护与许可

唯一规则源为 [BrownieCoder/proxy-rulesets](https://github.com/BrownieCoder/proxy-rulesets)；本仓库是教学与多客户端生成输出。版本和 SHA256 锁在 [source.lock.json](source.lock.json)，不手工维护第二套域名。更新方法见[维护与来源](docs/维护与来源.md)。

Python 3.10+ 标准库即可离线验证，无需安装第三方包：

```sh
python3 scripts/rules.py validate
python3 -m unittest discover -s tests
git diff --check
```

采用 GPL-2.0-only，保留 [LICENSE](LICENSE) 原文和[来源致谢](ATTRIBUTION.md)。README、教程及项目注释使用简体中文；许可证与协议字段保留规范原文。
