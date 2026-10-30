import requests
from werkzeug.security import generate_password_hash
import json

# 1. Define the destination URL
# url = "http://127.0.0.1:5000/api/login"

# # 2. Create your payload as a native Python dictionary
# payload = {
#     "username": "Ben",
#     "password": "bf194378",
# }

# # 3. Send the POST request using the `json=` parameter
# response = requests.post(url, json=payload)

# # 4. View the server's response
# print(f"Status Code: {response.status_code}")
# print(response.cookies.get_dict())

url = "http://127.0.0.1:5000/api/participate/NOC/CPV"

response = requests.get(url)

print (response)

import requests

BASE = "http://127.0.0.1:5000/api"

# Log in as a viewer. The Session remembers the cookie.
viewer = requests.Session()
r = viewer.post(f"{BASE}/login", json={"username": "Ben", "password": "bf194378"})
print(r.status_code, r.json())                          # 200 {'message': 'Logged in as sam', 'role': 'viewer'}
print(viewer.get(f"{BASE}/participate/NOC/CPV"))       # 200

# Log out
print(viewer.post(f"{BASE}/logout").json())             # {'message': 'Logged out'}
print(viewer.get(f"{BASE}/participate/NOC/CPV").status_code)       # 401
