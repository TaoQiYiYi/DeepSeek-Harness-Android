#!/usr/bin/env python3
"""v0.2.2-rc2 (build35): version bump + build + sync + docs."""
import hashlib
import os
import re
import shutil
import subprocess

WS = '/var/minis/workspace/dshport'
SH = '/var/minis/shared/dshport-transfer/out'
OUT = WS + '/out'
os.chdir(WS)

# 1) 版本号
mf = 'app/AndroidManifest.xml'
s = open(mf, encoding='utf-8').read()
assert s.count('android:versionCode="34"') == 1 and s.count('"0.2.2-rc1"') == 1
s = s.replace('android:versionCode="34"', 'android:versionCode="35"').replace('"0.2.2-rc1"', '"0.2.2-rc2"')
open(mf, 'w', encoding='utf-8').write(s)
rt = 'app/java/com/dshport/mobile/Runtime.java'
s = open(rt, encoding='utf-8').read()
assert s.count('APP_VERSION = "0.2.2-rc1"') == 1
s = s.replace('APP_VERSION = "0.2.2-rc1"', 'APP_VERSION = "0.2.2-rc2"')
open(rt, 'w', encoding='utf-8').write(s)
print('1) version -> 0.2.2-rc2 / 35 OK')

# 2) 语法检查
r = subprocess.run(['node', '--check', 'app/assets/mobile.js'], capture_output=True, text=True)
print('2) mobile.js:', 'OK' if r.returncode == 0 else 'FAIL ' + r.stderr[:200])

# 3) 构建
env = dict(os.environ, OUTNAME='DSHPort-full', VERSION_NAME='0.2.2-rc2', VERSION_CODE='35')
r = subprocess.run(['sh', 'build.sh'], env=env, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stdout[-1200:]); print(r.stderr[-800:]); raise SystemExit('BUILD FAIL')
built = OUT + '/DSHPort-full-0.2.2-rc2.apk'
if not os.path.exists(built):
    built = OUT + '/DSHPort-full.apk'
assert os.path.exists(built), 'build output not found'
NEW = OUT + '/DSHPort-full-0.2.2-rc2-core0.2.1a2-build35.apk'
shutil.copy2(built, NEW)
if built != OUT + '/DSHPort-full-0.2.2-rc2.apk':
    shutil.copy2(built, OUT + '/DSHPort-full-0.2.2-rc2.apk')
apk_sha = hashlib.sha256(open(NEW, 'rb').read()).hexdigest()
print('3) build OK:', os.path.getsize(NEW), apk_sha[:24])

# 4) 链路验证：APK 内 assets 含修复
subprocess.run('rm -rf /tmp/v35 && mkdir -p /tmp/v35', shell=True)
subprocess.run('unzip -o -q "%s" assets/mobile-critical.css assets/mobile.js -d /tmp/v35' % NEW, shell=True)
c1 = open('/tmp/v35/assets/mobile-critical.css', encoding='utf-8').read().count('vnGTiq_field')
c2 = open('/tmp/v35/assets/mobile.js', encoding='utf-8').read().count('vnGTiq_field')
print('4) 包内修复命中: critical=%d mobile.js=%d' % (c1, c2))
assert c1 >= 3 and c2 >= 3, 'fix not found in APK assets'

# 5) RELEASE md -> rc2
md = open(OUT + '/RELEASE-0.2.2-rc1.md', encoding='utf-8').read()
md = md.replace('v0.2.2-rc1 更新说明', 'v0.2.2-rc2 更新说明').replace('build 34', 'build 35')
md = md.replace('DSHPort-full-0.2.2-rc1-core0.2.1a2-build34.apk', 'DSHPort-full-0.2.2-rc2-core0.2.1a2-build35.apk')
md = re.sub('- SHA-256：[^\n]+', '- SHA-256：`%s`' % apk_sha, md)
if '字体设置展开区' not in md:
    md = md.replace('- 「+」菜单弹出后闪退',
        '- 设置 →「更多字体设置」展开区文字被挤压（正文/代码/终端字体行）—— 窄屏下文字与输入框改为换行排布\n- 「+」菜单弹出后闪退')
open(OUT + '/RELEASE-0.2.2-rc2.md', 'w', encoding='utf-8').write(md)
os.remove(OUT + '/RELEASE-0.2.2-rc1.md')
shutil.copy2(OUT + '/RELEASE-0.2.2-rc2.md', SH + '/RELEASE-0.2.2-rc2.md')
print('5) RELEASE -> rc2 OK')

# 6) shared 同步 + 清理旧 rc1 产物（shared 保留 build34 一份作回退）
shutil.copy2(NEW, SH + '/DSHPort-full-0.2.2-rc2-core0.2.1a2-build35.apk')
shutil.copy2(NEW, SH + '/DSHPort-full-0.2.2-rc2.apk')
for f in list(os.listdir(OUT)):
    if 'rc1' in f and (f.endswith('.apk') or f.endswith('.md')):
        os.remove(os.path.join(OUT, f)); print('rm out:', f)
for f in list(os.listdir(SH)):
    if 'rc1' in f and (f.endswith('.apk') or f.endswith('.md')):
        if 'build34' in f:
            print('keep(回退):', f); continue
        os.remove(os.path.join(SH, f)); print('rm shared:', f)

# 7) 源码包重打（rc2 / build35）
ps = WS + '/tools/pack_src.py'
s = open(ps, encoding='utf-8').read()
s = s.replace("dshport-src-0.2.2-rc1", "dshport-src-0.2.2-rc2")
s = s.replace('v0.2.2-rc1（build32）', 'v0.2.2-rc2（build35）')
s = s.replace('v0.2.2-rc1（build34）', 'v0.2.2-rc2（build35）')
s = s.replace('versionCode 32', 'versionCode 35').replace('versionCode 34', 'versionCode 35')
open(ps, 'w', encoding='utf-8').write(s)
r = subprocess.run(['python3', ps], capture_output=True, text=True)
print('7) pack:', (r.stdout or r.stderr).strip().splitlines()[:2])
SRCZ = OUT + '/dshport-src-0.2.2-rc2.zip'
NEWZ = OUT + '/dshport-src-0.2.2-rc2-build35.zip'
if os.path.exists(SRCZ):
    os.replace(SRCZ, NEWZ)
for f in list(os.listdir(SH)):
    if f.startswith('dshport-src-') and f.endswith('.zip'):
        os.remove(os.path.join(SH, f)); print('rm shared:', f)
if os.path.exists(NEWZ):
    shutil.copy2(NEWZ, SH)
    print('   src zip:', os.path.getsize(NEWZ), hashlib.sha256(open(NEWZ, 'rb').read()).hexdigest())

# 8) 收尾
subprocess.run('pkill -f "dsh/lib/bin[.]js"', shell=True)
print('8) 沙箱 dsh 已停')
print('== out =='); subprocess.run('ls -la ' + OUT, shell=True)
print('== shared =='); subprocess.run('ls -la ' + SH, shell=True)
