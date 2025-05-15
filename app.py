from flask import Flask, render_template
import os
import json
from checker import load_html, compare_html

app = Flask(__name__)

@app.route('/')
def index():
    with open('urls.json', 'r') as f:
        urls = json.load(f)

    reports = []
    for url in urls:
        domain = url.replace('https://', '').replace('http://', '').split('/')[0]
        dates = sorted(os.listdir(f'storage/{domain}'))
        if len(dates) >= 2:
            old_html = load_html(domain, dates[-2].replace('.html', ''))
            new_html = load_html(domain, dates[-1].replace('.html', ''))
            diff = compare_html(old_html, new_html)
            reports.append({'url': url, 'diff': diff})
    return render_template('index.html', reports=reports)
