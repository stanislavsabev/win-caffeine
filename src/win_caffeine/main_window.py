"""Main GUI window."""
from types import TracebackType
from typing import Tuple, Type

from win_caffeine import settings
from win_caffeine import utils
from win_caffeine import qt
from win_caffeine import screen_lock
from win_caffeine import qworker


class LabeledSpinbox(qt.QWidget):
    def __init__(
        self,
        label_text: str = "",
        value: int = 0,
        min_value: int = settings.MIN_INT,
        max_value: int = settings.MAX_INT,
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


class DurationWidget(qt.QWidget):
    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent)
        self.checkbox = qt.QCheckBox("Set Duration")
        self.checkbox.stateChanged.connect(self.on_enable_duration_changed)
        self.duration = LabeledSpinbox(
            "Duration (min)", 2 * settings.HOUR, orientation=qt.Qt.Horizontal
        )
        self.interval = LabeledSpinbox(
            "Refresh interval (sec)", 2 * settings.MINUTE, orientation=qt.Qt.Horizontal
        )
        layout = qt.QVBoxLayout()
        layout.addWidget(self.checkbox)
        layout.addWidget(self.duration)
        layout.addWidget(self.interval)
        self.setLayout(layout)

    def on_enable_duration_changed(self):
        enabled = self.checkbox.isChecked()
        self.duration.setEnabled(enabled)
        self.interval.setEnabled(enabled)


class MainWindow(qt.QMainWindow):
    def __init__(
        self,
        parent: qt.QWidget | None = None,
        flags: qt.Qt.WindowFlags | None = None,
    ) -> None:
        flags = flags or qt.Qt.WindowFlags()
        super().__init__(parent, flags)
        self.toggle_button_icons = {
            "on": qt.QIcon(settings.IconPath.coffee_on),
            "off": qt.QIcon(settings.IconPath.coffee_off),
        }
        self.thread_pool = qt.QThreadPool()
        self.mode_label = qt.QLabel()
        self.toggle_button = qt.QPushButton()
        self.settings_button = qt.QPushButton()
        self.exit_button = qt.QPushButton()
        self.duration_widget = DurationWidget()
        self.central_widget = qt.QWidget()
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        central_layout = qt.QVBoxLayout()
        self.mode_label.setText(self.get_state_message())
        self.duration_widget.checkbox.setChecked(False)
        self.duration_widget.on_enable_duration_changed()

        self.setup_buttons()
        buttons_layout = qt.QHBoxLayout()
        buttons_layout.addWidget(self.toggle_button)
        buttons_layout.addWidget(self.settings_button)
        buttons_layout.addWidget(self.exit_button)
        central_layout.addWidget(self.duration_widget)
        central_layout.addWidget(self.mode_label)
        central_layout.addLayout(buttons_layout)
        self.central_widget.setLayout(central_layout)
        self.setCentralWidget(self.central_widget)

    def setup_buttons(self):
        self.toggle_button.setObjectName("toggle_button")
        self.settings_button.setObjectName("settings_button")
        self.exit_button.setObjectName("exit_button")
        for btn in [self.settings_button, self.exit_button]:
            btn.setFixedSize(qt.QSize(25, 25))

        self.toggle_button.setToolTip("Settings")
        self.toggle_button.setIcon(qt.QIcon(settings.IconPath.SETTINGS))

    def connect_signals(self):
        self.toggle_button.clicked.connect(self.on_toggle_button_clicked)
        self.settings_button.clicked.connect(self.on_settings_button_clicked)
        self.exit_button.clicked.connect(self.on_exit_button_clicked)
        self.update_toggle_button()

    def close(self) -> bool:
        return self.hide()

    def update_toggle_button(self):
        mode = "on"
        next_mode = "off"
        if screen_lock.is_on():
            mode, next_mode = next_mode, mode
        self.toggle_button.setIcon(self.toggle_button_icons[mode])
        self.toggle_button.setText(f"Turn {next_mode}")

    def get_state_message(self) -> str:
        state = "enabled" if screen_lock.is_on() else "disabled"
        return f"Screen lock is {state}"

    def on_toggle_button_clicked(self):
        action = self.stop_screen_lock
        if screen_lock.is_on():
            if self.duration_widget.checkbox.isChecked():
                action = self.run_prevent_lock_duration
            else:
                action = screen_lock.prevent_screen_lock

        try:
            action()
        except Exception:
            self.statusBar().showMessage("Screen lock action failed!", 2)
        finally:
            self.mode_label.setText(self.get_state_message())
            self.update_toggle_button()

    def on_settings_button_clicked(self):
        pass

    def on_exit_button_clicked(self):
        pass

    def stop_screen_lock(self):
        if not screen_lock.is_on():
            if self.duration_widget.checkbox.isChecked():
                screen_lock.reset_end_time()
            screen_lock.release_screen_lock()

    def run_prevent_lock_duration(self):
        if not self.duration_widget.isEnabled():
            self.statusBar().showMessage("Duration lock prevent is running!", 2)
            return

        worker = qworker.QWorker(
            screen_lock.run_prevent_screen_lock,
            self.duration_widget.duration.spin_box.value(),
            self.duration_widget.interval.spin_box.value(),
        )
        worker.signals.error.connect(self.on_duration_error)
        worker.signals.before_start.connect(self.on_before_start)
        worker.signals.finished.connect(self.on_finished)
        worker.signals.progress.connect(self.on_progress)
        # worker.run()
        self.thread_pool.start(worker)

    def on_duration_error(
        self,
        exc_info: Tuple[Type[BaseException], BaseException, TracebackType],
    ):
        exc_type, exc, tb = exc_info
        print(exc.args)

    def on_before_start(
        self,
    ):
        self.duration_widget.setEnabled(False)

    def on_finished(
        self,
    ):
        self.mode_label.setText(self.get_state_message())
        self.duration_widget.setEnabled(True)
        self.duration_widget.on_enable_duration_changed()

    def on_progress(self, msg: str):
        td_str = utils.get_time_hh_mm_ss(int(msg))
        self.mode_label.setText(self.get_state_message() + f" ({td_str})")
