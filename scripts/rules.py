#!/usr/bin/env python3
"""从已提交的公开源导入规则，生成并验证本项目采用的配置子集。"""
# SPDX-License-Identifier: GPL-2.0-only
# Copyright (C) 2026 SiriAI-RouteKit contributors
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://github.com/BrownieCoder/proxy-rulesets"
FILES = {
    "rules/siri-ai-domains.txt": "rules/domains.txt",
    "rules/siri-ai-provenance.json": "rules/provenance.json",
    "research/SiriAI-audit.json": "research/domain-audit.json",
}
FIELDS = {"domain", "source", "evidence_type", "user_provided_status",
          "verified_date", "first_observed", "purpose", "confidence", "notes", "target_policy"}
DOMAIN = re.compile(r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(source, *args):
    result = subprocess.run(["git", "-C", str(source), *args], capture_output=True)
    require(result.returncode == 0, "无法读取公开源 Git 元数据或已提交文件；未输出可能含私有值的 stderr")
    return result.stdout


def source_snapshot(source):
    """只读取白名单内三个公开文件及来源标识，不遍历配置目录。"""
    origin = git(source, "config", "--get", "remote.origin.url").decode().strip()
    require(origin in {SOURCE_URL, SOURCE_URL + ".git",
                       "git@github.com:BrownieCoder/proxy-rulesets.git",
                       "ssh://git@github.com/BrownieCoder/proxy-rulesets.git"},
            "公开源身份不匹配：要求 BrownieCoder/proxy-rulesets")
    head = git(source, "rev-parse", "HEAD").decode().strip()
    require(re.fullmatch(r"[a-f0-9]{40}", head), "源 HEAD 不是完整 Git SHA-1")
    data = {name: git(source, "show", f"{head}:{name}") for name in FILES}
    for name, expected in data.items():
        candidate = source / name
        require(not candidate.is_symlink(), f"源文件不能是符号链接：{name}")
        require(candidate.read_bytes() == expected, f"源文件存在未提交修改：{name}")
    return head, data


def validate_data(data):
    raw = data["rules/siri-ai-domains.txt"].decode("utf-8")
    domains = raw.splitlines()
    require(bool(domains), "规则集不能为空")
    require(raw == "\n".join(domains) + "\n", "域名源必须使用 LF 并有末尾换行")
    require(len(domains) == len(set(domains)), "存在重复域名")
    require(domains == sorted(domains), "域名必须按字母排序")
    require(all(DOMAIN.fullmatch(d) for d in domains), "只接受小写精确域名；禁止通配符、规则前缀或空行")
    provenance = json.loads(data["rules/siri-ai-provenance.json"])
    require(isinstance(provenance, list), "来源记录必须是列表")
    require(all(isinstance(p, dict) and FIELDS <= p.keys() for p in provenance), "来源记录字段不完整")
    require(sorted(p["domain"] for p in provenance) == domains, "来源记录必须逐域对应且不重复")
    for p in provenance:
        require(isinstance(p["source"], str) and p["source"].startswith("https://support.apple.com/"), "正式域名须有 Apple Support 来源")
        require(re.fullmatch(r"\d{4}-\d{2}-\d{2}", p["verified_date"]), "核验日期格式无效")
        require(all(p[field] for field in ("evidence_type", "purpose", "confidence", "target_policy")), "来源记录不得缺少用途、置信度或策略")
    audit = json.loads(data["research/SiriAI-audit.json"])
    require(isinstance(audit, list) and len(audit) == 18, "应完整保留本次 18 条用户候选审计")
    require(all(isinstance(p, dict) and p.get("status") in {"ACCEPTED", "CANDIDATE", "REJECTED"} for p in audit), "审计状态无效")
    accepted = [p["domain"] for p in audit if p["status"] == "ACCEPTED"]
    require(sorted(accepted) == domains, "正式域名与审计接纳项不一致")
    require(all(p.get("production_rule_type") == "DOMAIN" for p in audit if p["status"] == "ACCEPTED"), "正式规则只允许 DOMAIN")
    return domains


def generated(domains):
    rule_lines = "\n".join(f"DOMAIN,{d}" for d in domains)
    provider = "# 自动生成；修改须回到唯一源仓库。\npayload:\n" + "".join(f"  - DOMAIN,{d}\n" for d in domains)
    shadow = "# 自动生成的规则集；导入 [Rule] 时需补充目标策略。\n" + rule_lines + "\n"
    shadow_example = ("# 自动生成；仅演示。未匹配流量全部直连，不要覆盖日常配置。\n"
                      "# 先在首页选择已有可用节点。无需证书、解密或订阅内容。\n"
                      "[General]\n\n[Proxy Group]\nSiriAI = select,PROXY\n\n[Rule]\n"
                      + "".join(f"DOMAIN,{d},SiriAI\n" for d in domains) + "FINAL,DIRECT\n")
    mihomo = """# 自动生成；本文件是无节点演示，不应覆盖日常配置。
# REJECT 是未配置出口时的显式阻断；先按教程关联已有策略或节点。
# 将 rules/clash-meta.yaml 放入内核 HomeDir 下对应相对路径。
mode: rule
proxy-groups:
  - name: SiriAI
    type: select
    proxies:
      - REJECT
rule-providers:
  SiriAI:
    type: file
    behavior: classical
    format: yaml
    path: ./rules/clash-meta.yaml
rules:
  - RULE-SET,SiriAI,SiriAI
  - MATCH,DIRECT
"""
    return {"rules/clash-meta.yaml": provider.encode(),
            "rules/shadowrocket.list": shadow.encode(),
            "examples/shadowrocket.conf": shadow_example.encode(),
            "examples/clash-meta.yaml": mihomo.encode()}


def write_files(root, files):
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def read_local(root):
    return {source: (root / local).read_bytes() for source, local in FILES.items()}


def validate_lock(root, data):
    lock = json.loads((root / "source.lock.json").read_text())
    require(lock.get("source_url") == SOURCE_URL, "锁文件源身份不匹配")
    require(lock.get("license") == "GPL-2.0-only", "锁文件许可证不匹配")
    require(re.fullmatch(r"[a-f0-9]{40}", lock.get("commit", "")), "锁文件缺少真实完整提交号")
    require(set(lock.get("files", {})) == set(FILES), "锁文件白名单不匹配")
    for name, local in FILES.items():
        require(lock["files"][name] == {"local": local, "sha256": digest(data[name])}, f"锁文件校验失败：{local}")
    return lock


def validate(root, source=None):
    data = read_local(root)
    domains = validate_data(data)
    lock = validate_lock(root, data)
    for name, content in generated(domains).items():
        require((root / name).read_bytes() == content, f"生成物漂移：{name}；运行 generate 后审查 diff")
    # 对当前生成子集核对实际字段关系；不假装是通用客户端解析器。
    sample = (root / "examples/shadowrocket.conf").read_text()
    groups = set(re.findall(r"^(\w+) = select,PROXY$", sample, re.M)) | {"DIRECT", "PROXY", "REJECT"}
    for domain, target in re.findall(r"^DOMAIN,([^,]+),([^,\n]+)$", sample, re.M):
        require(domain in domains and target in groups, "Shadowrocket 域名或策略引用无效")
    config = (root / "examples/clash-meta.yaml").read_text()
    providers = set(re.findall(r"^  (\w+):$", config, re.M))
    policies = set(re.findall(r"^  - name: (\w+)$", config, re.M)) | {"DIRECT", "REJECT"}
    for provider, target in re.findall(r"^  - RULE-SET,([^,]+),([^,\n]+)$", config, re.M):
        require(provider in providers and target in policies, "Mihomo provider 或策略引用无效")
    require(config.index("RULE-SET,SiriAI,SiriAI") < config.index("MATCH,DIRECT"), "Mihomo 顺序无效")
    if source:
        head, latest = source_snapshot(source)
        for name in FILES:
            pinned = git(source, "show", f"{lock['commit']}:{name}")
            require(pinned == data[name], f"锁定提交内容不同：{name}")
            require(latest[name] == data[name], f"指定源当前 HEAD 的规则已变化：{name}；请审查后重新导入")
        print(f"已核对指定本地源当前 HEAD：{head}；未联网检查远程最新版本")
    else:
        print("仅校验本地锁定版本；未检查源仓库当前 HEAD 或远程最新版本")
    print(f"通过：{len(domains)} 个精确域，来源/审计/生成物/示例引用一致；客户端未实测")


def import_source(root, source):
    head, data = source_snapshot(source)
    domains = validate_data(data)
    lock = {"source_url": SOURCE_URL, "commit": head, "license": "GPL-2.0-only",
            "files": {name: {"local": local, "sha256": digest(data[name])} for name, local in FILES.items()}}
    outputs = {FILES[name]: content for name, content in data.items()}
    outputs["source.lock.json"] = (json.dumps(lock, indent=2, ensure_ascii=False) + "\n").encode()
    outputs.update(generated(domains))
    write_files(root, outputs)
    validate(root, source)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["import", "generate", "validate"])
    parser.add_argument("--source", type=Path, help="公开 proxy-rulesets checkout；不读取私人配置")
    args = parser.parse_args()
    try:
        if args.command == "import":
            require(args.source is not None, "import 必须明确指定 --source")
            import_source(ROOT, args.source.resolve())
        elif args.command == "generate":
            require(args.source is None, "generate 不读取外部源；使用 import --source 更新")
            data = read_local(ROOT)
            domains = validate_data(data)
            validate_lock(ROOT, data)
            write_files(ROOT, generated(domains))
            validate(ROOT)
        else:
            validate(ROOT, args.source.resolve() if args.source else None)
    except (ValueError, OSError, KeyError, TypeError, UnicodeError) as error:
        print(f"验证失败：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
