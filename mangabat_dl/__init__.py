from typing import Any, Generator, List
from .fetcher import _search, _fetch
from .classes import Manga, MangaResult

__version__ = 'v0.0.1'

def download_manga(mangabat_url, **params) -> Manga:
    """
    Download manga by giving manga url

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

    Return
    --------
    
    :class:`Manga` object
    """
    m = Manga(_fetch(mangabat_url))
    m.download(**params)
    return m

def fetch(mangabat_url: str) -> Manga:
    """
    Fetch mangabat url

    return :class:`Manga`
    """
    return Manga(_fetch(mangabat_url))

def search_all(query: str) -> List[MangaResult]:
    """
    Search all manga

    return :class:`List[MangaResult]`
    """
    return [MangaResult(data) for data in _search(query)]

def search(query: str) -> MangaResult:
    """
    Search 1 manga

    return :class:`MangaResult`
    """
    return MangaResult(_search(query).__next__())

def search_iter(query: str) -> Generator[MangaResult, Any, Any]:
    """
    Search manga, but it return :class:`Iterator` object

    Usage ::

        from mangabat_dl import search_iter
        for result in search_iter('Konosuba'):
            print(result)

    yield :class:`MangaResult`
    """
    for data in _search(query):
        yield MangaResult(data)