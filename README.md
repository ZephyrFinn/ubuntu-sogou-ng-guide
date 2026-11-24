# Ubuntu 26.04 搜狗 NG：安装、配置与排错记录

这是一台 Ubuntu 26.04.1 / GNOME / Wayland / amd64 电脑的实际排错记录，以及从中整理出的配置工具。**不是搜狗官方 Ubuntu 适配包，也不保证其他机器可用。**

最终用户反馈：麒麟前端能够输入中文；修复了小鹤双拼被重复转换的问题。引擎独立测试能产生中文候选。此前出现过多屏底部候选窗越界、微信候选窗不显示；**新版是否完全解决这些位置问题，尚未完成验证。**

## 最终采用的组件

| 组件 | 验证时安装的版本 |
| --- | --- |
| `com.sogou.ime.ng.fcitx5.kylin` | `10.0.10.0-1418` |
| `sogou-ime-ng` | `10.0.10.0-1418` |
| `cpis-base` | `10.0.10.0-2291-deb11u1` |
| `cpis-engine-plugin-libime-v3-{common,pinyin26,wubi}` | `10.0.10.0-114` |
| 配套搜狗词库、默认配置 | `10.0.2-3` |

记录日期：2026-11-24。完整来源、版本和 SHA-256 在 [packages.lock.json](packages.lock.json)。这份锁定清单用于复核当时的下载内容，不代表厂商的支持或再分发许可。

## 配置是怎样工作的？

```text
应用程序
  → Fcitx5
  → 搜狗 NG 麒麟前端 / CPIS keyflow
      小鹤 nihk → 全拼 nihao
  → CPIS 拼音引擎（底层双拼关闭）
      nihao → 你好等候选
  → 搜狗自己的候选面板 → 用户选词上屏
```

前端配置主要位于：

```text
~/.config/cpis/module/im/fcitx5/com.sogou.ime.ng.fcitx5.kylin/keyflow.ini
```

底层旧式拼音设置可能位于：

```text
~/.config/cpis/sogou/touch/env.ini
~/.config/cpis/sogou/env.ini
```

**前端与底层同时打开双拼，会重复解码。** 本机的典型症状是输入 `nihk` 出现“你哈哦”。需要保留前端小鹤，底层采用 `QuanPin=1`、`ShuangPin=0`，不是把小鹤整体关闭。

## 开始使用

1. 先看 [安装指南](docs/INSTALL.md)，确认系统、架构、来源和依赖。
2. 只读检查现有环境：

   ```bash
   python3 scripts/check-environment.py
   ```

3. 查看舒适输入方案将做的修改（默认不写文件）：

   ```bash
   python3 scripts/configure.py
   ```

4. 确认后写入用户配置；旧文件会自动备份。关闭搜狗属性设置窗口后执行，避免其关闭时覆盖配置：

   ```bash
   python3 scripts/configure.py --apply --live
   ```

工具不会安装软件、删除词库、修改 `/etc`、结束进程或操作真实机器人。`--live` 通过当前用户会话的 D-Bus 更新已运行的搜狗设置；如果会话接口不可用，文件仍已写入，需在保存工作后重新登录并验证。

## 舒适输入方案

- 小鹤双拼，前端解码一次；显示双拼展开提示。
- Shift 切中英文；默认中文、简体、半角、中文标点。
- 横排候选：沿用当前已验证的 `SogouClassic` 布局；每页 5 项。
- 数字键盘半角；数字后的标点智能处理。
- 关闭标点自动配对，避免额外补入成对符号。
- 候选窗跟随光标；保留当前字号和 DPI 设置。
- 不修改 Fcitx5 全局快捷键。请确认 Fcitx5 自己没有同时绑定单独 Shift。

这个方案是可选的习惯配置，不是客观的“最佳设置”。可编辑 [config/comfort.json](config/comfort.json) 调整标点、候选数量等。

发布前再次读取本机配置时，每页候选为 5、候选和组合字号均为 14、DPI 感知开启；双拼展开提示已被关闭，符号按钮和简繁按钮也被隐藏。上述界面微调与脚本的推荐预设可能不同，不影响“小鹤前端 + 全拼底层”这一修复。仓库没有直接复制整个私人配置目录。

## 修复了什么，哪些还没验证？

| 问题 | 实际证据与状态 |
| --- | --- |
| Deepin 前端 `Engine not initialized` | 同一运行库和拼音插件的隔离测试：Deepin 原始授权目录返回 `-99`；麒麟包原始授权目录初始化成功并返回中文候选。最终换用完整麒麟前端包，未修改签名或伪装系统。 |
| 更换安装包后仍有旧引擎 | 旧进程继续持有 D-Bus 服务；清理已核实的旧进程后，由 `/opt/apps/com.cpis/bin/` 下的新版接管。 |
| 小鹤 `nihk` → “你哈哦” | 前端和底层双拼都打开；隔离对照关闭底层后，`nihao` 的候选由“你哈哦”变为“你好”。 |
| 候选窗越界、微信中不显示 | 旧版观察到了问题；一次性移动窗口没有持续解决。新版、多屏缩放和微信尚需继续实际验证。 |

详见 [完整排错过程](docs/DEBUGGING.md)。

## 能改皮肤吗？

可以调整部分外观，但它使用 CPIS 自己的 XML 皮肤，**Fcitx5 通用主题不一定作用于搜狗候选窗**。当前皮肤为 `SogouClassic`；字号等有独立设置，整套皮肤切换需要额外验证。仓库不附带厂商皮肤文件。参见 [外观与皮肤](docs/APPEARANCE.md)。

## 数据与授权

本仓库只提供自写配置工具、脱敏说明和来源清单，不包含搜狗/CPIS 闭源二进制、签名授权文件、厂商皮肤、个人词库、聊天内容或原始日志。下载和使用上游软件时应阅读其许可。包内容 SHA-256 一致只说明与记录内容一致，不等于验证了来源身份或完整安全性。

自写脚本和文档以 [MIT](LICENSE) 发布；上游软件不受本仓库许可证覆盖。

## 原始参考

- [搜狗 Linux 官方下载入口](https://shurufa.sogou.com/linux)
- [CPIS 开发方软件仓库](http://repo.taotics.com/cross-platform-input-solution/)
- [最初试用的 Ubuntu 26.04 社区打包项目](https://github.com/sunxfancy/sogou-ng-fcitx5-ubuntu)
- [Deepin Next 发布及适配范围说明](https://bbs.deepin.org.cn/en/post/274902)
- [Deepin 社区 NG 配置经验](https://bbs.deepin.org.cn/en/post/274595)
