import os
import difflib
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def fetch_html(url):
    response = requests.get(url)
    return response.text

def save_html(content, domain):
    date_str = datetime.now().strftime('%Y-%m-%d')
    path = f'storage/{domain}'
    os.makedirs(path, exist_ok=True)
    with open(f'{path}/{date_str}.html', 'w', encoding='utf-8') as f:
        f.write(content)

def load_html(domain, date_str):
    path = f'storage/{domain}/{date_str}.html'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def compare_html(old_html, new_html):
    diff = difflib.unified_diff(
        old_html.splitlines(),
        new_html.splitlines(),
        lineterm=''
    )
    return '\n'.join(diff)

def extract_elements(html):
    soup = BeautifulSoup(html, 'html.parser')
    elements = {
        'headings': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
        'paragraphs': len(soup.find_all('p')),
        'images': len(soup.find_all('img')),
        'links': len(soup.find_all('a')),
        'divs': len(soup.find_all('div')),
    }
    return elements

def compare_elements(old_elements, new_elements):
    changes = {}
    for key in old_elements:
        if old_elements[key] != new_elements[key]:
            changes[key] = {
                'old': old_elements[key],
                'new': new_elements[key]
            }
    return changes
