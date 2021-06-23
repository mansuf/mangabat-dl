import requests
import bs4
import urllib.parse
import io
import re
import logging
from datetime import datetime
from .utils import convert_query_search
from .constants import MANGABAT_SEARCH_URL
from .errors import MangaNotFound, Mangabat404

log = logging.getLogger(__name__)

def _fetch_chapter_images(chapter_url):
    r = requests.get(chapter_url)
    r.raise_for_status()
    parser = bs4.BeautifulSoup(r.text, 'html.parser')
    urls = []
    for element in parser.find('div', attrs={'class': ['container-chapter-reader']}).find_all('img'):
        urls.append(element.attrs['src'])
    return urls

def _fetch(mangabat_url):
    r = requests.get(mangabat_url)
    r.raise_for_status()

    # Check if this page is exist
    if '404 - PAGE NOT FOUND' in r.text:
        raise Mangabat404('the page you\'re looking for is not exist')
    parser = bs4.BeautifulSoup(r.text, 'html.parser')

    data = {}

    # Finding title
    data['title'] = parser.find('h1').decode_contents()

    # Finding absolute url
    data['url'] = parser.find('link', {'rel': 'canonical'}).attrs['href']

    # Finding short description
    data['short_description'] = parser.find('meta', attrs={'property': 'og:description'}).attrs['content']

    # Finding long description
    long_desc_parser = parser.find('div', {'id': 'panel-story-info-description'})
    long_descriptions = ''
    for text in long_desc_parser.strings:
        long_descriptions += text
    data['long_description'] = long_descriptions

    # Is this manga is trending / Hot ?
    hot = parser.find('em', {'class': ['item-hot']})
    if hot is None:
        data['is_trending'] = False
    else:
        data['is_trending'] = True

    # Find init for alt-titles, authors, status, genres
    _info = []
    for element in parser.find_all('td'):
        if 'table-value' in  element.attrs['class']:
            _info.append(element)
        else:
            continue

    # Finding alternative titles
    at = _info[0].find('h2').decode_contents()
    if ';' in at:
        at = [i.strip() for i in io.StringIO(at.replace(';', '\n')).readlines()]
    else:
        at = [at]
    data['alternative_titles'] = at

    # Finding authors
    authors = []
    for i in _info[1].find_all('a'):
        authors.append(i.decode_contents())
    data['authors'] = authors

    # Finding status manga
    data['status'] = _info[2].decode_contents()

    # Finding genres
    genres = []
    for i in _info[3].find_all('a'):
        genres.append(i.decode_contents())
    data['genres'] = genres

    # Finding total views
    views = parser.find('i', {'class': ['info-view']}).parent.parent
    data['total_views'] = int(views.find('span', {'class': ['stre-value']}).decode_contents().replace(',', ''))

    # Finding latest updated
    updated = parser.find('i', {'class': ['info-time']}).parent.parent
    date = updated.find('span', {'class': ['stre-value']}).decode_contents()
    lu = re.compile(r'PM|AM').sub('', date).strip()
    data['latest_updated'] = datetime.strptime(lu, '%b %d,%Y - %H:%M')


    # Finding cover image
    for element in parser.find_all('span'):
        try:
            element.attrs['class']
        except KeyError:
            continue
        else:
            if 'info-image' in element.attrs['class']:
                data['cover_img'] = element.find('img').attrs['src']
                break
            else:
                continue

    # Finding chapters
    chapters = []
    for element in parser.find('ul', attrs={'class': ['row-content-chapter']}).find_all('li'):
        a = element.find('a')
        data_chap = {}
        name = a.decode_contents()
        url = a.attrs['href']
        # This is Chapter name
        data_chap['name'] = name

        # This is chapter number
        r = re.compile(r'chap-[0-9.]{1,}')
        data_chap['chapter'] = float(r.search(url).group().replace('chap-', '').strip())

        # This is chapter url
        data_chap['url'] = url
        chapters.append(data_chap)

    # Reverse the chapters as it starts from zero
    chapters.reverse()
    data['chapters'] = chapters
    return data

def _search_parse_manga(body, results):
    parser = bs4.BeautifulSoup(body, 'html.parser')
    rs = parser.find('div', {'class': ['panel-list-story']}).find_all('div', {'class': 'list-story-item'})
    for r in rs:
        data = {}
        # Finding title, and manga url
        a = r.find('a')
        data['title'] = a.attrs['title']
        data['url'] = a.attrs['href']

        # Finding author
        at = r.find('span', {'class': ['item-author']}).attrs['title']
        data['authors'] = [i.strip() for i in io.StringIO(at.replace(',', '\n'))]

        # Finding cover image
        img = a.find('img')
        data['cover_img'] = img.attrs['src']

        # Is this manga is trending / Hot ?
        hot = a.find('em', {'class': ['item-hot']})
        if hot is None:
            data['is_trending'] = False
        else:
            data['is_trending'] = True

        # Finding rating manga
        data['rating'] = float(a.find('em', {'class': ['item-rate']}).decode_contents())
        
        # Finding latest chapters
        latest_chapters = []
        chapters = r.find_all('a', {'class': ['item-chapter']})
        for c in chapters:
            chapter = {}
            chapter['url'] = c.attrs['href']
            chapter['title'] = c.attrs['title']
            latest_chapters.append(chapter)
        data['latest_chapters'] = latest_chapters

        # Finding latest updated and total view manga
        _init = r.find_all('span', {'class': ['item-time']})

        # Parsing latest update into datetime object
        lu = _init[0].decode_contents()
        data['latest_updated'] = datetime.strptime(lu, 'Updated : %b %d,%Y - %H:%M')

        # Parsing total view into integer object
        tv = _init[1].decode_contents()
        data['total_views'] = int(re.compile(r'[0-9,]{1,}').search(tv).group().replace(',', ''))

        results.append(data)

def _search(query):
    alias = convert_query_search(query)
    url = MANGABAT_SEARCH_URL + urllib.parse.quote(alias)
    r = requests.get(url)
    r.raise_for_status()

    parser = bs4.BeautifulSoup(r.text, 'html.parser')
    results = []

    # Check if we're looking for is exist
    exist = parser.find('div', {'class': ['panel-list-story']})
    if exist is None:
        raise MangaNotFound('manga "%s" cannot be found' % query)


    # Finding pages result
    pages = []
    ps = parser.find('div', {'class': ['group-page']})
    # Indicating that results search have more than 1 page
    if ps is not None:
        for p in ps.find_all('a'):
            try:
                # Indicating that this is last page
                if 'page-last' in p.attrs['class']:
                    pages.append(p.attrs['href'])
                # Indicating that we're in current page
                elif 'page-blue' in p.attrs['class']:
                    continue
            # Indicating this is pages that we're looking for
            except KeyError:
                pages.append(p.attrs['href'])

    # Do parsing in page 1
    _search_parse_manga(r.text, results)

    for r in results:
        yield r

    # Do parsing in next pages
    for page in pages:
        r = requests.get(page)
        n_results = []
        _search_parse_manga(r.text, n_results)
        for r in n_results:
            yield r
