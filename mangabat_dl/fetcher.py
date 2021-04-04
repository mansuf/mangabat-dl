import requests
import bs4

session = requests.Session()

def fetch_manga_chapter_info(chapter_url):
    r = session.get(chapter_url, cookies={'content_server': 'server2'})

    parser = bs4.BeautifulSoup(r.text, 'html.parser')

    urls = []
    for element in parser.find('div', attrs={'class': ['container-chapter-reader']}).find_all('img'):
        urls.append(element.attrs['src'])

    return urls

def fetch_manga_info(mangabat_url, fetch_images_chapters=False):
    r = session.get(mangabat_url)

    parser = bs4.BeautifulSoup(r.text, 'html.parser')

    data = {}

    # Finding title
    data['title'] = parser.find('h1').decode_contents()

    # Finding short description
    data['short-description'] = parser.find('meta', attrs={'property': 'og:description'}).attrs['content']
    # data['description'] = parser.find('div', id='panel-story-info-description').decode_contents().replace('<br/>', '\n').replace('<br>', '\n').replace('</br>', '\n')

    # Find init for alt-titles, authors, status, genres
    _info = []
    for element in parser.find_all('td'):
        if 'table-value' in  element.attrs['class']:
            _info.append(element)
        else:
            continue

    # Finding alternative titles
    data['alternative-titles'] = _info[0].find('h2').decode_contents()

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

    # Finding cover image
    for element in parser.find_all('span'):
        try:
            element.attrs['class']
        except KeyError:
            continue
        else:
            if 'info-image' in element.attrs['class']:
                data['cover-img'] = element.find('img').attrs['src']
                break
            else:
                continue

    # Finding chapters
    chapters = []
    for element in parser.find('ul', attrs={'class': ['row-content-chapter']}).find_all('li'):
        a = element.find('a')
        data_chap = {}
        data_chap['name'] = a.decode_contents()
        data_chap['url'] = a.attrs['href']
        if fetch_images_chapters:
            data_chap['image-urls'] = fetch_manga_chapter_info(a.attrs['href'])
        chapters.append(data_chap)
    data['chapters'] = chapters
    return data