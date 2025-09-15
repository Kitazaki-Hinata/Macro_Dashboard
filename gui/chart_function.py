'''从数据库中读取数据并以图标的方式展示'''

# Pylance/pyright 在 pyqtgraph 上缺少类型存根；在此处局部忽略
import pyqtgraph as pg  # type: ignore[reportMissingTypeStubs]
import os
import sqlite3
import logging
import numpy as np
from typing import Any, Sequence, Tuple, List, Protocol, cast
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget, QLayout  # 改为 PySide6
from PySide6.QtCore import Qt

# if TYPE_CHECKING:
#     # 仅在类型检查时导入更多符号（当前无需额外内容）
#     pass


class MainWindowProtocol(Protocol):
    """仅声明 ChartFunction 需要用到的主窗口属性。

    将这些属性约束为 QWidget，有助于 Pylance 推断 .layout()/setLayout()/addWidget 等成员类型。
    """

    graph_widget_2: QWidget
    four_chart_one: QWidget
    four_chart_two: QWidget
    four_chart_three: QWidget
    four_chart_four: QWidget

# 设置日志
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class ChartFunction:
    def __init__(self, main_window: MainWindowProtocol) -> None:
        self.main_window: MainWindowProtocol = main_window

        # 初始化每个图表部分的图表控件
        self.init_chart_widgets(self.main_window.graph_widget_2)

        self.init_chart_widgets(self.main_window.four_chart_one)
        self.init_chart_widgets(self.main_window.four_chart_two)
        self.init_chart_widgets(self.main_window.four_chart_three)
        self.init_chart_widgets(self.main_window.four_chart_four)

    def init_chart_widgets(self, window: QWidget) -> None:
        """Initialize chart widgets
        window 形参：传入需要清空的控件
        例如，window = self.main_window.graph_widiget_2"""
        # 窗口需要新建一个布局
        layout_obj = window.layout()
        if layout_obj is None:
            layout_obj = QVBoxLayout()  # 或者 QHBoxLayout()，根据你的需求
            window.setLayout(layout_obj)

        self.single_plot_widget: Any = pg.PlotWidget()    # create plot widget
        self.chart_title: QLabel = QLabel("Data Name will be here")
        self.chart_title.setMaximumHeight(50)
        self.chart_title.setMinimumHeight(50)
        self.chart_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_title.setStyleSheet(
            '''
            font-family : "Comfortaa", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
            font-weight : Normal;
            font-size : 16px;
            color : #ffffff;
            '''
        )
        layout_nn: QLayout = cast(QLayout, layout_obj)
        layout_nn.addWidget(self.chart_title)
        layout_nn.addWidget(self.single_plot_widget)   # 添加图表到布局的下方
        layout_nn.setContentsMargins(20, 0, 20, 20)

        self.single_plot_widget.setBackground('#262a2f')
        self.single_plot_widget.showGrid(x=True, y=True, alpha=0.15)   # 网格alpha透明度
        plot_item = self.single_plot_widget.getPlotItem()
        view_box = plot_item.getViewBox()
        if view_box is not None:
            view_box.setBackgroundColor('#262a2f')
        
        # 设置坐标轴标签字体
        font = pg.QtGui.QFont()
        font.setPixelSize(12)
        font.setFamilies(["Comfortaa", "Microsoft YaHei UI", "Segoe UI", "Arial"])
        self.single_plot_widget.getAxis('left').setTickFont(font)
        self.single_plot_widget.getAxis('bottom').setTickFont(font)
        self.single_plot_widget.addLegend()

    def _get_database_path(self) -> str:
        '''内部方法，获取数据库的path'''
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "..", "data.db")


    def _get_data_from_database(self, data_name: str) -> Tuple[List[str], List[float]]:
        '''获取database的数据
        返回两个list，第一个是date，第二个是数据（float）'''
        db_path = self._get_database_path()

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
                # 明确指定返回的精确类型
                dates = [str(d) for d in dates]    # ["2020-01-01", "2020-01-02"]
                values = [float(x) for x in values.tolist()]   # [2.0, 2.1]
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

    def plot_data(self, data_name: str, color: Sequence[str] = ("#90b6e7",)) -> None:
        """Plot data to single chart，绘制数据并展示"""
        self.single_plot_widget.clear()
        # 设置轴标签字体
        font = pg.QtGui.QFont()
        font.setPixelSize(12)
        font.setFamilies(["Comfortaa", "Microsoft YaHei UI", "Segoe UI", "Arial"])
        self.single_plot_widget.setLabel('left', 'Value', color="#ffffff", **{'font-family': "Comfortaa, Microsoft YaHei UI, Segoe UI, Arial, sans-serif", 'font-size': '12px'})
        self.single_plot_widget.setLabel('bottom', 'Date', color="#ffffff", **{'font-family': "Comfortaa, Microsoft YaHei UI, Segoe UI, Arial, sans-serif", 'font-size': '12px'})

        dates, values = self._get_data_from_database(data_name)

        # 同步更新标题
        self.chart_title.setText(str(data_name))

        # 0-很多位数，绘图的时候用这个数字，后续再将日期映射过来
        x_data: List[int] = list(range(len(dates)))
        pen: Any = pg.mkPen(color=color[0], width=2)  # type: ignore[reportUnknownVariableType]

        self.single_plot_widget.plot(
            x=x_data,
            y=values,
            pen=pen,
            name=data_name,  # 显示在legend而不是标题头
            symbol='o',  # 数据点的标记符号，o是圆形
            symbolSize=2,    # 标记点大小，px像素
            symbolBrush=color[0]  # 标记点填充颜色
        )

        axis = self.single_plot_widget.getAxis('bottom')
        # pyqtgraph 期望 setTicks 接收形如 [[(index, label), ...]] 的列表
        ticks: List[tuple[int, str]] = [(i, dates[i]) for i in range(len(dates))]
        axis.setTicks([ticks])

        # 设置坐标轴刻度标签字体
        font = pg.QtGui.QFont()
        font.setPixelSize(10)
        font.setFamilies(["Comfortaa", "Microsoft YaHei UI", "Segoe UI", "Arial"])

        self.single_plot_widget.getAxis('left').setTickFont(font)
        self.single_plot_widget.getAxis('bottom').setTickFont(font)
        self.single_plot_widget.addLegend()
