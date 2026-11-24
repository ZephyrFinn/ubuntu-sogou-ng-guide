# 外观与皮肤

## 使用哪一层主题？

本指南的搜狗 NG 使用 CPIS 自己的候选面板。它不等同于 Fcitx5 自带的 Classic UI；给 Fcitx5 安装普通主题，不能保证改变搜狗候选窗。

本机的面板 ini 为：

```text
/opt/apps/com.cpis/etc/modules/im/fcitx5/com.sogou.ime.ng.fcitx5.kylin/isp.ini
```

其当前配置：

```ini
[skin.Default]
skinfolder=/opt/apps/com.cpis/etc/resources/skin/
skinname=SogouClassic
```

安装包附带 `Default` 和 `SogouClassic` 两个皮肤目录。本机沿用 `SogouClassic`，没有在发布前验证切换到其他皮肤的完整显示效果。

## 优先通过设置调整

优先在搜狗自己的属性设置中调整候选数量、字号和 DPI；每次只改一项，实际检查再保留。部分外观页面可能只是保留的界面，按钮是否实现要看版本，不要只凭选项存在就认定有效。

本机可读到的前端配置包括：

```ini
[KEYFLOW_SETTING]
pagesize = 5
pcstyle_cands_size = 14
pcstyle_comps_size = 14
dpi_awareness = true
pc_composition_wnd_follow_cursor = true
```

`pagesize` 为每页候选数；两个 size 值分别对应候选文字和组合文字。仓库舒适方案保留当前字号，不强制写死为更大或更小。高分屏上相同数字的实际视觉大小可能不同。

前端 ini 的运行时设置名通常带 `config_` 前缀，例如 `config_pcstyle_cands_size`。本机通过 `AcquireEngineStat` / `RewriteEngineStat` 操作，配合持久文件配置；并不是把 `config_` 前缀原样写进 ini。

## 自定义 XML 皮肤：可行，但需要单独验证

通常涉及以下文件：

```text
/opt/apps/com.cpis/etc/resources/skin/SogouClassic/global.xml
/opt/apps/com.cpis/etc/resources/skin/SogouClassic/window_pc_composition.xml
```

这些 XML 描述颜色、字体、边框、留白和候选布局。要做自定义皮肤，建议在自己机器上复制一份安装包自带皮肤到独立目录，再修改副本；不要直接覆盖厂商原目录。之后需要在面板配置的 `[skin.Default]` 指向副本，并重新加载面板。

**这个版本是否支持通过用户目录的 isp.ini 覆盖系统皮肤路径，尚未完成验证。** 不要把复制到 `~/.config/fcitx5/themes/` 当成已验证方法。若只能改系统面板配置，需要操作者明确决定、先备份，且软件更新可能覆盖该设置。

本仓库不执行皮肤替换、不提供未验证的自动主题安装器，也不分发厂商 XML、图片或字体。可以另做原创配色/布局修改工具，但仍需在自己的屏幕、微信和底部输入区域检查显示效果。

## 不要用皮肤掩盖定位问题

缩小字号可能让越界不明显，但不等于修复坐标处理。候选窗跟随光标与“靠近底部自动向上避让”也不是同一功能。多屏、缩放和微信位置问题应单独验证。

参考：[Deepin 社区的 NG 字号与皮肤配置经验](https://bbs.deepin.org.cn/en/post/274595)。该记录含多个历史版本，路径和能力不能不加检查地照搬。
