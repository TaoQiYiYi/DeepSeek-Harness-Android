# DeepSeek-Harness-Android

> 把官方 DeepSeek Harness 完整搬进 Android 手机 —— 非官方移植项目

DSHPort 不是重写，也不是套壳：它直接运行官方发布的 `@deepseek-ai/dsh` 引擎包，
搭配为 Android 定制的 arm64 Node.js 运行时、常驻前台服务与 WebView 外壳，
把桌面端完整的 Agent 体验——聊天会话、工具调用、插件系统、本地工作区——
原样带到手机上。安装一个 APK 即用，无需 root，无需 Termux。

引擎全程在设备本地运行（127.0.0.1 + 一次性 token 鉴权），数据不出手机；
使用需自备 DeepSeek API Key。

## 为 Android 做了哪些适配

官方 dsh 没有移动端目标，本项目针对平台差异做了必要的兼容处理
（均为小改动 + 失败回退，不影响桌面端原有行为）：

- **Node 原生模块**：没有 Android 预编译的模块降级为 JS 实现（基于官方 `--expose-internals` 运行模式）
- **文件系统**：Android 应用域禁止硬链接 → 会话 / 附件存储自动降级为 rename / copyFile
- **插件系统**：内置 pnpm，插件安装开箱即用
- **移动端 UI**：设置面板、会话侧栏针对小屏重新适配
- **桌面专属功能**：「打开配置文件」等改为 Android 通道（调起系统文本编辑器）

## 运行要求

- Android 8.0+ / arm64 设备
- 自备 DeepSeek API Key

## 免责声明

本项目为个人学习交流性质的**非官方**移植，与 DeepSeek 官方无关。
官方项目：https://github.com/deepseek-ai/deepseek-harness
