from time import sleep, perf_counter
import bs4
import requests
import re
from collections import deque
from random import uniform
from momonga import ArticleRepository
from ReferredLink import ReferredLink


def raw_content(href, retries=3):
    headers = {
        'User-Agent': 'Wikipedia-Article-Analyser/0.0 (https://put.poznan.pl/; pawel.charkiewicz@student.put.poznan.pl)'
    }

    for attempt in range(retries):
        try:
            response = requests.get("https://en.wikipedia.org" + href, headers=headers, timeout=10)
            response.raise_for_status()
            return bs4.BeautifulSoup(response.text, 'html.parser'), response.text
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                sleep(uniform(5, 10))
            else:
                print("All retry attempts failed.")
                return None, None


def extract_links(content, referral):
    links = set()
    if content:
        for link in content.find_all('a', href=True):
            href = link['href']

            if not re.match(r'/wiki/[^:]+$', href):
                continue

            if re.search(r'/(File|Category|Help|Template|Special|Wikipedia):', href):
                continue

            if href.startswith('#') or 'action=edit' in href:
                continue

            if re.search(r'/wiki/(Lists_|List_of_)', href):
                continue

            if re.search(r'/wiki/.*#.*', href):
                continue

            links.add(ReferredLink(href.rstrip(), referral))

    return links


repository = ArticleRepository()

stored_links = repository.stored_links()
search_links = deque(repository.explorable_links())

MAX_CAP = 1000

total = len(stored_links)+1
current = 1

start, end, mean = None, None, 7.5
while search_links or total <= MAX_CAP:
    link = search_links.popleft()
    if link in stored_links:
        print(f'Link {link.link} is already in the db, skipping...')
        continue
    if start is None or end is None:
        pass
    else:
        mean += (end-start-mean) / current
    print(f'Processing {link.link}. {current} of session, {total} overall, {MAX_CAP-total} to go, ETA {round((MAX_CAP-total) * mean)} seconds')

    start = perf_counter()

    content, raw = raw_content(link.link)
    if raw is None:
        print(f"Unable to process {link.link}, skipping...")
        start, end = None, None
        sleep(uniform(5, 10))
    links = extract_links(content, link.link)

    # Repository-wise operations come first
    repository.store_article(link.link, raw, [link.referral])
    repository.remove_explorable_link(link.link)
    repository.add_explorable_links(links-set(search_links))

    links_in_stored = links.intersection(stored_links)
    links_in_explorable = links.difference(stored_links)
    repository.update_stored_referrals(links_in_stored, link.link)
    repository.update_explorable_referrals(links_in_explorable, link.link)

    # Then the local shenanigans
    stored_links.add(link)
    search_links.extend(links - stored_links)

    current += 1
    total += 1

    print("Polite crawlers go mimimi...")
    sleep(uniform(5, 10))

    end = perf_counter()


