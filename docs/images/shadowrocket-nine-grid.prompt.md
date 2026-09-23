# Shadowrocket 九宫格图生成说明

- 工具：内置 image_gen（imagegen 技能），未使用 CLI/API fallback。
- 用途：教程操作示意，不是真实客户端截图。
- 完整模块地址在 Markdown 正文中提供，不让用户从图片抄写长 URL。
- 原始提示词：

```text
Use case: infographic-diagram. Create a polished, extremely simple Chinese beginner tutorial infographic for installing a Siri AI rule MODULE into Shadowrocket. One large square image, 3 by 3 grid, EXACTLY NINE equal panels, read left to right then top to bottom, high resolution 2048 square or higher. White background, navy text, blue tap accents, minimal iOS-style schematic UI fragments (NOT real screenshots), very large readable Simplified Chinese text. No complex backgrounds or decoration, no photography. Each panel has a prominent number 1-9 and one SHORT title with a simple illustrative UI fragment underneath. Title above grid: "Shadowrocket 添加 Siri AI 模块". Subtitle: "复制地址 → 粘贴添加 → 启用模块". Render exact panel text:
1 "复制模块地址" — show a URL field with placeholder "正文中的完整链接" and a Copy button "复制". Do NOT render a fake or shortened functional URL, no QR codes.
2 "打开小火箭" — generic outlined smartphone with label "Shadowrocket", simple launch/tap icon.
3 "点「配置」" — simple bottom navigation fragment with 配置 circled in blue.
4 "进入「模块」" — simple list row "模块" with chevron and tap indicator.
5 "点右上角「＋」" — simple header "模块" with a large blue plus at upper right circled.
6 "粘贴模块地址" — empty/new URL input showing "已复制的完整链接", callout "粘贴". It is a remote module URL, not full configuration import or subscription node import.
7 "确认添加" — simple dialog with button "确定" highlighted. No invented extra options.
8 "启用 Siri AI" — one list row "Siri AI" with an ON toggle, small caption "确认模块已开启".
9 "使用「配置」路由" — simple selected radio list item "配置 ✓", small caption "连接你已有的可用节点".
Footer one short line: "操作示意｜菜单以当前版本为准｜需已有可用节点". No promise of network success or Siri eligibility, no guarantee of automatic unlock. No CA, MITM, certificates, script, DNS, proxy node imports or account entry anywhere. Keep plenty of whitespace. Diagrammatic fragments, not fabricated authentic screenshots. Avoid tiny text. Correct Chinese spelling, exact nine panels, no extra panel. User wants the easiest clear copy/paste tutorial, not technical engineering details.
```
