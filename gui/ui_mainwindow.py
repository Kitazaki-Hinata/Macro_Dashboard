'''
主窗口的设置与控件信号
class mainWindow(QMainWindow, Ui_MainWindow):
    # 明确声明拖动状态的类型，避免"类型未知"
    _dragging: bool
    _drag_offset: QPoint

    # 新增：记录窗口原始位置和大小
    _normal_geometry: Optional[QRect] = Nonemain.py文件
'''

import os
import logging
from typing import Optional, Any
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, QEvent, QPoint, QRect
from PySide6.QtGui import QResizeEvent, QMouseEvent
from gui import *
from .ui_function import UiFunctions
from gui.custom_grip import CustomGrip

# 全局化窗口是否全屏，开始是false
global_state = False

class mainWindow(QMainWindow, Ui_MainWindow):
    # 明确声明拖动状态的类型，避免“类型未知”
    _dragging: bool
    _drag_offset: QPoint

    # 新增：记录窗口原始位置和大小
    _normal_geometry: Optional[QRect] = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)  # type: ignore
        self.ui_functions = UiFunctions(self)
        self.chart_functions = ChartFunction(self)
        self.table_functions = TableFunction(self)

        # import fonts 使用字体
        self.load_custom_fonts()

        # 读取更新日期设置
        existing_data: dict[str, Any] = self.ui_functions.get_settings_from_json()
        date_today: str = existing_data["recent_update_time"]
        self.table_update_label.setText(f"Recent Update Time : {date_today}")
        self.update_label_2.setText(f"Recent Update Time : {date_today}")
        self.four_update_label.setText(f"Recent Update Time : {date_today}")

        # 实例化ONE PAGE小窗口
        self.one_chart_settings_window = QWidget()
        self.one_chart_ui = Ui_OneChartSettingsPanel()
        self.one_chart_ui.setupUi(self.one_chart_settings_window) # type: ignore
        self.one_chart_ui.first_color_btn.clicked.connect(
            lambda : self.ui_functions.set_color(self.one_chart_ui.first_color_btn)
        )
        self.one_chart_ui.second_color_btn.clicked.connect(
            lambda : self.ui_functions.set_color(self.one_chart_ui.second_color_btn)
        )

        # 实例化FOUR PAGE小窗口
        self.four_chart_settings_window = QWidget()
        self.four_chart_ui = Ui_FourChartSettingsPanel()
        self.four_chart_ui.setupUi(self.four_chart_settings_window) # pyright: ignore[reportUnknownMemberType]
        self.four_chart_ui.first_color_btn.clicked.connect(
            lambda: self.ui_functions.set_color(self.four_chart_ui.first_color_btn)
        )
        self.four_chart_ui.second_color_btn.clicked.connect(
            lambda: self.ui_functions.set_color(self.four_chart_ui.second_color_btn)
        )
        self.four_chart_ui.third_color_btn.clicked.connect(
            lambda: self.ui_functions.set_color(self.four_chart_ui.third_color_btn)
        )
        self.four_chart_ui.fourth_color_btn.clicked.connect(
            lambda: self.ui_functions.set_color(self.four_chart_ui.fourth_color_btn)
        )

        # 实例化TABLE PAGE小窗口
        self.table_settings_window = QWidget()
        self.table_ui = Ui_TableSettingsPanel()
        self.table_ui.setupUi(self.table_settings_window) # type: ignore

        # 去除系统标题栏, Qt6 命名空间的枚举
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)

        # 初始化左边栏按钮样式
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

        # 为 header_right_btn_container 添加鼠标事件
        self.header_right_btn_container.installEventFilter(self)
        self.header_text_and_icon.installEventFilter(self)

        # 边缘
        self.left_grip = CustomGrip(self, Qt.Edge.LeftEdge, True)
        self.right_grip = CustomGrip(self, Qt.Edge.RightEdge, True)
        self.top_grip = CustomGrip(self, Qt.Edge.TopEdge, True)
        self.bottom_grip = CustomGrip(self, Qt.Edge.BottomEdge, True)

        # 四角 grip（用 Qt.Corner 枚举）
        self.topleft_grip = CustomGrip(self, Qt.Corner.TopLeftCorner, True)
        self.topright_grip = CustomGrip(self, Qt.Corner.TopRightCorner, True)
        self.bottomleft_grip = CustomGrip(self, Qt.Corner.BottomLeftCorner, True)
        self.bottomright_grip = CustomGrip(self, Qt.Corner.BottomRightCorner, True)

        '''Settings page btn signal connection'''
        # 点击api确认按钮，保存输入的API
        self.api_save_btn.clicked.connect(self.ui_functions.settings_api_save)
        # 重置日志文件按钮
        self.clear_log_btn.clicked.connect(self.ui_functions.clear_logs)
        self.download_for_all_check.stateChanged.connect(self.ui_functions.download_all_checkbox_settings)

        '''Notes Editor page btn '''
        self.note_add_btn.clicked.connect(self.ui_functions.note_add_extra_page)
        self.note_delete_btn.clicked.connect(self.ui_functions.note_delete_page)
        self.note_rename_btn.clicked.connect(self.ui_functions.note_rename_page)
        self.note_instructions_btn.clicked.connect(self.ui_functions.note_open_instruction)

        # 初始化note按钮，识别并读取txt文件
        self.initialize_txt_note_btn()
        self.save_text.clicked.connect(lambda: self.ui_functions.note_save_file(self._get_current_file_name()))

        '''Chart & Table page btn '''
        self.one_set_preference.clicked.connect(lambda: self.ui_functions.open_settings_window(self.one_chart_ui, self.one_chart_settings_window, "one"))
        self.four_settings_button.clicked.connect(lambda: self.ui_functions.open_settings_window(self.four_chart_ui, self.four_chart_settings_window, "four"))
        self.page_table_set_preference.clicked.connect(lambda: self.ui_functions.open_settings_window(self.table_ui, self.table_settings_window, "table"))
        # 四图表中的联动checkbox
        self.connect_charts.stateChanged.connect(self.ui_functions.on_connect_charts_changed)


        '''SETTINGS page btn '''
        self.one_chart_ui.finish_btn.clicked.connect(lambda : self.ui_functions.one_finish_settings(self.one_chart_ui, self.one_chart_settings_window))
        self.one_chart_ui.cancel_btn.clicked.connect(lambda : self.ui_functions.one_close_setting_window(self.one_chart_ui, self.one_chart_settings_window))
        self.one_chart_ui.reset_btn.clicked.connect(lambda : self.ui_functions.one_reset_settings(self.one_chart_ui))

        self.four_chart_ui.finish_btn.clicked.connect(
            lambda: self.ui_functions.four_finish_settings(self.four_chart_ui, self.four_chart_settings_window)
        )
        self.four_chart_ui.cancel_btn.clicked.connect(
            lambda: self.ui_functions.four_close_setting_window(self.four_chart_ui, self.four_chart_settings_window)
        )
        self.four_chart_ui.reset_btn.clicked.connect(lambda : self.ui_functions.four_reset_settings(self.four_chart_ui))

        self.table_ui.finish_btn.clicked.connect(
            lambda: self.ui_functions.table_finish_settings(self.table_ui, self.table_settings_window)
        )
        self.table_ui.cancel_btn.clicked.connect(
            lambda: self.ui_functions.table_close_setting_window(self.table_settings_window)
        )



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
        for _, button in btn_dict.items():
            if button != btn:
                button.setChecked(False)
                button.setStyleSheet("")  # 恢复QSS
                button.style().unpolish(button)
                button.style().polish(button)
                button.update()

        # show stack pages
        if btn_name == "one_page_btn":
            self.stackedWidget.setCurrentWidget(self.page_one_container)
            self.one_page_btn.setStyleSheet(
                '''
                background : #90b6e7;
                icon: url(:/png_check/png/one_check.png);
                icon-size: 20px 20px;
                border-left : 2px solid white;
                padding-right : 2px;
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
                padding-right : 2px;
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
                padding-right : 2px;
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
                padding-right : 2px;
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
                padding-right : 2px;
                '''
            )
            # 进入设置页时刷新 .env 到输入框
            try:
                self.ui_functions.settings_api_load()
            except Exception:
                pass

    # 事件过滤器，拖动窗口
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        # 禁止最大化或全屏时拖动窗口
        if self.isMaximized() or self.isFullScreen():
            return super().eventFilter(obj, event)
        if obj == self.header_right_btn_container or obj == self.header_text_and_icon:
            if event.type() == QEvent.Type.MouseButtonPress and isinstance(event, QMouseEvent) and event.button() == Qt.MouseButton.LeftButton:
                self._dragging = True
                self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                return True
            elif event.type() == QEvent.Type.MouseMove and isinstance(event, QMouseEvent) and getattr(self, '_dragging', False):
                self.move(event.globalPosition().toPoint() - self._drag_offset)
                return True
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self._dragging = False
                return True
        return super().eventFilter(obj, event)

    def _toggle_max_restore(self):
        global global_state
        if global_state == True:
            global_state = False
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
            global_state = True
            # 记住窗口位置和大小
            self.showMaximized()
            self.window_btn.setStyleSheet(
                '''
                image: url(:/svg/svg/small_window.svg);
                padding : 4px;
                image-position : center;
                '''
            )


    def resizeEvent(self, event: QResizeEvent) -> None:
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

    def initialize_txt_note_btn(self):
        # initialize txt docs into note editor，每次打开软件时初始化note按钮
        # txt文档路径 file path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        note_dir = os.path.join(parent_dir, "note")
        if not os.path.exists(note_dir):  # create folder if not exist
            os.makedirs(note_dir)

        # 获取当前目录下的文件
        try:
            all_items = os.listdir(note_dir)
            txt_files: list[str] = []
            for item in all_items:
                full_path = os.path.join(note_dir, item)
                if os.path.isfile(full_path) and item.endswith('.txt'):
                    txt_files.append(full_path)

            # 过滤User_instructions.txt
            txt_files = [f for f in txt_files if not f.endswith("User_instructions.txt")]
        except Exception:
            logging.error("Failed to get txt file in note folder, continue")
            return

        # 遍历名称，创建按钮
        layout = self.scrollAreaWidgetContents.layout()
        for note_path in txt_files:
            note_name = os.path.basename(note_path)
            note_name_no_ext = os.path.splitext(note_name)[0]
            safe_var_name = note_name_no_ext.replace(' ', '_').replace('-', '_')    # 去除非法字符
            new_button = QPushButton(note_name_no_ext)
            new_button.setObjectName(note_name_no_ext)
            layout.insertWidget(0, new_button) # type: ignore

            # 设置为mainWindow的属性
            setattr(self, safe_var_name, new_button)
            # 连接槽函数，传递文件名参数
            new_button.clicked.connect(lambda checked: self.ui_functions.note_btn_open_file_slot(note_name_no_ext)) # type: ignore
        return

    def _get_current_file_name(self):
        """提取当前文件名，在save note功能里面使用"""
        try:
            text = self.note_update_label.text()
            # 检查文本格式是否符合预期
            if ":" in text:
                return text.split(":")[1].strip()  # 使用strip()替代[1:]切片
            else:
                # 如果格式不符合预期，返回空字符串或其他默认值
                return ""
        except Exception:
            # 发生异常时返回空字符串
            return ""

    def load_custom_fonts(self):
        '''提取文件下面的ttf字体文件然后安装字体，并设置后备字体避免缺字'''
        try:
            current_file_path = os.path.dirname(os.path.abspath(__file__))
            font_folder_path = os.path.join(current_file_path, "font")

            # 尝试加载 Comfortaa 字体
            comfortaa_id = QFontDatabase.addApplicationFont(os.path.join(font_folder_path, "Comfortaa-Medium.ttf"))
            comfortaa_families = QFontDatabase.applicationFontFamilies(comfortaa_id)

            # 设定字体栈，包含常见的中英文字体作为后备
            families: list[str] = []
            if comfortaa_families:
                families.append(comfortaa_families[0])
            # Windows 常见中文/英文字体后备
            families.extend(["Microsoft YaHei UI", "Segoe UI", "Arial", "sans-serif"])

            app_font = QFont()
            app_font.setFamilies(families)
            # 可根据 UI 视觉设置默认字号（不强制）
            # app_font.setPointSize(10)

            # 应用到整个应用程序，优先级高于单个控件默认
            QApplication.setFont(app_font)
            self.setFont(app_font)

            if comfortaa_families:
                logging.info(f"Applied font: {comfortaa_families[0]}")
                logging.info("Applied font Comfortaa-Medium.ttf with fallbacks")
            else:
                logging.info("Comfortaa not loaded; using fallback font stack")

        except Exception as e:
            logging.error(f"Failed to load custom fonts: {e}, continue with system defaults")