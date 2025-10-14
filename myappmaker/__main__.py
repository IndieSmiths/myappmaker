"""Facility for launching the application - myappmaker.

Myappmaker: visual desktop app builder with features for both non-technical
and technical users, including block coding and many more.
"""

### standard library import
import sys


### third-party import
from PySide6.QtWidgets import QApplication


### local imports

from .appinfo import ORG_DIR_NAME, APP_DIR_NAME

from .mainwindow import MainWindow



def main():
    """Instantiate app, its main window and start app's loop."""

    ### instantiate app and do extra setups

    app = QApplication(sys.argv)
    app.setOrganizationName(ORG_DIR_NAME)
    app.setApplicationName(APP_DIR_NAME)

    ### instantiate and show window

    window = MainWindow(app)
    window.show()

    ### start app's loop
    app.exec()


### when file is run as script, execute main()

if __name__ == "__main__":
    main()
