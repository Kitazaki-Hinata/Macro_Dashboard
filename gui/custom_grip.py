'''窗口拖拽等效果的类'''

from typing import Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QResizeEvent, QMouseEvent

class CustomGrip(QWidget):
    def __init__(self, parent: Optional[QWidget], edge_or_corner: Qt.Edge | Qt.Corner, hover: bool = True):
        super().__init__(parent)
        self.edge_or_corner: Qt.Edge | Qt.Corner = edge_or_corner
        self.setMouseTracking(True)
        self._pressed: bool = False
        self._start_pos: QPoint = QPoint()
        self._start_geom: QRect = QRect()
        # 设置光标
        cursor_map: dict[Qt.Edge | Qt.Corner, Qt.CursorShape] = {
            Qt.Edge.LeftEdge: Qt.CursorShape.SizeHorCursor,
            Qt.Edge.RightEdge: Qt.CursorShape.SizeHorCursor,
            Qt.Edge.TopEdge: Qt.CursorShape.SizeVerCursor,
            Qt.Edge.BottomEdge: Qt.CursorShape.SizeVerCursor,
            Qt.Corner.TopLeftCorner: Qt.CursorShape.SizeFDiagCursor,
            Qt.Corner.TopRightCorner: Qt.CursorShape.SizeBDiagCursor,
            Qt.Corner.BottomLeftCorner: Qt.CursorShape.SizeBDiagCursor,
            Qt.Corner.BottomRightCorner: Qt.CursorShape.SizeFDiagCursor,
        }
        self.setCursor(cursor_map.get(edge_or_corner, Qt.CursorShape.ArrowCursor))
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
        elif self.edge_or_corner == Qt.Corner.TopLeftCorner:
            self.setGeometry(0, 0, grip_size, grip_size)
        elif self.edge_or_corner == Qt.Corner.TopRightCorner:
            self.setGeometry(w - grip_size, 0, grip_size, grip_size)
        elif self.edge_or_corner == Qt.Corner.BottomLeftCorner:
            self.setGeometry(0, h - grip_size, grip_size, grip_size)
        elif self.edge_or_corner == Qt.Corner.BottomRightCorner:
            self.setGeometry(w - grip_size, h - grip_size, grip_size, grip_size)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self._start_pos = event.globalPosition().toPoint()
            parent = self.parentWidget()
            if parent:
                self._start_geom = parent.geometry()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self._pressed:
            return
        delta = event.globalPosition().toPoint() - self._start_pos
        geom = QRect(self._start_geom)
        # 从主窗口获取最小宽度和高度
        parent = self.parentWidget()
        if not parent:
            return
        min_width = parent.minimumWidth()
        min_height = parent.minimumHeight()

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
        elif self.edge_or_corner == Qt.Corner.TopLeftCorner:
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
        elif self.edge_or_corner == Qt.Corner.TopRightCorner:
            new_right = geom.right() + delta.x()
            if new_right < geom.left() + min_width:
                new_right = geom.left() + min_width
            geom.setRight(new_right)
            
            new_top = geom.top() + delta.y()
            max_top = geom.bottom() - min_height
            if new_top > max_top:
                new_top = max_top
            geom.setTop(new_top)
        elif self.edge_or_corner == Qt.Corner.BottomLeftCorner:
            new_left = geom.left() + delta.x()
            max_left = geom.right() - min_width
            if new_left > max_left:
                new_left = max_left
            geom.setLeft(new_left)
            
            new_bottom = geom.bottom() + delta.y()
            if new_bottom < geom.top() + min_height:
                new_bottom = geom.top() + min_height
            geom.setBottom(new_bottom)
        elif self.edge_or_corner == Qt.Corner.BottomRightCorner:
            new_right = geom.right() + delta.x()
            if new_right < geom.left() + min_width:
                new_right = geom.left() + min_width
            geom.setRight(new_right)
            
            new_bottom = geom.bottom() + delta.y()
            if new_bottom < geom.top() + min_height:
                new_bottom = geom.top() + min_height
            geom.setBottom(new_bottom)

        if parent:
            parent.setGeometry(geom)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._pressed = False

    def resizeEvent(self, event: QResizeEvent):
        self.update_geometry()