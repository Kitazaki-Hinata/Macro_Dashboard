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


class MainWindowProtocol(Protocol):
    """协议类，声明 ChartFunction 需要用到的主窗口属性
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

class OnlyXWheelViewBox(pg.ViewBox):
    def wheelEvent(self, ev):
        # 只缩放x轴
        if ev.modifiers() == Qt.ControlModifier:
            # 支持Ctrl+滚轮缩放y轴（可选）
            super().wheelEvent(ev)
            return
        # 横向缩放
        if ev.delta() != 0:
            scale = 1.02 ** (ev.delta() / 120)
            self.scaleBy((1/scale, 1))
            ev.accept()
        else:
            super().wheelEvent(ev)


class CustomViewBox(pg.ViewBox):
    # ViewBox类来处理鼠标移动事件
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.setMouseMode(self.PanMode)
        
    def mouseDragEvent(self, ev, axis=None):
        if ev.button() == Qt.LeftButton:
            # 直接调用父类处理，实现平移
            super().mouseDragEvent(ev, axis=axis)
        else:
            super().mouseDragEvent(ev, axis=axis)

    def wheelEvent(self, ev, axis=None):
        # 只缩放x轴
        if ev.modifiers() == Qt.ControlModifier:
            # 支持Ctrl+滚轮缩放y轴（可选）
            super().wheelEvent(ev, axis=axis)
            return
        # 横向缩放
        if ev.delta() != 0:
            scale = 1.02 ** (ev.delta() / 120)
            self.scaleBy((1/scale, 1))
            ev.accept()
        else:
            super().wheelEvent(ev, axis=axis)

###########################################
# 主类ChartFunction

class ChartFunction:
    def __init__(self, main_window: MainWindowProtocol) -> None:
        self.main_window: MainWindowProtocol = main_window
        # 添加存储十字线和标签的字典
        self.crosshairs = {}
        self.labels = {}

        # 保存四个四分图的plotwidget引用
        self.four_plot_widgets = {}
        self._four_charts_linked = False
        self._four_charts_mouse_conn = []
        self._four_charts_range_conn = []
        self.init_chart_widgets(self.main_window.graph_widget_2, "main_plot_widget")
        self.four_plot_widgets["four_chart_one_plot"] = self.init_chart_widgets(self.main_window.four_chart_one, "four_chart_one_plot")
        self.four_plot_widgets["four_chart_two_plot"] = self.init_chart_widgets(self.main_window.four_chart_two, "four_chart_two_plot")
        self.four_plot_widgets["four_chart_three_plot"] = self.init_chart_widgets(self.main_window.four_chart_three, "four_chart_three_plot")
        self.four_plot_widgets["four_chart_four_plot"] = self.init_chart_widgets(self.main_window.four_chart_four, "four_chart_four_plot")

    def init_chart_widgets(self, window: QWidget, object_name: str):
        """Initialize chart widgets 并设置objectName"""
        layout_obj = window.layout()
        if layout_obj is None:
            layout_obj = QVBoxLayout()
            window.setLayout(layout_obj)

        # 使用自定义的ViewBox
        self.single_plot_widget: Any = pg.PlotWidget(viewBox=CustomViewBox())

        self.single_plot_widget.setObjectName(object_name)  # 设置objectName
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
        self.chart_title.setObjectName(f"{object_name}_title")

        # layout_nn：图表的布局，Layout
        layout_nn: QLayout = cast(QLayout, layout_obj)
        layout_nn.addWidget(self.chart_title)
        layout_nn.addWidget(self.single_plot_widget)
        layout_nn.setContentsMargins(20, 0, 20, 20)

        # 设置图表widget和网格的背景颜色，以及plotitem绘图区域的颜色
        self.single_plot_widget.setBackground('#262a2f')
        self.single_plot_widget.showGrid(x=True, y=True, alpha=0.15)
        view_box = self.single_plot_widget.getPlotItem().getViewBox()
        view_box.setBackgroundColor('#262a2f')
        view_box.setMouseEnabled(x=True, y=True)

        # 下面这个强制设定只能横向移动，暂时用不上
        # self.single_plot_widget.setMouseEnabled(x=True, y=False)

        # 设置坐标轴标签字体
        font = pg.QtGui.QFont()
        font.setPixelSize(12)
        font.setFamilies(["Comfortaa"])
        self.single_plot_widget.getAxis('left').setTickFont(font)
        self.single_plot_widget.getAxis('bottom').setTickFont(font)
        self.single_plot_widget.addLegend()
        
        # 保存对标题标签的引用，以便后续访问
        if object_name == "main_plot_widget":
            self.main_plot_widget_title = self.chart_title
        if object_name == "four_chart_one_plot":
            self.four_chart_one_plot_title = self.chart_title
        if object_name == "four_chart_two_plot":
            self.four_chart_two_plot_title = self.chart_title
        if object_name == "four_chart_three_plot":
            self.four_chart_three_plot_title = self.chart_title
        if object_name == "four_chart_four_plot":
            self.four_chart_four_plot_title = self.chart_title

        # 为每个图表widget初始化十字线和标签
        v_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#ffffff', style=Qt.DashLine))
        h_line = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('#ffffff', style=Qt.DashLine))
        v_line.setOpacity(0.3)
        h_line.setOpacity(0.3)
        self.single_plot_widget.addItem(v_line, ignoreBounds=True)
        self.single_plot_widget.addItem(h_line, ignoreBounds=True)
        
        # 创建十字线右上角的移动标签
        label = pg.TextItem("", anchor=(0, 1), color='#ffffff')
        label.setFont(pg.QtGui.QFont("Comfortaa", 10))
        self.single_plot_widget.addItem(label, ignoreBounds=True)
        
        # 存入字典，保存引用以便后续访问
        self.crosshairs[object_name] = (v_line, h_line)
        self.labels[object_name] = label
        
        # 初始隐藏十字线的数字标签
        v_line.hide()
        h_line.hide()
        label.hide()
        
        # 连接鼠标移动事件
        self.single_plot_widget.scene().sigMouseMoved.connect(
            lambda pos: self.on_mouse_move(pos, object_name)
        )

        return self.single_plot_widget

    def on_mouse_move(self, pos, object_name):
        """显示十字线和数据提示"""
        # 获取对应图表的组件
        plot_widget = None
        if object_name == "main_plot_widget":
            plot_widget = self.main_window.graph_widget_2.findChild(pg.PlotWidget, "main_plot_widget")
        elif object_name == "four_chart_one_plot":
            plot_widget = self.main_window.four_chart_one.findChild(pg.PlotWidget, "four_chart_one_plot")
        elif object_name == "four_chart_two_plot":
            plot_widget = self.main_window.four_chart_two.findChild(pg.PlotWidget, "four_chart_two_plot")
        elif object_name == "four_chart_three_plot":
            plot_widget = self.main_window.four_chart_three.findChild(pg.PlotWidget, "four_chart_three_plot")
        elif object_name == "four_chart_four_plot":
            plot_widget = self.main_window.four_chart_four.findChild(pg.PlotWidget, "four_chart_four_plot")
        
        if plot_widget is None:
            return
            
        plot_item = plot_widget.getPlotItem()
        v_line, h_line = self.crosshairs[object_name]
        label = self.labels[object_name]
        
        # 检查鼠标是否在绘图区域内
        if plot_item.sceneBoundingRect().contains(pos):
            mouse_point = plot_item.vb.mapSceneToView(pos)
            x_val = mouse_point.x()
            y_val = mouse_point.y()
            
            # 更新十字线位置
            v_line.setPos(x_val)
            h_line.setPos(y_val)
            
            # 获取当前图表中的所有曲线
            items = plot_item.listDataItems()
            if items:
                # 准备显示的数据文本
                data_texts = []
                for item in items:
                    if hasattr(item, 'getData') and item.getData() is not None:
                        x_data, y_data = item.getData()
                        if x_data is not None and y_data is not None and len(x_data) > 0:
                            # 找到最接近的x值索引
                            distances = np.abs(np.array(x_data) - x_val)
                            if len(distances) > 0:
                                min_index = np.argmin(distances)
                                if min_index < len(x_data) and min_index < len(y_data):
                                    nearest_x = x_data[min_index]
                                    nearest_y = y_data[min_index]

                                    # 获取曲线名称（如果有的话）
                                    name = getattr(item, 'opts', {}).get('name', 'Data')
                                    data_texts.append(f"Date : {nearest_x}\n{name} : {nearest_y:.2f}")
                
                # 如果有数据，则更新标签文本
                if data_texts:
                    # 将所有数据项连接成多行文本
                    label_text = "\n".join(data_texts)
                    label.setText(label_text)
                    label.setPos(x_val, y_val)
            
            # 显示十字线和标签
            v_line.show()
            h_line.show()
            label.show()
        else:
            # 隐藏十字线和标签
            v_line.hide()
            h_line.hide()
            label.hide()

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

    def plot_data(self, data_name: str, color: list[str] = ["#90b6e7"], widget = None) -> None:
        """Plot data to single chart，绘制数据并展示
        widget是plot widget, self.single_plot_widget"""
        # 保存当前十字线和标签的引用
        plot_item = widget.getPlotItem()
        view_box = plot_item.getViewBox()
        object_name = widget.objectName()
        
        # 获取现有的十字线和标签
        v_line, h_line = self.crosshairs[object_name]
        label = self.labels[object_name]
        
        # 保存当前的可见状态
        v_line_visible = v_line.isVisible()
        h_line_visible = h_line.isVisible()
        label_visible = label.isVisible()
        
        # 保存当前标签的位置和文本
        label_pos = label.pos()
        label_text = label.toHtml()
        
        # 清除图表内容但保留十字线和标签
        for item in plot_item.items:
            if item not in [v_line, h_line, label]:
                plot_item.removeItem(item)
                
        # 重新添加十字线和标签以确保它们在最上层
        plot_item.addItem(v_line, ignoreBounds=True)
        plot_item.addItem(h_line, ignoreBounds=True)
        plot_item.addItem(label, ignoreBounds=True)
        
        # 恢复十字线和标签的状态
        if v_line_visible: v_line.show()
        else: v_line.hide()
            
        if h_line_visible: h_line.show()
        else: h_line.hide()
            
        if label_visible:
            label.show()
            label.setHtml(label_text)
            label.setPos(label_pos)
        else:
            label.hide()
        
        # 设置轴标签字体
        font = pg.QtGui.QFont()
        font.setPixelSize(12)
        font.setFamilies(["Comfortaa"])
        widget.setLabel('left', 'Value', color="#ffffff", **{'font-family': "Comfortaa", 'font-size': '12px'})
        widget.setLabel('bottom', 'Date', color="#ffffff", **{'font-family': "Comfortaa", 'font-size': '12px'})

        dates, values = self._get_data_from_database(data_name)

        # 同步更新标题
        if hasattr(self, 'main_plot_widget_title') and widget.objectName() == "main_plot_widget":
            self.main_plot_widget_title.setText(str(data_name))

        x_data: List[int] = list(range(len(dates)))
        pen: Any = pg.mkPen(color=color[0], width=2)  # type: ignore[reportUnknownVariableType]

        widget.plot(
            x=x_data,
            y=values,
            pen=pen,
            name=data_name
        )
        axis = widget.getAxis('bottom')

        # # 设置日期轴的刻度
        n = len(dates)
        step = max(1, n // 5)
        ticks = [(i, dates[i]) for i in range(0, n, step)]
        # 保证最后一个日期也显示
        if (n - 1) not in [i for i, _ in ticks]:
            ticks.append((n - 1, dates[-1]))
        axis.setTicks([ticks])

        # 设置坐标轴字体
        font = pg.QtGui.QFont()
        font.setPixelSize(10)
        font.setFamilies(["Comfortaa"])

        widget.getAxis('left').setTickFont(font)
        widget.getAxis('bottom').setTickFont(font)
        widget.addLegend()

        # 设置x轴范围只显示数据范围
        if x_data:
            widget.setXRange(min(x_data), max(x_data), padding=0)

    def link_four_charts(self, linked: bool):
        """联动或取消联动四个四分图的ViewBox，并同步十字线和自适应缩放、拖拽缩放"""
        widgets = [
            self.four_plot_widgets.get("four_chart_one_plot"),
            self.four_plot_widgets.get("four_chart_two_plot"),
            self.four_plot_widgets.get("four_chart_three_plot"),
            self.four_plot_widgets.get("four_chart_four_plot"),
        ]
        widgets = [w for w in widgets if w is not None]
        if not widgets or len(widgets) < 2:
            return

        # 解绑所有鼠标事件和范围同步
        # --- 修改开始 ---
        if hasattr(self, "_four_charts_mouse_conn") and self._four_charts_mouse_conn:
            for w, slot in self._four_charts_mouse_conn:
                try:
                    w.scene().sigMouseMoved.disconnect(slot)
                except Exception:
                    pass
            self._four_charts_mouse_conn.clear()
        # --- 修改结束 ---
        if hasattr(self, "_four_charts_range_conn") and self._four_charts_range_conn:
            for conn in self._four_charts_range_conn:
                try:
                    conn.disconnect()
                except Exception:
                    pass
            self._four_charts_range_conn.clear()

        if linked:
            master = widgets[0]
            master_vb = master.getViewBox()
            for w in widgets[1:]:
                vb = w.getViewBox()
                vb.setXLink(master_vb)
                vb.setYLink(master_vb)
            for w in widgets:
                w.enableAutoRange(axis='xy', enable=True)

            def sync_crosshair(pos):
                for w in widgets:
                    plot_item = w.getPlotItem()
                    if plot_item.sceneBoundingRect().contains(pos):
                        mouse_point = plot_item.vb.mapSceneToView(pos)
                        x_val = mouse_point.x()
                        y_val = mouse_point.y()
                        object_name = w.objectName()
                        v_line, h_line = self.crosshairs[object_name]
                        label = self.labels[object_name]
                        v_line.setPos(x_val)
                        h_line.setPos(y_val)
                        items = plot_item.listDataItems()
                        data_texts = []
                        for item in items:
                            if hasattr(item, 'getData') and item.getData() is not None:
                                x_data, y_data = item.getData()
                                if x_data is not None and y_data is not None and len(x_data) > 0:
                                    distances = np.abs(np.array(x_data) - x_val)
                                    if len(distances) > 0:
                                        min_index = np.argmin(distances)
                                        if min_index < len(x_data) and min_index < len(y_data):
                                            nearest_x = x_data[min_index]
                                            nearest_y = y_data[min_index]
                                            name = getattr(item, 'opts', {}).get('name', 'Data')
                                            data_texts.append(f"Date : {nearest_x}\n{name} : {nearest_y:.2f}")
                        if data_texts:
                            label_text = "\n".join(data_texts)
                            label.setText(label_text)
                            label.setPos(x_val, y_val)
                        v_line.show()
                        h_line.show()
                        label.show()
                    else:
                        object_name = w.objectName()
                        v_line, h_line = self.crosshairs[object_name]
                        label = self.labels[object_name]
                        v_line.hide()
                        h_line.hide()
                        label.hide()
            # --- 修改开始 ---
            self._four_charts_mouse_conn = []
            for w in widgets:
                # 保存 slot 以便后续 disconnect
                slot = sync_crosshair
                w.scene().sigMouseMoved.connect(slot)
                self._four_charts_mouse_conn.append((w, slot))
            # --- 修改结束 ---

            self._four_charts_range_conn = []
            def sync_range(*args, **kwargs):
                target_range = master_vb.viewRange()
                for w in widgets[1:]:
                    vb = w.getViewBox()
                    vb.blockSignals(True)
                    vb.setRange(xRange=target_range[0], yRange=target_range[1], padding=0)
                    vb.blockSignals(False)
            conn = master_vb.sigRangeChanged.connect(sync_range)
            self._four_charts_range_conn.append(conn)
            self._four_charts_linked = True
        else:
            for w in widgets:
                vb = w.getViewBox()
                vb.setXLink(None)
                vb.setYLink(None)
            self._four_charts_linked = False