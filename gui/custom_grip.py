'''窗口拖拽等效果的类'''

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QPoint

class CustomGrip(QWidget):
    def __init__(self, parent, edge, hover=True):
        super().__init__(parent)
        self.edge = edge
        self.setMouseTracking(True)
        self._pressed = False
        self._start_pos = QPoint()
        self._start_geom = QRect()
        self.setCursor({
            Qt.Edge.LeftEdge: Qt.SizeHorCursor,
            Qt.Edge.RightEdge: Qt.SizeHorCursor,
            Qt.Edge.TopEdge: Qt.SizeVerCursor,
            Qt.Edge.BottomEdge: Qt.SizeVerCursor,
        }[edge])
        self.update_geometry()

    def update_geometry(self):
        parent = self.parentWidget()
        if not parent:
            return
        w, h = parent.width(), parent.height()
        grip_size = 6  # 可自行调整
        if self.edge == Qt.Edge.LeftEdge:
            self.setGeometry(0, 0, grip_size, h)
        elif self.edge == Qt.Edge.RightEdge:
            self.setGeometry(w - grip_size, 0, grip_size, h)
        elif self.edge == Qt.Edge.TopEdge:
            self.setGeometry(0, 0, w, grip_size)
        elif self.edge == Qt.Edge.BottomEdge:
            self.setGeometry(0, h - grip_size, w, grip_size)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._start_pos = event.globalPosition().toPoint()
            self._start_geom = self.parentWidget().geometry()

    def mouseMoveEvent(self, event):
        if not self._pressed:
            return
        delta = event.globalPosition().toPoint() - self._start_pos
        geom = QRect(self._start_geom)
        min_width, min_height = 400, 300  # 可根据需要调整
        if self.edge == Qt.Edge.LeftEdge:
            geom.setLeft(min(geom.right() - min_width, geom.left() + delta.x()))
        elif self.edge == Qt.Edge.RightEdge:
            geom.setRight(max(geom.left() + min_width, geom.right() + delta.x()))
        elif self.edge == Qt.Edge.TopEdge:
            geom.setTop(min(geom.bottom() - min_height, geom.top() + delta.y()))
        elif self.edge == Qt.Edge.BottomEdge:
            geom.setBottom(max(geom.top() + min_height, geom.bottom() + delta.y()))
        self.parentWidget().setGeometry(geom)

    def mouseReleaseEvent(self, event):
        self._pressed = False

    def resizeEvent(self, event):
        self.update_geometry()