# An easy to use compiling mangabat-dl
# Using PyInstaller
# DO NOT IMPORT FROM ANOTHER PYTHON SCRIPT
import re
import PyInstaller.__main__
from pathlib import Path

# Base path
base = Path(__name__).parent

# Find version without importing it
script = (base / 'mangabat_dl' / '__init__.py').read_text()
regex = re.compile(r'v[0-9]{1}.[0-9]{1}.[0-9]{1,3}')
version = regex.search(script).group()

# Compile for one-file bundled executable.
PyInstaller.__main__.run([
    'mangabat_dl/__main__.py',
    '-F',
    '--name',
    'mangabat-dl_%s_packed_x64' % version
])

# Re-import PyInstaller module to prevent errors
import PyInstaller.__main__

# Compile for one-folder bundle containing an executable
PyInstaller.__main__.run([
    'mangabat_dl/__main__.py',
    '--name',
    'mangabat-dl_%s_x64' % version
])
