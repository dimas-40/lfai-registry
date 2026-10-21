import sys, time
from cdp import Tab
t = Tab(9335, ws=open("dev_tab.txt").read().strip())
expr = sys.argv[1]
print(t.js(expr))
