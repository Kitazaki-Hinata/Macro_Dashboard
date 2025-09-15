'''从数据库中读取数据并以图标的方式展示'''

import pyqtgraph as pg
import os
import sqlite3
import logging
import numpy as np
from PySide6.QtWidgets import QVBoxLayout, QLabel  # 改为 PySide6
from PySide6.QtCore import Qt

# 设置日志
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class ChartFunction():
    def __init__(self, main_window):
        self.main_window = main_window

        # 初始化每个图表部分的图表控件
        self.init_chart_widgets(self.main_window.graph_widget_2)

        self.init_chart_widgets(self.main_window.four_chart_one)
        self.init_chart_widgets(self.main_window.four_chart_two)
        self.init_chart_widgets(self.main_window.four_chart_three)
        self.init_chart_widgets(self.main_window.four_chart_four)

    def init_chart_widgets(self, window):
        """Initialize chart widgets
        window 形参：传入需要清空的控件
        例如，window = self.main_window.graph_widiget_2"""
        # 窗口需要新建一个布局
        if window.layout() is None:
            layout = QVBoxLayout()  # 或者 QHBoxLayout()，根据你的需求
            window.setLayout(layout)

        self.single_plot_widget = pg.PlotWidget()    # create plot widget
        self.chart_title = QLabel("Data Name will be here")
        self.chart_title.setMaximumHeight(50)
        self.chart_title.setMinimumHeight(50)
        self.chart_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_title.setStyleSheet(
            '''
            font-family : "Comfortaa";
            font-weight : Normal;
            font-size : 16px;
            color : #ffffff;
            '''
        )
        window.layout().addWidget(self.chart_title)
        window.layout().addWidget(self.single_plot_widget)   # 添加图表到布局的下方
        window.layout().setContentsMargins(20, 0, 20, 20)

        self.single_plot_widget.setBackground('#262a2f')
        self.single_plot_widget.showGrid(x=True, y=True, alpha=0.15)   # 网格alpha透明度
        self.single_plot_widget.getPlotItem().getViewBox().setBackgroundColor('#262a2f')
        
        # 设置坐标轴标签字体
        font = pg.QtGui.QFont()
        font.setPixelSize(12)
        font.setFamily("Comfortaa")
        self.single_plot_widget.getAxis('left').setTickFont(font)
        self.single_plot_widget.getAxis('bottom').setTickFont(font)
        self.single_plot_widget.addLegend()

    def _get_database_path(self) -> str:
        '''内部方法，获取数据库的path'''
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "..", "data.db")


    def _get_data_from_database(self, data_name):
        '''获取database的数据
        返回两个list，第一个是date，第二个是数据'''
        try:
            db_path = self._get_database_path()
        except:
            logger.error("Failed to get database path, please download data first")
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Time_Series'")
            table_exists = cursor.fetchone()

            if not table_exists:
                logger.error("Time_Series table does not exist in database")
                conn.close()
                raise FileNotFoundError("Time_Series table does not exist")

            cursor.execute("PRAGMA table_info(Time_Series)")
            columns = [column[1] for column in cursor.fetchall()]

            if data_name not in columns:
                logger.error(f"Data column '{data_name}' not found in Time_Series table")
                conn.close()
                raise ValueError(f"Data column '{data_name}' not found")

            query = f'SELECT date, "{data_name}" FROM Time_Series WHERE "{data_name}" IS NOT NULL ORDER BY date'
            cursor.execute(query)
            data = cursor.fetchall()   # 返回tuples ((2020-01-01, 2.0), (2020-01-02, 2.1))

            if data:
                dates, values = zip(*data)
                # 处理None值并转换为float
                values = np.array(values, dtype=object)
                values = np.where(values != None, values.astype(float), 0.0)
                dates = list(dates)    # ["2020-01-01", "2020-01-02"]
                values = values.tolist()   # ["2", "2.1"]
            else:
                dates, values = [], []

            conn.close()
            return dates, values

        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return [], []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return [], []

    def plot_data(self, data_name, color : list[str] = ["#90b6e7"]):
        """Plot data to single chart，绘制数据并展示"""

        self.single_plot_widget.clear()
        # 设置轴标签字体
        font = pg.QtGui.QFont()
        font.setPixelSize(12)
        font.setFamily("Arial")
        self.single_plot_widget.setLabel('left', 'Value', color="#ffffff", **{'font-family': "Comfortaa", 'font-size': '12px'})
        self.single_plot_widget.setLabel('bottom', 'Date', color="#ffffff", **{'font-family': "Comfortaa", 'font-size': '12px'})

        dates , values = self._get_data_from_database(data_name)

        x_data = list(range(len(dates)))  # 0-很多位数，绘图的时候用这个数字，后续再将日期映射过来
        pen = pg.mkPen(color=color[0], width=2)

        self.single_plot_widget.plot(
            x=x_data,
            y=values,
            pen=pen,
            name=data_name,  # 显示在legend而不是标题头
            symbol='o',  #数据点的标记符号，o是圆形
            symbolSize=2,    #标记点大小，px像素
            symbolBrush=color[0]  # 标记点填充颜色
        )

        axis = self.single_plot_widget.getAxis('bottom')
        axis.setTicks(dates)
        # 设置坐标轴刻度标签字体
        font = pg.QtGui.QFont()
        font.setPixelSize(10)
        font.setFamily("Comfortaa")

        self.single_plot_widget.getAxis('left').setTickFont(font)
        self.single_plot_widget.getAxis('bottom').setTickFont(font)
        self.single_plot_widget.addLegend()
