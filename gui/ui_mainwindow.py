'''
主窗口的设置与控件信号
启动窗口请前往main.py文件
'''


from gui import *
from .ui_function import UiFunctions
from gui.custom_grip import CustomGrip

# 全局化窗口是否全屏，开始是false
GLOBAL_STATE = False

class mainWindow(QMainWindow, Ui_MainWindow):
    # 明确声明拖动状态的类型，避免“类型未知”
    _dragging: bool
    _drag_offset: QPoint

    # 新增：记录窗口原始位置和大小
    _normal_geometry: QRect = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)  # type: ignore
        self.ui_functions = UiFunctions(self)

        # 去除系统标题栏（使用 Qt6 命名空间的枚举）
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)

        # 初始化按钮样式
        self.one_page_btn.setStyleSheet(
            '''
            background : #90b6e7;
            icon: url(:/png_check/png/one_check.png);
            icon-size: 20px 20px;
            border-left : 2px solid white;
            '''
        )

        # 上边栏 信号连接
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.window_btn.clicked.connect(self._toggle_max_restore)
        self.close_btn.clicked.connect(self.close)

        # left menu btn signal connection  左边栏按钮信号定义
        self.one_page_btn.clicked.connect(self.left_bar_button_slot)
        self.four_page_btn.clicked.connect(self.left_bar_button_slot)
        self.table_btn.clicked.connect(self.left_bar_button_slot)
        self.note_btn.clicked.connect(self.left_bar_button_slot)
        self.settings_btn.clicked.connect(self.left_bar_button_slot)

        # 修改：为 header_right_btn_container 添加鼠标事件
        self.header_right_btn_container.installEventFilter(self)
        self.header_text_and_icon.installEventFilter(self)

        # 边缘
        self.left_grip = CustomGrip(self, Qt.Edge.LeftEdge, True)
        self.right_grip = CustomGrip(self, Qt.Edge.RightEdge, True)
        self.top_grip = CustomGrip(self, Qt.Edge.TopEdge, True)
        self.bottom_grip = CustomGrip(self, Qt.Edge.BottomEdge, True)

        # 四角 grip（用 Qt.Corner 枚举）
        self.topleft_grip = CustomGrip(self, Qt.TopLeftCorner, True)
        self.topright_grip = CustomGrip(self, Qt.TopRightCorner, True)
        self.bottomleft_grip = CustomGrip(self, Qt.BottomLeftCorner, True)
        self.bottomright_grip = CustomGrip(self, Qt.BottomRightCorner, True)

        # 点击api确认按钮，保存输入的API
        self.api_save_btn.clicked.connect(self.ui_functions.settings_api_save)

        # 重置日志文件按钮
        self.clear_lag_btn.clicked.connect(self.ui_functions.clear_logs)


    def left_bar_button_slot(self):
        '''left bar btn clicked slot, when click, change page (stack)'''
        btn = self.sender()
        btn_name = btn.objectName()

        # 所有按钮列表
        btn_dict = {
            "one_page_btn" : self.one_page_btn,
            "four_page_btn" : self.four_page_btn,
            "table_btn" : self.table_btn,
            "note_btn" : self.note_btn,
            "settings_btn" : self.settings_btn,
        }

        # clear effect 清除自带的效果保留qss效果
        for name, button in btn_dict.items():
            if button != btn:  # 比较按钮对象而不是名称
                button.setChecked(False)
                button.setStyleSheet("")

        # show stack pages
        if btn_name == "one_page_btn":
            self.stackedWidget.setCurrentWidget(self.page_one_container)
            self.one_page_btn.setStyleSheet(
                '''
                background : #90b6e7;
                icon: url(:/png_check/png/one_check.png);
                icon-size: 20px 20px;
                border-left : 2px solid white;
                '''
            )
        elif btn_name == "four_page_btn":
            self.stackedWidget.setCurrentWidget(self.page_four_container)
            self.four_page_btn.setStyleSheet(
                '''
                background : #90b6e7;
                icon: url(:/png_check/png/four_check.png);
                icon-size: 20px 20px;
                border-left : 2px solid white;
                '''
            )
        elif btn_name == "table_btn":
            self.stackedWidget.setCurrentWidget(self.page_table_container)
            self.table_btn.setStyleSheet(
                '''
                background : #90b6e7;
                icon: url(:/png_check/png/table_check.png);
                icon-size: 20px 20px;
                border-left : 2px solid white;
                '''
            )
        elif btn_name == "note_btn":
            self.stackedWidget.setCurrentWidget(self.page_note_container)
            self.note_btn.setStyleSheet(
                '''
                background : #90b6e7;
                icon: url(:/png_check/png/note_btn_check.png);
                icon-size: 20px 20px;
                border-left : 2px solid white;
                '''
            )
        elif btn_name == "settings_btn":
            self.stackedWidget.setCurrentWidget(self.page_settings_container)
            self.settings_btn.setStyleSheet(
                '''
                background : #90b6e7;
                icon: url(:/png_check/png/settings_check.png);
                icon-size: 20px 20px;
                border-left : 2px solid white;
                '''
            )
            # 进入设置页时刷新 .env 到输入框
            try:
                self.ui_functions.settings_api_load()
            except Exception:
                pass

    # 修改：事件过滤器用于拖动窗口
    def eventFilter(self, obj, event):
        # 禁止最大化或全屏时拖动窗口
        if self.isMaximized() or self.isFullScreen():
            return super().eventFilter(obj, event)
        if obj == self.header_right_btn_container or obj == self.header_text_and_icon:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self._dragging = True
                self._drag_offset = event.globalPos() - self.frameGeometry().topLeft()
                return True
            elif event.type() == QEvent.MouseMove and getattr(self, '_dragging', False):
                self.move(event.globalPos() - self._drag_offset)
                return True
            elif event.type() == QEvent.MouseButtonRelease:
                self._dragging = False
                return True
        return super().eventFilter(obj, event)

    def _toggle_max_restore(self):
        global GLOBAL_STATE
        if GLOBAL_STATE == True:
            GLOBAL_STATE = False
            # 恢复窗口位置和大小
            if self._normal_geometry:
                self.setGeometry(self._normal_geometry)
            self.showNormal()
            self.window_btn.setStyleSheet(
                '''
                image: url(:/svg/svg/big_window.svg);
                padding : 4px;
                image-position : center;
                '''
            )
            self.resize(self.width()+0, self.height()+0)
        else:
            GLOBAL_STATE = True
            # 记住窗口位置和大小
            self._normal_geometry = self.geometry()
            self.showMaximized()
            self.window_btn.setStyleSheet(
                '''
                image: url(:/svg/svg/small_window.svg);
                padding : 4px;
                image-position : center;
                '''
            )

    def resizeEvent(self, event):
        # grip 跟随窗口大小变化自动调整
        super().resizeEvent(event)
        self.left_grip.update_geometry()
        self.right_grip.update_geometry()
        self.top_grip.update_geometry()
        self.bottom_grip.update_geometry()
        # 四角 grip 跟随调整
        self.topleft_grip.update_geometry()
        self.topright_grip.update_geometry()
        self.bottomleft_grip.update_geometry()
        self.bottomright_grip.update_geometry()