import json
from datetime import datetime, timedelta
from checker import fetch_html, save_html, load_html, compare_html, extract_elements, compare_elements
from email_utils import send_email

def run():
    with open('urls.json', 'r') as f:
        urls = json.load(f)

    for url in urls:
        domain = url.replace('https://', '').replace('http://', '').split('/')[0]
        new_html = fetch_html(url)
        save_html(new_html, domain)

        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        old_html = load_html(domain, yesterday)

        if old_html:
            diff = compare_html(old_html, new_html)
            old_elements = extract_elements(old_html)
            new_elements = extract_elements(new_html)
            element_changes = compare_elements(old_elements, new_elements)

            if diff or element_changes:
                body = f"Changes detected in {url}:\n\n"
                if diff:
                    body += f"HTML differences:\n{diff}\n\n"
                if element_changes:
                    body += f"Element changes:\n{element_changes}\n"
                send_email(f'Changes detected in {url}', body)

if __name__ == '__main__':
    run()
