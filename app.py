from flask import Flask, request, redirect, render_template, send_file
import os
import json
from datetime import datetime
from checker import fetch_html, compare_html_detailed, save_html, load_html
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)

URL_FILE = 'urls.json'
STORAGE_DIR = 'storage'

# Ensure data dir
os.makedirs(STORAGE_DIR, exist_ok=True)
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
        domain_path = os.path.join(STORAGE_DIR, domain)
        if not os.path.exists(domain_path):
            continue
        dates = sorted([f.replace('.html', '') for f in os.listdir(domain_path)])
        if len(dates) >= 2:
            old_html = load_html(domain, dates[-2])
            new_html = load_html(domain, dates[-1])
            report = compare_html_detailed(old_html, new_html)
            reports.append({"url": url, "domain": domain, "report": report})

    return render_template('index.html', reports=reports)

@app.route('/add-url', methods=['POST'])
def add_url():
    url = request.form['url'].strip()
    if url:
        with open(URL_FILE, 'r') as f:
            urls = json.load(f)
        if url not in urls:
            urls.append(url)
            with open(URL_FILE, 'w') as f:
                json.dump(urls, f, indent=4)
    return redirect('/')

@app.route('/run-daily-task')
def run_daily_task():
    try:
        with open(URL_FILE, 'r') as f:
            urls = json.load(f)
        today = datetime.now().strftime('%Y-%m-%d')
        for url in urls:
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            html = fetch_html(url)
            save_html(domain, today, html)
        return "✅ Đã crawl HTML cho tất cả domain"
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"

@app.route('/download-report/<domain>')
def download_report(domain):
    domain_path = os.path.join(STORAGE_DIR, domain)
    dates = sorted([f.replace('.html', '') for f in os.listdir(domain_path)])
    if len(dates) < 2:
        return "Không đủ dữ liệu để so sánh."

    old_html = load_html(domain, dates[-2])
    new_html = load_html(domain, dates[-1])
    report = compare_html_detailed(old_html, new_html)

    pdf_path = f"{domain}_seo_report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setFont("Helvetica", 12)
    text = c.beginText(50, 800)
    text.textLine(f"📊 SEO Change Report: {domain}")
    text.textLine("")
    for section, changes in report.items():
        text.textLine(f"{section.upper()}")
        for line in changes:
            text.textLine(f"- {line[:100]}")
        text.textLine("")
    c.drawText(text)
    c.showPage()
    c.save()
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
