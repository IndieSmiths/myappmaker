"""Facility for configurations."""

### standard library import
from pathlib import Path

### third-party imports
from PySide6.QtCore import QStandardPaths

### local imports
from .appinfo import APP_TITLE, ORG_DIR_NAME, APP_DIR_NAME



###

WRITEABLE_DIR = (
    Path(QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation))
    / ORG_DIR_NAME
    / APP_DIR_NAME
)


###

if not WRITEABLE_DIR.exists():
    WRITEABLE_DIR.mkdir(parents=True)

###

STROKES_DATA_DIR = WRITEABLE_DIR / 'strokes_data'

if not STROKES_DATA_DIR.exists():
    STROKES_DATA_DIR.mkdir()
