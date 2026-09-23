// 通过真正执行页面脚本，验证导入、失败保护和复制退路；不唤起真实代理 App。
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { webcrypto } = require('node:crypto');
const root = path.join(__dirname, '..');
const script = fs.readFileSync(path.join(root, 'install/install.js'), 'utf8');
const hashes = JSON.parse(fs.readFileSync(path.join(root, 'install/assets.json')));
const raw = 'https://raw.githubusercontent.com/BrownieCoder/SiriAI-RouteKit/6bce8d5563cd13aef913035971decab4890fc267/';

async function page(client, options = {}) {
  const nodes = {};
  for (const id of ['resource-url', 'status', 'open-client', 'copy-url', 'copy-status']) {
    nodes[id] = {
      textContent: '', value: '', href: '', hidden: true, attributes: { 'aria-disabled': 'true' },
      listeners: {}, addEventListener(event, fn) { this.listeners[event] = fn; },
      getAttribute(name) { return this.attributes[name]; }, setAttribute(name, value) { this.attributes[name] = value; },
      focus() { this.focused = true; }, select() { this.selected = true; }
    };
  }
  if (client === 'mihomo') nodes['open-client'] = null;
  const fetched = [], copied = [], window = { location: { href: 'https://example.invalid/?url=evil' } };
  if (options.blockedLaunch) Object.defineProperty(window.location, 'href', {
    get() { return 'https://example.invalid/'; },
    set() { throw new Error('navigation blocked'); }
  });
  const context = {
    document: { body: { dataset: { client } }, getElementById: id => nodes[id] },
    window, navigator: { clipboard: options.clipboard === false ? undefined : { writeText: async value => copied.push(value) } },
    crypto: webcrypto, Uint8Array, AbortController, setTimeout, clearTimeout,
    fetch: async (url, init) => {
      fetched.push(url);
      assert.equal(init.credentials, 'omit');
      if (options.offline) throw new Error('offline');
      if (url === 'assets.json') return { ok: true, json: async () => hashes };
      assert.ok(url.startsWith(raw));
      const bytes = options.tampered ? Buffer.from('<html>wrong file</html>') : fs.readFileSync(path.join(root, url.slice(raw.length)));
      return { ok: options.notFound !== true, arrayBuffer: async () => bytes };
    }
  };
  vm.runInNewContext(script, context);
  for (let i = 0; i < 50 && nodes.status.textContent === ''; i++) await new Promise(resolve => setTimeout(resolve, 5));
  assert.notEqual(nodes.status.textContent, '', 'resource check completes');
  return { nodes, window, copied, fetched };
}

for (const [client, protocol, parameter, resource] of [
  ['shadowrocket', 'shadowrocket:', 'module', 'modules/siri-ai.module'],
  ['clashx-meta', 'clashx:', 'url', 'examples/clash-remote.yaml'],
  ['clash-verge-rev', 'clash-verge:', 'url', 'examples/clash-remote.yaml']
]) {
  test(`${client}: 下载、显示、复制、解码目标完全一致`, async () => {
    const state = await page(client);
    const link = new URL(state.nodes['open-client'].href);
    assert.equal(link.protocol, protocol);
    assert.equal(link.searchParams.get(parameter), raw + resource);
    assert.equal(state.fetched.at(-1), link.searchParams.get(parameter));
    assert.match(new URL(link.searchParams.get(parameter)).pathname, /^\/BrownieCoder\/SiriAI-RouteKit\/[a-f0-9]{40}\//);
    assert.match(link.search, /https%3A%2F%2Fraw/);
    assert.equal(state.nodes['resource-url'].value, raw + resource);
    await state.nodes['copy-url'].listeners.click();
    assert.deepEqual(state.copied, [raw + resource]);
    assert.equal(state.nodes['open-client'].getAttribute('aria-disabled'), 'false');
    if (client === 'clashx-meta') assert.equal(link.searchParams.get('name'), 'SiriAI-Example-No-Nodes');
    if (client === 'clash-verge-rev') assert.deepEqual([...link.searchParams.keys()], ['url']);
    if (client === 'shadowrocket') assert.equal(state.window.location.href, link.href);
    else assert.match(state.window.location.href, /example.invalid/); // Clash 不自动激活。
    assert.doesNotMatch(state.nodes.status.textContent, /安装成功|导入成功/);
  });
}
for (const failure of ['notFound', 'tampered', 'offline']) {
  test(`${failure}: 不唤起客户端、不声称成功，保留地址`, async () => {
    const state = await page('shadowrocket', { [failure]: true });
    assert.equal(state.nodes['open-client'].href, '');
    assert.equal(state.nodes['open-client'].getAttribute('aria-disabled'), 'true');
    let prevented = false;
    state.nodes['open-client'].listeners.click({ preventDefault() { prevented = true; } });
    assert.ok(prevented);
    assert.match(state.window.location.href, /example.invalid/);
    assert.match(state.nodes.status.textContent, /未打开客户端/);
    assert.equal(state.nodes['resource-url'].value, raw + 'modules/siri-ai.module');
  });
}
test('Clipboard 不可用时选中完整地址，不伪报复制成功', async () => {
  const state = await page('shadowrocket', { clipboard: false, offline: true });
  await state.nodes['copy-url'].listeners.click();
  assert.ok(state.nodes['resource-url'].selected);
  assert.ok(state.nodes['resource-url'].focused);
  assert.doesNotMatch(state.nodes['copy-status'].textContent, /已复制/);
});
test('其他 Mihomo GUI 只复制地址，不捏造通用 scheme', async () => {
  const state = await page('mihomo');
  assert.equal(state.nodes['open-client'], null);
  assert.match(state.window.location.href, /example.invalid/);
  assert.match(state.nodes.status.textContent, /不能自动合并/);
});

test('浏览器阻止自动唤起不被误报为资源失败', async () => {
  const state = await page('shadowrocket', { blockedLaunch: true });
  assert.equal(state.nodes['open-client'].getAttribute('aria-disabled'), 'false');
  assert.match(state.nodes.status.textContent, /浏览器没有自动打开/);
  assert.doesNotMatch(state.nodes.status.textContent, /文件暂不可用/);
});
test('复制不可用的资源地址时仍明确不能导入', async () => {
  const state = await page('shadowrocket', { notFound: true });
  await state.nodes['copy-url'].listeners.click();
  assert.match(state.nodes['copy-status'].textContent, /尚不可用/);
  assert.doesNotMatch(state.nodes['copy-status'].textContent, /请到客户端粘贴/);
});

// main 可以在页面校验后更新；客户端仍必须下载刚才校验的提交版本。
test('分支在校验后变更不影响客户端二次下载的内容', async () => {
  const state = await page('clashx-meta');
  const verifiedURL = state.fetched.at(-1);
  const verifiedBytes = fs.readFileSync(path.join(root, 'examples/clash-remote.yaml'));
  const handoffURL = new URL(state.nodes['open-client'].href).searchParams.get('url');
  const remote = new Map([
    [verifiedURL, verifiedBytes],
    ['https://raw.githubusercontent.com/BrownieCoder/SiriAI-RouteKit/main/examples/clash-remote.yaml', Buffer.from('changed after verification')]
  ]);
  assert.deepEqual(remote.get(handoffURL), verifiedBytes);
  await state.nodes['copy-url'].listeners.click();
  assert.equal(state.copied[0], verifiedURL);
});
test('无 JavaScript 的页面地址也使用同一固定提交', () => {
  for (const [client, file] of [
    ['shadowrocket', 'modules/siri-ai.module'],
    ['clashx-meta', 'examples/clash-remote.yaml'],
    ['clash-verge-rev', 'examples/clash-remote.yaml'],
    ['mihomo', 'examples/clash-remote.yaml']
  ]) {
    const html = fs.readFileSync(path.join(root, 'install', client + '.html'), 'utf8');
    const address = html.match(/id="resource-url"[^>]*value="([^"]+)"/)[1];
    assert.equal(address, raw + file);
    assert.match(new URL(address).pathname, /^\/BrownieCoder\/SiriAI-RouteKit\/[a-f0-9]{40}\//);
  }
});
