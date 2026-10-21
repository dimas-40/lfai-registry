# helpers for phone ADB UI automation
PH=$(cat ~/.phone_ip):5900
A(){ timeout 25 adb -s $PH shell "$@"; }
dump(){ A "uiautomator dump /sdcard/ui.xml >/dev/null 2>&1; cat /sdcard/ui.xml" > ui.xml; python3 - <<'PY'
import re
x=open('ui.xml',encoding='utf-8',errors='ignore').read()
for n in re.finditer(r'<node [^>]*>', x):
    s=n.group(0)
    t=re.search(r' text="([^"]*)"',s).group(1); d=re.search(r'content-desc="([^"]*)"',s).group(1)
    r=re.search(r'resource-id="([^"]*)"',s).group(1); b=re.search(r'bounds="([^"]*)"',s).group(1)
    m=re.search(r'class="([^"]*)"',s); c=(m.group(1) if m else '').split('.')[-1]
    if t or d or 'EditText' in c: print(f"{c[:10]:10} {b:24} {r[-25:]:25} | {t[:60]} | {d[:40]}")
PY
}
tapb(){ python3 -c "import re,sys;a=list(map(int,re.findall(r'\d+',sys.argv[1])));print((a[0]+a[2])//2,(a[1]+a[3])//2)" "$1"; }
