from typing import List
import typing
from win_caffeine import qt
from win_caffeine import settings


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
        self.label = qt.QLabel(label_text)
        self.spin_box = qt.QSpinBox()
        self.spin_box.setMaximum(max_value)
        self.spin_box.setMinimum(min_value)
        layout.addWidget(self.label)
        layout.addWidget(self.spin_box)
        self.setLayout(layout)
        self.setValue(value)

    def setValue(self, value: int):
        self.spin_box.setValue(value)

    def value(self) -> int:
        return self.spin_box.value()

    def setText(self, text: str):
        self.label.setText(text)

    def text(self) -> int:
        return self.label.text()


class DurationModel(typing.Protocol):
    duration_minutes: int
    refresh_interval_sec: int


class DurationWidget(qt.QWidget):
    def __init__(self, model: DurationModel, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent)
        self._model = model
        self.checkbox = qt.QCheckBox("Set Duration")
        self.checkbox.stateChanged.connect(self.on_enable_duration_changed)
        self.duration = LabeledSpinbox("Duration (min)", value=0, orientation=qt.Qt.Horizontal)
        self.interval = LabeledSpinbox(
            "Refresh interval (sec)", value=0, orientation=qt.Qt.Horizontal
        )
        layout = qt.QVBoxLayout()
        layout.addWidget(self.checkbox)
        layout.addWidget(self.duration)
        layout.addWidget(self.interval)
        self.setLayout(layout)
        self.duration.spin_box.valueChanged.connect(self.on_duration_changed)
        self.interval.spin_box.valueChanged.connect(self.on_interval_changed)

    def setEnabled(self, enabled: bool):
        self.duration.setEnabled(enabled)
        self.interval.setEnabled(enabled)
        super().setEnabled(enabled)

    def on_enable_duration_changed(self, state: qt.Qt.CheckState):
        enabled = state == qt.Qt.CheckState.Checked
        self.duration.setEnabled(enabled)
        self.interval.setEnabled(enabled)

    def on_duration_changed(self, value):
        self._model.duration_minutes = value

    def on_interval_changed(self, value):
        self._model.refresh_interval_sec = value


class RadioButtonGroup(qt.QWidget):
    def __init__(
        self,
        options: List[str],
        default_ndx: int = 0,
        exclusive: bool = None,
        parent: qt.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        buttons_group = qt.QButtonGroup(self)
        if exclusive is not None:
            buttons_group.setExclusive(exclusive)

        layout = qt.QHBoxLayout()
        for ndx, option in enumerate(options):
            btn = qt.QRadioButton(option)
            btn.setObjectName(option)
            buttons_group.addButton(btn, ndx)
            if ndx == default_ndx:
                btn.setChecked(True)
            layout.addWidget(btn)
        self.setLayout(layout)
        self.buttons_group = buttons_group

    def setButtonChecked(self, ndx):
        self.buttons_group.button(ndx).setChecked(True)
