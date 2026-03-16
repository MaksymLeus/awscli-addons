import urllib.request
from json import load

def show():
    url = "https://api.ipify.org?format=json"
    # ✅ Standard User-Agent prevents blocks
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = load(response)
            print(f"🌐 Public IP: {data['ip']}")
    except Exception as e:
        print(f"❌ Error fetching public IP: {e}")
