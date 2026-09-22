"""验证来源版本、生成漂移与拒绝不完整数据的行为。"""
# SPDX-License-Identifier: GPL-2.0-only
import contextlib
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("routekit_rules", Path(__file__).resolve().parents[1] / "scripts/rules.py")
rules = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rules)


class SourceContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        self.output = self.base / "output"
        self.source.mkdir()
        self.output.mkdir()
        self.data = rules.read_local(rules.ROOT)
        self.run_git("init", "-q")
        self.run_git("remote", "add", "origin", rules.SOURCE_URL)
        rules.write_files(self.source, self.data)
        self.commit_source()
        with contextlib.redirect_stdout(io.StringIO()):
            rules.import_source(self.output, self.source)

    def run_git(self, *args):
        subprocess.run(["git", "-C", str(self.source), *args], check=True, capture_output=True)

    def commit_source(self):
        self.run_git("add", "rules", "research")
        self.run_git("-c", "user.name=测试样本", "-c", "user.email=test@example.invalid",
                     "commit", "-qm", "固定公开测试样本")

    def test_committed_source_roundtrip(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            rules.validate(self.output, self.source)
        self.assertIn("未联网检查", output.getvalue())
        lock = json.loads((self.output / "source.lock.json").read_text())
        self.assertEqual(len(lock["commit"]), 40)
        self.assertEqual(len(lock["files"]), 3)

    def test_local_only_is_not_latest_claim(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            rules.validate(self.output)
        self.assertIn("未检查源仓库当前 HEAD", output.getvalue())

    def test_reject_dirty_source(self):
        path = self.source / "rules/siri-ai-domains.txt"
        path.write_bytes(path.read_bytes() + b"unapproved.example.com\n")
        with self.assertRaisesRegex(ValueError, "未提交修改"):
            rules.import_source(self.output, self.source)

    def test_reject_wrong_origin_without_exposing_it(self):
        self.run_git("remote", "set-url", "origin", "https://invalid.example/source.git")
        with self.assertRaisesRegex(ValueError, "公开源身份不匹配"):
            rules.validate(self.output, self.source)

    def test_detect_new_committed_source(self):
        path = self.source / "rules/siri-ai-provenance.json"
        content = json.loads(path.read_text())
        content[0]["notes"] += " 测试：上游证据发生变化。"
        path.write_text(json.dumps(content, ensure_ascii=False) + "\n")
        self.commit_source()
        with self.assertRaisesRegex(ValueError, "当前 HEAD 的规则已变化"):
            rules.validate(self.output, self.source)

    def test_reject_generated_drift(self):
        path = self.output / "examples/shadowrocket.conf"
        path.write_text(path.read_text().replace(",SiriAI\n", ",DIRECT\n"))
        with self.assertRaisesRegex(ValueError, "生成物漂移"):
            rules.validate(self.output)

    def test_reject_canonical_tamper_by_hash(self):
        path = self.output / "rules/provenance.json"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "锁文件校验失败"):
            rules.validate(self.output)

    def test_reject_duplicate_and_wildcard(self):
        data = dict(self.data)
        raw = data["rules/siri-ai-domains.txt"]
        data["rules/siri-ai-domains.txt"] = raw + raw.splitlines()[0] + b"\n"
        with self.assertRaisesRegex(ValueError, "重复域名"):
            rules.validate_data(data)
        data["rules/siri-ai-domains.txt"] = b"*.apple.com\n"
        with self.assertRaisesRegex(ValueError, "只接受小写精确域名"):
            rules.validate_data(data)

    def test_reject_unverified_provenance(self):
        data = dict(self.data)
        provenance = json.loads(data["rules/siri-ai-provenance.json"])
        provenance.pop()
        data["rules/siri-ai-provenance.json"] = json.dumps(provenance).encode()
        with self.assertRaisesRegex(ValueError, "来源记录必须逐域对应"):
            rules.validate_data(data)


if __name__ == "__main__":
    unittest.main()
