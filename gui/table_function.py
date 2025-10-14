'''从csv文件夹中读取table csv然后展示table的槽函数'''

import logging
import pandas as pd
import numpy as np
from typing import Protocol
from PySide6.QtWidgets import QWidget, QTableView, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel, QColor


class MainWindowProtocol(Protocol):
    """
    协议类，声明 ChartFunction 需要用到的主窗口属性
    """

    table_container: QWidget
    tableView: QTableView


# 设置日志
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class TableFunction:
    def __init__(self, main_window: MainWindowProtocol):
        self.main_window : MainWindowProtocol = main_window

    def show_table(self, table_data: pd.DataFrame, stretch : bool = False):
        """在table页面展示csv转换后的table数据（带自定义样式）"""

        # 使用MVC架构，创建模型
        self.model = QStandardItemModel()

        # 填充数据（跳过第一列）
        table_data_list = table_data.values.tolist()
        for i, row in enumerate(table_data_list):
            for j, value in enumerate(row):
                # 跳过第一列（索引列）
                if j == 0:
                    continue
                if "." and "%" in str(value):
                    parts = str(value).split(".")
                    item = QStandardItem(str(parts[0]+"."+parts[1][:3]+" %"))
                elif "." in str(value):
                    parts = str(value).split(".")
                    item = QStandardItem(str(parts[0]+"."+parts[1][:3]))
                else:
                    item = QStandardItem(str(value))


                # 设置内容居中
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # 设置 alternating row colors：奇偶行不同背景
                if i % 2 == 0:
                    item.setBackground(Qt.GlobalColor.transparent)
                else:
                    item.setBackground(QColor("#2b2e32"))

                # 设置字体颜色、加粗
                font = item.font()
                font.setBold(False)
                item.setFont(font)
                item.setForeground(Qt.GlobalColor.white)

                # 添加模型item（注意列索引需要调整）
                self.model.setItem(i, j-1, item)

        # 设置表头（去掉第一列的表头）
        headers = table_data.columns.tolist()
        self.model.setHorizontalHeaderLabels(headers[1:])

        # 在tableview中设置数据
        self.table = self.main_window.tableView
        self.table.setModel(self.model)

        # 拉伸列宽
        if stretch:
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        else:
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        # 交替行颜色
        self.table.setAlternatingRowColors(True)

        # 样式表 QSS
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #252526;
                color: white;
                font-weight: bold;
                border: 1px solid #2b2e32;
                padding: 4px;
            }
    
            QTableView {
                gridline-color: #2b2e32;
                background-color: transparent;
                alternate-background-color: #2b2e32;
                color: white;
                selection-background-color: #3e4146;
                selection-color: white;
            }
    
            QTableCornerButton::section {
                background-color: #252526;
                border: 1px solid #2b2e32;
            }
        """)
