import sys
from urllib.parse import urljoin
import xbmcgui
import xbmcplugin
import requests
from bs4 import BeautifulSoup
from .plugin2 import m

BASE_URL = 'https://doomovies.net'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
HEADERS = {"User-Agent": USER_AGENT, "Referer": BASE_URL}
SESSION = requests.Session()


def get_page(url: str, referer: str = '') -> str:
    if referer:
        HEADERS['Referer'] = referer
    return SESSION.get(url, headers=HEADERS, timeout=10).text

def get_soup(url: str, referer: str = '') -> BeautifulSoup:
    response = get_page(url, referer)
    return BeautifulSoup(response, 'html.parser')
    
def main():
    sub_menu(urljoin(BASE_URL, '/release/2023/'))

def sub_menu(url: str):
    if not '/page/' in url:
        url = urljoin(url, 'page/1')
    soup = get_soup(url)
    movies = soup.find_all(class_='item movies')
    for movie in movies:
        title = movie.h3.a.text
        link = movie.h3.a['href']
        thumbnail = movie.img['src']
        quality = movie.span.text
        title = f'{title} ({quality})'
        m.add_dir(title, link, 'doo_links', thumbnail, m.addon_fanart, title, isFolder=False)
    pages = []
    pagination = soup.find(class_='pagination')
    if pagination:
        for a in pagination.find_all('a'):
            if a.text and a.text not in pages:
                pages.append(a.text)
                title = a.text
                link = a['href']
                m.add_dir(f'Page {title}', link, 'doo_submenu', m.addon_icon, m.addon_fanart, f'Page {title}')

def get_links(url: str):
    links = []
    _ids = []
    soup = get_soup(url)
    for dooplay in soup.find_all(class_='dooplay_player_option'):
        play_num = dooplay['data-nume']
        label = dooplay.span.text
        if str(label).lower() == 'watch trailer':
            continue
        _id = dooplay['data-post']
        link = urljoin(BASE_URL, f'/wp-json/dooplayer/v2/{_id}/movie/{play_num}')
        links.append([label, link])
    tbody = soup.find('tbody')
    if tbody:
        for tr in tbody.find_all('tr'):
            if 'English' in str(tr):
                label = tr.a.text
                link = tr.a['href']
                links.append([label, link])
    return links

def play_video(title, url, thumbnail):
    links = get_links(url)
    link = m.get_multilink(links)
    if not link:
        quit()
    if 'dooplayer' in link:
        page = SESSION.get(link, headers=HEADERS, timeout=10).json()
        link = page.get('embed_url')
    else:
        link = SESSION.get(link, headers=HEADERS, timeout=10).url
    if not link:
        sys.exit()
    try:
        import resolveurl
        if resolveurl.HostedMediaFile(link).valid_url():
            link = resolveurl.HostedMediaFile(link).resolve()
    except:
        pass
    liz = xbmcgui.ListItem(title, path=link)
    liz.setInfo('video', {'title': title, 'plot':title})
    liz.setArt({'thumb': thumbnail, 'icon': thumbnail, 'poster': thumbnail})
    liz.setProperty('IsPlayable', 'true')
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, liz)
    return True
  
            
def runner(p: dict):
    name = p.get('name', '')
    url = p.get('url', '')
    mode = p.get('mode')
    icon = p.get('icon', m.addon_icon)
    description = p.get('description', '')
    page = p.get('page', '')
    if page: page = int(page)
    
    m.set_content('movies')
    
    if mode == 'doo_main':
        main()
    elif mode == 'doo_submenu':
        sub_menu(url)
    elif mode == 'doo_links':
        play_video(name, url, icon)
    m.end_directory()