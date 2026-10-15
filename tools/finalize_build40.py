#!/usr/bin/env python3
"""rc3 build40: 会话页「工作区」区块对齐（右侧 31px 缺口）→ 构建/校验/文档/同步"""
import hashlib
import os
import shutil
import subprocess

WS = '/var/minis/workspace/dshport'
SH = '/var/minis/shared/dshport-transfer/out'
OUT = WS + '/out'
os.chdir(WS)
APK = 'DSHPort-full-0.2.2-rc3-core0.2.1a2-build40.apk'

# 1) Manifest versionCode 39 -> 40（幂等）
mf = 'app/AndroidManifest.xml'
s = open(mf, encoding='utf-8').read()
if 'android:versionCode="39"' in s:
    s = s.replace('android:versionCode="39"', 'android:versionCode="40"')
open(mf, 'w', encoding='utf-8').write(s)
print('1) manifest:', [l.strip() for l in s.splitlines() if 'version' in l])

# 2) 构建
env = dict(os.environ, OUTNAME='DSHPort-full', VERSION_NAME='0.2.2-rc3', VERSION_CODE='40')
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
subprocess.run('rm -rf /tmp/v40 && mkdir -p /tmp/v40', shell=True)
subprocess.run('unzip -o -q "%s" assets/mobile.js -d /tmp/v40' % NEW, shell=True)
mj = open('/tmp/v40/assets/mobile.js', encoding='utf-8').read()
import re
checks = {
    '链收尾行': len(re.findall(r'bhn1Oq_sectionHeader.. \{ width: 100%', mj)),
    '对齐补丁': mj.count('bhn1Oq_root"] { padding-right: 0'),
    'groupSection宽': mj.count('bhn1Oq_groupSection"] { width: calc(100% + 18px)'),
    '主页': mj.count('data-dshm-home'),
}
print('3) assets:', checks)
assert checks['链收尾行'] >= 1 and checks['对齐补丁'] >= 1 and checks['groupSection宽'] >= 1, '关键规则缺失'
badging = subprocess.run('/opt/tx/aapt2 dump badging "%s" 2>/dev/null | head -1' % NEW, shell=True, capture_output=True, text=True).stdout.strip()
print('   badging:', badging[:100])
assert "versionCode='40'" in badging and "versionName='0.2.2-rc3'" in badging, '版本错误'

# 4) 文档
sha = '`%s`' % apk_sha
release = open(WS + '/tools/tpl_release_rc3.md', encoding='utf-8').read()
release = release.replace('__APK__', APK).replace('__SIZE__', str(os.path.getsize(NEW))).replace('__SHA__', sha)
release = release.replace('versionCode 39', 'versionCode 40')
release = release.replace('- 修复该页内容不铺满屏幕的问题（部分屏宽下列表被限制在 280px）。',
                          '- 修复该页内容不铺满屏幕的问题（部分屏宽下列表被限制在 280px）。\n- 修复「工作区」区块比顶部按钮短一截的问题，列表行与按钮右缘对齐。')
open(OUT + '/RELEASE-0.2.2-rc3.md', 'w', encoding='utf-8').write(release)
update = open(WS + '/tools/tpl_update_rc3.md', encoding='utf-8').read()
update = update.replace('__APK__', APK).replace('__SHA__', sha)
update = update.replace('build 38 → 39', 'build 39 → 40')
update = update.replace('## 8. 系统返回键分级', '## 8. 修复：「工作区」区块比上面短一截（build 40）\n- 会话选择页里工作区列表的右缘与顶部「新会话」按钮差约 31px；已对齐（差 1px 内）。\n\n## 9. 系统返回键分级')
open(OUT + '/UPDATE-0.2.2-rc2-to-rc3.md', 'w', encoding='utf-8').write(update)
print('4) 文档 OK')

# 5) 源码包
subprocess.run(['python3', 'tools/pack_src.py'], capture_output=True, text=True)
src_old = OUT + '/dshport-src-0.2.2-rc3.zip'
src_new = OUT + '/dshport-src-0.2.2-rc3-build40.zip'
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
old38 = SH + '/DSHPort-full-0.2.2-rc3-core0.2.1a2-build38.apk'
if os.path.exists(old38):
    os.remove(old38); print('rm shared: build38（已被 39/40 取代）')
for f in list(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    if f.endswith('.apk') and 'build40' not in f and f != 'DSHPort-full-0.2.2-rc3.apk':
        os.remove(p); print('rm out:', f)
    elif f.startswith('dshport-src-') and 'build40' not in f:
        os.remove(p); print('rm out:', f)
print('6) 同步清理 OK')
print('== out ==')
for f in sorted(os.listdir(OUT)):
    print(' ', f)
print('== shared apks ==')
for f in sorted(os.listdir(SH)):
    if f.endswith('.apk'):
        print(' ', f)
