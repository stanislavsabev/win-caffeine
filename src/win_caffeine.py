import sys

from win_caffeine import qt
import qdarktheme


icon_path = "assets/coffee-on.png"


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
        cw = qt.QWidget()
        lay = qt.QVBoxLayout(self)
        btn = qt.QPushButton(qt.QIcon(icon_path), "Toggle")
        lay.addWidget(btn)
        cw.setLayout(lay)
        self.setCentralWidget(cw)


def main():
    # Enable HiDPI.
    qdarktheme.enable_hi_dpi()

    # Create the application
    app = qt.QApplication([])
    is_dark = is_dark_theme(app.palette())

    qdarktheme.setup_theme("auto", default_theme="light")
    is_dark = is_dark_theme(app.palette())

    # Create the main window
    window = MainWindow()
    # Create the system tray icon
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
