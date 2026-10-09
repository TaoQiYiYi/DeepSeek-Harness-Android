# DSHPort 源码包（v0.2.0）

官方 DeepSeek Harness (dsh 0.2.0-rc.2) 的 Android 移植 —— Android 壳应用源码 + 引擎补丁。

## 目录结构
- app/                  Android 壳应用源码（Java + Manifest + 资源 + assets/mobile.js 手机 UI 适配）
- build.sh              构建脚本（aapt2 + javac + d8 + apksigner；用 OUTNAME/VERSION_NAME/VERSION_CODE 环境变量）
- tools/                图标生成脚本、沙箱测试服务器脚本
- patches/              引擎补丁（对应 node_modules 内的修改文件，按原路径放置即生效）
  - node-addon-require-builtin/lib/index.js       无 Android 原生绑定 → --expose-internals JS 适配层
  - node-addon-system/lib/flock.js                flock 原生包 → koffi FFI 直调 bionic libc
  - dsh-session-persistence-jsonl/lib/index.js    硬链接 EACCES → 降级 rename/copyFile
  - dsh-attachment-local/lib/index.js             同上（附件硬链接降级）
  - dsh-api-settings-controller/lib/index.js      「打开配置文件」Android 通道（v0.2.0）
  - _links.tsv                                    运行时符号链接清单（解压重建用）

## 注意
- 不含 assets/runtime.zip（235MB 构建产物，含 Node 运行时前缀 + 全套 node_modules）
- 完整构建需要：API30 android.jar、aapt2/d8/apksigner 工具链、以及打好补丁的运行时
