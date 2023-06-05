import sys
from typing import Callable

from win_caffeine import qt


class QWorkerSignals(qt.QObject):
    before_start = qt.Signal()
    result = qt.Signal(object)
    error = qt.Signal(tuple)  # Tuple[Type[BaseException], BaseException, TracebackType]
    finished = qt.Signal()
    progress = qt.Signal(str)


class QWorker(qt.QRunnable):
    def __init__(self, func: Callable, *args, **kwargs) -> None:
        super(QWorker, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = QWorkerSignals()
        self.kwargs["progress_callback"] = self.signals.progress.emit

    def run(self) -> None:
        try:
            self.signals.before_start.emit()
            result = self.func(*self.args, **self.kwargs)
        except Exception:
            self.signals.error.emit(sys.exc_info())
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
