#!/usr/bin/env python3
"""List pinned upstream files, or explicitly download them. Never installs."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("packages"))
    args = parser.parse_args()
    lock = Path(__file__).resolve().parents[1] / "packages.lock.json"
    records = json.loads(lock.read_text())["packages"]
    print("来源包含厂商 HTTP 仓库；记录的 SHA-256 不是签名验证。")
    print("仅下载您有权使用的软件；本工具不安装、不添加源、不修改授权文件。")
    for item in records:
        print(item["package"], item["version"], item["url"])
    if not args.download:
        print("仅列出清单。阅读 docs/INSTALL.md 后，显式指定 --download 才下载。")
        return
    args.output.mkdir(parents=True, exist_ok=True)
    for item in records:
        path = args.output / item["url"].rsplit("/", 1)[-1]
        if path.exists():
            if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                raise SystemExit(f"已有文件校验失败，未覆盖: {path}")
            print("已有且校验通过:", path.name)
            continue
        with urllib.request.urlopen(item["url"], timeout=90) as response:
            data = response.read()
        if len(data) != item["size"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise SystemExit(f"下载内容校验失败，未写入: {path.name}")
        with path.open("xb") as target:
            target.write(data)
        print("下载并校验通过:", path.name)


if __name__ == "__main__":
    main()
