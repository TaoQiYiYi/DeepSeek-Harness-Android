#!/usr/bin/env python3
"""rc3 build38: 主页适配 + ⋯靠右 + 设置返回修复 → 构建/校验/文档/同步"""
import hashlib
import os
import shutil
import subprocess

WS = '/var/minis/workspace/dshport'
SH = '/var/minis/shared/dshport-transfer/out'
OUT = WS + '/out'
os.chdir(WS)
APK = 'DSHPort-full-0.2.2-rc3-core0.2.1a2-build38.apk'

# 1) Manifest versionCode 37 -> 38（幂等）
mf = 'app/AndroidManifest.xml'
s = open(mf, encoding='utf-8').read()
if 'android:versionCode="37"' in s:
    s = s.replace('android:versionCode="37"', 'android:versionCode="38"')
open(mf, 'w', encoding='utf-8').write(s)
print('1) manifest:', [l.strip() for l in s.splitlines() if 'version' in l])

# 2) 构建
env = dict(os.environ, OUTNAME='DSHPort-full', VERSION_NAME='0.2.2-rc3', VERSION_CODE='38')
r = subprocess.run(['sh', 'build.sh'], env=env, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stdout[-1200:]); print(r.stderr[-500:]); raise SystemExit('BUILD FAIL')
built = OUT + '/DSHPort-full-0.2.2-rc3.apk'
assert os.path.exists(built)
NEW = OUT + '/' + APK
shutil.copy2(built, NEW)
apk_sha = hashlib.sha256(open(NEW, 'rb').read()).hexdigest()
print('2) build OK:', os.path.getsize(NEW), apk_sha)

# 3) 校验
subprocess.run('rm -rf /tmp/v38 && mkdir -p /tmp/v38', shell=True)
subprocess.run('unzip -o -q "%s" assets/mobile.js -d /tmp/v38' % NEW, shell=True)
mj = open('/tmp/v38/assets/mobile.js', encoding='utf-8').read()
print('3) assets: home=%d menu=%d dotsFixed=%d closeTxt=%d' % (
    mj.count('data-dshm-home'), mj.count('dshm-home-menu'),
    mj.count('"更多操作"] { position: fixed'), mj.count("t.indexOf('关闭')")))
badging = subprocess.run('/opt/tx/aapt2 dump badging "%s" 2>/dev/null | head -1' % NEW, shell=True, capture_output=True, text=True).stdout.strip()
print('   badging:', badging[:100])
assert "versionCode='38'" in badging and "versionName='0.2.2-rc3'" in badging, '版本错误'

# 4) 文档
sha = '`%s`' % apk_sha
release = open(WS + '/tools/tpl_release_rc3.md', encoding='utf-8').read()
release = release.replace('__APK__', APK).replace('__SIZE__', str(os.path.getsize(NEW))).replace('__SHA__', sha)
release = release.replace('versionCode 37', 'versionCode 38')
open(OUT + '/RELEASE-0.2.2-rc3.md', 'w', encoding='utf-8').write(release)
update = open(WS + '/tools/tpl_update_rc3.md', encoding='utf-8').read()
update = update.replace('__APK__', APK).replace('__SHA__', sha)
update = update.replace('build 36 → 37', 'build 37 → 38')
open(OUT + '/UPDATE-0.2.2-rc2-to-rc3.md', 'w', encoding='utf-8').write(update)
print('4) 文档 OK')

# 5) 源码包
subprocess.run(['python3', 'tools/pack_src.py'], capture_output=True, text=True)
src_old = OUT + '/dshport-src-0.2.2-rc3.zip'
src_new = OUT + '/dshport-src-0.2.2-rc3-build38.zip'
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
# shared: 移除 build36（已被 37/38 取代），保留 build37（用户当前版）+ build34 回退
old36 = SH + '/DSHPort-full-0.2.2-rc2-core0.2.1a2-build36.apk'
if os.path.exists(old36):
    os.remove(old36); print('rm shared: build36（已被取代）')
for f in list(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    if f.endswith('.apk') and 'build38' not in f and f != 'DSHPort-full-0.2.2-rc3.apk':
        os.remove(p); print('rm out:', f)
    elif f.startswith('dshport-src-') and 'build38' not in f:
        os.remove(p); print('rm out:', f)
print('6) 同步清理 OK')
print('== out ==')
for f in sorted(os.listdir(OUT)):
    print(' ', f)
print('== shared apks ==')
for f in sorted(os.listdir(SH)):
    if f.endswith('.apk'):
        print(' ', f)
