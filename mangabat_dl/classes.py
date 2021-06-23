import json
import re
import logging
import requests
import os
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path
from .constants import DOWNLOAD_MODES
from .fetcher import _fetch, _fetch_chapter_images
from .downloader import MangabatDownloader
from .utils import filter_forbidden_names

dl_log = logging.getLogger('mangabat_dl.downloader')
dl_log.setLevel(logging.CRITICAL)

class ChapterPage:
    def __init__(self, data) -> None:
        self._data = data

    @property
    def manga(self):
        """
        Get :class:`Manga` from this chapter

        return :class:`Manga`
        """
        return self._data['manga']

    @property
    def name(self) -> str:
        """
        Get chapter name

        return :class:`str`
        """
        return self._data['name']

    @property
    def chapter(self) -> float:
        """
        Get chapter number

        return :class:`float`
        """
        return self._data['chapter']

    @property
    def chapter_url(self) -> str:
        """
        Get chapter url

        return :class:`float`
        """
        return self._data['url']

    @property
    def page(self) -> int:
        """
        Get chapter page number

        return :class:`int`
        """
        file = self.page_filename
        num = int(re.compile(r'[0-9]{1,}').search(file).group())
        return num

    @property
    def page_filename(self) -> str:
        """
        Get chapter page filename (1.jpg, etc)

        return :class:`str`
        """
        r = re.compile('[0-9]{1,}.jpg')
        file = r.search(self.url).group()
        return file

    @property
    def url(self) -> str:
        """
        Get page url

        return :class:`str`
        """
        return self._data['image']

    def download(
        self,
        folder: str=None,
        progress_bar: bool=True,
        replace: bool=False,
        **requests_params
    ):
        """
        Download this chapter page
        """
        downloader = MangabatDownloader()
        downloader.download(
            self.url,
            self.manga,
            self.name,
            self.chapter,
            self.page_filename,
            folder,
            progress_bar,
            replace,
            **requests_params
        )
        downloader.close()

class Chapter:
    def __init__(self, data) -> None:
        self._data = data
        self._cached_pages = None

    @property
    def manga(self):
        """
        Get :class:`Manga` from this chapter

        return :class:`Manga`
        """
        return self._data['manga']

    @property
    def name(self) -> str:
        """
        Get chapter name

        return :class:`str`
        """
        return self._data['name']

    @property
    def chapter(self) -> float:
        """
        Get chapter number

        return :class:`float`
        """
        return self._data['chapter']

    @property
    def url(self) -> str:
        """
        Get chapter url

        return :class:`float`
        """
        return self._data['url']

    def get_all_chapter_pages(self) -> List[ChapterPage]:
        """
        Get chapter pages

        return :class:`List[ChapterPage]`
        """
        if self._cached_pages is None:
            self._cached_pages = [
                ChapterPage({
                    "name": self.name,
                    "chapter": self.chapter,
                    "url": self.url,
                    "manga": self.manga,
                    "image": i
                }) for i in _fetch_chapter_images(self.url)
            ]
        return self._cached_pages

    def download(
        self,
        start_page: int=None,
        end_page: int=None,
        folder: str=None,
        progress_bar: bool=True,
        replace: bool=False,
        **requests_params
    ):
        """
        Download this chapter

        Params
        --------
        start_page: :class:`int` (Optional)
            Set start download in given page number
        end_page: :class:`int` (Optional)
            Set finish download in given page number
        folder: :class:`str` (Optional)
            Choose folder where you want to store this chapter
        progress_bar: :class:`bool` (Optional, default: `True`)
            Set progress bar for downloading
        replace: :class:`bool` (Optional, default: `False`)
            replace file if exist
        """
        if start_page is not None and end_page is not None:
            if start_page >= end_page:
                raise ValueError('start_page cannot be same or more than end_page')

        # Start downloading all of them
        if start_page is None and end_page is None:
            for page in self.get_all_chapter_pages():
                page.download(folder, progress_bar, replace, **requests_params)
            return

        for page in self.get_all_chapter_pages():
            if page.page >= start_page:
                if end_page is not None:
                    if page.page <= end_page:
                        page.download(folder, progress_bar, replace, **requests_params)
                    else:
                        dl_log.warn('Ignoring page %s as param "end_page" is %s' % (
                            page.page,
                            end_page
                        ), extra={"type": 'DOWNLOADER'})
                        continue
                else:
                    page.download(folder, progress_bar, replace, **requests_params)
            else:
                dl_log.warn('Ignoring page %s as param "start_page" is %s' % (
                    page.page,
                    start_page
                ), extra={"type": 'DOWNLOADER'})
                continue

class Manga:
    def __init__(self, data):
        self._data = data

        # add manga class to Chapter class
        chapters = []
        for i in data['chapters']:
            copy = i.copy()
            copy['manga'] = self
            chapters.append(copy)

        self._chapters = {i['chapter']: Chapter(i) for i in chapters}
    
    @property
    def title(self) -> str:
        """
        Get manga title

        return :class:`str`
        """
        return self._data['title']

    @property
    def authors(self) -> List[str]:
        """
        Get manga authors

        return :class:`List[str]`
        """
        return self._data['authors']

    @property
    def url(self) -> str:
        """
        Get manga website url

        return :class:`str`
        """
        return self._data['url']

    @property
    def short_description(self) -> str:
        """
        Get manga description in short text

        return :class:`str`
        """
        return self._data['short_description']

    @property
    def long_description(self) -> str:
        """
        Get manga description in long text

        return :class:`str`
        """
        return self._data['long_description']

    @property
    def is_trending(self) -> bool:
        """
        Is this manga is trending right now ?

        return :class:`bool`
        """
        return self._data['is_trending']

    @property
    def alternative_titles(self) -> List[str]:
        """
        Get alternative titles manga

        return :class:`List[str]`
        """
        return self._data['alternative_titles']

    @property
    def status(self) -> str:
        """
        Get status manga

        return :class:`str`
        """
        return self._data['status']

    @property
    def genres(self) -> List[str]:
        """
        Get manga genres

        return :class:`List[str]`
        """
        return self._data['genres']

    @property
    def cover_image(self) -> str:
        """
        Get cover image manga url

        return :class:`str`
        """
        return self._data['cover_img']

    @property
    def latest_updated(self) -> datetime:
        """
        Get latest date that this manga has been updated

        return :class:`datetime`
        """
        return self._data['latest_updated']

    @property
    def views(self) -> int:
        """
        Get total views of this manga

        return :class:`int`
        """
        return self._data['total_views']

    @property
    def chapters(self) -> List[Chapter]:
        """
        Get all chapters in this manga

        return :class:`List[Chapter]`
        """
        return list(self._chapters.values())

    @property
    def latest_chapter(self) -> float:
        """
        Get latest chapter in this manga

        return :class:`float`
        """
        latest_chapter = max(list(self._chapters))
        return self._chapters[latest_chapter]

    @property
    def total_chapters(self) -> int:
        """
        Get total chapters in this manga

        return :class:`int`
        """
        return len(self._chapters)

    def to_JSON(self) -> str:
        """
        Return :class:`Manga` data in JSON format

        return :class:`str`
        """
        data = self._data.copy()
        # datetime object is not JSON serializable
        # so we need convert it to strings
        data['latest_updated'] = data['latest_updated'].strftime('%d %b %Y - %H:%M:%S')

        return json.dumps(data)

    def to_dict(self) -> dict:
        """
        Return :class:`MangaResult` data in :class:`dict` format

        return :class:`dict`
        """
        return self._data.copy()

    def download(
        self,
        start_chapter: int=None,
        end_chapter: int=None,
        folder: str=None,
        progress_bar: bool=True,
        replace: bool=False,
        mode: str="default",
        **requests_params
    ):
        """
        Download this manga

        Params
        --------
        start_chapter: :class:`int` (Optional)
            Set start download in given chapter number
        end_chapter: :class:`int` (Optional)
            Set finish download in given chapter number
        folder: :class:`str` (Optional)
            Choose folder where you want to store this manga
        progress_bar: :class:`bool` (Optional, default: `True`)
            Set progress bar for downloading
        replace: :class:`bool` (Optional, default: `False`)
            replace file if exist
        mode: :class:`str` (Optional, default: `default`)
            Set downloader mode
            Available options is `default`, `tachiyomi`.

            `default`:
                Download in default mode.
            `tachiyomi`:
                Download for Tachiyomi local / Offline manga
                https://tachiyomi.org/help/guides/local-manga/#folder-structure

        """
        if mode not in DOWNLOAD_MODES:
            raise ValueError('"%s" is not valid download mode' % mode)
        if start_chapter is not None and end_chapter is not None:
            if start_chapter >= end_chapter:
                raise ValueError('start_chapter cannot be same or more than end_chapter')

        # Start downloading all of them
        if start_chapter is None and end_chapter is None:
            for chap in self.chapters:
                chap.download(
                    folder=folder,
                    progress_bar=progress_bar,
                    replace=replace,
                    **requests_params
                )
            return

        for chap in self.chapters:
            if chap.chapter >= start_chapter:
                if end_chapter is not None:
                    if chap.chapter <= end_chapter:
                        chap.download(
                            folder=folder,
                            progress_bar=progress_bar,
                            replace=replace,
                            **requests_params
                        )
                    else:
                        dl_log.warn('Ignoring chapter %s as param "end_chapter" is %s' % (
                            chap.chapter,
                            end_chapter
                        ), extra={"type": 'DOWNLOADER'})
                        continue
                else:
                    chap.download(
                        folder=folder,
                        progress_bar=progress_bar,
                        replace=replace,
                        **requests_params
                    )
            else:
                dl_log.warn('Ignoring chapter %s as param "start_chapter" is %s' % (
                    chap.chapter,
                    start_chapter
                ), extra={"type": 'DOWNLOADER'})
                continue

        # Base path
        if folder is not None:
            _folder = filter_forbidden_names(folder)
        else:
            _folder = None
        base = Path(_folder or os.getcwd())

        # Folder Manga path
        manga_path = base / filter_forbidden_names(self.title)

        # Write some information for Tachiyomi offline manga
        if mode == 'tachiyomi':
            dl_log.info('Downloading cover "%s"' % (
                self.title
            ), extra={"type": 'DOWNLOADER'})

            # Getting cover img data
            r = requests.get(self.cover_image)
            r.raise_for_status()

            # Write it
            (manga_path / 'cover.jpg').write_bytes(r.content)

            dl_log.info('Writing manga "%s" informations in details.json' % (
                self.title
            ), extra={"type": 'DOWNLOADER'})

            # This is inside details.json
            data = {
                "title": self.title,
                "author": self.authors,
                'artist': self.authors,
                'description': self.long_description,
                'genre': self.genres,
                'status': self.status
            }

            # Write it
            (manga_path / 'details.json').write_text(json.dumps(data))

class MangaResult:
    def __init__(self, data):
        self._data = data

    def fetch(self) -> Manga:
        """
        Fetch all informations in this manga

        return :class:`Manga`
        """
        data = _fetch(self.url)
        return Manga(data)

    def __repr__(self) -> str:
        return '<MangaResult title="%s" authors="%s">' % (
            self._data['title'],
            self._data['authors']
        )

    @property
    def title(self) -> str:
        """
        Get manga title

        return :class:`str`
        """
        return self._data['title']

    @property
    def authors(self) -> List[str]:
        """
        Get manga authors

        return :class:`List[str]`
        """
        return self._data['authors']

    @property
    def url(self) -> str:
        """
        Get manga website url

        return :class:`str`
        """
        return self._data['url']

    @property
    def cover_image(self) -> str:
        """
        Get cover image manga url

        return :class:`str`
        """
        return self._data['cover_img']

    @property
    def is_trending(self) -> bool:
        """
        Is this manga is trending right now ?

        return :class:`bool`
        """
        return self._data['is_trending']

    @property
    def rating(self) -> float:
        """
        Get manga rating

        return :class:`float`
        """
        return self._data['rating']

    @property
    def latest_chapters(self) -> List[Dict[str, str]]:
        """
        Get 2 of the latest chapters manga

        return :class:`list`
        """
        return self._data['latest_chapters']

    @property
    def latest_updated(self) -> datetime:
        """
        Get latest date that this manga has been updated

        return :class:`datetime`
        """
        return self._data['latest_updated']

    @property
    def views(self) -> int:
        """
        Get total views of this manga

        return :class:`int`
        """
        return self._data['total_views']

    def to_JSON(self) -> str:
        """
        Return :class:`MangaResult` data in JSON format

        return :class:`str`
        """
        data = self._data.copy()
        # datetime object is not JSON serializable
        # so we need convert it to strings
        data['latest_updated'] = data['latest_updated'].strftime('%d %b %Y - %H:%M:%S')

        return json.dumps(data)

    def to_dict(self) -> dict:
        """
        Return :class:`MangaResult` data in :class:`dict` format

        return :class:`dict`
        """
        return self._data.copy()
