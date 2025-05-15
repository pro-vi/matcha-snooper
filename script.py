import os, json, requests
from bs4 import BeautifulSoup

WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
STATUS_FILE = 'status.json'
CATALOG_URL = 'https://www.marukyu-koyamaen.co.jp/english/shop/products/catalog/matcha?viewall=1'

def load_status():
    try:
        return json.load(open(STATUS_FILE))
    except FileNotFoundError:
        return {}

def save_status(s):
    json.dump(s, open(STATUS_FILE,'w'), indent=2)

def fetch_products():
    """Scrape the catalog page for every matcha product."""
    r = requests.get(CATALOG_URL, headers={'User-Agent':'Mozilla/5.0'})
    soup = BeautifulSoup(r.text, 'html.parser')
    items = []
    for li in soup.select('ul.products li.product'):
        a = li.select_one('a.woocommerce-loop-product__link')
        name = a.select_one('h4').get_text(strip=True)
        url  = a['href']
        # stock is determined by CSS class on the <li>
        instock = 'instock' in li.get('class', [])
        items.append({'name': name, 'url': url, 'instock': instock})
    return items

def notify(product):
    payload = {
        'content': f'✅ **{product["name"]}** is back in stock!\n{product["url"]}'
    }
    requests.post(WEBHOOK_URL, json=payload)

def main():
    prev = load_status()
    new  = {}
    products = fetch_products()

    for p in products:
        url = p['url']
        new[url] = p['instock']
        # if it was previously out-of-stock (or unseen) and now in-stock → notify
        if p['instock'] and not prev.get(url, False):
            notify(p)

    save_status(new)

if __name__=='__main__':
    main()
