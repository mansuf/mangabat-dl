import pathlib
from setuptools import setup
import re

HERE = pathlib.Path(__file__).parent

README_PATH = (HERE / "README.md")

README = README_PATH.read_text()

# Find version without importing it
REGEX_VERSION = r'v[0-9]{1}.[0-9]{1}.[0-9]{1,3}'
VERSION = re.findall(REGEX_VERSION, (HERE / "mangabat_dl/__init__.py").read_text())[0]

setup(
  name = 'mangabat-dl',         
  packages = ['mangabat_dl'],   
  version = VERSION,
  license='The Unlicense',
  description = 'Download manga from mangabat with Python',
  long_description= README,
  long_description_content_type= 'text/markdown',
  author = 'Rahman Yusuf',              
  author_email = 'danipart4@gmail.com',
  entry_points= {
    'console_scripts': [
      'mangabat-dl=mangabat_dl.__main__:main',
    ]
  },
  url = 'https://github.com/mansuf/mangabat-dl',  
  download_url = 'https://github.com/mansuf/mangabat-dl/releases',
  keywords = ['mangabat', 'manga', 'manga-download'], 
  install_requires=[           
          'requests',
          'bs4',
          'tqdm',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: The Unlicense (Unlicense)',  
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9'
  ],
  python_requires='>=3.5'
)