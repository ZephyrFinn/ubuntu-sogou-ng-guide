#!/usr/bin/env python3
"""Read-only summary; does not print input history, environment secrets or logs."""
from pathlib import Path
import os
import subprocess


def run(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=10)
        return (result.stdout or result.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return str(exc)


print("Session:", os.environ.get("XDG_SESSION_TYPE", "unknown"))
print("Desktop:", os.environ.get("XDG_CURRENT_DESKTOP", "unknown"))
print(run(["uname", "-m"]))
print(run(["dpkg-query", "-W", "-f=${binary:Package}\t${Version}\t${db:Status-Abbrev}\n",
           "cpis-base", "sogou-ime-ng", "com.sogou.ime.ng.fcitx5.kylin",
           "com.sogou.ime.ng.fcitx5.deepin", "cpis-engine-plugin-libime-v3-pinyin26"]))
print("Current IM:", run(["fcitx5-remote", "-n"]))
keyflow = Path.home() / ".config/cpis/module/im/fcitx5/com.sogou.ime.ng.fcitx5.kylin/keyflow.ini"
if keyflow.exists():
    for line in keyflow.read_text(encoding="utf-8-sig").splitlines():
        if line.strip().startswith(("shuangpin_", "pagesize", "encn", "default.mode",
                                    "default.fullshape", "default.tradition")):
            print(line)
for path in [Path.home()/".config/cpis/sogou/env.ini",
             Path.home()/".config/cpis/sogou/touch/env.ini"]:
    if path.exists():
        print(path.relative_to(Path.home()))
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.startswith(("QuanPin=", "ShuangPin=", "ShuangPinName=")):
                print(" ", line)
