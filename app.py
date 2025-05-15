from flask import request, redirect, render_template
import os
import json
from checker import load_html, compare_html

@app.route('/')
def index():
    # Nếu chưa có file thì khởi tạo rỗng
    if os.path.exists('urls.json'):
        with open('urls.json', 'r') as f:
            urls = json.load(f)
    else:
        urls = []

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

    if os.path.exists('urls.json'):
        with open('urls.json', 'r') as f:
            existing = json.load(f)
    else:
        existing = []

    all_urls = list(set(existing + new_urls))

    with open('urls.json', 'w') as f:
        json.dump(all_urls, f, indent=4)

    return redirect('/')
