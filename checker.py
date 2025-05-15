import os
import requests
from bs4 import BeautifulSoup

def fetch_html(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers, timeout=15)
    res.encoding = res.apparent_encoding
    return res.text

def save_html(domain, date_str, content):
    folder = os.path.join('storage', domain)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, f'{date_str}.html'), 'w', encoding='utf-8') as f:
        f.write(content)

def load_html(domain, date_str):
    path = os.path.join('storage', domain, f'{date_str}.html')
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def compare_html_detailed(old_html, new_html):
    old_soup = BeautifulSoup(old_html, 'html.parser')
    new_soup = BeautifulSoup(new_html, 'html.parser')

    report = {}

    # 1. Compare Text
    old_text = old_soup.get_text(separator=' ').strip()
    new_text = new_soup.get_text(separator=' ').strip()
    if old_text != new_text:
        report['text_diff'] = ["Nội dung văn bản đã thay đổi"]

    # 2. Compare Headings
    heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    old_headings = [tag.get_text().strip() for tag in old_soup.find_all(heading_tags)]
    new_headings = [tag.get_text().strip() for tag in new_soup.find_all(heading_tags)]
    if old_headings != new_headings:
        report['headings'] = [f"Từ: {old_headings}", f"Thành: {new_headings}"]

    # 3. Compare Meta Title
    old_title = old_soup.title.string.strip() if old_soup.title else ''
    new_title = new_soup.title.string.strip() if new_soup.title else ''
    if old_title != new_title:
        report['title'] = [f"Từ: {old_title}", f"Thành: {new_title}"]

    # 4. Compare Meta Description
    old_desc = old_soup.find('meta', attrs={'name': 'description'})
    new_desc = new_soup.find('meta', attrs={'name': 'description'})
    old_desc = old_desc['content'].strip() if old_desc and 'content' in old_desc.attrs else ''
    new_desc = new_desc['content'].strip() if new_desc and 'content' in new_desc.attrs else ''
    if old_desc != new_desc:
        report['meta_description'] = [f"Từ: {old_desc}", f"Thành: {new_desc}"]

    # 5. Compare Links
    old_links = sorted(set(a['href'] for a in old_soup.find_all('a', href=True)))
    new_links = sorted(set(a['href'] for a in new_soup.find_all('a', href=True)))
    added = [l for l in new_links if l not in old_links]
    removed = [l for l in old_links if l not in new_links]
    if added or removed:
        report['links'] = []
        if added:
            report['links'].append(f"+ Thêm: {added}")
        if removed:
            report['links'].append(f"- Mất: {removed}")

    return report
