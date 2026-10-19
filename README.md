# DeepSeek-Harness-Android

**把官方 DeepSeek Harness 完整搬进 Android 手机 —— 非官方移植**

[![Latest Release](https://img.shields.io/github/v/release/TaoQiYiYi/DeepSeek-Harness-Android?label=%E6%9C%80%E6%96%B0%E7%89%88)](https://github.com/TaoQiYiYi/DeepSeek-Harness-Android/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/TaoQiYiYi/DeepSeek-Harness-Android/total?label=%E4%B8%8B%E8%BD%BD)](https://github.com/TaoQiYiYi/DeepSeek-Harness-Android/releases)
[![Platform](https://img.shields.io/badge/Android-8.0%2B%20%7C%20arm64-3DDC84?logo=android&logoColor=white)](#运行要求)
[![License](https://img.shields.io/github/license/TaoQiYiYi/DeepSeek-Harness-Android)](LICENSE)

---

## 📥 下载

| 版本 | 类型 | 说明 |
| :--- | :--- | :--- |
| **[v0.2.2](https://github.com/TaoQiYiYi/DeepSeek-Harness-Android/releases/latest)** | ✅ 正式版 | **推荐**。内核 0.2.1-rc.1，首次启动需重新解压运行时 1–3 分钟 |
| [v0.2.2-rc.3](https://github.com/TaoQiYiYi/DeepSeek-Harness-Android/releases/tag/DeepSeek-Harness-Android-0.2.2rc3) | 🧪 预览版 | 安卓 UI 全面独立成页 |
| [全部版本](https://github.com/TaoQiYiYi/DeepSeek-Harness-Android/releases) | 📦 历史 | 含 0.2.0 / 0.2.1 及各预览版 |

> 覆盖安装即可升级，**会话与配置全部保留**（签名一致）。

---

## 🎉 这是什么

DSHPort 不是重写，也不是套壳：它直接运行官方发布的 `@deepseek-ai/dsh` 引擎包，搭配为 Android 定制的 arm64 Node.js 运行时、常驻前台服务与 WebView 外壳，把桌面端完整的 Agent 体验——聊天会话、工具调用、插件系统、本地工作区——原样带到手机上。

安装一个 APK 即用，**无需 root，无需 Termux**。

> 引擎全程在设备本地运行（`127.0.0.1` + 一次性 token 鉴权），数据不出手机；使用需自备 DeepSeek API Key。

---

## ✨ 特性

- **一个 APK 开箱即用** —— 内置 Node.js 运行时与 pnpm，插件安装无需额外配置
- **完整的 Agent 体验** —— 聊天会话、工具调用、插件系统、本地工作区全部可用
- **手机界面原生级适配** —— 对话页 / 会话选择页 / 主页独立成页，返回键分级处理
- **应用内更新** —— 设置 →「获取更新」，自动检查 GitHub Releases 并一键安装
- **运行日志** —— 设置 →「日志」，查看 / 一键复制，便于反馈问题
- **手机目录可作为工作区** —— 存储权限引导，目录选择器直接打开「手机存储」

---

## 🧩 为 Android 做了哪些适配

官方 dsh 没有移动端目标，本项目针对平台差异做了必要的兼容处理（均为小改动 + 失败回退，不影响桌面端原有行为）：

| 差异点 | 处理方式 |
| :--- | :--- |
| **Node 原生模块** | 没有 Android 预编译的模块降级为纯 JS 实现（基于官方 `--expose-internals` 运行模式） |
| **文件系统** | Android 应用域禁止硬链接 → 会话 / 附件存储自动降级为 `rename` / `copyFile` |
| **插件系统** | 内置 pnpm，插件安装开箱即用 |
| **移动端 UI** | 设置面板、会话侧栏针对小屏重新适配；手机宽度 ≤ 720px 时页面独立化 |
| **桌面专属功能** | 「打开配置文件」等改为 Android 通道（调起系统文本编辑器） |

---

## 📱 运行要求

| 项目 | 要求 |
| :--- | :--- |
| 系统 | Android 8.0+（minSdk 26） |
| 架构 | **arm64**（不支持 32 位 / x86） |
| 网络 | 首次启动需联网解压运行时 |
| API Key | 自备 DeepSeek API Key（设置 → 模型） |

---

## 🚀 安装

1. 从 [Releases](https://github.com/TaoQiYiYi/DeepSeek-Harness-Android/releases/latest) 下载最新 APK。
2. 允许「安装未知来源应用」后安装。
3. 首次启动会解压运行时（**约 1–3 分钟，有进度提示**），仅一次。
4. 进入 设置 → 模型，填入自己的 DeepSeek API Key。

---

## ❓ 常见问题

<details>
<summary><b>首次启动卡在解压界面很久？</b></summary>

首次启动需要把内置运行时解压到应用私有目录，视手机性能约 1–3 分钟，有进度提示，属正常现象。之后启动秒开。
</details>

<details>
<summary><b>界面白屏 / 显示异常？</b></summary>

多半是第三方移动端适配插件（如 `dsh-web-mobile`）冲突。页面加载约 6.5 秒仍无内容时会自动弹出「页面渲染异常」：

- **重载** —— 再试一次
- **禁用插件重载** —— 临时移开插件并重启引擎（下次打开自动还原）
- **忽略** —— 不做处理

界面恢复后，到 设置 → 插件 停用可疑插件即可。
</details>

<details>
<summary><b>升级后提示找不到模块 / 引擎启动失败？</b></summary>

请确认安装的是最新版本。v0.2.2（build 46–50）已修复「覆盖安装后旧运行时残留符号链接导致引擎启动失败」的问题。
</details>

<details>
<summary><b>旧版本的会话和配置还在吗？</b></summary>

在。签名一致，直接覆盖安装即可，会话、工作区与配置全部沿用；v0.2.2 升级内核后老会话同样兼容。
</details>

<details>
<summary><b>怎么反馈问题？</b></summary>

设置 →「日志」→ 复制日志，连同机型与系统版本一起提 [Issue](https://github.com/TaoQiYiYi/DeepSeek-Harness-Android/issues)。
</details>

---

## 📜 版本历史

| 版本 | 日期 | 类型 | DSH 内核 | 要点 |
| :--- | :--- | :--- | :--- | :--- |
| [v0.2.2](https://github.com/TaoQiYiYi/DeepSeek-Harness-Android/releases/latest) | 2026-10-19 | 正式 | 0.2.1-rc.1 | 内核升级至官方最新、换核启动失败修复、运行时 r9 |
| [v0.2.2-rc.3](https://github.com/TaoQiYiYi/DeepSeek-Harness-Android/releases/tag/DeepSeek-Harness-Android-0.2.2rc3) | 2026-10-15 | 预览 | 0.2.1-alpha.2 | 安卓 UI 全面独立成页、返回键分级 |
| [v0.2.2-rc.2](https://github.com/TaoQiYiYi/DeepSeek-Harness-Android/releases/tag/DeepSeek-Harness-Android-0.2.2rc2) | 2026-10-12 | 预览 | 0.2.1-alpha.2 | 字体设置挤压修复、插件兼容与白屏自救 |
| [v0.2.2-rc.1](https://github.com/TaoQiYiYi/DeepSeek-Harness-Android/releases/tag/DeepSeek-Harness-Android-0.2.2rc1) | 2026-10-10 | 预览 | 0.2.1-alpha.2 | 手机界面全面适配、应用内更新、日志工具 |
| [v0.2.1](https://github.com/TaoQiYiYi/DeepSeek-Harness-Android/releases/tag/DeepSeek-Harness-Android-0.2.1) | 2026-10-09 | 正式 | 0.2.0-rc.2 | 部分机型兼容性修复 |
| [v0.2.0](https://github.com/TaoQiYiYi/DeepSeek-Harness-Android/releases/tag/DeepSeek-Harness-Android-0.2.0) | 2026-10-09 | 首个版本 | 0.2.0-rc.2 | 项目首次公开 |

---

## 📂 仓库结构

| 路径 | 说明 |
| :--- | :--- |
| `app/` | Android 应用本体：`AndroidManifest.xml`、Java 源码、资源与内置运行时 `assets/` |
| `patches/` | 针对 dsh 内核的 Android 兼容补丁（硬链接降级、原生模块替换等） |
| `tools/` | 开发辅助脚本（图标生成、沙箱内引擎重启 / 停止） |
| `build.sh` | 打包脚本：aapt2 → javac → d8 → 签名，依赖特定构建环境 |

> 本项目为个人自用工具，构建流程绑定作者本地环境，**未提供开箱即用的构建说明**；如需自行编译，请按 `build.sh` 中的步骤自备 aapt2 / d8 / apksigner。

---

## 🙏 致谢

感谢以下朋友的反馈与测试帮助：

归鹿（QQ 498899434）、航航（抖音 93271465086）、秋秋（QQ 1448209757）、残章尽（抖音 43161814697），以及另外 9 位不愿意透露姓名的用户。

---

## ⚠️ 免责声明

本项目为个人学习交流性质的**非官方**移植，与 DeepSeek 官方无关，请勿用于商业用途。

- 官方项目：[deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)
- 使用本项目产生的任何后果由使用者自行承担
