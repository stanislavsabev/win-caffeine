from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Create the application
app = QApplication([])

# Create the main window (optional)
window = QMainWindow()  # Replace with your main window class or use None

# Create the system tray icon
tray_icon = QSystemTrayIcon(QIcon("icon.png"), parent=app)
tray_icon.setToolTip("App Name")

# Create the system tray menu
tray_menu = QMenu()
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
