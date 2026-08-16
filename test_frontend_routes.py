import urllib.request

endpoints = [
    '/',
    '/dashboard',
    '/demystified.html',
    '/PITCH_DECK.html',
    '/api/status'
]

for ep in endpoints:
    try:
        res = urllib.request.urlopen(f'http://localhost:8000{ep}')
        print(f"[OK] {ep}: HTTP {res.status} ({res.headers.get('content-type')})")
    except Exception as e:
        print(f"[FAIL] {ep}: {e}")
