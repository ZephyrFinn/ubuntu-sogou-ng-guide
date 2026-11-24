# 安装与恢复

## 适用范围

实际验证环境是 Ubuntu 26.04.1、amd64、GNOME、Wayland，使用原生 Fcitx5。没有验证 ARM、其他发行版、所有 Qt/GTK 应用或所有显示器组合。

原来测试的 `sogou-ime-ng-fcitx5-ubuntu` 是社区整合的 openKylin 旧组件。本指南最终采用的却是开发方的 `com.sogou.ime.ng.fcitx5.kylin` 前端和配套新版组件。**名字里都带“搜狗 NG”，不代表是同一套包。**

## 来源与下载

锁定清单包括 13 个包，来自 CPIS 开发方公开仓库：

- `senbena-deb11u1 / utils`：CPIS 运行库；
- `senbena-dailybuild / utils`：麒麟前端、搜狗主程序和 v3 插件；
- `senbena / utils`：词库与默认配置。

这里包含 dailybuild 来源，不能把它宣传为官方 Ubuntu 稳定发布。仓库当前仅提供 HTTP 下载；本指南记录的哈希可检查文件是否与当时版本一致，**不能替代签名验证或证明 HTTP 传输未被攻击**。不接受这个来源条件时，请不要执行下载和安装。没有将整个厂商源添加到 APT，也没有执行其在线安装脚本。

先列出文件，再明确选择是否下载（约百 MB；以清单 size 合计为准）：

```bash
python3 scripts/fetch-packages.py
python3 scripts/fetch-packages.py --download
```

不会自动安装。上游可能下架旧文件；此时停止，不要用名字相似的未知镜像或任意版本混装。

## 检查安装脚本

厂商前端的安装脚本会重启 CPIS 后端。默认配置包的安装脚本还可能调整默认用户目录权限。本次实机首次安装时，对这两份脚本做过本地处理：

- 去掉前端 `postinst` 中的 `killall` 行；
- 去掉默认配置包 `postinst` 中放宽用户目录写权限的操作。

因此，本指南**不提供直接自动安装的命令链**。先用 `dpkg-deb -e` 检查下载包的维护脚本，再按自己的环境决定。不要通过忽略依赖、修改系统身份、修改签名授权文件来强行运行。

用于查看包信息的例子：

```bash
dpkg-deb -I packages/com.sogou.ime.ng.fcitx5.kylin_10.0.10.0-1418_amd64.deb
dpkg-deb -e packages/com.sogou.ime.ng.fcitx5.kylin_10.0.10.0-1418_amd64.deb /tmp/sogou-frontend-control
cat /tmp/sogou-frontend-control/postinst
```

## 模拟安装，再决定是否安装

全新环境先模拟完整包集合：

```bash
apt-get -s install ./packages/*.deb
```

若已经安装了本指南排查过的社区整合包，模拟替换时显式指定旧包名：

```bash
apt-get -s install ./packages/*.deb sogou-ime-ng-fcitx5-ubuntu-
```

若已采用同版 CPIS 和搜狗主程序，只需要替换 Deepin 前端，本机实际通过的模拟是：

```bash
apt-get -s install ./packages/com.sogou.ime.ng.fcitx5.kylin_10.0.10.0-1418_amd64.deb com.sogou.ime.ng.fcitx5.deepin-
```

尾部 `-` 是 APT 指定移除该包的语法。审查输出，确认只涉及预期软件包；不要清除 `fcitx5*` 或运行通配符 purge。完成备份、审核维护脚本后，才由操作者将对应模拟命令的 `apt-get -s` 换成 `sudo apt install`。不要把不同文件集合放进同一个目录后盲目通配符安装。

## Fcitx5 配置

1. 保存工作后注销并重新登录，或按本机的服务管理方式完整重载 CPIS 和 Fcitx5。仅替换安装包不会自动证明旧进程已退出。
2. 打开 Fcitx5 配置，保留“键盘－英语（美国）”和备用输入法。
3. 添加“搜狗输入法 Next 麒麟版”；删除列表中已经卸载的 Deepin 前端条目。
4. 选择搜狗，实际测试中文候选、空格选词、Shift 切换和多个应用。
5. 需要本仓库的小鹤方案时，再执行 `python3 scripts/configure.py --apply --live`。

本机保留了 Rime。Fcitx5 主进程有响应、状态栏出现、API 返回成功，都不能单独证明实际中文输入正常。

## 确认没有旧引擎占用服务

```bash
pgrep -af cpis-engine-service
gdbus call --session --dest org.freedesktop.DBus \
  --object-path /org/freedesktop/DBus \
  --method org.freedesktop.DBus.GetConnectionUnixProcessID com.cpis.engine
```

新版预期从 `/opt/apps/com.cpis/bin/` 启动。早期整合包从 `/usr/bin/` 启动。如果旧可执行文件已经删除而进程还活着，它仍可能占用 D-Bus 名称。本机是核对完整命令行后，只向已确认的旧 PID 发送正常退出信号，没有按模糊名称批量杀进程。

## 恢复用户配置

配置工具把修改前的文件备份到：

```text
~/.local/share/ubuntu-sogou-ng-guide/backups/<时间>/
```

`restore-map.json` 记录每个文件的原目标和备份路径。关闭搜狗属性设置后，按映射将对应备份复制回去，重新登录并检查。某文件原先不存在时，映射会明确记录 `existed: false`；不要把不存在的备份当成有效空文件覆盖。

用户词库不在工具修改范围内。不需要通过删除 `~/.config/cpis`、`~/.sogouinput` 或整套 Fcitx5 来恢复设置。
