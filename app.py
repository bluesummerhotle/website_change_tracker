from flask import Flask, render_template
import os
import json
from checker import load_html, compare_html

app = Flask(__name__)

@app.route('/')
from flask import request, redirect

@app.route('/add-url', methods=['POST'])
def add_url():
    new_urls = request.form['urls'].strip().split('\n')

    # Làm sạch URL
    new_urls = [url.strip() for url in new_urls if url.strip()]

    # Gộp vào urls.json hiện tại
    with open('urls.json', 'r') as f:
        existing = json.load(f)

    all_urls = list(set(existing + new_urls))

    with open('urls.json', 'w') as f:
        json.dump(all_urls, f, indent=4)

    return redirect('/')

def index():
    with open('urls.json', 'r') as f:
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
