import sys

from win_caffeine import qt
from win_caffeine import screen_lock
import qdarktheme

APP_NAME = "win-caffeine"
ON_OFF_MODE = {
    True: "off",
    False: "on",
}


def get_icon_path(mode, theme) -> str:
    return f"assets/coffee-{mode}-{theme}.png"


def is_dark_theme(palette: qt.QPalette) -> bool:
    text_color = palette.color(palette.Text)
    lum = sum((text_color.red(), text_color.green(), text_color.blue())) // 3
    return lum > 127


def theme_from_palette(palette) -> str:
    return "dark" if is_dark_theme(palette) else "light"


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
        central_layout.addWidget(mode_label)
        central_layout.addWidget(toggle_button)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    def close(self) -> bool:
        return self.hide()

    def update_toggle_button(self):
        mode = ON_OFF_MODE[screen_lock.is_on()]
        next_mode = ON_OFF_MODE[not screen_lock.is_on()]
        self.toggle_button.setText(f"Turn {next_mode}")
        self.toggle_button.setIcon(self.button_icons[mode])

    def get_state_message(self) -> str:
        state = "disabled" if screen_lock.is_on() else "enabled"
        return f"Screen lock is {state}"

    def on_toggle_toggle_button_clicked(self):
        action = screen_lock.prevent_screen_lock
        if screen_lock.is_on():
            action = screen_lock.release_screen_lock
        try:
            action()
        except Exception:
            self.statusBar().showMessage("Screen lock action failed!", 2)
        finally:
            self.mode_label.setText(self.get_state_message())


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
