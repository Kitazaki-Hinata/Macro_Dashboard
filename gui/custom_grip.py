'''窗口拖拽等效果的类'''

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QPoint

class CustomGrip(QWidget):
    def __init__(self, parent, edge_or_corner, hover=True):
        super().__init__(parent)
        self.edge_or_corner = edge_or_corner
        self.setMouseTracking(True)
        self._pressed = False
        self._start_pos = QPoint()
        self._start_geom = QRect()
        # 设置光标
        cursor_map = {
            Qt.Edge.LeftEdge: Qt.SizeHorCursor,
            Qt.Edge.RightEdge: Qt.SizeHorCursor,
            Qt.Edge.TopEdge: Qt.SizeVerCursor,
            Qt.Edge.BottomEdge: Qt.SizeVerCursor,
            Qt.TopLeftCorner: Qt.SizeFDiagCursor,
            Qt.TopRightCorner: Qt.SizeBDiagCursor,
            Qt.BottomLeftCorner: Qt.SizeBDiagCursor,
            Qt.BottomRightCorner: Qt.SizeFDiagCursor,
        }
        self.setCursor(cursor_map.get(edge_or_corner, Qt.ArrowCursor))
        self.update_geometry()

    def update_geometry(self):
        parent = self.parentWidget()
        if not parent:
            return
        w, h = parent.width(), parent.height()
        grip_size = 8  # 四角略大
        # 边缘
        if self.edge_or_corner == Qt.Edge.LeftEdge:
            self.setGeometry(0, 0, grip_size, h)
        elif self.edge_or_corner == Qt.Edge.RightEdge:
            self.setGeometry(w - grip_size, 0, grip_size, h)
        elif self.edge_or_corner == Qt.Edge.TopEdge:
            self.setGeometry(0, 0, w, grip_size)
        elif self.edge_or_corner == Qt.Edge.BottomEdge:
            self.setGeometry(0, h - grip_size, w, grip_size)
        # 四角
        elif self.edge_or_corner == Qt.TopLeftCorner:
            self.setGeometry(0, 0, grip_size, grip_size)
        elif self.edge_or_corner == Qt.TopRightCorner:
            self.setGeometry(w - grip_size, 0, grip_size, grip_size)
        elif self.edge_or_corner == Qt.BottomLeftCorner:
            self.setGeometry(0, h - grip_size, grip_size, grip_size)
        elif self.edge_or_corner == Qt.BottomRightCorner:
            self.setGeometry(w - grip_size, h - grip_size, grip_size, grip_size)

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
        # 边缘
        if self.edge_or_corner == Qt.Edge.LeftEdge:
            geom.setLeft(min(geom.right() - min_width, geom.left() + delta.x()))
        elif self.edge_or_corner == Qt.Edge.RightEdge:
            geom.setRight(max(geom.left() + min_width, geom.right() + delta.x()))
        elif self.edge_or_corner == Qt.Edge.TopEdge:
            geom.setTop(min(geom.bottom() - min_height, geom.top() + delta.y()))
        elif self.edge_or_corner == Qt.Edge.BottomEdge:
            geom.setBottom(max(geom.top() + min_height, geom.bottom() + delta.y()))
        # 四角
        elif self.edge_or_corner == Qt.TopLeftCorner:
            geom.setLeft(min(geom.right() - min_width, geom.left() + delta.x()))
            geom.setTop(min(geom.bottom() - min_height, geom.top() + delta.y()))
        elif self.edge_or_corner == Qt.TopRightCorner:
            geom.setRight(max(geom.left() + min_width, geom.right() + delta.x()))
            geom.setTop(min(geom.bottom() - min_height, geom.top() + delta.y()))
        elif self.edge_or_corner == Qt.BottomLeftCorner:
            geom.setLeft(min(geom.right() - min_width, geom.left() + delta.x()))
            geom.setBottom(max(geom.top() + min_height, geom.bottom() + delta.y()))
        elif self.edge_or_corner == Qt.BottomRightCorner:
            geom.setRight(max(geom.left() + min_width, geom.right() + delta.x()))
            geom.setBottom(max(geom.top() + min_height, geom.bottom() + delta.y()))
        self.parentWidget().setGeometry(geom)

    def mouseReleaseEvent(self, event):
        self._pressed = False

    def resizeEvent(self, event):
        self.update_geometry()