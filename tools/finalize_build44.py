#!/usr/bin/env python3
"""rc3 build44: 版本号显示修复（运行时读取 PackageManager versionName）→ 构建/校验/文档/同步"""
import hashlib
import os
import shutil
import subprocess

WS = '/var/minis/workspace/dshport'
SH = '/var/minis/shared/dshport-transfer/out'
OUT = WS + '/out'
os.chdir(WS)
APK = 'DSHPort-full-0.2.2-rc3-core0.2.1a2-build44.apk'

# 1) Manifest versionCode 43 -> 44（幂等）
mf = 'app/AndroidManifest.xml'
s = open(mf, encoding='utf-8').read()
if 'android:versionCode="43"' in s:
    s = s.replace('android:versionCode="43"', 'android:versionCode="44"')
open(mf, 'w', encoding='utf-8').write(s)
print('1) manifest:', [l.strip() for l in s.splitlines() if 'version' in l])

# 2) 构建
env = dict(os.environ, OUTNAME='DSHPort-full', VERSION_NAME='0.2.2-rc3', VERSION_CODE='44')
r = subprocess.run(['sh', 'build.sh'], env=env, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stdout[-1200:]); print(r.stderr[-500:]); raise SystemExit('BUILD FAIL')
built = OUT + '/DSHPort-full-0.2.2-rc3.apk'
assert os.path.exists(built), 'output apk missing'
NEW = OUT + '/' + APK
shutil.copy2(built, NEW)
apk_sha = hashlib.sha256(open(NEW, 'rb').read()).hexdigest()
print('2) build OK:', os.path.getsize(NEW), apk_sha)

# 3) 校验（mobile.js 内容 + dex 内新代码）
subprocess.run('rm -rf /tmp/v44 && mkdir -p /tmp/v44', shell=True)
subprocess.run('unzip -o -q "%s" assets/mobile.js classes.dex -d /tmp/v44' % NEW, shell=True)
mj = open('/tmp/v44/assets/mobile.js', encoding='utf-8').read()
dex = open('/tmp/v44/classes.dex', 'rb').read()
checks = {
    '标题左对齐': mj.count('grid-template-columns: 0 minmax(0, 1fr) !important'),
    '插件页模式': mj.count('data-dshm-page'),
    '页面根检测': mj.count('pageRootEl'),
    '让路窗口': mj.count('__dshmExitChatUntil'),
    'dex含appVerName': dex.count(b'appVerName'),
    'dex含方法名': dex.count(b'appVersionName'),
    'dex含旧常量兜底': dex.count(b'0.2.2-rc3'),
    'dex不含rc2显示值': dex.count(b'0.2.2-rc2'),
    '自适应对齐': mj.count('hHd-Xa_regionArea"] { margin-left: 0'),
    '主页模式': mj.count('data-dshm-home'),
    '空态检测': mj.count('工作区文件'),
}
print('3) assets+dex:', checks)
assert (checks['标题左对齐'] >= 1 and checks['插件页模式'] >= 3 and checks['页面根检测'] >= 3
        and checks['让路窗口'] >= 3 and checks['dex含appVerName'] >= 1
        and checks['dex含方法名'] >= 1 and checks['dex含旧常量兜底'] >= 1
        and checks['自适应对齐'] >= 1 and checks['主页模式'] >= 1 and checks['空态检测'] >= 1), '关键规则缺失'
# dex 内不得再有 rc2 版本串（兜底常量已改 rc3）
assert checks['dex不含rc2显示值'] == 0, 'dex 里仍残留 0.2.2-rc2'
badging = subprocess.run('/opt/tx/aapt2 dump badging "%s" 2>/dev/null | head -1' % NEW, shell=True, capture_output=True, text=True).stdout.strip()
print('   badging:', badging[:110])
assert "versionCode='44'" in badging and "versionName='0.2.2-rc3'" in badging, '版本错误'

# 4) 文档（模板纯占位符替换）
SRC = 'dshport-src-0.2.2-rc3-build44.zip'
sha = '`%s`' % apk_sha
release = open(WS + '/tools/tpl_release_rc3.md', encoding='utf-8').read()
release = (release.replace('__APK__', APK).replace('__SIZE__', str(os.path.getsize(NEW)))
           .replace('__SHA__', sha).replace('__SRC__', SRC).replace('__VC__', '44'))
open(OUT + '/RELEASE-0.2.2-rc3.md', 'w', encoding='utf-8').write(release)
update = open(WS + '/tools/tpl_update_rc3.md', encoding='utf-8').read()
update = update.replace('__APK__', APK).replace('__SHA__', sha).replace('__VC__', '44')
open(OUT + '/UPDATE-0.2.2-rc2-to-rc3.md', 'w', encoding='utf-8').write(update)
print('4) 文档 OK')

# 5) 源码包
subprocess.run(['python3', 'tools/pack_src.py'], capture_output=True, text=True)
src_old = OUT + '/dshport-src-0.2.2-rc3.zip'
src_new = OUT + '/' + SRC
if os.path.exists(src_old):
    os.replace(src_old, src_new)
src_sha = hashlib.sha256(open(src_new, 'rb').read()).hexdigest() if os.path.exists(src_new) else 'N/A'
print('5) src zip:', os.path.getsize(src_new) if os.path.exists(src_new) else 'MISSING', src_sha)

# 6) 同步 shared + 清理
shutil.copy2(NEW, SH + '/' + APK)
shutil.copy2(OUT + '/RELEASE-0.2.2-rc3.md', SH + '/RELEASE-0.2.2-rc3.md')
shutil.copy2(OUT + '/UPDATE-0.2.2-rc2-to-rc3.md', SH + '/UPDATE-0.2.2-rc2-to-rc3.md')
if os.path.exists(src_new):
    shutil.copy2(src_new, SH)
for old in [SH + '/DSHPort-full-0.2.2-rc3-core0.2.1a2-build42.apk', SH + '/dshport-src-0.2.2-rc3-build42.zip']:
    if os.path.exists(old):
        os.remove(old); print('rm shared:', os.path.basename(old))
for f in list(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    if f.endswith('.apk') and 'build44' not in f:
        os.remove(p); print('rm out:', f)
    elif f.startswith('dshport-src-') and 'build44' not in f:
        os.remove(p); print('rm out:', f)
print('6) 同步清理 OK')
print('== out ==')
for f in sorted(os.listdir(OUT)):
    print(' ', f)
print('== shared apks/zips ==')
for f in sorted(os.listdir(SH)):
    if f.endswith(('.apk', '.zip')):
        print(' ', f)
