import requests

# แทนที่ด้วย GitHub Personal Access Token ของคุณ
token = 'YOUR_GITHUB_TOKEN'

# ข้อมูลสำหรับสร้าง repository ใหม่
repo_data = {
    'name': 'smartfan-server',  # ชื่อ repository ใหม่
    'description': 'SmartFan server project',  # คำอธิบาย repository
    'private': False,  # กำหนดว่า repository จะเป็น public หรือ private
}

# Header สำหรับการ authenticate ด้วย GitHub token
headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/vnd.github.v3+json',
}

# URL สำหรับการสร้าง repository
url = 'https://api.github.com/user/repos'

# ส่ง POST request ไปยัง GitHub API
response = requests.post(url, json=repo_data, headers=headers)

# ตรวจสอบผลลัพธ์
if response.status_code == 201:
    print('Repository created successfully:', response.json())
else:
    print('Error creating repository:', response.status_code, response.json())
