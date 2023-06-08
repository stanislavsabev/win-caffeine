from typing import List
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

    def on_enable_duration_changed(self, state):
        enabled = state == qt.Qt.CheckState.Checked
        self.duration.setEnabled(enabled)
        self.interval.setEnabled(enabled)


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
