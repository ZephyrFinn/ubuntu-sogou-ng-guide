#!/usr/bin/env python3
"""Apply an opt-in user-only profile; never run as root or restart processes."""
import argparse
import datetime
import getpass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

IM = "com.sogou.ime.ng.fcitx5.kylin"
REPO = Path(__file__).resolve().parents[1]


def update_section(text, section, settings):
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines)
                  if line.strip() == f"[{section}]"), None)
    if start is None:
        lines += [f"[{section}]"] + [f"{k} = {v}" for k, v in settings.items()]
        return "\n".join(lines) + "\n"
    end = next((i for i in range(start + 1, len(lines))
                if re.match(r"^\s*\[", lines[i])), len(lines))
    seen = set()
    for i in range(start + 1, end):
        match = re.match(r"^\s*([^;#=]+?)\s*=", lines[i])
        if match and match[1].strip() in settings:
            key = match[1].strip()
            lines[i] = f"{key} = {settings[key]}"
            seen.add(key)
    lines[end:end] = [f"{key} = {value}" for key, value in settings.items()
                      if key not in seen]
    return "\n".join(lines) + "\n"


def plan(home, settings, template):
    keyflow = home / f".config/cpis/module/im/fcitx5/{IM}/keyflow.ini"
    source = keyflow if keyflow.exists() else template
    if not source.exists():
        raise FileNotFoundError("未找到麒麟前端配置，请先安装并核对版本。")
    changes = [(keyflow, update_section(source.read_text(encoding="utf-8-sig"),
                                        "KEYFLOW_SETTING", settings))]
    for relative in [".config/cpis/sogou/env.ini", ".config/cpis/sogou/touch/env.ini"]:
        path = home / relative
        if path.exists():
            text = path.read_text(encoding="utf-8-sig")
            for key, value in [("QuanPin", "1"), ("ShuangPin", "0")]:
                text = re.sub(r"^" + key + r"\s*=.*$", key + "=" + value,
                              text, flags=re.M)
            changes.append((path, text))
    return changes


def call(service, method, *args):
    return subprocess.run(
        ["gdbus", "call", "--session", "--dest", f"com.cpis.{service}",
         "--object-path", f"/com/cpis/{service}",
         "--method", f"com.cpis.{service}.{method}", *args],
        capture_output=True, text=True, timeout=15)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="备份并写入用户配置")
    parser.add_argument("--live", action="store_true", help="同时更新当前用户 D-Bus 会话")
    args = parser.parse_args()
    if args.live and not args.apply:
        parser.error("--live 需要同时指定 --apply")
    if os.geteuid() == 0:
        parser.error("请用普通桌面用户运行，不要 sudo。")
    settings = json.loads((REPO / "config/comfort.json").read_text())
    if not 3 <= int(settings["pagesize"]) <= 9:
        parser.error("候选数必须在 3–9 之间")
    home = Path.home()
    template = Path(f"/opt/apps/com.cpis/etc/modules/im/fcitx5/{IM}/keyflow.ini")
    changes = plan(home, settings, template)
    for path, _ in changes:
        print("将更新:", path)
    print("设置:", json.dumps(settings, ensure_ascii=False, indent=2))
    if not args.apply:
        print("仅预览。确认后执行 --apply；实时更新另加 --live。")
        return
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = home / ".local/share/ubuntu-sogou-ng-guide/backups" / stamp
    backup.mkdir(parents=True)
    record = []
    for i, (path, text) in enumerate(changes):
        old = backup / f"{i}-{path.name}"
        existed = path.exists()
        if existed:
            shutil.copy2(path, old)
        record.append({"target": str(path), "existed": existed,
                       "backup": str(old) if existed else None})
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8-sig")
    (backup / "restore-map.json").write_text(json.dumps(record, indent=2))
    print("已写入。备份:", backup)
    if args.live:
        uid = f"{getpass.getuser()}#im.module=fcitx5|im.name={IM}"
        try:
            failures = []
            for key, value in settings.items():
                name = "config_" + key.replace(".", "_")
                result = call("panel", "RewriteEngineStat", uid, name, value, "true")
                check = call("panel", "AcquireEngineStat", uid, name)
                if result.returncode or check.returncode or repr(value) not in check.stdout:
                    failures.append(key)
            result = call("engine", "SetValues", uid,
                          "{'user.env:QuanPin':'1', 'user.env:ShuangPin':'0'}")
            if result.returncode or "[0" not in result.stdout:
                failures.append("底层全拼状态")
            if failures:
                print("未确认实时生效:", ", ".join(failures))
                print("文件已保存；重新登录后验证，不要因此清空词库。")
            else:
                print("实时状态已读回。请实际测试 nihk、Shift、标点和候选窗。")
        except (OSError, subprocess.TimeoutExpired) as exc:
            print("实时接口不可用:", exc)
            print("文件已保存；保存工作后重新登录并验证。")


if __name__ == "__main__":
    main()
