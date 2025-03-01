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

    app = QApplication(sys.argv)
    app.setOrganizationName(ORG_DIR_NAME)
    app.setApplicationName(APP_DIR_NAME)

    window = MainWindow()
    window.show()

    app.exec()


### when file is run as script...

if __name__ == "__main__":

    ### execute main()
    main()
