/* 固定目标，不读取 URL 查询参数，不接受外部重定向目标。 */
(() => {
  "use strict";
  // 校验、复制和客户端二次下载必须绑定同一已发布提交；更新步骤见维护文档。
  const rawBase = "https://raw.githubusercontent.com/BrownieCoder/SiriAI-RouteKit/6bce8d5563cd13aef913035971decab4890fc267/";
  const profiles = {
    shadowrocket: { path: "modules/siri-ai.module", scheme: "shadowrocket://install?module=", label: "一键导入 Shadowrocket", auto: true },
    "clashx-meta": { path: "examples/clash-remote.yaml", scheme: "clashx://install-config?name=SiriAI-Example-No-Nodes&url=", label: "导入示例并切换到 ClashX.Meta" },
    "clash-verge-rev": { path: "examples/clash-remote.yaml", scheme: "clash-verge://install-config?url=", label: "导入示例到 Clash Verge Rev" },
    mihomo: { path: "examples/clash-remote.yaml" }
  };
  const client = document.body.dataset.client;
  const profile = profiles[client];
  if (!profile) return;
  const address = document.getElementById("resource-url");
  const status = document.getElementById("status");
  const open = document.getElementById("open-client");
  const copy = document.getElementById("copy-url");
  const url = rawBase + profile.path;
  let available = false;
  address.value = url;
  copy.hidden = false;
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(url);
      document.getElementById("copy-status").textContent = available
        ? "地址已复制。请到客户端粘贴。"
        : "地址已复制，但在线文件尚不可用。请等文件发布或网络恢复后再导入。";
    } catch {
      address.focus();
      address.select();
      document.getElementById("copy-status").textContent = "请长按或按复制快捷键，复制上方已选中的完整地址。";
    }
  });
  if (open) {
    open.addEventListener("click", event => {
      if (open.getAttribute("aria-disabled") === "true") event.preventDefault();
      else status.textContent = "正在尝试打开客户端；请在客户端内确认。没有打开时，复制下方地址。";
    });
  }
  async function checkResource() {
    // 只下载本项目的公开清单和目标文件；404/旧生成物不触发客户端导入。
    const abort = new AbortController();
    const timeout = setTimeout(() => abort.abort(), 10000);
    try {
      const manifestResponse = await fetch("assets.json", { signal: abort.signal, cache: "no-store", credentials: "omit" });
      if (!manifestResponse.ok) throw new Error("清单不可达");
      const manifest = await manifestResponse.json();
      const response = await fetch(url, { signal: abort.signal, cache: "no-store", credentials: "omit" });
      if (!response.ok) throw new Error("资源不可达");
      const hash = await crypto.subtle.digest("SHA-256", await response.arrayBuffer());
      const actual = Array.from(new Uint8Array(hash), n => n.toString(16).padStart(2, "0")).join("");
      if (actual !== manifest[profile.path]) throw new Error("内容不匹配");
      available = true;
      if (!open) {
        status.textContent = "示例地址可访问。它不含节点，不能自动合并现有配置。";
        return;
      }
      open.href = profile.scheme + encodeURIComponent(url);
      open.setAttribute("aria-disabled", "false");
      open.textContent = profile.label;
      status.textContent = "文件已核对。请确认 App 已安装，再打开客户端。";
      if (profile.auto) {
        status.textContent = "正在打开 Shadowrocket… 请在 App 内确认安装；若没有打开，请点上方按钮。";
        try {
          window.location.href = open.href;
        } catch {
          status.textContent = "浏览器没有自动打开 Shadowrocket。请点上方按钮，或复制地址到客户端。";
        }
      }
    } catch {
      status.textContent = "在线文件暂不可用或版本尚未同步，未打开客户端。请稍后重试；不要把尚未发布的地址当作可用订阅。下方保留地址和备用步骤。";
      if (open) open.textContent = "暂不能自动导入";
    } finally {
      clearTimeout(timeout);
    }
  }
  checkResource();
})();
