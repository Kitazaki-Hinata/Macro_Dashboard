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
        grip_size = 8
        # edge 边缘
        if self.edge_or_corner == Qt.Edge.LeftEdge:
            self.setGeometry(0, 0, grip_size, h)
        elif self.edge_or_corner == Qt.Edge.RightEdge:
            self.setGeometry(w - grip_size, 0, grip_size, h)
        elif self.edge_or_corner == Qt.Edge.TopEdge:
            self.setGeometry(0, 0, w, grip_size)
        elif self.edge_or_corner == Qt.Edge.BottomEdge:
            self.setGeometry(0, h - grip_size, w, grip_size)
        # angles 四角
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
        # 从主窗口获取最小宽度和高度
        min_width = self.parentWidget().minimumWidth()
        min_height = self.parentWidget().minimumHeight()

        if self.edge_or_corner == Qt.Edge.LeftEdge:
            new_left = geom.left() + delta.x()
            max_left = geom.right() - min_width
            if new_left > max_left:
                new_left = max_left
            geom.setLeft(new_left)
        elif self.edge_or_corner == Qt.Edge.RightEdge:
            new_right = geom.right() + delta.x()
            if new_right < geom.left() + min_width:
                new_right = geom.left() + min_width
            geom.setRight(new_right)
        elif self.edge_or_corner == Qt.Edge.TopEdge:
            new_top = geom.top() + delta.y()
            max_top = geom.bottom() - min_height
            if new_top > max_top:
                new_top = max_top
            geom.setTop(new_top)
        elif self.edge_or_corner == Qt.Edge.BottomEdge:
            new_bottom = geom.bottom() + delta.y()
            if new_bottom < geom.top() + min_height:
                new_bottom = geom.top() + min_height
            geom.setBottom(new_bottom)
        elif self.edge_or_corner == Qt.TopLeftCorner:
            # 左上角同时处理
            new_left = geom.left() + delta.x()
            max_left = geom.right() - min_width
            if new_left > max_left:
                new_left = max_left
            geom.setLeft(new_left)
            
            new_top = geom.top() + delta.y()
            max_top = geom.bottom() - min_height
            if new_top > max_top:
                new_top = max_top
            geom.setTop(new_top)
        elif self.edge_or_corner == Qt.TopRightCorner:
            new_right = geom.right() + delta.x()
            if new_right < geom.left() + min_width:
                new_right = geom.left() + min_width
            geom.setRight(new_right)
            
            new_top = geom.top() + delta.y()
            max_top = geom.bottom() - min_height
            if new_top > max_top:
                new_top = max_top
            geom.setTop(new_top)
        elif self.edge_or_corner == Qt.BottomLeftCorner:
            new_left = geom.left() + delta.x()
            max_left = geom.right() - min_width
            if new_left > max_left:
                new_left = max_left
            geom.setLeft(new_left)
            
            new_bottom = geom.bottom() + delta.y()
            if new_bottom < geom.top() + min_height:
                new_bottom = geom.top() + min_height
            geom.setBottom(new_bottom)
        elif self.edge_or_corner == Qt.BottomRightCorner:
            new_right = geom.right() + delta.x()
            if new_right < geom.left() + min_width:
                new_right = geom.left() + min_width
            geom.setRight(new_right)
            
            new_bottom = geom.bottom() + delta.y()
            if new_bottom < geom.top() + min_height:
                new_bottom = geom.top() + min_height
            geom.setBottom(new_bottom)

        self.parentWidget().setGeometry(geom)

    def mouseReleaseEvent(self, event):
        self._pressed = False

    def resizeEvent(self, event):
        self.update_geometry()