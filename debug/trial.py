import os
import sys
import logging
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, Protocol
from gui.chart_function import ChartFunction
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
import pyqtgraph as pg



class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQtGraph Example")
        self.resize(800, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # 创建主绘图部件
        self.main_plot_widget = pg.PlotWidget()
        self.create_chart(self.main_plot_widget)
        layout.addWidget(self.main_plot_widget)

    def create_chart(self, main_plot_widget: pg.PlotWidget):
        plot_item = main_plot_widget.getPlotItem()
        pen = pg.mkPen(color="#ffffff", width=2)

        x_data = [1,2,3]
        float_values = [4,5,6]

        font = pg.QtGui.QFont()
        font.setPixelSize(12)
        font.setFamilies(["Comfortaa"])
        right_viewbox = pg.ViewBox()
        plot_item.scene().addItem(right_viewbox)  # 添加到场景

        # 链接右侧轴
        main_plot_widget.showAxis('right')
        right_axis = main_plot_widget.getAxis('right')
        right_axis.setTickFont(font)
        right_axis.linkToView(right_viewbox)
        right_axis.setLabel(x_data, color="#ffffff")

        # 设置X轴链接
        right_viewbox.setXLink(plot_item.vb)

        # 同步视图
        def update_views():
            right_viewbox.setGeometry(plot_item.vb.sceneBoundingRect())
            right_viewbox.linkedViewChanged(plot_item.vb, right_viewbox.XAxis)

        update_views()
        plot_item.vb.sigResized.connect(update_views)

        # 添加第二个曲线到右侧ViewBox
        second_curve = pg.PlotCurveItem()
        second_curve.setData(x=x_data, y=float_values, pen=pen)
        right_viewbox.addItem(second_curve)

        # 自动调整范围
        right_viewbox.enableAutoRange(axis=pg.ViewBox.YAxis)

if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    app.exec()