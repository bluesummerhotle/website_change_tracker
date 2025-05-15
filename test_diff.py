import requests
from bs4 import BeautifulSoup
from difflib import unified_diff

# === CẤU HÌNH URL CỦA MÀY ===
url = "https://dongphuchaianh.vn"

# === GIẢ LẬP HTML HÔM QUA ===
html_yesterday = """
<html>
<head><title>Đồng phục Hải Anh</title></head>
<body>
<h1>Đồng phục chất lượng cao</h1>
<p>Chúng tôi chuyên cung cấp đồng phục cho doanh nghiệp và trường học.</p>
</body>
</html>
"""

# === LẤY HTML HÔM NAY ===
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers, timeout=15)
response.encoding = response.apparent_encoding
html_today = response.text

# === SO SÁNH HTML HÔM QUA VÀ HÔM NAY ===
diff = list(unified_diff(
    html_yesterday.splitlines(),
    html_today.splitlines(),
    fromfile='2025-05-14.html',
    tofile='2025-05-15.html',
    lineterm=''
))

# === IN RA 50 DÒNG ĐẦU CỦA KHÁC BIỆT (Nếu có) ===
print("🔍 SO SÁNH HTML HÔM QUA VÀ HÔM NAY\n")
if diff:
    print('\n'.join(diff[:50]))
else:
    print("✅ Không có thay đổi.")

