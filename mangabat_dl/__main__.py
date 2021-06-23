import argparse
import logging
from mangabat_dl import fetch
from mangabat_dl.constants import DOWNLOAD_MODES

parser = argparse.ArgumentParser(description='Download manga from mangabat')
parser.add_argument('MANGABAT_URL', help='A valid mangabat url')
parser.add_argument('--quiet', '-q', help='No output', action='store_true')
parser.add_argument('--start-chapter', help='Begin download from given chapter number', type=float)
parser.add_argument('--end-chapter', help='Finish download from given chapter number', type=float)
parser.add_argument('--replace', '-r', help='Replace manga if exist', action='store_true')
parser.add_argument('--folder', '-f', help='Store manga in given folder')
parser.add_argument(
    '--download-mode',
    help='Set download mode, available options is "default" and "tachiyomi"', 
    choices=DOWNLOAD_MODES
)

downloader_log = logging.getLogger('mangabat_dl.downloader')

args = parser.parse_args()

if not args.quiet:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(type)s | %(message)s')
    handler.setFormatter(formatter)
    downloader_log.addHandler(handler)
    downloader_log.setLevel(logging.INFO)

manga = fetch(args.MANGABAT_URL)
manga.download(
    args.start_chapter,
    args.end_chapter,
    args.folder,
    not args.quiet,
    args.replace,
    "default" if args.download_mode is None else args.download_mode
)
