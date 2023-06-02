"""win_coffeine implementation."""
import functools
import sys

from win_caffeine import const
from win_caffeine import qt
from win_caffeine import screen_lock
import qdarktheme

APP_NAME = "win-caffeine"
ON_OFF_MODE = ["off", "on"]


def get_icon_path(mode, theme) -> str:
    return f"assets/coffee-{mode}-{theme}.png"


def is_dark_theme(palette: qt.QPalette) -> bool:
    text_color = palette.color(palette.Text)
    lum = sum((text_color.red(), text_color.green(), text_color.blue())) // 3
    return lum > 127


def theme_from_palette(palette) -> str:
    return "dark" if is_dark_theme(palette) else "light"


class LabeledSpinbox(qt.QWidget):
    def __init__(
        self,
        label_text: str = "",
        value: int = 0,
        min_value: int = const.MIN_INT,
        max_value: int = const.MAX_INT,
        orientation: qt.Qt.Orientation = qt.Qt.Horizontal,
        parent: qt.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        if orientation == qt.Qt.Horizontal:
            layout = qt.QHBoxLayout()
        else:
            layout = qt.QVBoxLayout()
        label = qt.QLabel(label_text)
        spin_box = qt.QSpinBox()
        spin_box.setMaximum(max_value)
        spin_box.setMinimum(min_value)
        spin_box.setValue(value)
        layout.addWidget(label)
        layout.addWidget(spin_box)
        self.setLayout(layout)
        self.label = label
        self.spin_box = spin_box


class MainWindow(qt.QMainWindow):
    def __init__(
        self,
        theme,
        parent: qt.QWidget | None = None,
        flags: qt.Qt.WindowFlags | None = None,
    ) -> None:
        flags = flags or qt.Qt.WindowFlags()
        super().__init__(parent, flags)
        self.button_icons = {mode: qt.QIcon(get_icon_path(mode, theme)) for mode in ["on", "off"]}
        self.setup_ui()

    def setup_ui(self):
        central_widget = qt.QWidget()
        central_layout = qt.QVBoxLayout()

        toggle_button = qt.QPushButton()
        toggle_button.setObjectName("toggle_button")
        toggle_button.clicked.connect(self.on_toggle_toggle_button_clicked)
        self.toggle_button = toggle_button
        self.update_toggle_button()

        mode_label = qt.QLabel(self.get_state_message())
        self.mode_label = mode_label

        enable_duration_checkbox = qt.QCheckBox("Set Duration")
        enable_duration_checkbox.stateChanged.connect(self.on_enable_duration_state_changed)
        duration_widget = LabeledSpinbox(
            "Duration (min)", 2 * const.HOUR, orientation=qt.Qt.Horizontal
        )
        interval_widget = LabeledSpinbox(
            "Refresh interval (sec)", 2 * const.MINUTE, orientation=qt.Qt.Horizontal
        )

        self.enable_duration_checkbox = enable_duration_checkbox
        self.duration_widget = duration_widget
        self.interval_widget = interval_widget
        is_duration_enabled = False
        enable_duration_checkbox.setChecked(is_duration_enabled)
        self.on_enable_duration_state_changed()

        central_layout.addWidget(enable_duration_checkbox)
        central_layout.addWidget(duration_widget)
        central_layout.addWidget(interval_widget)
        central_layout.addWidget(mode_label)
        central_layout.addWidget(toggle_button)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    def close(self) -> bool:
        return self.hide()

    def update_toggle_button(self):
        mode = ON_OFF_MODE[int(screen_lock.is_on())]
        next_mode = ON_OFF_MODE[int(not screen_lock.is_on())]
        self.toggle_button.setText(f"Turn {next_mode}")
        self.toggle_button.setIcon(self.button_icons[mode])

    def get_state_message(self) -> str:
        state = "enabled" if screen_lock.is_on() else "disabled"
        return f"Screen lock is {state}"

    def on_enable_duration_state_changed(self):
        enabled = self.enable_duration_checkbox.isChecked()
        self.duration_widget.setEnabled(enabled)
        self.interval_widget.setEnabled(enabled)

    def on_toggle_toggle_button_clicked(self):
        action = screen_lock.release_screen_lock
        if screen_lock.is_on():
            if self.enable_duration_checkbox.isChecked():
                action = functools.partial(
                    screen_lock.run_prevent_screen_lock,
                    self.duration_widget.spin_box.value(),
                    self.interval_widget.spin_box.value(),
                )
            else:
                action = screen_lock.prevent_screen_lock
        try:
            action()
        except Exception:
            self.statusBar().showMessage("Screen lock action failed!", 2)
        finally:
            self.mode_label.setText(self.get_state_message())
            self.update_toggle_button()


def gui(*args, **kwargs):
    # Enable HiDPI.
    qdarktheme.enable_hi_dpi()

    # Create the application
    app = qt.QApplication([])
    qdarktheme.setup_theme("auto", default_theme="light")

    mode = ON_OFF_MODE[screen_lock.is_on()]
    theme = theme_from_palette(app.palette())
    icon_path = get_icon_path(mode, theme)

    # Create the main window
    window = MainWindow(theme=theme)
    window.setWindowTitle(APP_NAME)
    window.setWindowIcon(qt.QIcon(icon_path))
    window.setFixedSize(qt.QSize(200, 180))

    # Create the system tray icon
    tray_icon = qt.QSystemTrayIcon(qt.QIcon(icon_path), parent=app)
    tray_icon.setToolTip(APP_NAME)

    # Create the system tray menu
    tray_menu = qt.QMenu()
    tray_menu.addAction("Restore", window.showNormal)  # Restore the main window
    tray_menu.addAction("Exit", app.quit)  # Quit the application
    tray_icon.setContextMenu(tray_menu)

    # Show the main window
    window.show()

    # Minimize to system tray
    tray_icon.show()
    app.setQuitOnLastWindowClosed(False)

    # Start the application event loop
    app.exec_()


def cmd(*args, **kwargs):
    pass


def main():
    # TODO: parse args

    # clear existing state
    screen_lock.release_screen_lock()

    # choose UI or cmd
    args = []
    gui(args)


if __name__ == "__main__":
    sys.exit(main())
