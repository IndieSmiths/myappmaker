"""Facility for configurations."""

### standard library import
from pathlib import Path


### third-party imports

from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QCursor


### local imports
from .appinfo import APP_TITLE, ORG_DIR_NAME, APP_DIR_NAME



### anonymous object holding references for the whole package

REFS = type('ReferenceNamespace', (), {})()
REFS.cursor = QCursor()


### define a location (directory) we can use to write data for this app;
###
### if it doesn't exist, create it

WRITEABLE_DIR = (

    Path(
        QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
    )

    / ORG_DIR_NAME
    / APP_DIR_NAME

)

if not WRITEABLE_DIR.exists():
    WRITEABLE_DIR.mkdir(parents=True)


### define other useful paths under our writeable directory,

## filepath for preferences data
PREFERENCES_FILEPATH = WRITEABLE_DIR / 'preferences.pyl'

## directory for storing strokes data (create if doesn't exist
## already)

STROKES_DATA_DIR = WRITEABLE_DIR / 'strokes_data'

if not STROKES_DATA_DIR.exists():
    STROKES_DATA_DIR.mkdir()
