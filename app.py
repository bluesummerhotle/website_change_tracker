from flask import Flask, request, redirect, render_template
import os
import json
from checker import load_html, compare_html
from scheduler import run  # để gọi từ route /run-daily-task

app = Flask(__name__)

URL_FILE = '/tmp/urls.json'

# 🔧 Tạo file /tmp/urls.json rỗng nếu chưa có
if not os.path.exists(URL_FILE):
    with open(URL_FILE, 'w') as f:
        json.dump([], f)

@app.route('/')
def index():
    with open(URL_FILE, 'r') as f:
        urls = json.load(f)

    reports = []

    for url in urls:
        domain = url.replace('https://', '').replace('http://', '').split('/')[0]
        try:
            dates = sorted(os.listdir(f'storage/{domain}'))
            if len(dates) >= 2:
                old_html = load_html(domain, dates[-2].replace('.html', ''))
                new_html = load_html(domain, dates[-1].replace('.html', ''))
                diff = compare_html(old_html, new_html)
                reports.append({'url': url, 'diff': diff})
        except FileNotFoundError:
            continue

    return render_template('index.html', reports=reports)

@app.route('/add-url', methods=['POST'])
def add_url():
    new_urls = request.form['urls'].strip().split('\n')
    new_urls = [url.strip() for url in new_urls if url.strip()]

    if os.path.exists(URL_FILE):
        with open(URL_FILE, 'r') as f:
            existing = json.load(f)
    else:
        existing = []

    all_urls = list(set(existing + new_urls))

    with open(URL_FILE, 'w') as f:
        json.dump(all_urls, f, indent=4)

    return redirect('/')

@app.route('/run-daily-task')
def run_daily_task():
    run()
    return "✅ Đã chạy kiểm tra thay đổi!"
