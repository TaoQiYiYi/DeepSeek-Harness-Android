#!/usr/bin/env python3
"""rc3 build43: 标题左对齐 + 插件/自动化页独立成页 + 返回键体系重构 → 构建/校验/文档/同步"""
import hashlib
import os
import shutil
import subprocess

WS = '/var/minis/workspace/dshport'
SH = '/var/minis/shared/dshport-transfer/out'
OUT = WS + '/out'
os.chdir(WS)
APK = 'DSHPort-full-0.2.2-rc3-core0.2.1a2-build43.apk'

# 1) Manifest versionCode 42 -> 43（幂等）
mf = 'app/AndroidManifest.xml'
s = open(mf, encoding='utf-8').read()
if 'android:versionCode="42"' in s:
    s = s.replace('android:versionCode="42"', 'android:versionCode="43"')
open(mf, 'w', encoding='utf-8').write(s)
print('1) manifest:', [l.strip() for l in s.splitlines() if 'version' in l])

# 2) 构建
env = dict(os.environ, OUTNAME='DSHPort-full', VERSION_NAME='0.2.2-rc3', VERSION_CODE='43')
r = subprocess.run(['sh', 'build.sh'], env=env, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stdout[-1200:]); print(r.stderr[-500:]); raise SystemExit('BUILD FAIL')
built = OUT + '/DSHPort-full-0.2.2-rc3.apk'
assert os.path.exists(built), 'output apk missing'
NEW = OUT + '/' + APK
shutil.copy2(built, NEW)
apk_sha = hashlib.sha256(open(NEW, 'rb').read()).hexdigest()
print('2) build OK:', os.path.getsize(NEW), apk_sha)

# 3) 校验（打包进 APK 的 mobile.js 内容）
subprocess.run('rm -rf /tmp/v43 && mkdir -p /tmp/v43', shell=True)
subprocess.run('unzip -o -q "%s" assets/mobile.js -d /tmp/v43' % NEW, shell=True)
mj = open('/tmp/v43/assets/mobile.js', encoding='utf-8').read()
checks = {
    '标题左对齐': mj.count('grid-template-columns: 0 minmax(0, 1fr) !important'),
    '插件页模式': mj.count('data-dshm-page'),
    '页面根检测': mj.count('pageRootEl'),
    '让路窗口': mj.count('__dshmExitChatUntil'),
    'frX守卫': mj.count('frX'),
    '会话行收抽屉': mj.count('isSessionNav'),
    '自适应对齐': mj.count('hHd-Xa_regionArea"] { margin-left: 0'),
    '主页模式': mj.count('data-dshm-home'),
    '空态检测': mj.count('工作区文件'),
}
print('3) assets:', checks)
assert (checks['标题左对齐'] >= 1 and checks['插件页模式'] >= 3 and checks['页面根检测'] >= 3
        and checks['让路窗口'] >= 3 and checks['frX守卫'] >= 2 and checks['会话行收抽屉'] >= 2
        and checks['自适应对齐'] >= 1 and checks['主页模式'] >= 1 and checks['空态检测'] >= 1), '关键规则缺失'
badging = subprocess.run('/opt/tx/aapt2 dump badging "%s" 2>/dev/null | head -1' % NEW, shell=True, capture_output=True, text=True).stdout.strip()
print('   badging:', badging[:110])
assert "versionCode='43'" in badging and "versionName='0.2.2-rc3'" in badging, '版本错误'

# 4) 文档（模板纯占位符替换）
SRC = 'dshport-src-0.2.2-rc3-build43.zip'
sha = '`%s`' % apk_sha
release = open(WS + '/tools/tpl_release_rc3.md', encoding='utf-8').read()
release = release.replace('__APK__', APK).replace('__SIZE__', str(os.path.getsize(NEW))).replace('__SHA__', sha).replace('__SRC__', SRC)
open(OUT + '/RELEASE-0.2.2-rc3.md', 'w', encoding='utf-8').write(release)
update = open(WS + '/tools/tpl_update_rc3.md', encoding='utf-8').read()
update = update.replace('__APK__', APK).replace('__SHA__', sha)
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
for old in ['DSHPort-full-0.2.2-rc3-core0.2.1a2-build41.apk', 'DSHPort-full-0.2.2-rc3-core0.2.1a2-build40.apk']:
    p = SH + '/' + old
    if os.path.exists(p):
        os.remove(p); print('rm shared:', old.split('build')[-1], '（已被更新版取代）')
for f in list(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    if f.endswith('.apk') and 'build43' not in f:
        os.remove(p); print('rm out:', f)
    elif f.startswith('dshport-src-') and 'build43' not in f:
        os.remove(p); print('rm out:', f)
print('6) 同步清理 OK')
print('== out ==')
for f in sorted(os.listdir(OUT)):
    print(' ', f)
print('== shared apks ==')
for f in sorted(os.listdir(SH)):
    if f.endswith(('.apk', '.zip')):
        print(' ', f)
print('== shared docs ==')
for f in sorted(os.listdir(SH)):
    if f.endswith('.md'):
        print(' ', f)
