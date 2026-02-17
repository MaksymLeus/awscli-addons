import urllib.request
import json

def show():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=5) as response:
            data = json.load(response)
            print(f"🌐 Public IP: {data['ip']}")
    except Exception as e:
        print(f"❌ Error fetching public IP: {e}")
