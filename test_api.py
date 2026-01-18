import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("🧪 TEST API")
print("=" * 60)

# Test 1: Routes HTML
print("\n1️⃣ TEST ROUTES HTML:")
routes = ["/", "/upload", "/dashboard"]
for route in routes:
    try:
        response = requests.get(f"{BASE_URL}{route}")
        print(f"✅ GET {route} → Status {response.status_code}")
    except Exception as e:
        print(f"❌ GET {route} → {e}")

# Test 2: API Video
print("\n2️⃣ TEST API VIDEO:")
api_routes = [
    "/api/video/upload",
    "/api/video/videos",
    "/api/dashboard/videos"
]

for route in api_routes:
    try:
        response = requests.get(f"{BASE_URL}{route}")
        print(f"✅ GET {route} → Status {response.status_code}")
        if response.status_code != 404:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ GET {route} → {e}")

# Test 3: Upload test
print("\n3️⃣ TEST UPLOAD:")
try:
    with open("test_video.mp4", "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/api/video/upload", files=files)
        print(f"✅ POST /api/video/upload → Status {response.status_code}")
        print(f"   Response: {response.json()}")
except FileNotFoundError:
    print("❌ Fichier test_video.mp4 non trouvé (créez un fichier test)")
except Exception as e:
    print(f"❌ Erreur upload: {e}")

print("\n" + "=" * 60)