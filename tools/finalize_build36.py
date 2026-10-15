#!/usr/bin/env python3
"""build36: version bump + build + verify + sync + docs."""
import hashlib
import os
import re
import shutil
import subprocess

WS = '/var/minis/workspace/dshport'
SH = '/var/minis/shared/dshport-transfer/out'
OUT = WS + '/out'
os.chdir(WS)

# 1) versionCode 35 -> 36（versionName 保持 0.2.2-rc2）
mf = 'app/AndroidManifest.xml'
s = open(mf, encoding='utf-8').read()
assert s.count('android:versionCode="35"') == 1
s = s.replace('android:versionCode="35"', 'android:versionCode="36"', 1)
open(mf, 'w', encoding='utf-8').write(s)
print('1) versionCode -> 36 (versionName 保持 0.2.2-rc2)')

# 2) 语法检查
r = subprocess.run(['node', '--check', 'app/assets/mobile.js'], capture_output=True, text=True)
print('2) mobile.js:', 'OK' if r.returncode == 0 else 'FAIL ' + r.stderr[:200])

# 3) 构建
env = dict(os.environ, OUTNAME='DSHPort-full', VERSION_NAME='0.2.2-rc2', VERSION_CODE='36')
r = subprocess.run(['sh', 'build.sh'], env=env, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stdout[-1500:]); print(r.stderr[-800:]); raise SystemExit('BUILD FAIL')
built = OUT + '/DSHPort-full-0.2.2-rc2.apk'
assert os.path.exists(built), 'build output missing'
NEW = OUT + '/DSHPort-full-0.2.2-rc2-core0.2.1a2-build36.apk'
shutil.copy2(built, NEW)
apk_sha = hashlib.sha256(open(NEW, 'rb').read()).hexdigest()
print('3) build OK:', os.path.getsize(NEW), apk_sha[:24])

# 4) 校验：badging + assets 内兼容补丁
subprocess.run('/opt/tx/aapt2 dump badging "%s" 2>/dev/null | head -1' % NEW, shell=True)
subprocess.run('rm -rf /tmp/v36 && mkdir -p /tmp/v36', shell=True)
subprocess.run('unzip -o -q "%s" assets/mobile.js -d /tmp/v36' % NEW, shell=True)
mj = open('/tmp/v36/assets/mobile.js', encoding='utf-8').read()
print('4) assets 校验: pluginOwnsMobile=%d, removeMyCss=%d, dshm-crit清理=%d' % (
    mj.count('pluginOwnsMobile'), mj.count('removeMyCss'), mj.count("getElementById('dshm-crit')")))

# 5) shared 同步 + 清 build35
shutil.copy2(NEW, SH + '/DSHPort-full-0.2.2-rc2-core0.2.1a2-build36.apk')
shutil.copy2(NEW, SH + '/DSHPort-full-0.2.2-rc2.apk')
for d in (OUT, SH):
    for f in list(os.listdir(d)):
        if f.endswith('.apk') and 'build36' not in f and f != 'DSHPort-full-0.2.2-rc2.apk':
            if 'build34' in f:
                print('keep(回退):', f); continue
            os.remove(os.path.join(d, f)); print('rm:', f)

# 6) RELEASE md 更新（文件名/校验值 + 兼容条目）
md = open(OUT + '/RELEASE-0.2.2-rc2.md', encoding='utf-8').read()
md = md.replace('DSHPort-full-0.2.2-rc2-core0.2.1a2-build35.apk', 'DSHPort-full-0.2.2-rc2-core0.2.1a2-build36.apk')
md = re.sub('- SHA-256：[^\n]+', '- SHA-256：`%s`' % apk_sha, md)
if 'dsh-web-mobile' not in md:
    md = md.replace('- 设置 →「更多字体设置」展开区',
        '- **第三方移动端适配插件兼容（如 dsh-web-mobile）**：插件接管界面时，本应用的适配自动让位，避免双方冲突；新增页面渲染异常自动检测与「禁用插件重载」自救\n- 设置 →「更多字体设置」展开区')
open(OUT + '/RELEASE-0.2.2-rc2.md', 'w', encoding='utf-8').write(md)
shutil.copy2(OUT + '/RELEASE-0.2.2-rc2.md', SH + '/RELEASE-0.2.2-rc2.md')
print('6) RELEASE 更新 OK')

# 7) 源码包重打
ps = WS + '/tools/pack_src.py'
r = subprocess.run(['python3', ps], capture_output=True, text=True)
print('7) pack:', (r.stdout or r.stderr).strip().splitlines()[:2])
SRCZ = OUT + '/dshport-src-0.2.2-rc2.zip'
NEWZ = OUT + '/dshport-src-0.2.2-rc2-build36.zip'
if os.path.exists(SRCZ):
    os.replace(SRCZ, NEWZ)
for f in list(os.listdir(SH)):
    if f.startswith('dshport-src-') and f.endswith('.zip'):
        os.remove(os.path.join(SH, f)); print('rm shared:', f)
if os.path.exists(NEWZ):
    shutil.copy2(NEWZ, SH)
    print('   src zip:', os.path.getsize(NEWZ), hashlib.sha256(open(NEWZ, 'rb').read()).hexdigest())

print('== out =='); subprocess.run('ls ' + OUT, shell=True)
