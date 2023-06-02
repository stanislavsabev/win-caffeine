import sys
import PySide2.QtGui

from win_caffeine import qt
import qdarktheme


light_icon_path = "assets/coffee-on.png"
dark_icon_path = "assets/coffee-on-dark.png"


def is_dark_theme(palette: qt.QPalette) -> bool:
    text_color = palette.color(palette.Text)
    lum = sum((text_color.red(), text_color.green(), text_color.blue())) // 3
    return lum > 127


class MainWindow(qt.QMainWindow):
    def __init__(
        self,
        parent: qt.QWidget | None = None,
        flags: qt.Qt.WindowFlags | None = None,
    ) -> None:
        flags = flags or qt.Qt.WindowFlags()
        super().__init__(parent, flags)
        central_widget = qt.QWidget()
        central_layout = qt.QVBoxLayout()

        icon_path = dark_icon_path if is_dark_theme(self.palette()) else light_icon_path
        toggle_button = qt.QPushButton(qt.QIcon(icon_path), "Toggle")
        toggle_button.setObjectName("toggle_button")
        toggle_button.clicked.connect(self.on_toggle_toggle_button_clicked)
        
        central_layout.addWidget(toggle_button)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    def close(self) -> bool:
        return self.hide()

    def on_toggle_toggle_button_clicked(self):
        print('clicked')


def main():
    # Enable HiDPI.
    qdarktheme.enable_hi_dpi()

    # Create the application
    app = qt.QApplication([])
    qdarktheme.setup_theme("auto", default_theme="light")

    # Create the main window
    window = MainWindow()
    # Create the system tray icon
    icon_path = dark_icon_path if is_dark_theme(app.palette()) else light_icon_path
    tray_icon = qt.QSystemTrayIcon(qt.QIcon(icon_path), parent=app)
    tray_icon.setToolTip("App Name")

    # Create the system tray menu
    tray_menu = qt.QMenu()
    tray_menu.addAction("Restore", window.showNormal)  # Restore the main window
    tray_menu.addAction("Exit", app.quit)  # Quit the application
    tray_icon.setContextMenu(tray_menu)

    # Show the main window (optional)
    if window is not None:
        window.show()

    # Minimize to system tray
    tray_icon.show()
    app.setQuitOnLastWindowClosed(False)

    # Start the application event loop
    app.exec_()


if __name__ == "__main__":
    sys.exit(main())
