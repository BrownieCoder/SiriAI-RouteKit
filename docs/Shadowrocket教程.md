# Shadowrocket：把规则加入自己的配置

**范围：** 已有可用节点的用户。当前只有本地文件，尚无本项目在线订阅地址。下面详细菜单和格式参考 [LOWERTOP 社区维护手册](https://github.com/LOWERTOP/Shadowrocket/wiki)，该手册声明自己是非官方项目。官方 [App Store 说明](https://apps.apple.com/us/app/shadowrocket/id932747118)确认支持域名规则和 URL/iCloud Drive 导入。核验于 2026-09-22；本项目未进行真机导入测试。

## 最简单的做法：在配置副本加 5 条规则

规则是一张“遇到这个主机就用这个出口”的表。它不创建代理节点，也不改变 Apple 账户。

1. 先在首页确认已有节点可连接，再读完[设备与账号要求](设备与账号要求.md)。节点名称的国旗不能证明实际出口地区。
2. 打开“配置”，找到当前有勾选标记的配置。点它进入编辑菜单，选择“复制”，在副本上操作，保留原配置便于回退。
3. 点副本后面的 `ⓘ` →“规则”→右上角 `+`。类型选 `DOMAIN`，域名填写下表一行，策略选已有的 `PROXY`。依次添加 5 条。不要选 `DOMAIN-SUFFIX` 或 `DOMAIN-KEYWORD`。

| 类型 | 域名 | 策略 |
|---|---|---|
| DOMAIN | apple-relay.apple.com | PROXY |
| DOMAIN | apple-relay.cloudflare.com | PROXY |
| DOMAIN | apple-relay.fastly-edge.com | PROXY |
| DOMAIN | cp4.cloudflare.com | PROXY |
| DOMAIN | guzzoni.apple.com | PROXY |

4. 把这 5 条排在宽泛的 Apple、China、Global/CDN 规则之前，保留已有安全/拦截规则的优先级；不要修改原来的 `FINAL` 兜底。检查是否有模块覆盖了这些规则。
5. 每条保存后回到配置菜单，点“使用配置”或“编译配置”，确认勾选的是副本。首页“全局路由”选“配置”，再选定自己已有的可用节点。
6. 打开“配置 → 测试规则”，分别输入五个域名，确认命中所加精确规则及 `PROXY`。这里只证明匹配结果。
7. 做一次不含个人信息的 Siri 请求，再在“数据 → 代理”的日志记录中按时间核对实际目标、规则、策略与错误。只有实际连接能验证网络情况。

如果界面顺序不同，以所安装版本菜单为准。没有保存/没有重新编译、仍选择旧配置、全局路由选“代理”或“直连”、模块抢先命中，都会让刚添加的规则看似失效。

## 想用独立策略组

在副本 `ⓘ → 代理分组 → +`，命名 `SiriAI`，类型选 `select`，加入自己已有的节点或 `PROXY`，然后把五条规则的目标改成 `SiriAI`。之后在该组里选择出口。组只是已有出口的选择器；不能因为创建了组就以为已经有节点。

## 使用文件或纯文本

[examples/shadowrocket.conf](../examples/shadowrocket.conf)是不带节点的独立演示，可保存到“文件”/iCloud Drive 后通过分享菜单交给 Shadowrocket；如果当前版本没有该分享项，在“配置”中新建本地配置并使用“编辑纯文本”粘贴。保留原配置，再编译和使用示例。

**演示的 `FINAL,DIRECT` 会让所有未命中流量直连。日常配置请采用上面的副本加规则流程，不要整份替换。** 示例 `SiriAI = select,PROXY` 使用首页已经选择的代理。

[rules/shadowrocket.list](../rules/shadowrocket.list)是两字段规则集，供 `RULE-SET` 引用；它不是完整配置，直接贴入 `[Rule]` 需要给每条补第三字段策略。三字段写法可从自动生成的示例取用。将来只有发布了真实公开文件链接，才能添加 `RULE-SET,实际规则链接,SiriAI`；不要把本地电脑路径或虚构 raw URL 当订阅地址。

## DNS 和出口怎么排查？

先确认规则测试及实际连接记录，再区分“域名没有解析”“解析后连不上”“选错策略”“出口服务不通”。不在日志里公开节点地址、账号或完整配置。Relay/PCC 相关入口包含 UDP/443，出口需兼容相应协议；不要默认强制屏蔽 QUIC 就一定能回退成功。[Apple 网络主机清单](https://support.apple.com/en-us/101555)

不要为了本规则集安装 CA、启用 HTTPS 解密或开启 MITM。网络匹配正确仍无法使用时，回到资格、语言、模型与等待名单，不反复堆叠宽后缀。
