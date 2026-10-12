#!/usr/bin/env python3
"""build36 patch2: critical-css guard in MainActivity + removeMyCss clears both ids."""
# A) mobile.js: 让位时同时移除 #dshm-crit
F = '/var/minis/workspace/dshport/app/assets/mobile.js'
s = open(F, encoding='utf-8').read()
a = "    try { var s = document.getElementById('dshm-css'); if (s && s.parentNode) s.parentNode.removeChild(s); } catch (e) {}"
assert s.count(a) == 1, 'anchor A'
s = s.replace(a, "    try { var a = document.getElementById('dshm-css'); if (a && a.parentNode) a.parentNode.removeChild(a); } catch (e) {}\n    try { var b = document.getElementById('dshm-crit'); if (b && b.parentNode) b.parentNode.removeChild(b); } catch (e) {}", 1)
open(F, 'w', encoding='utf-8').write(s)
print('A) mobile.js OK')

# B) MainActivity: 注入兜底 CSS 前检查插件
F = '/var/minis/workspace/dshport/app/java/com/dshport/mobile/MainActivity.java'
s = open(F, encoding='utf-8').read()
a = '''            String js = "(function(){try{if(document.getElementById('dshm-crit'))return;"'''
assert s.count(a) == 1, 'anchor B'
s = s.replace(a, '''            String js = "(function(){try{if(window.__DSH_BOOT__&&JSON.stringify(window.__DSH_BOOT__).indexOf('dsh-web-mobile')!==-1)return;"
                    + "if(document.getElementById('dshm-crit'))return;"''', 1)
open(F, 'w', encoding='utf-8').write(s)
print('B) MainActivity OK')
