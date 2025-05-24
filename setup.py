from setuptools import setup

APP = ['circle-crop-gui/src/main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['PIL'],
    'includes': ['tkinter', 'PIL.ImageTk', 'PIL.Image', 'PIL.ImageDraw'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)