import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import time

BASE_URL = "https://www.explainxkcd.com/wiki/index.php/"

def get_comic_image_and_text(num):
    url = BASE_URL + str(num)
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Page {num} not found or error.")
        return None

    soup = BeautifulSoup(r.text, 'html.parser')

    # Find comic image (first <img> inside content)
    img_tag = soup.find('div', id='mw-content-text')
    if img_tag:
        img_tag = img_tag.find('img')
    if not img_tag:
        image_url = None
    else:
        src = img_tag.get('src')
        if src.startswith('//'):
            image_url = 'https:' + src
        elif src.startswith('/'):
            image_url = 'https://www.explainxkcd.com' + src
        else:
            image_url = src

    # Extract explanation paragraphs
    content_div = soup.find('div', id='mw-content-text')
    if not content_div:
        explanation = ''
    else:
        # Remove tables, divs, lists, scripts etc. inside content_div to get mostly text paragraphs
        for tag in content_div.find_all(['table', 'div', 'ul', 'ol', 'style', 'script', 'noscript']):
            tag.decompose()
        paragraphs = content_div.find_all('p')
        explanation = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

    return {
        'num': num,
        'url': url,
        'image_url': image_url,
        'explanation': explanation
    }

def create_feed(start=1, end=5, feed_file='explainxkcd.xml'):
    fg = FeedGenerator()
    fg.title('Explain XKCD Comics')
    fg.link(href='https://www.explainxkcd.com', rel='alternate')
    fg.description('Scraped explanations and comics from explainxkcd.com')

    for num in range(start, end + 1):
        data = get_comic_image_and_text(num)
        if data is None:
            continue

        fe = fg.add_entry()
        fe.id(data['url'])
        fe.title(f"xkcd #{data['num']}")
        fe.link(href=data['url'])

        content_html = ''
        if data['image_url']:
            content_html += f'<img src="{data["image_url"]}" alt="XKCD comic #{data["num"]}"><br/>'
        if data['explanation']:
            paragraph_html = ''.join(f'<p>{para}</p>' for para in data['explanation'].split('\n\n'))
            content_html += paragraph_html

        fe.content(content_html, type='html')
        print(f"Added comic {num}")

        time.sleep(2)  # polite delay

    fg.rss_file(feed_file)
    print(f"Feed saved to {feed_file}")

if __name__ == '__main__':
    create_feed(1, 10)
