from flask import Flask, request, redirect, render_template, send_file
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)

URL_FILE = '/tmp/urls.json'
STORAGE_DIR = 'storage'

# Ensure data dir
os.makedirs(STORAGE_DIR, exist_ok=True)
if not os.path.exists(URL_FILE):
    with open(URL_FILE, 'w') as f:
        json.dump([], f)

def fetch_html(url):
    response = requests.get(url, timeout=10)
    return response.text

def save_html(domain, timestamp, html):
    domain_path = os.path.join(STORAGE_DIR, domain)
    os.makedirs(domain_path, exist_ok=True)
    file_path = os.path.join(domain_path, f"{timestamp}.html")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)

def load_html(domain, timestamp):
    file_path = os.path.join(STORAGE_DIR, domain, f"{timestamp}.html")
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def compare_html_detailed(old_html, new_html):
    report = {}
    old_soup = BeautifulSoup(old_html, 'html.parser')
    new_soup = BeautifulSoup(new_html, 'html.parser')

    def diff_text(label, old, new):
        if old != new:
            print(f"🔍 {label} thay đổi:\n- TRƯỚC: {old}\n- SAU: {new}")
            return [f"{label} thay đổi:", f"    Trước: {old}", f"    Sau: {new}"]
        return []

    # Title
    old_title = old_soup.title.string.strip() if old_soup.title and old_soup.title.string else ''
    new_title = new_soup.title.string.strip() if new_soup.title and new_soup.title.string else ''
    report['TITLE'] = diff_text("Tiêu đề", old_title, new_title)

    # Meta Description
    old_desc = old_soup.find('meta', attrs={'name': 'description'})
    new_desc = new_soup.find('meta', attrs={'name': 'description'})
    old_meta = old_desc['content'].strip() if old_desc and 'content' in old_desc.attrs else ''
    new_meta = new_desc['content'].strip() if new_desc and 'content' in new_desc.attrs else ''
    report['META DESCRIPTION'] = diff_text("Mô tả meta", old_meta, new_meta)

    # Headings
    old_headings = set(h.get_text(strip=True)[:100] for h in old_soup.find_all(['h1', 'h2', 'h3']))
    new_headings = set(h.get_text(strip=True)[:100] for h in new_soup.find_all(['h1', 'h2', 'h3']))
    added = new_headings - old_headings
    removed = old_headings - new_headings
    report['HEADINGS'] = [f"+ {h}" for h in added] + [f"- {h}" for h in removed]

    # Text content (keyword-level diff)
    old_text = old_soup.get_text(separator=' ', strip=True)
    new_text = new_soup.get_text(separator=' ', strip=True)
    old_words = set(old_text.lower().split())
    new_words = set(new_text.lower().split())
    added_words = new_words - old_words
    removed_words = old_words - new_words
    report['TEXT'] = [f"+ {w}" for w in list(added_words)[:15]] + [f"- {w}" for w in list(removed_words)[:15]]

    # Internal Links
    old_links = set(a['href'] for a in old_soup.find_all('a', href=True))
    new_links = set(a['href'] for a in new_soup.find_all('a', href=True))
    report['LINKS'] = [f"+ {l}" for l in sorted(new_links - old_links)[:5]] + [f"- {l}" for l in sorted(old_links - new_links)[:5]]

    return report

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
        if not os.path.exists(URL_FILE):
            with open(URL_FILE, 'w') as f:
                json.dump([], f)
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
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
        for url in urls:
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            html = fetch_html(url)
            save_html(domain, timestamp, html)
        return "✅ Đã crawl HTML với timestamp theo từng lần trong ngày"
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
        text.textLine(f"{section}")
        for line in changes:
            text.textLine(f"- {line[:120]}")
        text.textLine("")
    c.drawText(text)
    c.showPage()
    c.save()
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
