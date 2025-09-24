import sys
import csv
import shutil
import os
from bs4 import BeautifulSoup

# --- CONFIG ---
HTML_PATH = os.path.join('docs', 'index.html')
BACKUP_PATH = os.path.join('docs', 'index.html.bak')
TABLE_HEADERS = ['SVD File', 'Bug Description', 'PR', 'Status']
CSV_COLUMNS = ['SVD File', 'Bug Description', 'PR', 'Status']


def main(csv_path):
    # Backup the HTML file
    shutil.copy2(HTML_PATH, BACKUP_PATH)
    print(f"Backup created at {BACKUP_PATH}")

    # Read CSV and filter columns
    rows = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filtered = [row.get(col, '') for col in CSV_COLUMNS]
            rows.append(filtered)

    # Parse HTML
    with open(HTML_PATH, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Find the table with the correct headers
    table = None
    for t in soup.find_all('table'):
        headers = [th.get_text(strip=True) for th in t.find_all('th')]
        if headers == TABLE_HEADERS:
            table = t
            break
    if not table:
        print("Error: Could not find the table with the correct headers.")
        sys.exit(1)

    # Find the header row and remove all data rows
    trs = table.find_all('tr')
    if not trs:
        print("Error: Table has no rows.")
        sys.exit(1)
    header_tr = trs[0]
    for tr in trs[1:]:
        tr.decompose()

    # Build the new table HTML as a string
    indent = '      '
    table_html = '\n' + indent + str(header_tr) + '\n'
    for row in rows:
        pr_url = row[2].strip()
        if pr_url:
            pr_cell = f'<a href="{pr_url}">link</a>'
        else:
            pr_cell = ''
        row_html = f'<tr><td>{row[0]}</td> <td>{row[1]}</td> <td>{pr_cell}</td> <td>{row[3]}</td></tr>'
        table_html += row_html + '\n'

    # Replace the table's contents (preserve <table> tag and attributes)
    table.clear()
    table.append(BeautifulSoup(table_html, 'html.parser'))

    # Write back to HTML
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print(f"Replaced {len(rows)} rows in the table.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} path/to/file.csv")
        sys.exit(1)
    main(sys.argv[1])
