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

        # 记录原始值
        orig_left, orig_right = geom.left(), geom.right()
        orig_top, orig_bottom = geom.top(), geom.bottom()

        # 边缘
        if self.edge_or_corner == Qt.Edge.LeftEdge:
            new_left = min(geom.right() - min_width, geom.left() + delta.x())
            # 限制最小宽度，不移动窗口
            if geom.right() - new_left < min_width:
                new_left = geom.right() - min_width
            geom.setLeft(new_left)
        elif self.edge_or_corner == Qt.Edge.RightEdge:
            new_right = max(geom.left() + min_width, geom.right() + delta.x())
            if new_right - geom.left() < min_width:
                new_right = geom.left() + min_width
            geom.setRight(new_right)
        elif self.edge_or_corner == Qt.Edge.TopEdge:
            new_top = min(geom.bottom() - min_height, geom.top() + delta.y())
            if geom.bottom() - new_top < min_height:
                new_top = geom.bottom() - min_height
            geom.setTop(new_top)
        elif self.edge_or_corner == Qt.Edge.BottomEdge:
            new_bottom = max(geom.top() + min_height, geom.bottom() + delta.y())
            if new_bottom - geom.top() < min_height:
                new_bottom = geom.top() + min_height
            geom.setBottom(new_bottom)
        # 四角
        elif self.edge_or_corner == Qt.TopLeftCorner:
            new_left = min(geom.right() - min_width, geom.left() + delta.x())
            new_top = min(geom.bottom() - min_height, geom.top() + delta.y())
            if geom.right() - new_left < min_width:
                new_left = geom.right() - min_width
            if geom.bottom() - new_top < min_height:
                new_top = geom.bottom() - min_height
            geom.setLeft(new_left)
            geom.setTop(new_top)
        elif self.edge_or_corner == Qt.TopRightCorner:
            new_right = max(geom.left() + min_width, geom.right() + delta.x())
            new_top = min(geom.bottom() - min_height, geom.top() + delta.y())
            if new_right - geom.left() < min_width:
                new_right = geom.left() + min_width
            if geom.bottom() - new_top < min_height:
                new_top = geom.bottom() - min_height
            geom.setRight(new_right)
            geom.setTop(new_top)
        elif self.edge_or_corner == Qt.BottomLeftCorner:
            new_left = min(geom.right() - min_width, geom.left() + delta.x())
            new_bottom = max(geom.top() + min_height, geom.bottom() + delta.y())
            if geom.right() - new_left < min_width:
                new_left = geom.right() - min_width
            if new_bottom - geom.top() < min_height:
                new_bottom = geom.top() + min_height
            geom.setLeft(new_left)
            geom.setBottom(new_bottom)
        elif self.edge_or_corner == Qt.BottomRightCorner:
            new_right = max(geom.left() + min_width, geom.right() + delta.x())
            new_bottom = max(geom.top() + min_height, geom.bottom() + delta.y())
            if new_right - geom.left() < min_width:
                new_right = geom.left() + min_width
            if new_bottom - geom.top() < min_height:
                new_bottom = geom.top() + min_height
            geom.setRight(new_right)
            geom.setBottom(new_bottom)

        # 只改变大小，不移动窗口位置
        self.parentWidget().setGeometry(geom)

    def mouseReleaseEvent(self, event):
        self._pressed = False

    def resizeEvent(self, event):
        self.update_geometry()