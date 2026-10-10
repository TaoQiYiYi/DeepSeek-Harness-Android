#!/usr/bin/env python3
"""Package the DSHPort v0.2.2-rc1 (build32) source bundle."""
import os
import shutil
import zipfile

SRC = '/var/minis/workspace/dshport'
STAGE = '/tmp/src-stage'
NAME = 'dshport-src-0.2.2-rc1'
ROOT = os.path.join(STAGE, NAME)
OUT = os.path.join(SRC, 'out', NAME + '.zip')

shutil.rmtree(STAGE, ignore_errors=True)
os.makedirs(ROOT)

# ---- app 源码（不含 runtime.zip 构建产物）----
shutil.copytree(os.path.join(SRC, 'app'), os.path.join(ROOT, 'app'),
                ignore=shutil.ignore_patterns('runtime.zip', 'build', '*.class', '*.dex'))
shutil.copy2(os.path.join(SRC, 'build.sh'), ROOT)
shutil.copytree(os.path.join(SRC, 'tools'), os.path.join(ROOT, 'tools'))
if os.path.exists(os.path.join(SRC, 'out', '安装说明.md')):
    shutil.copy2(os.path.join(SRC, 'out', '安装说明.md'), ROOT)

# ---- 引擎补丁（当前生效版）----
PATCHES = [
    'node-addon-require-builtin/lib/index.js',
    '@deepseek-ai/node-addon-system/lib/flock.js',
    '@deepseek-ai/dsh-session-persistence-jsonl/lib/index.js',
    '@deepseek-ai/dsh-attachment-local/lib/index.js',
    '@deepseek-ai/dsh-api-settings-controller/lib/index.js',
    '@deepseek-ai/dsh-host-directory-picker-browse/lib/index.js',
]
for rel in PATCHES:
    src = os.path.join('/opt/dshstage/node_modules', rel)
    dst = os.path.join(ROOT, 'patches', 'node_modules', rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
shutil.copy2('/opt/build/_links.tsv', os.path.join(ROOT, 'patches', '_links.tsv'))

README = '''# DSHPort 源码包 v0.2.2-rc1（build32）

官方 DeepSeek Harness（dsh **0.2.1-alpha.2**）的 Android 移植源码。
App 显示名：DeepSeek Harness ｜ 包名：com.dshport.mobile ｜ versionCode 34

## 目录
- `app/`          Android 壳应用源码（Java + Manifest + 资源 + WebView 注入脚本）
- `build.sh`      构建脚本（aapt2 + javac + d8 + apksigner 一条龙）
- `tools/`        图标生成脚本、沙箱测试服务器脚本
- `patches/`      引擎补丁：把 `patches/node_modules/**` 按相同路径覆盖到运行时树即为完整补丁
- `patches/_links.tsv`  运行时符号链接清单（1205 条，解压运行时后用于重建符号链接）

## 引擎补丁清单（路径相对 node_modules）
| 补丁 | 作用 |
|---|---|
| `node-addon-require-builtin/lib/index.js` | 无 Android 原生绑定 → 基于官方 `--expose-internals` 的纯 JS 降级 |
| `@deepseek-ai/node-addon-system/lib/flock.js` | flock 无 Android 包 → koffi FFI 直调 bionic libc `flock()` |
| `@deepseek-ai/dsh-session-persistence-jsonl/lib/index.js` | Android 禁硬链接 → link 失败降级 rename / copyFile(EXCL) |
| `@deepseek-ai/dsh-attachment-local/lib/index.js` | ①硬链接降级 ②sharp 无 Android 版 → 纯 JS 图片头解析+原样直通 ③目录 fsync 跳过 App 不可读的祖先目录 |
| `@deepseek-ai/dsh-api-settings-controller/lib/index.js` | 「打开配置文件」Android 通道（复制到 DSH_SHARE_DIR + 标记文件）＋ 附件准入错误日志 |
| `@deepseek-ai/dsh-host-directory-picker-browse/lib/index.js` | 工作区选择器默认根目录支持 `DSH_PICKER_HOME` 环境变量（手机默认打开"手机存储"） |

## 运行时关键约束（踩坑记录）
1. **koffi 全平台必须同版本**：JS 包装与 `@koromix/koffi-android-arm64` 版本号一致（当前 3.3.2）。
   npm 上 Android 原生包最早只有 3.2.1，因此不能降级 JS 到 3.1.x，只能整体升到 3.3.2。
2. **targetSdk 必须 28**：否则无法从应用数据目录执行 Node 二进制（W^X）。
3. **Node 运行时为 Termux(bionic) 编译版**：OpenSSL 配置路径硬编码 Termux 路径，
   App 启动时会写入自带 `runtime/etc/tls/openssl.cnf` 并通过 `OPENSSL_CONF` 指定，
   避免部分设备（装有 Termux 时路径存在但不可读）启动即崩。
4. **不打包**：`app/assets/runtime.zip`（235MB，由 Node 运行时前缀 + 打好补丁的 node_modules
   打包而成，属于构建产物，未包含在本源码包内）。

## 构建
```sh
OUTNAME=DSHPort-full VERSION_NAME=0.2.2-rc1 VERSION_CODE=32 sh build.sh
```
依赖：aapt2（arm64）、API30 android.jar、d8、apksigner、JDK17。

## App 侧要点
- 前台服务守护 Node 引擎；WebView 加载 `127.0.0.1` 上带 token 鉴权的 dsh web UI
- `app/assets/mobile.js` + `mobile-critical.css`：手机端 UI 适配（侧栏浮层化、设置面板全屏、
  系统栏配色跟随主题）、「获取更新」（GitHub Releases + 系统安装器）、「日志」工具
- JS↔Java 通道：`console.log('__DSHM__' + JSON)` + `onConsoleMessage` 拦截
- 存储权限：`MANAGE_EXTERNAL_STORAGE` + 传统权限兜底级联授权；工作区可选手机目录
- 侧滑返回逐级处理：关面板 → 回退网页历史 → 才退出
- 应用内更新仓库：`TaoQiYiYi/DeepSeek-Harness-Android`

---
本项目为个人非官方移植，与 DeepSeek 官方无关。官方项目：deepseek-ai/deepseek-harness
'''
open(os.path.join(ROOT, 'README.md'), 'w', encoding='utf-8').write(README)

P_README = '''# patches/ 使用说明

`node_modules/` 下的文件按**原路径**覆盖到运行时树的对应位置即可。
`_links.tsv` 放在运行时包（runtime.zip）根目录，供解压时重建符号链接。

当前对应核心版本：@deepseek-ai/dsh **0.2.1-alpha.2**
'''
open(os.path.join(ROOT, 'patches', 'README.md'), 'w', encoding='utf-8').write(P_README)

# ---- zip ----
if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for dp, dns, fns in os.walk(ROOT):
        for f in fns:
            fp = os.path.join(dp, f)
            zf.write(fp, os.path.relpath(fp, STAGE))

cnt = sum(len(fs) for _, _, fs in os.walk(ROOT))
print('staged files:', cnt)
print('zip:', OUT, os.path.getsize(OUT), 'bytes')
for n in sorted(zipfile.ZipFile(OUT).namelist())[:40]:
    print('   ', n)
