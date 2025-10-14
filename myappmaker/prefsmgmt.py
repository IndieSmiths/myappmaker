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
    QSlider,

)

from PySide6.QtCore import Qt


### local imports

from .config import PREFERENCES_FILEPATH

from .ourstdlibs.pyl import load_pyl, save_pyl



### module-level objects/constants

@unique
class PreferencesKeys(Enum):
    """Enum defining dictionary keys representing preference settings."""

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

format_ratio_log_diff = "{:.2f}".format



### dialog definition

class PreferencesDialog(QDialog):
    """Dialog used for changing preferences."""

    def __init__(self, parent=None):
        """Initialize superclass and setup widgets."""

        ### initialize superclass
        super().__init__(parent)

        ### set title for dialog's window
        self.setWindowTitle('Preferences')

        ### create and store maps to assist in operations

        self.widget_map = {}
        self.widget_setter = {}
        self.slider_label_map = {}

        ### make sure preferences are ready to be read/changed
        prepare_preferences()

        ### create and populate grid layout

        grid = self.grid = QGridLayout()

        ## define and add caption labels

        row = 0

        # define

        preference_lbl = QLabel("Preference")
        value_lbl = QLabel("Value")

        preference_lbl.setStyleSheet(BOLD_TEXT_CSS)
        value_lbl.setStyleSheet(BOLD_TEXT_CSS)

        # add

        label_alignment = (
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTop
        )

        widget_alignment = Qt.AlignmentFlag.AlignLeft

        grid.addWidget(preference_lbl, row, 0, label_alignment)
        grid.addWidget(value_lbl, row, 1, widget_alignment)


        ## add label/widget pairs for each preference

        # widgets for SHOW_WIDGET_MENU_AFTER_DRAWING key

        row += 1

        key = PreferencesKeys.SHOW_WIDGET_MENU_AFTER_DRAWING.value

        btn = QPushButton("Show widget menu after drawing")

        style_button_like_label(btn)

        btn.setToolTip(
            "When enabled (default): after drawing, instead of automatically"
            " picking best match or failing, shows a menu listing widgets from"
            " best to worst matches"
        )

        btn.clicked.connect(partial(self.toggle_preference, key))
        grid.addWidget(btn, row, 0, label_alignment)

        check = self.show_widget_menu_check = QCheckBox()
        check.setChecked(PREFERENCES[key])

        self.widget_map[key] = check
        self.widget_setter[key] = check.setChecked

        check.checkStateChanged.connect(self.update_show_widget_menu)

        grid.addWidget(check, row, 1, widget_alignment)

        # widgets for RATIO_LOG_DIFF_TOLERANCE key

        row += 1

        key = PreferencesKeys.RATIO_LOG_DIFF_TOLERANCE.value

        lbl = QLabel("Width/height ratio similarity tolerance")

        lbl.setToolTip(
            "Small decimal number (default: 0.6) representing how much"
            " to tolerate differences between the width:height ratio of"
            " the drawings when comparing them."
        )

        grid.addWidget(lbl, row, 0, label_alignment)

        ratio_sld = QSlider(Qt.Orientation.Horizontal)

        ratio_sld.setRange(40, 100)
        ratio_sld.setSingleStep(1)
        value = int(PREFERENCES[key] * 100)
        ratio_sld.setValue(value)
        ratio_sld.valueChanged.connect(self.update_ratio_log_diff_tolerance_value)

        self.widget_map[key] = ratio_sld
        self.widget_setter[key] = lambda value: ratio_sld.setValue(int(value * 100))

        sld_label = QLabel(format_ratio_log_diff(PREFERENCES[key]))
        self.slider_label_map[key] = sld_label

        grid.addWidget(ratio_sld, row, 1, widget_alignment)
        grid.addWidget(sld_label, row, 2, widget_alignment)

        # widgets for MAXIMUM_TOLERABLE_HAUSDORFF_DISTANCE key

        row += 1

        key = PreferencesKeys.MAXIMUM_TOLERABLE_HAUSDORFF_DISTANCE.value

        lbl = QLabel("Tolerable veering off (pixels)")

        lbl.setToolTip(
            "The maximum number of pixels your hand is allowed to veer off"
            " from the original drawing (default: 60)"
        )

        grid.addWidget(lbl, row, 0, label_alignment)

        distance_sld = QSlider(Qt.Orientation.Horizontal)

        distance_sld.setRange(20, 100)
        distance_sld.setSingleStep(1)
        value = PREFERENCES[key]
        distance_sld.setValue(value)
        distance_sld.valueChanged.connect(
            self.update_maximum_tolerable_hausdorff_distance_value
        )

        self.widget_map[key] = distance_sld
        self.widget_setter[key] = distance_sld.setValue

        sld_label = QLabel(str(value))
        self.slider_label_map[key] = sld_label

        grid.addWidget(distance_sld, row, 1, widget_alignment)
        grid.addWidget(sld_label, row, 2, widget_alignment)

        ### create and add "Close" and "Set Default" buttons

        row += 1

        defaults_btn = QPushButton("Restore defaults")
        defaults_btn.clicked.connect(self.restore_defaults)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)

        grid.addWidget(defaults_btn, row, 0)
        grid.addWidget(close_btn, row, 1)

        ### flag to indicate when restoring defaults
        self.restoring_defaults = False

        ### finally set grid as teh layout for this dialog
        self.setLayout(self.grid)

    def update_show_widget_menu(self, state):
        """Update preference referring to usage of a widget menu."""

        ### if restoring defaults, exit method earlier
        if self.restoring_defaults:
            return

        ### otherwise, define value based on given state

        if state == Qt.CheckState.Checked:
            value = True

        elif state == Qt.CheckState.Unchecked:
            value = False

        ### but also watch out for invalid state (error)

        else:

            raise RuntimeError(
                "Checkbox shouldn't have a state other than Checked/Unchecked"
            )

        ### reaching this point, mean we have a valid state (value), so we
        ### update the preference's file

        PREFERENCES[
            PreferencesKeys.SHOW_WIDGET_MENU_AFTER_DRAWING.value
        ] = value

        try: save_pyl(PREFERENCES, PREFERENCES_FILEPATH)

        ### again, while watching out for errors

        except Exception as err:
            print(f"Failed to save preferences: {err}")

    def toggle_preference(self, key):
        """Toggle preference related to given key."""

        widget = self.widget_map[key]

        widget.setCheckState(
            getattr(
                Qt.CheckState,
                'Checked' if not widget.isChecked() else 'Unchecked',
            )
        )

    def update_ratio_log_diff_tolerance_value(self, value):
        """Update ratio log diff tolerance preference."""

        ### update text on slider

        ## convert value to float representing a hundredth of widget's value
        value /= 100

        ## update slider

        key = PreferencesKeys.RATIO_LOG_DIFF_TOLERANCE.value

        self.slider_label_map[key].setText(format_ratio_log_diff(value))

        ### if restoring defaults, stop at this point of the method

        if self.restoring_defaults:
            return

        ### otherwise, also update the preferences file

        PREFERENCES[key] = value

        try: save_pyl(PREFERENCES, PREFERENCES_FILEPATH)

        ### while watching out for possible errors

        except Exception as err:
            print(f"Failed to save preferences: {err}")

    def update_maximum_tolerable_hausdorff_distance_value(self, value):
        """Update maximum tolerable Hausdorff distance preference."""

        ### update text on slider

        key = PreferencesKeys.MAXIMUM_TOLERABLE_HAUSDORFF_DISTANCE.value
        self.slider_label_map[key].setText(str(value))

        ### if restoring defaults, stop at this point of the method

        if self.restoring_defaults:
            return

        ### otherwise, also update the preferences file

        PREFERENCES[key] = value

        try: save_pyl(PREFERENCES, PREFERENCES_FILEPATH)

        ### while watching out for possible errors

        except Exception as err:
            print(f"Failed to save preferences: {err}")

    def restore_defaults(self):
        """Restore defaults for all preferences."""

        ### turn flag on
        self.restoring_defaults = True

        ### update values on preferences dictionary and
        ### respective widgets

        for key, value in DEFAULT_PREFERENCES.items():

            PREFERENCES[key] = value
            self.widget_setter[key](value)

        ### update the preferences file
        try: save_pyl(PREFERENCES, PREFERENCES_FILEPATH)

        ### while watching out for possible errors

        except Exception as err:
            print(f"Failed to save preferences: {err}")

        ### turn flag off
        self.restoring_defaults = False


### helper functions

def validate_preferences(preferences):
    """Validate given preferences."""

    ### ensure every value in the given preferences dictionary
    ### has the same type of the value in the respective key in
    ### the default preferences dictionary

    for key, default_value in DEFAULT_PREFERENCES.items():

        ## get type of default value
        default_value_type = type(default_value)

        ## if corresponding key exists in given preferences,
        ## the respective value must be of same type as the
        ## default value, otherwise a type error is raised

        if key in preferences:

            actual_value_type = type(preferences[key])

            if default_value_type != actual_value_type:

                raise TypeError(
                    f"If the '{key!r}' key is present in preferences,"
                    f" it must be of {default_value_type} type, not of"
                    f" {actual_value_type} type"
                )

def style_button_like_label(button):
    """Style given button to look just like a regular label."""

    button.setStyleSheet("""
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

def prepare_preferences():
    """Setup to prepare/load preferences."""

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
