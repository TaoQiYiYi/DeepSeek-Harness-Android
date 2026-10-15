#!/usr/bin/env python3
"""rc3 build42: 对话页标题截断修复 + 新会话空态页识别（返回键/系统返回）→ 构建/校验/文档/同步"""
import hashlib
import os
import shutil
import subprocess

WS = '/var/minis/workspace/dshport'
SH = '/var/minis/shared/dshport-transfer/out'
OUT = WS + '/out'
os.chdir(WS)
APK = 'DSHPort-full-0.2.2-rc3-core0.2.1a2-build42.apk'

# 1) Manifest versionCode 41 -> 42（幂等）
mf = 'app/AndroidManifest.xml'
s = open(mf, encoding='utf-8').read()
if 'android:versionCode="41"' in s:
    s = s.replace('android:versionCode="41"', 'android:versionCode="42"')
open(mf, 'w', encoding='utf-8').write(s)
print('1) manifest:', [l.strip() for l in s.splitlines() if 'version' in l])

# 2) 构建
env = dict(os.environ, OUTNAME='DSHPort-full', VERSION_NAME='0.2.2-rc3', VERSION_CODE='42')
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
subprocess.run('rm -rf /tmp/v42 && mkdir -p /tmp/v42', shell=True)
subprocess.run('unzip -o -q "%s" assets/mobile.js -d /tmp/v42' % NEW, shell=True)
mj = open('/tmp/v42/assets/mobile.js', encoding='utf-8').read()
checks = {
    '标题放宽': mj.count('wSkVaW_headerUtilities'),
    'crumb放宽': mj.count('wSkVaW_crumb"] { max-width: 100%'),
    '空态检测': mj.count('工作区文件'),
    'tabHost腾位': mj.count('_tabHostHeader_'),
    '自适应对齐': mj.count('hHd-Xa_regionArea"] { margin-left: 0'),
    '主页': mj.count('data-dshm-home'),
}
print('3) assets:', checks)
assert checks['标题放宽'] >= 1 and checks['crumb放宽'] >= 1 and checks['空态检测'] >= 1 and checks['tabHost腾位'] >= 2, '关键规则缺失'
badging = subprocess.run('/opt/tx/aapt2 dump badging "%s" 2>/dev/null | head -1' % NEW, shell=True, capture_output=True, text=True).stdout.strip()
print('   badging:', badging[:100])
assert "versionCode='42'" in badging and "versionName='0.2.2-rc3'" in badging, '版本错误'

# 4) 文档
sha = '`%s`' % apk_sha
release = open(WS + '/tools/tpl_release_rc3.md', encoding='utf-8').read()
release = release.replace('__APK__', APK).replace('__SIZE__', str(os.path.getsize(NEW))).replace('__SHA__', sha)
release = release.replace('versionCode 41', 'versionCode 42')
release = release.replace('- 右上角「⋯」按钮贴紧最右侧的分栏切换按钮，不再隔一大段空隙。',
                          '- 右上角「⋯」按钮贴紧最右侧的分栏切换按钮，不再隔一大段空隙。\n- 修复会话名称在顶栏被截断的问题（如「插件设置调整…」只显示一个字），长标题在窄屏上尽可能完整显示。\n- 新会话的「开始」页（工作区文件/新建终端卡片）现在也被识别为会话页：带返回键、系统返回可退出，不再误判为主页。')
open(OUT + '/RELEASE-0.2.2-rc3.md', 'w', encoding='utf-8').write(release)
update = open(WS + '/tools/tpl_update_rc3.md', encoding='utf-8').read()
update = update.replace('__APK__', APK).replace('__SHA__', sha)
update = update.replace('build 40 → 41', 'build 41 → 42')
update = update.replace('## 10. 系统返回键分级',
                        '## 10. 修复：顶栏会话名被截断 + 新会话「开始」页适配（build 42）\n- 对话页顶栏的会话名称之前被压缩成一两个字（如「插...」）；已放宽，长标题尽可能完整显示。\n- 新会话的「开始」页（罗盘 + 工作区文件/新建终端卡片）之前没有返回键、滑动返回会退出程序；现已按会话页处理：左上角返回键 + 系统返回退回首页。\n\n## 11. 系统返回键分级')
open(OUT + '/UPDATE-0.2.2-rc2-to-rc3.md', 'w', encoding='utf-8').write(update)
print('4) 文档 OK')

# 5) 源码包
subprocess.run(['python3', 'tools/pack_src.py'], capture_output=True, text=True)
src_old = OUT + '/dshport-src-0.2.2-rc3.zip'
src_new = OUT + '/dshport-src-0.2.2-rc3-build42.zip'
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
old40 = SH + '/DSHPort-full-0.2.2-rc3-core0.2.1a2-build40.apk'
if os.path.exists(old40):
    os.remove(old40); print('rm shared: build40（已被 41/42 取代）')
for f in list(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    if f.endswith('.apk') and 'build42' not in f and f != 'DSHPort-full-0.2.2-rc3.apk':
        os.remove(p); print('rm out:', f)
    elif f.startswith('dshport-src-') and 'build42' not in f:
        os.remove(p); print('rm out:', f)
print('6) 同步清理 OK')
print('== out ==')
for f in sorted(os.listdir(OUT)):
    print(' ', f)
print('== shared apks ==')
for f in sorted(os.listdir(SH)):
    if f.endswith('.apk'):
        print(' ', f)
