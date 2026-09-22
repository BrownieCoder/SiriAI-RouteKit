# 尚待验证的候选

核验日：2026-09-22。以下是用户截图中的候选，不参与正式生成。原始规则类型、来源、置信度、处理原因和所需证据见唯一源导入的 [domain-audit.json](domain-audit.json)。

| 候选 | 当前证据缺口 | 纳入前需要什么 |
|---|---|---|
| mask-api.fe.apple-dns.net | Apple 未在核验的主机清单逐项说明此精确主机的 AI 用途 | 明确服务归因及脱敏可复现连接证据 |
| mask-t.apple-dns.net | 名字不能证明它与 Siri AI 的关系 | 官方逐项说明，或可复现的特定功能依赖 |
| mask.apple-dns.net | iCloud DNS 家族不等于 AI 专属 | 证明必要性、共享影响与客户端实际匹配方式 |
| apple-relay.mask.apple-dns.net | 不能从 apple-relay 字样推断为 PCC | 证明与 PCC 的实际依赖关系，不能只有 DNS 别名 |
| gspe1-ssl.ls.apple.com | 尚无本次范围所需的直接官方功能归因 | 证明精确主机与目标功能的关联及其它服务影响 |

来源边界：[Apple 企业网络文档](https://support.apple.com/en-us/101555)只将 `*.apple-dns.net` 归为 iCloud DNS 家族，并未为上述四个子域分别给出 Siri AI 归因。同样不能把 `ls.apple.com` 家族中其它主机的用途外推给 `gspe1-ssl`。

未发现需要立即加入的额外精确域名。共享搜索 `smoot.apple.com` 已有官方共享用途说明；整个后缀在本次默认范围拒绝。未来若要研究精确子域，应另开证据审计，而不是把“候选”当成可复制的备用生产规则。
