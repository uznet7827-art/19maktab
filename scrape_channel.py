from bs4 import BeautifulSoup
import urllib.request
import re
import time
import json

all_posts = {}
before = None

for step in range(20):
    url = 'https://t.me/s/maktab19_rasmiy' + (f'?before={before}' if before else '')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
    except Exception as e:
        print('Error:', e)
        break
    soup = BeautifulSoup(html, 'html.parser')
    messages = soup.find_all('div', class_='tgme_widget_message')
    if not messages:
        break
    new_found = 0
    min_id = None
    for msg in messages:
        data_post = msg.get('data-post')
        if not data_post:
            continue
        post_num = int(data_post.split('/')[-1])
        if min_id is None or post_num < min_id:
            min_id = post_num
        if data_post not in all_posts:
            text_div = msg.find('div', class_='tgme_widget_message_text')
            text = text_div.text.strip() if text_div else ''
            photos = re.findall(r"background-image:url\('(.*?)'\)", str(msg))
            time_tag = msg.find('time')
            dt = time_tag.get('datetime') if time_tag else ''
            if text or photos:
                all_posts[data_post] = {'num': post_num, 'dt': dt, 'text': text, 'photos': photos}
                new_found += 1
    print(f'Step {step}: found {new_found} new posts, min_id={min_id}')
    if not min_id or (before and min_id >= before):
        break
    before = min_id
    if min_id <= 1:
        break
    time.sleep(0.5)

print(f'Total posts collected: {len(all_posts)}')
with open('channel_posts.json', 'w', encoding='utf-8') as f:
    json.dump(all_posts, f, ensure_ascii=False, indent=2)

for p in sorted(all_posts.values(), key=lambda x: x['num']):
    if p['text']:
        clean_txt = p['text'].replace('\n', ' ')[:75]
        print(f"Post {p['num']} | {p['dt']} | Photos: {len(p['photos'])} | {clean_txt}")
