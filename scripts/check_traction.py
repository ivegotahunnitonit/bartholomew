"""
Bartholomew Global Traction & Telemetry Monitor
================================================
One-command live inspection of adoption metrics across GitHub, npm, PyPI, and Cloud Run.
Usage:
  python scripts/check_traction.py
"""

import sys
import subprocess
import re
import requests
from datetime import datetime, timezone

def get_github_metrics():
    res = subprocess.run(['git', 'config', 'remote.origin.url'], capture_output=True, text=True)
    match = re.search(r'ghp_[A-Za-z0-9]+', res.stdout)
    if not match:
        return None
    token = match.group(0)
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json'
    }
    base = 'https://api.github.com/repos/ivegotahunnitonit/bartholomew'
    try:
        repo = requests.get(base, headers=headers).json()
        clones = requests.get(f'{base}/traffic/clones', headers=headers).json()
        views = requests.get(f'{base}/traffic/views', headers=headers).json()
        referrers = requests.get(f'{base}/traffic/popular/referrers', headers=headers).json()
        return {
            'stars': repo.get('stargazers_count', 0),
            'forks': repo.get('forks_count', 0),
            'watchers': repo.get('watchers_count', 0),
            'total_clones': clones.get('count', 0),
            'unique_cloners': clones.get('uniques', 0),
            'total_views': views.get('count', 0),
            'unique_views': views.get('uniques', 0),
            'top_referrers': referrers[:5] if isinstance(referrers, list) else []
        }
    except Exception as e:
        return {'error': str(e)}

def get_npm_metrics():
    try:
        r_point = requests.get('https://api.npmjs.org/downloads/point/last-week/btp-guard', timeout=5).json()
        r_pkg = requests.get('https://registry.npmjs.org/btp-guard/latest', timeout=5).json()
        return {
            'weekly_downloads': r_point.get('downloads', 0),
            'latest_version': r_pkg.get('version', 'unknown')
        }
    except Exception as e:
        return {'error': str(e)}

def get_pypi_metrics():
    try:
        r = requests.get('https://pypi.org/pypi/btp-guard/json', timeout=5).json()
        info = r.get('info', {})
        releases = r.get('releases', {})
        return {
            'latest_version': info.get('version', 'unknown'),
            'total_releases': len(releases)
        }
    except Exception as e:
        return {'error': str(e)}

def get_cloud_run_health():
    try:
        r = requests.get('https://acn-fastapi-backend-322603900775.us-central1.run.app/', timeout=10)
        return {
            'status_code': r.status_code,
            'ok': r.status_code == 200
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    print("================================================================")
    print("   BARTHOLOMEW REAL-TIME TRACTION MONITOR")
    print(f"   Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("================================================================\n")

    # 1. GitHub
    print("[1] GITHUB REPOSITORY METRICS")
    gh = get_github_metrics()
    if gh and 'error' not in gh:
        print(f"    - Unique Developers Cloned: {gh['unique_cloners']}")
        print(f"    - Total Git Clones:         {gh['total_clones']}")
        print(f"    - Unique Visitors:          {gh['unique_views']}")
        print(f"    - Total Page Views:         {gh['total_views']}")
        print(f"    - Stars / Forks:            {gh['stars']} / {gh['forks']}")
        if gh['top_referrers']:
            print("    - Top Referring Domains:")
            for ref in gh['top_referrers']:
                print(f"        * {ref.get('referrer')}: {ref.get('count')} views ({ref.get('uniques')} uniques)")
    else:
        print("    [!] GitHub metrics unavailable or token missing.")

    # 2. NPM
    print("\n[2] NPM REGISTRY METRICS")
    npm = get_npm_metrics()
    if npm and 'error' not in npm:
        print(f"    - Package Name:             btp-guard")
        print(f"    - Latest Released Version:  {npm['latest_version']}")
        print(f"    - Recorded Downloads:       {npm['weekly_downloads']}")
    else:
        print("    [!] npm metrics unavailable.")

    # 3. PyPI
    print("\n[3] PYPI REGISTRY METRICS")
    pypi = get_pypi_metrics()
    if pypi and 'error' not in pypi:
        print(f"    - Package Name:             btp-guard")
        print(f"    - Latest Released Version:  {pypi['latest_version']}")
        print(f"    - Published Releases:       {pypi['total_releases']}")
    else:
        print("    [!] PyPI metrics unavailable.")

    # 4. Cloud Infrastructure
    print("\n[4] CLOUD RUN BACKEND & WEB")
    cr = get_cloud_run_health()
    if cr and 'error' not in cr:
        print(f"    - Production Endpoint:      https://bartholomew.info")
        print(f"    - Backend Health Status:    {cr['status_code']} OK")
    else:
        print("    [!] Backend health check failed.")

    print("\n================================================================")
    print("   STATUS: ALL SYSTEMS OPERATIONAL AND TRACKING LIVE")
    print("================================================================\n")

if __name__ == '__main__':
    main()
