#!/usr/bin/env python3
"""Final cleanup + fresh source repack + deliverable report."""
import hashlib
import os
import shutil
import subprocess

WS = '/var/minis/workspace/dshport'
SH = '/var/minis/shared/dshport-transfer'
OUT = WS + '/out'
SHO = SH + '/out'

B34 = OUT + '/DSHPort-full-0.2.2-rc1-core0.2.1a2-build34.apk'
assert os.path.exists(B34), 'build34 missing - ABORT'

try:
    if os.path.exists('/tmp/pack_src.py'):
        shutil.copy2('/tmp/pack_src.py', WS + '/tools/pack_src.py')
        print('pack_src.py 已存到 tools/（以后可用）')
except Exception as e:
    print('stash pack_src:', e)

def listing(d):
    print('---', d)
    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        if os.path.isfile(p):
            print('   %-64s %12d' % (f, os.path.getsize(p)))

print('===== 清理前 =====')
listing(OUT)
listing(SHO)

# 1) 删旧 APK（只留 build34 及同名别名）
for d in (OUT, SHO):
    for f in list(os.listdir(d)):
        if f.endswith('.apk') and 'build34' not in f and f != 'DSHPort-full-0.2.2-rc1.apk':
            os.remove(os.path.join(d, f))
            print('removed:', os.path.join(d, f))

# 2) 重新打包源码（含最新补丁）并改名为 build34
NEWZ = OUT + '/dshport-src-0.2.2-rc1-build34.zip'
if os.path.exists('/tmp/pack_src.py'):
    r = subprocess.run(['python3', '/tmp/pack_src.py'], capture_output=True, text=True)
    print((r.stdout or r.stderr or '(no output)').strip().splitlines()[:2])
    if os.path.exists(OUT + '/dshport-src-0.2.2-rc1.zip'):
        os.replace(OUT + '/dshport-src-0.2.2-rc1.zip', NEWZ)
if not os.path.exists(NEWZ):
    print('!! source zip missing')
# 清掉 shared 里的旧源码包，放入新的
for f in list(os.listdir(SHO)):
    if f.startswith('dshport-src-') and f.endswith('.zip'):
        os.remove(os.path.join(SHO, f))
        print('removed:', os.path.join(SHO, f))
if os.path.exists(NEWZ):
    shutil.copy2(NEWZ, SHO)

# 3) 更新说明同步
shutil.copy2(OUT + '/RELEASE-0.2.2-rc1.md', SHO)

# 4) /tmp 清理（大文件：rt-new*.zip、日志、暂存）
for f in list(os.listdir('/tmp')):
    p = os.path.join('/tmp', f)
    try:
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    except Exception:
        pass
print('/tmp 剩余:', os.listdir('/tmp'))

print('===== 清理后 =====')
listing(OUT)
listing(SHO)

print()
print('build34 sha256:', hashlib.sha256(open(B34, 'rb').read()).hexdigest())
if os.path.exists(NEWZ):
    print('src   sha256:', hashlib.sha256(open(NEWZ, 'rb').read()).hexdigest())
    print('src   size  :', os.path.getsize(NEWZ))
subprocess.run(['df', '-h', '/'])
