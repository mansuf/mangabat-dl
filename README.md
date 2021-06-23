# mangabat-dl

Download manga from mangabat with python

## Minimum Python version

```
3.5.x
```

## Installation

### Python Packages Index (PyPI)
```
pip install mangabat-dl
```

### Compiled for Windows 7, 8, and 10 (Using pyinstaller, CLI Only)
[download here](https://github.com/mansuf/mangabat-dl/releases)

**NOTE**: According [`pyinstaller`](https://github.com/pyinstaller/pyinstaller) it should support Windows 7,
but its recommended to use it on Windows 8+

### From the source

Clone the repository
```
git clone https://github.com/mansuf/mangabat-dl.git
cd mangabat-dl
```

And then run `setup.py`
```
python setup.py install
```

## Usage

### Command Line Interface (CLI)

<details>
    <summary>
        Options
    </summary>

```
MANGABAT_URL            A valid mangabat url
--quiet, -q             No output
--start-chapter         Begin download from given chapter number
--end-chapter           Finish download from given chapter number
--replace, -r           Replace manga if exist
--folder, -f            Store manga in given folder
--download-mode         Set download mode, available options is "default" and "tachiyomi"
```

</details>

<details>
    <summary>
        Example Usage
    </summary>

```
mangabat-dl "give mangabat url here"
```
</details>

### Embedding
Use `mangabat-dl` in your python script
<details>
    <summary>
        Usage
    </summary>

```python

import mangabat_dl

# Search 1 manga
result = mangabat_dl.search('hunter')

print(result)

# Output: <MangaResult title="..." authors="['...']">

manga = result.fetch()

print(manga.title)

# Output: ...

# Search all manga
results = mangabat_dl.search_all('hunter')

# Output: [<MangaResult title="..." authors="['...']">, ...]

# Search manga but return Iterator class
for manga in mangabat_dl.search_iter('hunter'):
    print(manga)

# Fetch manga from mangabat url
manga = mangabat_dl.fetch('give mangabat url here')

...

# Download manga from mangabat url

manga = mangabat_dl.download_manga('give mangabat url here')

...

```

</details>

