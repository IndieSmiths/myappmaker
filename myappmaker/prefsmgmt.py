"""Facility for managing preferences."""

### standard library imports

from enum import Enum, unique

from functools import partial

### third-party imports

## PySide6

from PySide6.QtWidgets import (

    QDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QCheckBox,

)

from PySide6.QtCore import Qt


### local imports

from .config import PREFERENCES_FILEPATH

from .ourstdlibs.pyl import load_pyl, save_pyl



### TODO add label and controls for the new preferences
### (ratio log diff tolerance and max tolerable Hausdorff distance)



### module-level objects/constants

@unique
class PreferencesKeys(Enum):
    SHOW_WIDGET_MENU_AFTER_DRAWING = 'show_widget_menu_after_drawing'
    RATIO_LOG_DIFF_TOLERANCE = 'ratio_log_diff_tolerance'
    MAXIMUM_TOLERABLE_HAUSDORFF_DISTANCE = (
        'maximum_tolerable_hausdorff_distance'
    )

DEFAULT_PREFERENCES = {
    PreferencesKeys.SHOW_WIDGET_MENU_AFTER_DRAWING.value: True,
    PreferencesKeys.RATIO_LOG_DIFF_TOLERANCE.value: 0.6,
    PreferencesKeys.MAXIMUM_TOLERABLE_HAUSDORFF_DISTANCE.value: 60,
}

PREFERENCES = DEFAULT_PREFERENCES.copy()

BOLD_TEXT_CSS = 'font-weight: bold;'



### dialog definition

class PreferencesDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle('Preferences')

        ###
        self.widget_map = {}

        ###
        prepare_preferences()

        ###

        grid = self.grid = QGridLayout()

        ### define captions, labels and widgets

        ## caption labels

        preference_lbl = QLabel("Preference")
        value_lbl = QLabel("Value")

        preference_lbl.setStyleSheet(BOLD_TEXT_CSS)
        value_lbl.setStyleSheet(BOLD_TEXT_CSS)

        ## add caption labels

        label_alignment = (
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTop
        )

        widget_alignment = Qt.AlignmentFlag.AlignLeft


        grid.addWidget(preference_lbl, 0, 0, label_alignment)
        grid.addWidget(value_lbl, 0, 1, widget_alignment)

        ### add label/widget pairs for each preference

        key = PreferencesKeys.SHOW_WIDGET_MENU_AFTER_DRAWING.value

        btn = get_button_like_label("Show widget menu after drawing")

        btn.setToolTip(
            "When enabled (default): after drawing, instead of automatically"
            " picking best match or failing, shows a menu listing widgets from"
            " best to worst matches"
        )

        btn.clicked.connect(partial(self.toggle_preference, key))
        grid.addWidget(btn, 1, 0, label_alignment)

        check = self.show_widget_menu_check = QCheckBox()
        self.widget_map[key] = check

        check.setCheckState(
            getattr(
                Qt.CheckState,
                'Checked' if PREFERENCES[key] else 'Unchecked',
            )
        )

        check.checkStateChanged.connect(self.update_show_widget_menu)

        grid.addWidget(check, 1, 1, widget_alignment)


        ###

        ###
        self.setLayout(self.grid)

    def update_show_widget_menu(self, state):

        if state == Qt.CheckState.Checked:
            value = True

        elif state == Qt.CheckState.Unchecked:
            value = False

        else:

            raise RuntimeError(
                "Checkbox shouldn't have a state other than Checked/Unchecked"
            )

        PREFERENCES[
            PreferencesKeys.SHOW_WIDGET_MENU_AFTER_DRAWING.value
        ] = value

        try: save_pyl(PREFERENCES, PREFERENCES_FILEPATH)
        except Exception as err:
            print(f"Failed to save preferences: {err}")

    def toggle_preference(self, key):

        widget = self.widget_map[key]

        widget.setCheckState(
            getattr(
                Qt.CheckState,
                'Checked' if not widget.isChecked() else 'Unchecked',
            )
        )


### helper functions

def validate_preferences(preferences):

    for key, default_value in DEFAULT_PREFERENCES.items():

        value_type = type(default_value)

        if (
            key in preferences
            and value_type != type(preferences[key])
        ):

            raise TypeError(
                f"If the '{key!r}' key is present in preferences,"
                f" it must of {value_type} type"
            )

def get_button_like_label(text):

    btn = QPushButton(text)

    btn.setStyleSheet("""
    QPushButton {
        border: none;
        background: transparent;
        text-align: left;
        color: palette(window-text);
    }
    QToolTip {
        background-color: #333;
        color: #fff;
        border: 1px solid #ccc;
        padding: 2px;
    }
    """)

    return btn

def prepare_preferences():

    ### if the preferences file doesn't exist, create it

    if (
        not PREFERENCES_FILEPATH.is_file()
        and not PREFERENCES_FILEPATH.exists()
    ):

        try: save_pyl(PREFERENCES, PREFERENCES_FILEPATH)
        except Exception as err:
            print(f"Failed to create preferences file: {err}")

    ### load preferences

    else:

        try: prefs = load_pyl(PREFERENCES_FILEPATH)

        except Exception as err:

            print(
                "Preferences couldn't be loaded (using defaults instead):"
                f" {err}"
            )

        else:

            try: validate_preferences(prefs)

            except Exception as err:

                print(
                    "Loaded preferences didn't validate"
                    f" (using defaults instead): {err}"
                )

            else:
                PREFERENCES.update(prefs)
