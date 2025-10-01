'''从数据库中读取数据并以图标的方式展示'''

# Pylance/pyright 在 pyqtgraph 上缺少类型存根；在此处局部忽略
from turtle import clear
import pyqtgraph as pg  # type: ignore[reportMissingTypeStubs]
try:
    from pyqtgraph.graphicsItems.LegendItem import LegendItem  # type: ignore
except Exception:  # pragma: no cover
    LegendItem = object  # type: ignore
import os
import sqlite3
import logging
import numpy as np
from typing import Any, Sequence, Tuple, List, Protocol, cast
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget, QLayout  # 改为 PySide6
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPainterPath, QColor, QTextDocument
from pyqtgraph.Point import Point
import pyqtgraph.functions as fn


class MainWindowProtocol(Protocol):
    """
    协议类，声明 ChartFunction 需要用到的主窗口属性
    将这些属性约束为 QWidget，有助于 Pylance   推断 .layout()/setLayout()/addWidget 等成员类型。
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
    '''继承pyqtgraph的wheelEvent类，修改滚轮的运作方式'''

    def wheelEvent(self, ev, axis=None):
        # 按住Ctrl键时只缩放y轴，并且方向相反
        if ev.modifiers() == Qt.ControlModifier:
            if ev.delta() != 0:
                # 加快缩放速度：使用更大的wheelScaleFactor
                original_factor = self.state['wheelScaleFactor']
                self.state['wheelScaleFactor'] = 0.09  # 加快速度

                # 反转滚轮方向，delta值取反
                reversed_delta = -ev.delta()

                # 只在y轴方向缩放
                mask = [False, True]  # x轴禁用，y轴启用
                s = 1.02 ** (reversed_delta * self.state['wheelScaleFactor'])
                s = [None, s]  # x轴不缩放，y轴缩放

                center = Point(fn.invertQTransform(self.childGroup.transform()).map(ev.pos()))
                self._resetTarget()
                self.scaleBy(s, center)
                ev.accept()
                self.sigRangeChangedManually.emit(mask)

                # 恢复原始缩放因子
                self.state['wheelScaleFactor'] = original_factor
            else:
                super().wheelEvent(ev, axis)
            return

        # 普通滚轮：只缩放x轴且加快速度（保持原方向）
        if ev.delta() != 0:
            # 加快缩放速度：使用更大的wheelScaleFactor
            original_factor = self.state['wheelScaleFactor']
            self.state['wheelScaleFactor'] = 0.09  # 加快速度

            # 只在x轴方向缩放
            mask = [True, False]  # x轴启用，y轴禁用
            s = 1.02 ** (-ev.delta() * self.state['wheelScaleFactor'])
            s = [s, None]  # x轴缩放，y轴不缩放

            center = Point(fn.invertQTransform(self.childGroup.transform()).map(ev.pos()))
            self._resetTarget()
            self.scaleBy(s, center)
            ev.accept()
            self.sigRangeChangedManually.emit(mask)

            # 恢复原始缩放因子
            self.state['wheelScaleFactor'] = original_factor
        else:
            super().wheelEvent(ev, axis)

    def mouseDragEvent(self, ev, axis=None):  # type: ignore[override]
        """限制：在绘图区内部拖动不允许改变 Y，仅允许 X 平移；在轴区域(出现 axis 参数) 保留默认行为。
        原理：记录拖动前的 YRange，调用父类实现后立即恢复 YRange，从而忽略内部拖动引起的 Y 平移。
        """
        try:
            # 使用 buttons() 兼容拖动过程中的连续事件；仅当在绘图区内部(axis is None) 且按下左键时锁定 Y
            if axis is None and (ev.buttons() & Qt.LeftButton):
                pre_y = self.viewRange()[1]
                super().mouseDragEvent(ev, axis)
                # 恢复 Y 轴范围，达到“锁定 Y”的效果
                try:
                    self.setYRange(pre_y[0], pre_y[1], padding=0)
                except Exception:
                    pass
                return
            # 其它情况（例如在轴上拖动 / 缩放）走默认逻辑
            super().mouseDragEvent(ev, axis)
        except Exception:
            # 出现异常时回退默认行为
            try:
                super().mouseDragEvent(ev, axis)
            except Exception:
                pass


## 回滚：使用最初简单的 TextItem 方案替代复杂阴影悬浮框
class ShadowTooltip(pg.TextItem):  # 轻量版，支持 HTML 上色
    def __init__(self, anchor=(0, 1)):
        super().__init__("", anchor=anchor, color='#ffffff')
        try:
            self.setFont(pg.QtGui.QFont("Comfortaa", 10))
        except Exception:
            pass
    # 直接继承 TextItem 的 setHtml 能渲染颜色，不再替换换行
    def toHtml(self):
        # TextItem 没有直接公开 toHtml，这里尽量兼容
        return getattr(self, 'text', '') if hasattr(self, 'text') else ''


class ChartFunction:
    def __init__(self, main_window: MainWindowProtocol) -> None:
        self.main_window: MainWindowProtocol = main_window
        # 添加存储十字线和标签的字典
        self.crosshairs = {}
        self.labels = {}
        # 可选：单位映射 {数据列名: 单位字符串}
        self.units_map = {}
        # 悬浮/调试配置
        self._hover_debug = True
        self._hover_debug_interval_ms = 300
        self._last_hover_log_ts = 0.0
        self._label_axis_tag = True
        self._show_empty_hint = True
        self._tooltip_follow_mouse = True   # 悬浮框跟随鼠标
        self._tooltip_edge_padding_ratio = 0.04  # 与上下边界的最小间距比例

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
        # 统一 legend 清理函数（供外部调用）
    def clean_legend(self, widget: QWidget):
        """移除一个 PlotWidget legend 中的所有条目，但不删除 LegendItem 自身。
        防止重复条目残留。外部在重新绘图前可调用。
        """
        try:
            if widget is None:
                return
            plot_item = widget.getPlotItem()
            legend = plot_item.legend
            if legend is None:
                return
            # pyqtgraph LegendItem 有 clear()，最可靠，一次性移除所有条目
            try:
                legend.clear()
            except Exception:
                # 回退方案：逐条移除
                for sample, lbl in list(getattr(legend, 'items', [])):
                    try:
                        legend.removeItem(sample)
                    except Exception:
                        try:
                            # 通过名字再试一次
                            name_txt = None
                            for attr in ('text', 'toPlainText'):
                                if hasattr(lbl, attr):
                                    try:
                                        val = getattr(lbl, attr)()
                                    except Exception:
                                        val = getattr(lbl, attr)
                                    if isinstance(val, str):
                                        name_txt = val
                                        break
                            if name_txt:
                                legend.removeItem(name_txt)
                        except Exception:
                            pass
        except Exception:
            pass

    def rebuild_legend(self, widget: QWidget):
        """强制根据当前真实存在的曲线重建 legend (主图专用)。
        1. 清空 legend 条目
        2. 遍历主 viewBox 中的 PlotDataItem/PlotCurveItem
        3. 若存在右侧 viewbox, 合并其曲线
        4. 按出现顺序添加唯一名称
        """
        try:
            if widget is None or widget.objectName() != 'main_plot_widget':
                return
            plot_item = widget.getPlotItem()
            # 先合并/移除可能出现的多个 legend 对象
            try:
                scene_items = plot_item.scene().items()
                legends = [it for it in scene_items if isinstance(it, LegendItem)]  # type: ignore[arg-type]
                if legends:
                    # 保留第一个，移除其余，统一指向 plot_item.legend
                    keep = legends[0]
                    for extra in legends[1:]:
                        try:
                            plot_item.scene().removeItem(extra)
                        except Exception:
                            pass
                    if plot_item.legend is None or plot_item.legend is not keep:
                        # 如果当前 plot_item.legend 丢失，重新 attach
                        try:
                            plot_item.legend = keep  # type: ignore[attr-defined]
                        except Exception:
                            pass
            except Exception:
                pass
            # 确保 legend 存在（若完全没有则新建）
            if plot_item.legend is None:
                widget.addLegend()
            legend = plot_item.legend  # type: ignore[assignment]
            cleared = False
            try:
                legend.clear()
                cleared = True
            except Exception:
                # 旧版本无 clear 方法：手动删除
                try:
                    for sample, lbl in list(getattr(legend, 'items', [])):
                        try:
                            legend.removeItem(sample)
                        except Exception:
                            # 名称方式
                            name_txt = None
                            for attr in ('text', 'toPlainText'):
                                if hasattr(lbl, attr):
                                    try:
                                        val = getattr(lbl, attr)()
                                    except Exception:
                                        val = getattr(lbl, attr)
                                    if isinstance(val, str):
                                        name_txt = val
                                        break
                            if name_txt:
                                try:
                                    legend.removeItem(name_txt)
                                except Exception:
                                    pass
                    cleared = True
                except Exception:
                    pass
            seen = set()
            def _maybe_add(it):
                try:
                    if not isinstance(it, pg.PlotDataItem):  # PlotCurveItem 继承 PlotDataItem
                        return
                    nm = getattr(it, 'opts', {}).get('name', None)
                    if not nm and hasattr(it, 'name'):
                        tmp = it.name() if callable(it.name) else it.name
                        if isinstance(tmp, str):
                            nm = tmp
                    if not isinstance(nm, str) or not nm:
                        return
                    if nm in seen:
                        return
                    legend.addItem(it, nm)
                    seen.add(nm)
                except Exception:
                    pass
            # 主 viewbox 曲线
            for it in plot_item.items:
                _maybe_add(it)
            # 右轴 viewbox 曲线
            try:
                if hasattr(widget, '_right_viewbox') and getattr(widget, '_right_viewbox') is not None:
                    rvb = getattr(widget, '_right_viewbox')
                    for it in list(getattr(rvb, 'addedItems', [])):
                        _maybe_add(it)
            except Exception:
                pass
        except Exception:
            pass

    def set_units_mapping(self, mapping: dict[str, str]):
        """设置单位映射: {列名: '单位'}，用于悬浮提示。
        示例: set_units_mapping({'CPI':'%', 'GDP':'$B'})
        """
        try:
            self.units_map.update(mapping)
        except Exception:
            self.units_map = mapping

    def sync_legend(self, widget: QWidget, desired_names: list[str]):
        """同步 legend，使其只包含 desired_names 中出现的曲线名称，移除多余项并添加缺失项。
        不强制调整顺序，只保证无重复、无过时。
        """
        try:
            if widget is None:
                return
            plot_item = widget.getPlotItem()
            legend = plot_item.legend
            if legend is None:
                return
            desired_set = set(desired_names)
            existing_entries = list(getattr(legend, 'items', []))
            # 记录已有 legend 名称
            existing_names = []
            for sample, lbl in existing_entries:
                name_txt = None
                for attr in ('text', 'toPlainText'):
                    if hasattr(lbl, attr):
                        try:
                            val = getattr(lbl, attr)()
                        except Exception:
                            val = getattr(lbl, attr)
                        if isinstance(val, str):
                            name_txt = val
                            break
                if name_txt:
                    existing_names.append(name_txt)
            # 移除不在 desired_set 中的
            for nm in existing_names:
                if nm not in desired_set:
                    try:
                        legend.removeItem(nm)
                    except Exception:
                        pass
            # 构建当前 plot 中曲线名 -> curve item 映射
            curve_map = {}
            for it in plot_item.items:
                if isinstance(it, pg.PlotCurveItem):
                    nm = getattr(it, 'name', None)
                    if callable(nm):
                        try:
                            nm = nm()
                        except Exception:
                            nm = None
                    if isinstance(nm, str) and nm:
                        curve_map[nm] = it
            # 添加缺失的 desired 名称
            for nm in desired_names:
                if nm in curve_map:
                    # 检查 legend 是否已有
                    found = False
                    for sample, lbl in list(getattr(legend, 'items', [])):
                        name_txt = None
                        for attr in ('text', 'toPlainText'):
                            if hasattr(lbl, attr):
                                try:
                                    val = getattr(lbl, attr)()
                                except Exception:
                                    val = getattr(lbl, attr)
                                if isinstance(val, str):
                                    name_txt = val
                                    break
                        if name_txt == nm:
                            found = True
                            break
                    if not found:
                        try:
                            legend.addItem(curve_map[nm], nm)
                        except Exception:
                            pass
        except Exception:
            pass

    def init_chart_widgets(self, window: QWidget, object_name: str):
        """Initialize chart widgets 并设置objectName"""
        layout_obj = window.layout()
        if layout_obj is None:
            layout_obj = QVBoxLayout()
            window.setLayout(layout_obj)

        self.single_plot_widget: Any = pg.PlotWidget(viewBox=OnlyXWheelViewBox())

        self.single_plot_widget.setObjectName(object_name)  # 设置objectName
        self.chart_title: QLabel = QLabel("Data Name will be here")
        self.chart_title.setMaximumHeight(50)
        self.chart_title.setMinimumHeight(50)
        self.chart_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_title.setStyleSheet(
            '''
            font-family : "Comfortaa";
            font-weight : Normal;
            font-size : 16px;
            color : #ffffff;
            margin-top : 3px; 
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
        # 允许 Y 拖动（以便在坐标轴区域拖动改变 Y），内部绘图区的垂直拖动会在 OnlyXWheelViewBox.mouseDragEvent 中被还原
        try:
            view_box.setMouseEnabled(x=True, y=True)
        except Exception:
            pass

        # 下面这个强制设定只能横向移动，暂时用不上
        # self.single_plot_widget.setMouseEnabled(x=True, y=False)

        # 设置坐标轴标签字体
        font = pg.QtGui.QFont()
        font.setPixelSize(12)
        font.setFamilies(["Comfortaa"])
        self.single_plot_widget.getAxis('left').setTickFont(font)
        self.single_plot_widget.getAxis('bottom').setTickFont(font)

        # 只有单图表界面设立legend
        if object_name == "main_plot_widget":
            self.single_plot_widget.addLegend()
            # 标记避免后续 plot_data 再次重复添加 legend
            try:
                setattr(self.single_plot_widget, '_legend_added', True)
            except Exception:
                pass
        
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

        # 为每个图表widget初始化十字线和标签（回滚简化版）
        v_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#ffffff', style=Qt.DashLine))
        h_line = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('#ffffff', style=Qt.DashLine))
        v_line.setOpacity(0.3); h_line.setOpacity(0.3)
        self.single_plot_widget.addItem(v_line, ignoreBounds=True)
        self.single_plot_widget.addItem(h_line, ignoreBounds=True)
        label = ShadowTooltip(anchor=(0, 1))
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
            lambda pos, obj_name=object_name: self.on_mouse_move(pos, obj_name)
        )

        return self.single_plot_widget

    def on_mouse_move(self, pos, object_name):
        """增强版（在原始回滚基础上）：日期格式化 + 彩色多曲线 + 单位支持"""
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
        v_line, h_line = self.crosshairs.get(object_name, (None, None))
        label = self.labels.get(object_name)
        if v_line is None or h_line is None or label is None:
            return
        if not plot_item.sceneBoundingRect().contains(pos):
            v_line.hide(); h_line.hide(); label.hide(); return

        mouse_point = plot_item.vb.mapSceneToView(pos)
        x_val = mouse_point.x(); y_val = mouse_point.y()
        v_line.setPos(x_val); h_line.setPos(y_val)

        # 收集左右轴曲线
        items = []
        left_items = []
        right_items = []
        try:
            for it in list(plot_item.listDataItems()):
                if hasattr(it, 'getData'):
                    items.append(it); left_items.append(it)
        except Exception:
            pass
        right_vb = None
        try:
            if hasattr(plot_widget, '_right_viewbox') and getattr(plot_widget, '_right_viewbox') is not None:  # type: ignore[attr-defined]
                right_vb = getattr(plot_widget, '_right_viewbox')  # type: ignore[attr-defined]
                collected = False
                try:
                    for it in list(getattr(right_vb, 'addedItems', [])):
                        if hasattr(it, 'getData'):
                            items.append(it); right_items.append(it); collected = True
                except Exception:
                    pass
                if not collected:
                    try:
                        for it in plot_item.scene().items():
                            if it not in items and hasattr(it, 'getData'):
                                try:
                                    if hasattr(it, 'getViewBox') and it.getViewBox() is right_vb:  # type: ignore
                                        items.append(it); right_items.append(it)
                                except Exception:
                                    pass
                    except Exception:
                        pass
        except Exception:
            right_vb = None
        if not items:
            if self._show_empty_hint:
                label.setHtml("<div style='color:#888'>(no data)</div>")
                label.setPos(x_val, y_val)
                v_line.show(); h_line.show(); label.show()
            else:
                label.hide()
            return

        units_map = getattr(self, 'units_map', {}) if hasattr(self, 'units_map') else {}

        # 取日期缓存
        date_cache = getattr(plot_widget, '_date_cache', None)
        formatted_date = None
        idx_candidate = None

        html_lines = []
        first_idx_used = None

        # 记录用于十字线水平线的“最接近鼠标”曲线点（按主 viewbox 坐标系下 y 与鼠标 y 的差值）
        nearest_y_for_hline = None  # 保持旧变量名兼容后面逻辑
        best_dist = None
        for item in items:
            if not hasattr(item, 'getData'):
                continue
            try:
                x_data, y_data = item.getData()
            except Exception:
                continue
            if x_data is None or y_data is None or len(x_data) == 0:
                continue
            try:
                distances = np.abs(np.array(x_data) - x_val)
            except Exception:
                continue
            if len(distances) == 0:
                continue
            min_index = int(np.argmin(distances))
            if min_index >= len(x_data) or min_index >= len(y_data):
                continue
            nearest_x = x_data[min_index]
            nearest_y = y_data[min_index]
            # 将右轴曲线的 y 映射到主轴坐标，便于统一比较
            candidate_y_main = nearest_y
            try:
                if right_vb is not None and item in right_items:
                    # 使用 pyqtgraph ViewBox 的 mapViewToView 实现坐标转换
                    candidate_point = right_vb.mapViewToView(plot_item.vb, pg.Point(nearest_x, nearest_y))  # type: ignore
                    candidate_y_main = float(candidate_point.y())
            except Exception:
                pass
            # 计算与鼠标 y 的距离（主轴坐标系）
            try:
                dist = abs(candidate_y_main - y_val)
                if best_dist is None or dist < best_dist:
                    best_dist = dist
                    nearest_y_for_hline = candidate_y_main
            except Exception:
                if nearest_y_for_hline is None:
                    nearest_y_for_hline = candidate_y_main
            if first_idx_used is None:
                first_idx_used = min_index
                idx_candidate = nearest_x
            name = getattr(item, 'opts', {}).get('name', 'Data') or 'Data'
            base_name = name
            if self._label_axis_tag:
                try:
                    if item in right_items:
                        name = f"{name}(R)"
                    else:
                        name = f"{name}(L)"
                except Exception:
                    pass
            unit = units_map.get(base_name, '')
            # 颜色
            color_hex = '#ffffff'
            try:
                pen_obj = getattr(item, 'opts', {}).get('pen', None)
                if pen_obj is not None:
                    qcolor = pen_obj.color()
                    color_hex = qcolor.name()
            except Exception:
                pass
            try:
                html_lines.append(f"<span style='color:{color_hex}'>{name} : {nearest_y:.2f}{unit}</span>")
            except Exception:
                continue

        # 日期格式化
        if date_cache is not None and first_idx_used is not None:
            # 优先用索引定位 date_cache
            if isinstance(first_idx_used, (int, float)):
                int_idx = int(first_idx_used)
                if 0 <= int_idx < len(date_cache):
                    raw_date = date_cache[int_idx]
                    formatted_date = self._format_date_string(raw_date)
        if formatted_date is None and isinstance(idx_candidate, (int, float)):
            # 可能 x_data 就是索引
            if date_cache and 0 <= int(idx_candidate) < len(date_cache):
                formatted_date = self._format_date_string(date_cache[int(idx_candidate)])
        if formatted_date is None:
            formatted_date = f"Index: {int(round(x_val))}" if isinstance(x_val, (int, float)) else ""

        # 构造 HTML
        final_html = [f"<div style='color:#bbbbbb'>Date : {formatted_date}</div>"]
        final_html.extend(f"<div>{line}</div>" for line in html_lines)
        # Debug 日志（节流）
        if self._hover_debug:
            try:
                import time
                now_ms = time.time()*1000
                if now_ms - self._last_hover_log_ts > self._hover_debug_interval_ms:
                    self._last_hover_log_ts = now_ms
                    try:
                        with open('./logs/debug_worker.log', 'a', encoding='utf-8') as f:
                            ln = ','.join([(getattr(it, 'opts', {}).get('name', 'Data') or 'Data') for it in items])
                            f.write(f"hover curves: {ln}\n")
                    except Exception:
                        pass
            except Exception:
                pass
        label.setHtml("".join(final_html))
        # 十字线水平线对齐第一条曲线最近点（更易读），若失败则用鼠标 y
        if nearest_y_for_hline is not None:
            h_line.setPos(nearest_y_for_hline)
        else:
            h_line.setPos(y_val)

        # 悬浮框位置策略
        if getattr(self, '_tooltip_follow_mouse', False):
            # 直接跟随鼠标坐标（数据坐标系），并做上下边界保护
            try:
                y_for_label = y_val
                # 边界范围
                yrange = plot_item.vb.viewRange()[1]
                y_min, y_max = yrange[0], yrange[1]
                span = max(1e-9, y_max - y_min)
                pad = span * getattr(self, '_tooltip_edge_padding_ratio', 0.04)
                if y_for_label > y_max - pad:
                    y_for_label = y_max - pad
                elif y_for_label < y_min + pad:
                    y_for_label = y_min + pad
                label.setPos(x_val, y_for_label)
            except Exception:
                # 回退原逻辑
                label.setPos(x_val, h_line.value())
        else:
            # 保留原来：对齐第一条曲线的 y
            label.setPos(x_val, h_line.value())
        v_line.show(); h_line.show(); label.show()

    # --------------------------------- 辅助：日期格式化 ---------------------------------
    def _format_date_string(self, raw: str):
        """尝试把多种常见日期格式标准化为 YYYY-MM-DD。
        输入可能是: '2024-01-05', '20240105', '2024/01/05', '05-01-2024', 等。
        若不能识别则原样返回。
        """
        if not raw or not isinstance(raw, str):
            return str(raw)
        txt = raw.strip()
        if not txt:
            return raw
        # 简单缓存可加（目前轻量不需要）
        formats_try = [
            "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y%m%d",
            "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y",
            "%m-%d-%Y", "%m/%d/%Y", "%m.%d.%Y",
        ]
        from datetime import datetime
        for fmt in formats_try:
            try:
                dt = datetime.strptime(txt, fmt)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                continue
        # 兜底：若包含 T (ISO) 或空格日期时间格式
        try:
            if 'T' in txt or ' ' in txt:
                dt = datetime.fromisoformat(txt.replace('Z','').strip())
                return dt.strftime("%Y-%m-%d")
        except Exception:
            pass
        return raw

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

    def plot_data(self, data_name: str, color: list[str] = ["#90b6e7"], widget = None, clear_line = True) -> None:
        """Plot data to single chart，绘制数据并展示
        widget是plot widget, self.single_plot_widget
        axis_label 是是否需要写x轴label，默认false，第一个图需要true"""
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
        
        # 清除主 viewbox 的内容但保留十字线和标签，不清理右侧 viewbox
        plot_item = widget.getPlotItem()
        # legend 清理交给外部 sync 方法，避免每次绘制都完全清空

        # 只移除主 viewbox 的曲线
        if clear_line :
            for item in plot_item.items:
                if item not in [v_line, h_line, label]:
                    plot_item.removeItem(item)
        # 如果有右侧 viewbox，清空其曲线
            if hasattr(widget, "_right_viewbox") and widget._right_viewbox is not None:
                right_vb = widget._right_viewbox
                for item in list(right_vb.addedItems):
                    right_vb.removeItem(item)
            else:
                err = open("./logs/table_error.txt", 'w')
                if not hasattr(widget, "_right_viewbox"):
                    err.write("no catch right viewbox tag\n") # hasattr(widget, "_right_viewbox") this "_right_viewbox" tag not get
                err.close()

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

        # 只绘制一条数据，不再循环多条
        dates, values = self._get_data_from_database(data_name)
        # 缓存日期序列供悬浮提示显示真实日期
        try:
            setattr(widget, '_date_cache', dates)
        except Exception:
            pass

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

        n = len(dates)
        step = max(1, n // 5)
        ticks = [(i, dates[i]) for i in range(0, n, step)]
        # 保证最后一个日期也显示
        try:
            if (n - 1) not in [i for i, _ in ticks]:
                ticks.append((n - 1, dates[-1]))
        except:
            logging.error("Data does not exist")
            pass
        axis.setTicks([ticks])

        # 设置坐标轴字体
        font = pg.QtGui.QFont()
        font.setPixelSize(10)
        font.setFamilies(["Comfortaa"])

        widget.getAxis('left').setTickFont(font)
        widget.getAxis('bottom').setTickFont(font)
        # 确保 legend 存在；如果被外部 clear() 或 clear() 时被销毁，重新创建
        if widget.objectName() == "main_plot_widget":
            try:
                plot_item = widget.getPlotItem()
                if plot_item.legend is None:
                    widget.addLegend()
                # 标记一次，防止外部逻辑误判
                setattr(widget, '_legend_added', True)
            except Exception:
                pass

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
                # vb.setYLink(master_vb)  # 不再同步y轴
            for w in widgets:
                w.enableAutoRange(axis='x', enable=True)  # 只对x轴自适应

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
                        items = plot_item.listDataItems()
                        nearest_y_for_hline = None
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
                                            if nearest_y_for_hline is None:
                                                nearest_y_for_hline = nearest_y
                                            name = getattr(item, 'opts', {}).get('name', 'Data')
                                            data_texts.append(f"Date : {nearest_x}\n{name} : {nearest_y:.2f}")
                        v_line.setPos(x_val)
                        if nearest_y_for_hline is not None:
                            h_line.setPos(nearest_y_for_hline)
                        else:
                            h_line.setPos(y_val)
                        if data_texts:
                            label_text = "\n".join(data_texts)
                            label.setText(label_text)
                            label.setPos(x_val, nearest_y_for_hline if nearest_y_for_hline is not None else y_val)
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

            self._four_charts_mouse_conn = []
            for w in widgets:
                # 保存 slot 以便后续 disconnect
                slot = sync_crosshair
                w.scene().sigMouseMoved.connect(slot)
                self._four_charts_mouse_conn.append((w, slot))

            self._four_charts_range_conn = []
            def sync_range(*args, **kwargs):
                # target_range = master_vb.viewRange()
                # for w in widgets[1:]:
                #     vb = w.getViewBox()
                #     vb.blockSignals(True)
                #     vb.setRange(xRange=target_range[0], yRange=target_range[1], padding=0)
                #     vb.blockSignals(False)
                # 不需要手动 setRange，ViewBox 链接后会自动同步范围，避免递归
                pass
            conn = master_vb.sigRangeChanged.connect(sync_range)
            self._four_charts_range_conn.append(conn)
            self._four_charts_linked = True
        else:
            for w in widgets:
                vb = w.getViewBox()
                vb.setXLink(None)
                vb.setYLink(None)
            self._four_charts_linked = False