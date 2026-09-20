import urllib.request

endpoints = [
    '/',
    '/dashboard',
    '/demo',
    '/monitor',
    '/demystified.html',
    '/PITCH_DECK.html',
    '/api/v1/badge/CERT-8991.svg',
    '/verify/CERT-8991',
    '/api/v1/adapters/launchdarkly'
]

for ep in endpoints:
    try:
        res = urllib.request.urlopen(f'http://localhost:8000{ep}')
        content_type = res.headers.get('content-type')
        print(f"[OK] {ep}: HTTP {res.status} ({content_type})")
    except Exception as e:
        print(f"[FAIL] {ep}: {e}")
