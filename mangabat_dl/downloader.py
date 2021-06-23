import os
import requests
import time
import re
import tqdm
import logging
from pathlib import Path
from .utils import filter_forbidden_names

log = logging.getLogger(__name__)
log.setLevel(logging.CRITICAL)

class MangabatDownloader(requests.Session):
    """
    The way its download it copied from https://github.com/choldgraf/download

    it was designed for mangabat downloader since download module
    doesn't support custom headers argument
    """
    _headers = {"referer": "https://read.mangabat.com/"}
        
    def download(
        self,
        url: str,
        manga,
        name_chapter: str,
        chapter: float,
        name_file: str,
        folder: str=None,
        progress_bar: bool=True,
        replace: bool=True,
        **requests_params
    ):
        name_manga = manga.title
        page = re.compile(r'[0-9]{1,}').search(name_file).group()
        # Base path
        if folder is not None:
            _folder = filter_forbidden_names(folder)
        else:
            _folder = None
        base = Path(_folder or os.getcwd())

        # Folder Manga path
        manga_path = base / filter_forbidden_names(name_manga)

        # Folder chapter path
        chapter_path = manga_path / filter_forbidden_names(name_chapter)
        chapter_path.mkdir(parents=True, exist_ok=True)

        # File images chapter path
        file_path = chapter_path / name_file

        # Make request
        r = self.get(url, headers=self._headers, stream=True, **requests_params)
        r.raise_for_status()

        # Get file size
        file_sizes = float(r.headers['Content-Length'])

        # Check if this file exist and have same file size
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            if file_sizes == stat.st_size:
                if not replace:
                    log.info('%s Chapter %s Page %s exist and have same size as the server has, skipping...' % (
                        name_manga,
                        chapter,
                        page
                    ), extra={"type": 'DOWNLOADER'})
                    return
            else:
                log.warning('File is exist but %s Chapter %s Page %s size doesn\'t match as the server has, re-downloading...' % (
                    name_manga,
                    chapter,
                    page
                ), extra={"type": 'DOWNLOADER'})

        log.info('Starting download %s Chapter %s page %s' % (
            name_manga,
            chapter,
            page
        ), extra={"type": 'DOWNLOADER'})

        # The parameters was adapted from 
        # https://github.com/choldgraf/download/blob/master/download/download.py#L366
        # Setting up progress bar
        if progress_bar:
            p_bar = tqdm.tqdm(
                desc='file_sizes',
                total=file_sizes,
                unit='B',
                unit_scale=True,
                ncols=80
            )
        else:
            p_bar = None

        # This was also adapted from 
        # https://github.com/choldgraf/download/blob/master/download/download.py#L377
        chunk_size = 8192  # 2 ** 13
        with open(file_path, "wb") as local_file:
            while True:
                t0 = time.time()
                chunk = r.raw.read(chunk_size)
                dt = time.time() - t0
                if dt < 0.005:
                    chunk_size *= 2
                elif dt > 0.1 and chunk_size > 8192:
                    chunk_size = chunk_size // 2
                if not chunk:
                    break
                local_file.write(chunk)
                if p_bar is not None:
                    p_bar.update(len(chunk))

        # Close the progress bar
        if p_bar is not None:
            p_bar.close()

        log.info('Finished download %s Chapter %s page %s' % (
            name_manga,
            chapter,
            page
        ), extra={"type": 'DOWNLOADER'})
