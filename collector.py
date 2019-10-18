from requests import get
from bs4 import BeautifulSoup as bs 
from tqdm import tqdm
from sqlalchemy import *
from operator import itemgetter
from time import sleep
from psycopg2.errors import UniqueViolation
from database import glados, engine


pages = range(245)
base_url = 'http://glados.biringa.com'
failed = []
extract = itemgetter('href', 'title')


def try_get(url):
    for _ in range(10):
        resp = get(url)
        if resp.ok:
            return resp
        else:
            sleep(1)
    else:
        error = resp.url, resp.status_code, resp.text
        failed.append(resp.url, resp.status_code)

print('collectings urls')
urls = []
for p in tqdm(pages):
    resp = try_get(f'{base_url}/list.php?page={p}')
    if resp:
        data = bs(resp.text).find_all('a', {'title': True})
        for d in data:
            ref, text = extract(d)
            ref = base_url+ref
            urls.append((ref, text))


with engine.connect() as cur:
    known = cur.execute(select([glados.c.text])).fetchall()
    known = set(i.text for i in known)


urls = [(url, text) for url, text in urls if text not in known]


print('collecting records')
for url, text in tqdm(urls):
    with engine.connect() as cur:
        while True:
            resp = try_get(url)
            if resp:
                try:
                    res = cur.execute(glados.insert().values(url=url, text=text, record=resp.content))
                    break
                except:
                    sleep(30)
