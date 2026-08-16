import urllib.request

urls = [
    'https://bartholomew.info/',
    'https://bartholomew.info/dashboard/admin',
    'https://bartholomew.info/dashboard/admin.html',
    'https://bartholomew.info/dashboard/admin/',
    'https://bartholomew.info/dashboard/orchestrator',
    'https://bartholomew.info/dashboard/orchestrator.html',
    'https://bartholomew.info/dashboard/orchestrator/',
    'https://bartholomew.info/bartholomew_vulnerability_scanner.png',
    'https://bartholomew.info/dashboard/bartholomew_vulnerability_scanner.png',
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req)
        print(f"[SUCCESS {res.getcode()}] {u}")
    except Exception as e:
        print(f"[FAILED] {u} => {e}")
