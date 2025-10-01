"""
主窗口的设置与控件信号
class mainWindow(QMainWindow, Ui_MainWindow):
    # 明确声明拖动状态的类型，避免"类型未知"
    _dragging: bool
    _drag_offset: QPoint

    # 新增：记录窗口原始位置和大小
    _normal_geometry: Optional[QRect] = Nonemain.py文件
"""

import os
from typing import Optional, Any
from weakref import WeakKeyDictionary
from PySide6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QListView
from PySide6.QtCore import QObject, QEvent, QPoint, QRect
from PySide6.QtGui import QResizeEvent, QMouseEvent
from gui import *
from .ui_function import UiFunctions
from gui.custom_grip import CustomGrip
from gui.i18n_support import (
    available_locales,
    format_language_name,
    set_locale,
    translate,
)
from gui.logging_i18n import log_error, log_info, log_warning

# 全局化窗口是否全屏，开始是false
global_state = False


class mainWindow(QMainWindow, Ui_MainWindow):
    # 明确声明拖动状态的类型，避免“类型未知”
    _dragging: bool
    _drag_offset: QPoint

    # 新增：记录窗口原始位置和大小
    _normal_geometry: Optional[QRect] = None

    def __init__(self, language: Optional[str] = None):
        super().__init__()
        self._current_language: str = set_locale(language or "zh")
        self._recent_update_time: str = ""

        self._original_stylesheets: WeakKeyDictionary[QWidget, str] = (
            WeakKeyDictionary()
        )
        self._font_family_map: dict[str, list[str]] = {}

        self.setupUi(self)  # type: ignore
        self._language_combo_view: Optional[QListView] = None
        self._init_language_selector()
        self._cache_widget_stylesheets()

        self.ui_functions = UiFunctions(self)
        self.chart_functions = ChartFunction(self)

        # import fonts 使用字体
        self.load_custom_fonts()

        # 读取更新日期设置
        existing_data: dict[str, Any] = self.ui_functions.get_settings_from_json()
        self._recent_update_time = existing_data.get("recent_update_time", "")
        self._apply_recent_update_labels()

        # 实例化ONE PAGE小窗口
        self.one_chart_settings_window = QWidget()
        self.one_chart_ui = Ui_OneChartSettingsPanel()
        self.one_chart_ui.setupUi(self.one_chart_settings_window)  # type: ignore
        self.one_chart_ui.first_color_btn.clicked.connect(
            lambda: self.ui_functions.set_color(self.one_chart_ui.first_color_btn)
        )
        self.one_chart_ui.second_color_btn.clicked.connect(
            lambda: self.ui_functions.set_color(self.one_chart_ui.second_color_btn)
        )

        # 实例化FOUR PAGE小窗口
        self.four_chart_settings_window = QWidget()
        self.four_chart_ui = Ui_FourChartSettingsPanel()
        self.four_chart_ui.setupUi(
            self.four_chart_settings_window
        )  # pyright: ignore[reportUnknownMemberType]
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
        self.table_ui.setupUi(self.table_settings_window)  # type: ignore

        # 去除系统标题栏, Qt6 命名空间的枚举
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)

        # 初始化左边栏按钮样式
        self.one_page_btn.setStyleSheet(
            """
            background : #90b6e7;
            icon: url(:/png_check/png/one_check.png);
            icon-size: 20px 20px;
            border-left : 2px solid white;
            """
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

        """Settings page btn signal connection"""
        # 点击api确认按钮，保存输入的API
        self.api_save_btn.clicked.connect(self.ui_functions.settings_api_save)
        # 重置日志文件按钮
        self.clear_log_btn.clicked.connect(self.ui_functions.clear_logs)
        self.download_for_all_check.stateChanged.connect(
            self.ui_functions.download_all_checkbox_settings
        )

        """Notes Editor page btn """
        self.note_add_btn.clicked.connect(self.ui_functions.note_add_extra_page)
        self.note_delete_btn.clicked.connect(self.ui_functions.note_delete_page)
        self.note_rename_btn.clicked.connect(self.ui_functions.note_rename_page)
        self.note_instructions_btn.clicked.connect(
            self.ui_functions.note_open_instruction
        )

        # 初始化note按钮，识别并读取txt文件
        self.initialize_txt_note_btn()
        self.save_text.clicked.connect(
            lambda: self.ui_functions.note_save_file(self._get_current_file_name())
        )

        """Chart & Table page btn """
        self.one_set_preference.clicked.connect(
            lambda: self.ui_functions.open_settings_window(
                self.one_chart_ui, self.one_chart_settings_window, "one"
            )
        )
        self.four_settings_button.clicked.connect(
            lambda: self.ui_functions.open_settings_window(
                self.four_chart_ui, self.four_chart_settings_window, "four"
            )
        )
        self.page_table_set_preference.clicked.connect(
            lambda: self.ui_functions.open_settings_window(
                self.table_ui, self.table_settings_window, "table"
            )
        )
        # 四图表中的联动checkbox
        self.connect_charts.stateChanged.connect(
            self.ui_functions.on_connect_charts_changed
        )

        """SETTINGS page btn """
        self.one_chart_ui.finish_btn.clicked.connect(
            lambda: self.ui_functions.one_finish_settings(
                self.one_chart_ui, self.one_chart_settings_window
            )
        )
        self.one_chart_ui.cancel_btn.clicked.connect(
            lambda: self.ui_functions.one_close_setting_window(
                self.one_chart_ui, self.one_chart_settings_window
            )
        )

        self.four_chart_ui.finish_btn.clicked.connect(
            lambda: self.ui_functions.four_finish_settings(
                self.four_chart_ui, self.four_chart_settings_window
            )
        )
        self.four_chart_ui.cancel_btn.clicked.connect(
            lambda: self.ui_functions.four_close_setting_window(
                self.four_chart_ui, self.four_chart_settings_window
            )
        )

        self.table_ui.finish_btn.clicked.connect(
            lambda: self.ui_functions.table_finish_settings(
                self.table_ui, self.table_settings_window
            )
        )
        self.table_ui.cancel_btn.clicked.connect(
            lambda: self.ui_functions.table_close_setting_window(
                self.table_settings_window
            )
        )

        self.refresh_translations()

    def _init_language_selector(self) -> None:
        try:
            layout = self.verticalLayout_23
        except AttributeError:
            self.language_combo = None  # type: ignore[attr-defined]
            self.language_label = None  # type: ignore[attr-defined]
            return

        container = QWidget(self.api_group_box)
        container.setObjectName("language_selector_container")
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.language_label = QLabel(container)
        self.language_label.setObjectName("language_label")
        self.language_label.setStyleSheet(
            "color: #dce6ff;\n"
            "font-family: 'Comfortaa';\n"
            "font-size: 11px;\n"
            "padding-right: 6px;"
        )
        row.addWidget(self.language_label)

        self.language_combo = QComboBox(container)
        self.language_combo.setObjectName("language_combo")
        self.language_combo.setMinimumWidth(170)
        self.language_combo.setMinimumHeight(30)
        self.language_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.language_combo.setStyleSheet(
            "QComboBox {\n"
            "    background-color: #202023;\n"
            "    color: #dce6ff;\n"
            "    border: 1px solid #404043;\n"
            "    border-radius: 8px;\n"
            "    padding: 4px 32px 4px 12px;\n"
            "    font-family: 'Comfortaa';\n"
            "    font-size: 11px;\n"
            "}\n"
            "QComboBox:hover {\n"
            "    border-color: #90b6e7;\n"
            "}\n"
            "QComboBox:focus {\n"
            "    border-color: #90b6e7;\n"
            "    background-color: #2b2e32;\n"
            "}\n"
            "QComboBox::drop-down {\n"
            "    width: 28px;\n"
            "    border-left: 1px solid #404043;\n"
            "    border-top-right-radius: 8px;\n"
            "    border-bottom-right-radius: 8px;\n"
            "    background: #202023;\n"
            "}\n"
            "QComboBox::down-arrow {\n"
            "    image: url(:/svg/svg/expand.svg);\n"
            "    width: 12px;\n"
            "    height: 12px;\n"
            "}\n"
            "QComboBox QAbstractItemView {\n"
            "    background-color: #202023;\n"
            "    border: 1px solid #404043;\n"
            "    border-radius: 6px;\n"
            "    color: #dce6ff;\n"
            "    selection-background-color: #90b6e7;\n"
            "    selection-color: #0c111f;\n"
            "}\n"
        )
        dropdown_view = QListView(container)
        dropdown_view.setObjectName("language_combo_view")
        dropdown_view.setCursor(Qt.CursorShape.PointingHandCursor)
        dropdown_view.setStyleSheet(
            "QListView {\n"
            "    background-color: #202023;\n"
            "    border: none;\n"
            "    padding: 4px;\n"
            "}\n"
            "QListView::item {\n"
            "    padding: 6px 12px;\n"
            "    color: #dce6ff;\n"
            "}\n"
            "QListView::item:selected {\n"
            "    background-color: #90b6e7;\n"
            "    color: #0c111f;\n"
            "}\n"
        )
        self.language_combo.setView(dropdown_view)
        self._language_combo_view = dropdown_view

        for locale in available_locales():
            self.language_combo.addItem(format_language_name(locale), locale)

        initial_index = self.language_combo.findData(self._current_language)
        if initial_index >= 0:
            self.language_combo.setCurrentIndex(initial_index)
        elif self.language_combo.count() > 0:
            self.language_combo.setCurrentIndex(0)
            current = self.language_combo.currentData()
            if isinstance(current, str):
                self._current_language = set_locale(current)

        row.addWidget(self.language_combo)
        row.addStretch()
        layout.insertWidget(0, container)

        self.language_combo.currentIndexChanged.connect(self._on_language_changed)

    def _apply_recent_update_labels(self) -> None:
        if self._recent_update_time:
            text = translate("status.recent_update", time=self._recent_update_time)
        else:
            text = translate("status.recent_update_missing")
        self.table_update_label.setText(text)
        self.update_label_2.setText(text)
        self.four_update_label.setText(text)

    def _on_language_changed(self, index: int) -> None:
        if not hasattr(self, "language_combo"):
            return
        combo = self.language_combo  # type: ignore[attr-defined]
        locale = combo.itemData(index)
        if not isinstance(locale, str):
            return
        if locale == self._current_language:
            return
        self._current_language = set_locale(locale)
        self.ui_functions.apply_language(locale, persist=True)
        self.refresh_translations()

    def refresh_translations(self) -> None:
        self.retranslateUi(self)

        text_updates: list[tuple[Any, str, str]] = [
            (self, "setWindowTitle", "ui.main.window_title"),
            (self.title_text, "setText", "ui.main.header_title"),
            (self.title_label_2, "setText", "ui.main.data_placeholder"),
            (self.table_title_label, "setText", "ui.table.placeholder"),
            (self.four_title_label, "setText", "ui.four.title"),
            (self.connect_charts, "setText", "ui.four.connect"),
            (self.four_title_label_3, "setText", "ui.notes.section_title"),
            (self.four_update_label_3, "setText", "ui.notes.section_subtitle"),
            (self.note_instructions_btn, "setText", "ui.notes.instructions_button"),
            (self.note_status_bar, "setText", "ui.notes.status_bar_hint"),
            (self.note_title_label, "setText", "ui.notes.editor_title"),
            (self.note_update_label, "setText", "ui.notes.default_current_file"),
            (self.note_label_notes, "setText", "notes.reminder.default"),
            (self.note_title_label_2, "setText", "ui.settings.panel_title"),
            (self.note_update_label_2, "setText", "ui.settings.panel_subtitle"),
            (self.setting_page_notify_text, "setText", "ui.settings.api_hint"),
            (self.bea_label, "setText", "ui.settings.api_label.bea"),
            (self.fred_label, "setText", "ui.settings.api_label.fred"),
            (self.bls_label, "setText", "ui.settings.api_label.bls"),
            (self.api_save_btn, "setText", "settings.actions.save"),
            (self.status_label, "setText", "ui.settings.status_placeholder"),
            (self.other_option_text, "setText", "ui.settings.about_title"),
            (self.download_text, "setText", "ui.download.heading"),
            (self.bea, "setText", "ui.download.sources.bea"),
            (self.yf, "setText", "ui.download.sources.yf"),
            (self.fred, "setText", "ui.download.sources.fred"),
            (self.bls, "setText", "ui.download.sources.bls"),
            (self.te, "setText", "ui.download.sources.te"),
            (self.ism, "setText", "ui.download.sources.ism"),
            (self.fw, "setText", "ui.download.sources.fw"),
            (self.dfm, "setText", "ui.download.sources.dfm"),
            (self.nyf, "setText", "ui.download.sources.nyf"),
            (self.cin, "setText", "ui.download.sources.cin"),
            (self.em, "setText", "ui.download.sources.em"),
            (self.fs, "setText", "ui.download.sources.fs"),
            (self.label, "setText", "ui.download.data_start_year"),
            (self.download_csv_check, "setText", "ui.download.options.csv"),
            (self.download_for_all_check, "setText", "ui.download.options.all"),
            (self.download_btn, "setText", "ui.download.actions.start"),
            (self.cancel_btn, "setText", "ui.download.actions.cancel"),
            (self.clear_log_btn, "setText", "ui.download.actions.clear_logs"),
            (self.parallel_download_check, "setText", "ui.download.options.parallel"),
            (self.max_threads_label, "setText", "ui.download.options.max_threads"),
            (self.console_text, "setText", "ui.download.console_title"),
            (self.read_and_agree_check, "setText", "ui.download.terms_checkbox"),
            (self.author_name_and_time, "setText", "ui.footer.signature"),
        ]

        for widget, method_name, key in text_updates:
            try:
                method = getattr(widget, method_name)
            except AttributeError:
                continue
            try:
                method(translate(key))
            except Exception:
                continue

        tooltip_updates: list[tuple[Any, str, str]] = [
            (self.note_list_text_container, "setToolTip", "ui.notes.tooltip"),
        ]

        for widget, method_name, key in tooltip_updates:
            try:
                method = getattr(widget, method_name)
            except AttributeError:
                continue
            try:
                method(translate(key))
            except Exception:
                continue

        self._apply_recent_update_labels()

        combo = getattr(self, "language_combo", None)
        if combo is not None:
            label = getattr(self, "language_label", None)
            if label is not None:
                label.setText(translate("settings.language.label"))
            for idx in range(combo.count()):
                locale = combo.itemData(idx)
                if isinstance(locale, str):
                    combo.setItemText(
                        idx,
                        translate(f"settings.language.option.{locale}"),
                    )

            current_index = combo.findData(self._current_language)
            if current_index >= 0 and combo.currentIndex() != current_index:
                combo.blockSignals(True)
                combo.setCurrentIndex(current_index)
                combo.blockSignals(False)

        self.ui_functions.apply_language(self._current_language, persist=False)
        self._apply_locale_font(self._current_language)

    def left_bar_button_slot(self):
        """left bar btn clicked slot, when click, change page (stack)"""
        btn = self.sender()
        btn_name = btn.objectName()

        # 所有按钮列表
        btn_dict = {
            "one_page_btn": self.one_page_btn,
            "four_page_btn": self.four_page_btn,
            "table_btn": self.table_btn,
            "note_btn": self.note_btn,
            "settings_btn": self.settings_btn,
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
                """
                background : #90b6e7;
                icon: url(:/png_check/png/one_check.png);
                icon-size: 20px 20px;
                border-left : 2px solid white;
                padding-right : 2px;
                """
            )
        elif btn_name == "four_page_btn":
            self.stackedWidget.setCurrentWidget(self.page_four_container)
            self.four_page_btn.setStyleSheet(
                """
                background : #90b6e7;
                icon: url(:/png_check/png/four_check.png);
                icon-size: 20px 20px;
                border-left : 2px solid white;
                padding-right : 2px;
                """
            )
        elif btn_name == "table_btn":
            self.stackedWidget.setCurrentWidget(self.page_table_container)
            self.table_btn.setStyleSheet(
                """
                background : #90b6e7;
                icon: url(:/png_check/png/table_check.png);
                icon-size: 20px 20px;
                border-left : 2px solid white;
                padding-right : 2px;
                """
            )
        elif btn_name == "note_btn":
            self.stackedWidget.setCurrentWidget(self.page_note_container)
            self.note_btn.setStyleSheet(
                """
                background : #90b6e7;
                icon: url(:/png_check/png/note_btn_check.png);
                icon-size: 20px 20px;
                border-left : 2px solid white;
                padding-right : 2px;
                """
            )
        elif btn_name == "settings_btn":
            self.stackedWidget.setCurrentWidget(self.page_settings_container)
            self.settings_btn.setStyleSheet(
                """
                background : #90b6e7;
                icon: url(:/png_check/png/settings_check.png);
                icon-size: 20px 20px;
                border-left : 2px solid white;
                padding-right : 2px;
                """
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
            if (
                event.type() == QEvent.Type.MouseButtonPress
                and isinstance(event, QMouseEvent)
                and event.button() == Qt.MouseButton.LeftButton
            ):
                self._dragging = True
                self._drag_offset = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
                return True
            elif (
                event.type() == QEvent.Type.MouseMove
                and isinstance(event, QMouseEvent)
                and getattr(self, "_dragging", False)
            ):
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
                """
                image: url(:/svg/svg/big_window.svg);
                padding : 4px;
                image-position : center;
                """
            )
            self.resize(self.width() + 0, self.height() + 0)
        else:
            global_state = True
            # 记住窗口位置和大小
            self.showMaximized()
            self.window_btn.setStyleSheet(
                """
                image: url(:/svg/svg/small_window.svg);
                padding : 4px;
                image-position : center;
                """
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
                if os.path.isfile(full_path) and item.endswith(".txt"):
                    txt_files.append(full_path)

            # 过滤User_instructions.txt
            txt_files = [
                f for f in txt_files if not f.endswith("User_instructions.txt")
            ]
        except Exception:
            log_error("notes.load_failed")
            return

        # 遍历名称，创建按钮
        layout = self.scrollAreaWidgetContents.layout()
        for note_path in txt_files:
            note_name = os.path.basename(note_path)
            note_name_no_ext = os.path.splitext(note_name)[0]
            safe_var_name = note_name_no_ext.replace(" ", "_").replace(
                "-", "_"
            )  # 去除非法字符
            new_button = QPushButton(note_name_no_ext)
            new_button.setObjectName(note_name_no_ext)
            layout.insertWidget(0, new_button)  # type: ignore

            # 设置为mainWindow的属性
            setattr(self, safe_var_name, new_button)
            # 连接槽函数，传递文件名参数
            new_button.clicked.connect(lambda checked: self.ui_functions.note_btn_open_file_slot(note_name_no_ext))  # type: ignore
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

    def _cache_widget_stylesheets(self) -> None:
        widgets: list[QWidget] = [self]
        widgets.extend(self.findChildren(QWidget))
        if self._language_combo_view is not None:
            widgets.append(self._language_combo_view)

        # 使用新的缓存覆盖旧的，以便后续能恢复原始样式
        self._original_stylesheets = WeakKeyDictionary()
        for widget in widgets:
            style = widget.styleSheet()
            if style:
                self._original_stylesheets[widget] = style

    @staticmethod
    def _deduplicate_sequence(items: list[Optional[str]]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for item in items:
            if not item:
                continue
            if item in seen:
                continue
            seen.add(item)
            ordered.append(item)
        return ordered

    def _apply_font_to_stylesheets(self, primary_family: str) -> None:
        if not getattr(self, "_original_stylesheets", None):
            return
        for widget, base_style in list(self._original_stylesheets.items()):
            if not base_style:
                continue
            if not primary_family or "Comfortaa" not in base_style:
                widget.setStyleSheet(base_style)
                continue
            if primary_family.lower().startswith("comfortaa"):
                widget.setStyleSheet(base_style)
            else:
                widget.setStyleSheet(base_style.replace("Comfortaa", primary_family))

    def _apply_locale_font(self, locale: str) -> None:
        if not self._font_family_map:
            return

        families = self._font_family_map.get(locale) or self._font_family_map.get("en")
        if not families:
            return

        primary_family = families[0]
        app_font = QFont()
        if hasattr(app_font, "setFamilies"):
            app_font.setFamilies(families)
        else:
            app_font.setFamily(primary_family)
        QApplication.setFont(app_font)

        target_widgets: list[QWidget] = [self]
        target_widgets.extend(self.findChildren(QWidget))
        if self._language_combo_view is not None:
            target_widgets.append(self._language_combo_view)

        for widget in target_widgets:
            font = widget.font()
            if hasattr(font, "setFamilies"):
                font.setFamilies(families)
            else:
                font.setFamily(primary_family)
            widget.setFont(font)

        self._apply_font_to_stylesheets(primary_family)
        self._apply_masked_input_font()

    def _apply_masked_input_font(self) -> None:
        fields = [
            getattr(self, "bea_api", None),
            getattr(self, "fred_api", None),
            getattr(self, "bls_api", None),
        ]
        uniform_font = QFont()
        if hasattr(uniform_font, "setFamilies"):
            uniform_font.setFamilies(["Segoe UI", "Arial", "sans-serif"])
        else:
            uniform_font.setFamily("Segoe UI")
        for field in fields:
            if field is None:
                continue
            try:
                field.setFont(uniform_font)
            except Exception:
                continue

    def load_custom_fonts(self):
        """提取文件下面的ttf字体文件然后安装字体，并设置后备字体避免缺字"""
        try:
            current_file_path = os.path.dirname(os.path.abspath(__file__))
            font_folder_path = os.path.join(current_file_path, "font")

            def _load_font(filename: str) -> Optional[str]:
                path = os.path.join(font_folder_path, filename)
                if not os.path.exists(path):
                    log_warning("fonts.file_missing", {"filename": filename})
                    return None
                font_id = QFontDatabase.addApplicationFont(path)
                if font_id < 0:
                    log_warning("fonts.load_failed", {"filename": filename})
                    return None
                families = QFontDatabase.applicationFontFamilies(font_id)
                if not families:
                    log_warning("fonts.no_family", {"filename": filename})
                    return None
                return families[0]

            comfortaa_family = _load_font("Comfortaa-Medium.ttf")
            source_han_family = _load_font("SourceHanSansSC-Medium.otf")

            english_sequence = self._deduplicate_sequence(
                [
                    comfortaa_family,
                    source_han_family,
                    "Microsoft YaHei UI",
                    "Segoe UI",
                    "Arial",
                    "sans-serif",
                ]
            )

            chinese_sequence = self._deduplicate_sequence(
                [
                    source_han_family,
                    comfortaa_family,
                    "Microsoft YaHei UI",
                    "PingFang SC",
                    "Segoe UI",
                    "Arial",
                    "sans-serif",
                ]
            )

            if not english_sequence:
                english_sequence = ["Segoe UI", "Arial", "sans-serif"]

            if not chinese_sequence:
                chinese_sequence = english_sequence

            self._font_family_map = {
                "en": english_sequence,
                "zh": chinese_sequence,
            }

            self._apply_locale_font(self._current_language)

            applied_stack = self._font_family_map.get(self._current_language, [])
            log_info(
                "fonts.applied_stack",
                {
                    "locale": self._current_language,
                    "stack": ", ".join(applied_stack) if applied_stack else "<default>",
                },
            )

        except Exception as e:
            log_error("fonts.exception", {"error": str(e)})
