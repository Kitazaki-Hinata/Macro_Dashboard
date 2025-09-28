from gui import *
from gui.subwindows.ui_prestart import Ui_Prestart_ui


class Prestart_ui(QWidget, Ui_Prestart_ui):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)

if __name__ == "__main__":
    app = QApplication([])
    window = Prestart_ui()
    window.show()
    app.exec()