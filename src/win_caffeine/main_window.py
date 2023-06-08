"""Main GUI window."""
from types import TracebackType
from typing import Callable, Tuple, Type

from win_caffeine import settings
from win_caffeine import utils
from win_caffeine import qt
from win_caffeine import custom_widgets as widgets
from win_caffeine import screen_lock
from win_caffeine import qworker


STATUS_MESSAGE_DURATION_MSEC = 3000


class MainWindow(qt.QMainWindow):
    """Main window."""

    def __init__(
        self,
        parent: qt.QWidget | None = None,
        flags: qt.Qt.WindowFlags | None = None,
    ) -> None:
        """Main window."""
        flags = flags or qt.Qt.WindowFlags()
        super().__init__(parent, flags)
        self.toggle_button_icons = {
            "on": qt.QIcon(settings.icon_path.coffee_on),
            "off": qt.QIcon(settings.icon_path.coffee_off),
        }
        self.toggle_action: Callable = None
        self.thread_pool = qt.QThreadPool()
        self.duration_widget = widgets.DurationWidget()
        self.method_widget = widgets.RadioButtonGroup(
            options=["NumLock", "Thread Exec State"], exclusive=True, default_opt_index=0
        )
        self.state_label = qt.QLabel()
        self.toggle_button = qt.QPushButton()
        self.settings_button = qt.QPushButton()
        self.exit_button = qt.QPushButton()
        self.central_widget = qt.QWidget()
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        central_layout = qt.QVBoxLayout()
        self.state_label.setText(self.get_state_message())
        self.duration_widget.checkbox.setChecked(False)
        self.duration_widget.on_enable_duration_changed(True)
        method_layout = qt.QVBoxLayout()
        method_layout.addWidget(qt.QLabel("Suspend method"))
        method_layout.addWidget(self.method_widget)
        self.setup_buttons()
        buttons_layout = qt.QHBoxLayout()
        buttons_layout.addWidget(self.toggle_button)
        buttons_layout.addWidget(self.settings_button)
        buttons_layout.addWidget(self.exit_button)
        central_layout.addLayout(method_layout)
        central_layout.addWidget(self.duration_widget)
        central_layout.addWidget(self.state_label)
        central_layout.addLayout(buttons_layout)
        self.central_widget.setLayout(central_layout)
        self.setCentralWidget(self.central_widget)
        self.setup_window()
        self.settings_button.setVisible(False)

    def setup_window(self):
        self.setWindowTitle(settings.APP_NAME)
        self.setWindowIcon(qt.QIcon(settings.icon_path.coffee_on))
        self.setFixedWidth(settings.WINDOW_FIXED_WIDTH)
        self.setFixedHeight(settings.WINDOW_FIXED_HEIGHT)

    def setup_buttons(self):
        self.toggle_button.setObjectName("toggle_button")
        self.settings_button.setObjectName("settings_button")
        self.exit_button.setObjectName("exit_button")
        for btn in [self.settings_button, self.exit_button]:
            btn.setFixedSize(qt.QSize(25, 25))
        self.settings_button.setIcon(qt.QIcon(settings.icon_path.settings))
        self.exit_button.setIcon(qt.QIcon(settings.icon_path.exit))
        self.settings_button.setToolTip("Settings")
        self.exit_button.setToolTip("Exit")
        self.method_widget.buttons_group.buttonClicked.connect(self.on_method_button_clicked)
        self.method_widget.setToolTip("Suspend method")

    def connect_signals(self):
        self.toggle_button.clicked.connect(self.on_toggle_button_clicked)
        self.update_toggle_state()
        self.settings_button.clicked.connect(self.on_settings_button_clicked)
        self.exit_button.clicked.connect(qt.QApplication.instance().quit)

    def close(self) -> bool:
        return self.hide()

    def update_toggle_state(self):
        print("self.update_toggle_state()")
        mode = "off"
        next_mode = "on"
        if screen_lock.is_suspend_screen_lock_on():
            mode, next_mode = next_mode, mode
            self.toggle_action = self.release_suspend_lock
            print("self.toggle_action = self.release_suspend_lock")
        else:
            self.toggle_action = self.run_suspend_lock
            print("self.toggle_action = self.run_suspend_lock")
        self.toggle_button.setIcon(self.toggle_button_icons[mode])
        self.toggle_button.setText(f"Turn {next_mode}")
        self.state_label.setText(self.get_state_message())

    def get_state_message(self) -> str:
        state = "disabled" if not screen_lock.is_suspend_screen_lock_on() else "enabled"
        return f"Suspend screen lock is {state}"

    def on_toggle_button_clicked(self):
        try:
            self.toggle_action()
        except Exception:
            self.statusBar().showMessage(
                "Screen lock action failed!", STATUS_MESSAGE_DURATION_MSEC
            )
        finally:
            self.update_toggle_state()

    def on_settings_button_clicked(self):
        print("Show settings dialog")

    def on_method_button_clicked(self, object):
        print("Key was pressed, id is:", self.method_widget.buttons_group.id(object))

    def release_suspend_lock(self):
        screen_lock.reset_duration_time()
        screen_lock.release_screen_lock_suspend()

    def run_suspend_lock(self):

        if not self.duration_widget.isEnabled():
            self.statusBar().showMessage(
                "Duration lock suspend is running!", STATUS_MESSAGE_DURATION_MSEC
            )
            return

        if self.duration_widget.checkbox.isChecked():
            worker = qworker.QWorker(
                screen_lock.duration_suspend_screen_lock,
                self.duration_widget.duration.spin_box.value(),
                self.duration_widget.interval.spin_box.value(),
            )
            worker.signals.error.connect(self.on_duration_error)
            worker.signals.before_start.connect(self.on_before_start)
            worker.signals.finished.connect(self.on_finished)
            worker.signals.progress.connect(self.on_progress)
            # worker.run()
            self.thread_pool.start(worker)
        else:
            screen_lock.suspend_screen_lock()

    def on_duration_error(
        self,
        exc_info: Tuple[Type[BaseException], BaseException, TracebackType],
    ):
        _, exc, _ = exc_info
        print(exc.args)

    def on_before_start(
        self,
    ):
        self.duration_widget.setEnabled(False)

    def on_finished(
        self,
    ):
        self.duration_widget.setEnabled(True)
        self.update_toggle_state()

    def on_progress(self, msg: str):
        td_str = utils.get_time_hh_mm_ss(int(msg))
        self.state_label.setText(self.get_state_message() + f" ({td_str})")
