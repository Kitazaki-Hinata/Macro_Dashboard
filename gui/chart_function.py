'''从数据库中读取数据并以图标的方式展示'''

import pyqtgraph as pg
import os
import sqlite3
import logging
from PySide6.QtWidgets import QVBoxLayout  # 改为 PySide6

# 设置日志
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class ChartFunction():
    def __init__(self, main_window):
        self.main_window = main_window
        self.init_chart_widgets()

    def init_chart_widgets(self):
        """Initialize chart widgets"""
        if hasattr(self.main_window, 'graph_widget_2'):
            # 清除原有布局内容
            if self.main_window.graph_widget_2.layout():
                for i in reversed(range(self.main_window.graph_widget_2.layout().count())):
                    item = self.main_window.graph_widget_2.layout().itemAt(i)
                    if item.widget():
                        item.widget().deleteLater()
            else:
                # 创建新布局实例
                self.main_window.graph_widget_2.setLayout(QVBoxLayout())

            # 创建 PlotWidget 并添加到布局中
            self.single_plot_widget = pg.PlotWidget()
            self.main_window.graph_widget_2.layout().addWidget(self.single_plot_widget)

            # 设置基本样式
            self.single_plot_widget.setBackground('w')
            self.single_plot_widget.showGrid(x=True, y=True, alpha=0.3)

    def _get_database_path(self) -> str:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "..", "data.db")

    def show_one_chart(self, data_name, chart_type: str):
        '''Display single chart with selected data'''
        db_path = self._get_database_path()

        if not os.path.exists(db_path):
            logger.error(f"Database file not found: {db_path}")
            raise FileNotFoundError(f"Database file not found: {db_path}")

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
            data = cursor.fetchall()

            dates = []
            values = []
            for date_str, value in data:
                dates.append(date_str)
                values.append(float(value) if value is not None else 0.0)

            if chart_type == "one":
                self._one_plot_data(dates, values, data_name)

            conn.close()

        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def _one_plot_data(self, dates, values, data_name):
        """Plot data to single chart"""
        if not hasattr(self, 'single_plot_widget'):
            self.init_chart_widgets()

        self.single_plot_widget.clear()
        self.single_plot_widget.setTitle(f"{data_name}", color='k', size='12pt')
        self.single_plot_widget.setLabel('left', 'Value')
        self.single_plot_widget.setLabel('bottom', 'Date')
        self.single_plot_widget.showGrid(x=True, y=True, alpha=0.3)

        x_data = list(range(len(dates)))
        pen = pg.mkPen(color='#90b6e7', width=2)

        self.single_plot_widget.plot(
            x=x_data,
            y=values,
            pen=pen,
            name=data_name,
            symbol='o',
            symbolSize=5,
            symbolBrush='#90b6e7'
        )

        axis = self.single_plot_widget.getAxis('bottom')
        tick_interval = max(1, len(dates) // 10)
        ticks = []

        for i, date_str in enumerate(dates):
            if i % tick_interval == 0 or i == len(dates) - 1:
                short_date = date_str[:10] if len(date_str) > 10 else date_str
                ticks.append((i, short_date))

        axis.setTicks([ticks])
        self.single_plot_widget.addLegend()