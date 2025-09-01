'''
主窗口的设置与控件信号
启动窗口请前往main.py文件
'''


from gui import *
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QSizePolicy, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, QEvent, Qt, QPoint, QObject
from .ui_function import UiFunctions  # 修改: 添加对UiFunctions的导入

class mainWindow(QMainWindow, Ui_MainWindow):
    # 明确声明拖动状态的类型，避免“类型未知”
    _dragging: bool
    _drag_offset: QPoint
    def __init__(self):
        super().__init__()
        # 由Qt Designer生成的setupUi未提供类型注解，Pylance会报告参数类型未知，这里忽略类型检查
        self.setupUi(self)  # type: ignore

        # ============== 自定义标题栏与无边框窗口 ==============
        try:
            # 去除系统标题栏（使用 Qt6 命名空间的枚举）
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        except Exception:
            pass

        # 构建自定义标题栏（放在右侧主区域顶部）
        try:
            self.title_bar = QFrame(self.frame)
            self.title_bar.setObjectName("title_bar")
            self.title_bar.setFixedHeight(36)
            self.title_bar.setStyleSheet(
                '#title_bar { background-color: #252526;}\n'
                "#title_label { color: #90b6e7; font-weight: 600; padding-left: 8px; }\n"
                "QToolButton { background-color: #252526; border: 0; border-radius: 9px; color: #90b6e7; }\n"
                "QToolButton:hover { background-color: #33363a; }\n"
                "QToolButton:pressed { background-color: #90b6e7; color: #252526; }\n"
            )

            hbox = QHBoxLayout(self.title_bar)
            hbox.setContentsMargins(8, 0, 8, 0)
            hbox.setSpacing(6)

            self.title_label = QLabel(self.title_bar)
            self.title_label.setObjectName("title_label")
            self.title_label.setText("Macro Data Dashboard")
            font = self.title_label.font()
            font.setFamily("Comfortaa")
            hbox.addWidget(self.title_label)

            spacer = QWidget(self.title_bar)
            spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            hbox.addWidget(spacer)

            self.btn_min = QToolButton(self.title_bar)
            self.btn_min.setIcon(QIcon(":/svg/svg/minimize.svg"))
            self.btn_min.setIconSize(QSize(16, 16))
            self.btn_min.setFixedSize(28, 24)
            self.btn_min.setToolTip("Minimize")
            try:
                self.btn_min.setCursor(Qt.CursorShape.PointingHandCursor)
            except Exception:
                pass
            hbox.addWidget(self.btn_min)

            self.btn_max = QToolButton(self.title_bar)
            self.btn_max.setIcon(QIcon(":/svg/svg/big_window.svg"))
            self.btn_max.setIconSize(QSize(16, 16))
            self.btn_max.setFixedSize(28, 24)
            self.btn_max.setToolTip("Maximize / Restore")
            try:
                self.btn_max.setCursor(Qt.CursorShape.PointingHandCursor)
            except Exception:
                pass
            hbox.addWidget(self.btn_max)

            self.btn_close = QToolButton(self.title_bar)
            self.btn_close.setIcon(QIcon(":/png/png/close.png"))
            self.btn_close.setIconSize(QSize(16, 16))
            self.btn_close.setFixedSize(28, 24)
            self.btn_close.setToolTip("Close")
            try:
                self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
            except Exception:
                pass
            hbox.addWidget(self.btn_close)

            # 图标回退：若图标不可用则显示文本
            try:
                if self.btn_min.icon().isNull():
                    self.btn_min.setText("–")
                if self.btn_max.icon().isNull():
                    self.btn_max.setText("□")
                if self.btn_close.icon().isNull():
                    self.btn_close.setText("×")
            except Exception:
                pass

            # 在标题栏与内容之间插入一个容器，避免其他控件覆盖标题栏
            self._title_container = QFrame(self.frame)
            self._title_container.setFrameShape(QFrame.Shape.NoFrame)
            vbox = QHBoxLayout(self._title_container)
            vbox.setContentsMargins(0, 0, 0, 0)
            vbox.setSpacing(0)
            vbox.addWidget(self.title_bar)

            # 将标题容器插入到右侧主区域顶部（stackedWidget 之前）
            self.verticalLayout_2.insertWidget(0, self._title_container)
            # 确保层级正确：标题容器在上，页面内容在下
            try:
                self._title_container.raise_()
                self.stackedWidget.lower()
            except Exception:
                pass
            # 确保标题栏有独立背景并在最上层
            try:
                self.title_bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)  # type: ignore[attr-defined]
            except Exception:
                pass
            self.title_bar.raise_()

            # 信号连接
            self.btn_min.clicked.connect(self.showMinimized)
            self.btn_max.clicked.connect(self._toggle_max_restore)
            self.btn_close.clicked.connect(self.close)

            # 拖动支持：在 title_bar 上安装事件过滤器
            self._dragging = False
            self._drag_offset = QPoint(0, 0)
            self.title_bar.installEventFilter(self)
        except Exception:
            pass

        # create instances
        self.ui_functions = UiFunctions(self)  # type: ignore[arg-type]

        # 避免 QTabWidget 的滚动箭头(>)出现在右上角遮挡标题栏按钮
        try:
            if hasattr(self, "tab_window"):
                self.tab_window.setUsesScrollButtons(False)
                # 强制 tab 条靠左贴边，减少右上角空位
                self.tab_window.setElideMode(Qt.TextElideMode.ElideRight)
                self.tab_window.setTabBarAutoHide(False)
                # 如存在 corner 控件（> 按钮等），移除可见性
                corner = self.tab_window.cornerWidget()
                if corner:
                    corner.setVisible(False)
                # 移除 Top 两侧 cornerWidget
                _empty1 = QWidget()
                _empty1.setFixedSize(0, 0)
                self.tab_window.setCornerWidget(_empty1, Qt.Corner.TopRightCorner)
                _empty2 = QWidget()
                _empty2.setFixedSize(0, 0)
                self.tab_window.setCornerWidget(_empty2, Qt.Corner.TopLeftCorner)
                # 样式隐藏 scroller 与 QToolButton（避免 '>' 按钮出现）
                ss = (self.tab_window.styleSheet() or "") + "\nQTabBar::scroller { width: 0px; }\nQTabBar QToolButton { width: 0px; height: 0px; margin: 0; padding: 0; }\n"
                self.tab_window.setStyleSheet(ss)
        except Exception:
            pass

        # left menu btn signal connection  左边栏按钮信号定义
        self.one_page_btn.clicked.connect(self.left_bar_button_slot)
        self.four_page_btn.clicked.connect(self.left_bar_button_slot)
        self.table_btn.clicked.connect(self.left_bar_button_slot)
        self.note_btn.clicked.connect(self.left_bar_button_slot)
        self.settings_btn.clicked.connect(self.left_bar_button_slot)
        self.setWindowIcon(QIcon(":/png/png/ico.png"))

        # settings signals
        # 点击api确认按钮，保存输入的API
        self.api_save_btn.clicked.connect(self.ui_functions.settings_api_save)

        # 重置日志文件按钮
        self.clear_lag_btn.clicked.connect(self.ui_functions.clear_logs)


    def left_bar_button_slot(self):
        '''left bar btn clicked slot, when click, change page (stack)'''
        btn = self.sender()
        btn_name = btn.objectName()

        # show stack pages
        if btn_name == "one_page_btn":
            self.stackedWidget.setCurrentWidget(self.page_one_container)
            self.one_page_btn.setStyleSheet("icon: url(:/png/png/one.png);\nicon-size: 20px 20px;")
        if btn_name == "four_page_btn":
            self.stackedWidget.setCurrentWidget(self.page_four_container)
        if btn_name == "table_btn":
            self.stackedWidget.setCurrentWidget(self.page_table_container)
        if btn_name == "note_btn":
            self.stackedWidget.setCurrentWidget(self.page_note_container)
        if btn_name == "settings_btn":
            self.stackedWidget.setCurrentWidget(self.page_settings_container)
            # 进入设置页时刷新 .env 到输入框
            try:
                self.ui_functions.settings_api_load()
            except Exception:
                pass
            

    # ============== 自定义标题栏：最大化/还原与拖动 ==============
    def _toggle_max_restore(self):
        try:
            if self.isMaximized():
                self.showNormal()
                # 还原图标
                from PySide6.QtGui import QIcon
                self.btn_max.setIcon(QIcon(":/svg/svg/big_window.svg"))
            else:
                self.showMaximized()
                from PySide6.QtGui import QIcon
                self.btn_max.setIcon(QIcon(":/svg/svg/small_window.svg"))
        except Exception:
            pass

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # type: ignore[override]
        try:
            if obj is getattr(self, "title_bar", None):
                if event.type() == QEvent.Type.MouseButtonDblClick:  # type: ignore[attr-defined]
                    self._toggle_max_restore()
                    return True
                if event.type() == QEvent.Type.MouseButtonPress:  # type: ignore[attr-defined]
                    try:
                        if event.button() == Qt.MouseButton.LeftButton:  # type: ignore[attr-defined]
                            self._dragging = True
                            try:
                                pos = event.globalPosition().toPoint()  # type: ignore[attr-defined]
                            except Exception:
                                pos = event.globalPos()  # type: ignore[attr-defined]
                            self._drag_offset = pos - self.frameGeometry().topLeft()
                            return True
                    except Exception:
                        pass
                    return True
                if event.type() == QEvent.Type.MouseMove and getattr(self, "_dragging", False):  # type: ignore[attr-defined]
                    try:
                        try:
                            pos = event.globalPosition().toPoint()  # type: ignore[attr-defined]
                        except Exception:
                            pos = event.globalPos()  # type: ignore[attr-defined]
                        self.move(pos - self._drag_offset)  # type: ignore[arg-type]
                    except Exception:
                        pass
                    return True
                if event.type() == QEvent.Type.MouseButtonRelease:  # type: ignore[attr-defined]
                    self._dragging = False
                    return True
        except Exception:
            pass
        return super().eventFilter(obj, event)  # type: ignore[arg-type]