import os
import json
from datetime import datetime, timedelta
from checker import fetch_html, save_html, load_html, compare_html, extract_elements, compare_elements
from email_utils import send_email

URL_FILE = '/tmp/urls.json'

# Nếu chưa có file, thoát
if not os.path.exists(URL_FILE):
    print("⚠️ Không có URL nào được theo dõi.")
    exit()

with open(URL_FILE, 'r') as f:
    urls = json.load(f)

for url in urls:
    domain = url.replace('https://', '').replace('http://', '').split('/')[0]
    try:
        new_html = fetch_html(url)
        save_html(new_html, domain)

        # Lấy HTML hôm qua
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        old_html = load_html(domain, yesterday)

        if old_html:
            diff = compare_html(old_html, new_html)
            old_elements = extract_elements(old_html)
            new_elements = extract_elements(new_html)
            element_changes = compare_elements(old_elements, new_elements)

            if diff or element_changes:
                body = f"🔔 Thay đổi phát hiện ở {url}:\n\n"
                if diff:
                    body += f"📄 HTML khác biệt:\n{diff}\n\n"
                if element_changes:
                    body += f"🧱 Thống kê thay đổi thẻ HTML:\n{json.dumps(element_changes, indent=2, ensure_ascii=False)}\n"
                send_email(f'🛎 Website thay đổi: {url}', body)

    except Exception as e:
        print(f"❌ Lỗi khi xử lý {url}: {str(e)}")
