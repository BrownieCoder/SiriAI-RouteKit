"""安装资产契约：精确域、拒绝漂移、规则范围、相对链接与旧锚点。"""
import contextlib
import hashlib
import importlib.util
import io
import json
import re
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('install_rules', ROOT / 'scripts/rules.py')
rules = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rules)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {'href', 'src'} and value:
                self.targets.append(value)


def anchors(text):
    explicit = set(re.findall(r'id="([^"]+)"', text))
    for heading in re.findall(r'^#{1,6} (.+)$', text, re.M):
        # GitHub 标题锚点的本项目子集；Unicode 汉字保留。
        explicit.add(re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-'))
    return explicit


class InstallAssetsTests(unittest.TestCase):
    def setUp(self):
        self.domains = (ROOT / 'rules/domains.txt').read_text().splitlines()
        self.outputs = rules.generated(self.domains)

    def test_module_contains_only_exact_rules_and_builtin_proxy(self):
        text = self.outputs['modules/siri-ai.module'].decode()
        active = [line for line in text.splitlines() if line and not line.startswith('#')]
        self.assertEqual(active, ['[Rule]'] + [f'DOMAIN,{d},PROXY' for d in self.domains])
        self.assertEqual(len(self.domains), 5)

    def test_remote_profile_is_self_contained_and_explicitly_empty(self):
        text = self.outputs['examples/clash-remote.yaml'].decode()
        self.assertIn('proxies: []\n', text)  # Verge 远程导入要求键存在。
        self.assertNotIn('rule-providers:', text)
        self.assertNotIn('proxy-providers:', text)
        self.assertNotIn('path:', text)
        self.assertIn('    proxies:\n      - REJECT\n', text)
        self.assertEqual(re.findall(r'^  - (DOMAIN,.*|MATCH,.*)$', text, re.M),
                         [f'DOMAIN,{d},SiriAI' for d in self.domains] + ['MATCH,DIRECT'])

    def test_all_format_domains_are_same_set_and_order(self):
        patterns = {
            'rules/clash-meta.yaml': r'^  - DOMAIN,([^,\n]+)$',
            'rules/shadowrocket.list': r'^DOMAIN,([^,\n]+)$',
            'examples/shadowrocket.conf': r'^DOMAIN,([^,\n]+),SiriAI$',
            'modules/siri-ai.module': r'^DOMAIN,([^,\n]+),PROXY$',
            'examples/clash-remote.yaml': r'^  - DOMAIN,([^,\n]+),SiriAI$',
        }
        for path, pattern in patterns.items():
            with self.subTest(path=path):
                self.assertEqual(re.findall(pattern, (ROOT / path).read_text(), re.M), self.domains)
        # 原离线 Mihomo 示例从同一 provider 引入，不能出现另一份 DOMAIN。
        offline = (ROOT / 'examples/clash-meta.yaml').read_text()
        self.assertIn('path: ./rules/clash-meta.yaml', offline)
        self.assertIn('RULE-SET,SiriAI,SiriAI', offline)

    def test_hashes_cover_all_generated_client_files(self):
        manifest = json.loads(self.outputs['install/assets.json'])
        self.assertEqual(set(manifest), set(self.outputs) - {'install/assets.json'})
        for path, sha in manifest.items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), sha)

    def test_new_asset_tampering_is_detected(self):
        for target in ('modules/siri-ai.module', 'examples/clash-remote.yaml', 'install/assets.json'):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source = {local: (ROOT / local).read_bytes() for local in rules.FILES.values()}
                source['source.lock.json'] = (ROOT / 'source.lock.json').read_bytes()
                rules.write_files(root, source | self.outputs)
                (root / target).write_bytes(b'altered\n')
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, '生成物漂移'):
                    rules.validate(root)

    def test_exact_rules_precede_broad_fallbacks_in_composed_fixture(self):
        # 脱敏组合样本验证精确域不会被 broad Apple/CDN/China/Global 抢先。
        exact = [('DOMAIN', d, 'SiriAI') for d in self.domains]
        suffixes = [('DOMAIN-SUFFIX', x, 'DIRECT') for x in ('apple.com', 'cloudflare.com', 'fastly-edge.com')]
        fixture = [('DOMAIN', 'blocked.example', 'REJECT')] + exact + suffixes + [('MATCH', '', 'DIRECT')]
        def route(domain):
            for kind, value, policy in fixture:
                if kind == 'MATCH' or (kind == 'DOMAIN' and value == domain) or (kind == 'DOMAIN-SUFFIX' and (domain == value or domain.endswith('.' + value))):
                    return policy
        for domain in self.domains:
            self.assertEqual(route(domain), 'SiriAI')
            self.assertEqual(route('other.' + domain), 'DIRECT')
        self.assertEqual(route('blocked.example'), 'REJECT')
        # 此样本不能证明 Shadowrocket 的模块排序或真实 UDP 转发。

    def test_local_markdown_and_html_links_and_anchors(self):
        paths = [ROOT / 'README.md', *ROOT.glob('docs/*.md'), *ROOT.glob('install/*.html')]
        for path in paths:
            text = path.read_text()
            links = re.findall(r'\]\(([^)]+)\)', text) if path.suffix == '.md' else []
            parser = Links()
            parser.feed(text)
            links += parser.targets
            for link in links:
                parsed = urlsplit(link)
                if parsed.scheme or parsed.netloc:
                    continue
                target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
                with self.subTest(source=path.name, link=link):
                    self.assertTrue(target.exists(), str(target))
                    if parsed.fragment and target.suffix in {'.md', '.html'}:
                        self.assertIn(unquote(parsed.fragment), anchors(target.read_text()))

    def test_install_pages_have_no_remote_code_or_permission_requests(self):
        for path in ROOT.glob('install/*.html'):
            text = path.read_text()
            self.assertNotRegex(text, r'<(?:script|iframe)[^>]+(?:src="https?://)')
            self.assertNotIn('http-equiv="Content-Security-Policy"', text)
        script = (ROOT / 'install/install.js').read_text()
        for forbidden in ('location.search', 'localStorage', 'sendBeacon', 'permissions.request', 'document.cookie'):
            self.assertNotIn(forbidden, script)


if __name__ == '__main__':
    unittest.main()
