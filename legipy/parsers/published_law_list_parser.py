# coding: utf-8

from bs4 import BeautifulSoup
import re
from urlparse import urljoin, urlparse, parse_qs

from ..common import cleanup_url, parse_date
from ..models import Law


def parse_published_law_list(url, html):
    soup = BeautifulSoup(html, 'html5lib', from_encoding='utf-8')
    results = []

    for year_header in soup.find_all('h3'):
        year = int(year_header.get_text())
        ul = year_header.find_next_sibling('ul')

        if not ul:
            continue

        for law_entry in ul.select('li a'):
            link_text = law_entry.get_text()
            law_num = re.match(ur'LOI\s+(?:([^\s]+)\s+)?n°\s+([^\s]+)',
                               link_text, re.I)

            if not law_num:
                continue

            legi_url = cleanup_url(urljoin(url, law_entry['href']))
            legi_qs = parse_qs(urlparse(legi_url).query)

            title = law_entry.next_sibling
            pub_date = re.match(ur'\s*du\s+(\d{1,2}(?:er)?\s+[^\s]+\s+\d{4})',
                                title)

            results.append(Law(
                year=year,
                legislature=int(legi_qs['legislature'][0]),
                number=law_num.group(2),
                type='law',
                kind=law_num.group(1),
                pub_date=parse_date(pub_date.group(1)) if pub_date else None,
                title=link_text + title,
                legi_url=legi_url,
                legi_id=legi_qs['idDocument'][0]
            ))

    return results
