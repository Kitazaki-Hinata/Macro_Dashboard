'''
这里包括所有ui的控件槽函数
动画等函数在gui_animation文件中
'''

# pyright: reportUnknownParameterType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportMissingTypeStubs=false

import os
import logging
import sqlite3
import json
import math
from datetime import datetime
from typing import Optional, Dict, Any, Protocol
import pyqtgraph as pg
import pandas as pd
from PySide6.QtCore import QTimer

from downloaders.common import CancellationToken, CancelledError

from gui import *


from dotenv import dotenv_values


class _MainWindowProto(Protocol):
    bea_api: Any
    fred_api: Any
    bls_api: Any
    status_label: Any
    console_area: Any
    int_year_spinbox: Any
    download_for_all_check: Any
    # sources checkboxes
    bea: Any
    yf: Any
    fred: Any
    bls: Any
    te: Any
    fw : Any
    dfm : Any
    em : Any
    fs : Any
    cin : Any
    ism : Any
    nyf : Any
    # parallel controls
    parallel_download_check: Any
    max_threads_spin: Any
    download_btn: Any
    cancel_btn: Any
    read_and_agree_check : Any
    # UI labels and controls for various pages
    title_label_2: Any
    table_update_label: Any
    update_label_2: Any
    four_update_label: Any
    # Note page controls
    note_enter_passage_name: Any
    note_status_bar: Any
    scrollAreaWidgetContents: Any
    plainTextEdit: Any
    save_text: Any
    note_update_label: Any
    note_label_notes: Any
    # Download controls
    download_csv_check: Any
    chart_functions : Any
    table_functions: Any
    four_chart_one: Any
    four_chart_two: Any
    four_chart_three: Any
    four_chart_four: Any


class _DownloadWorker(QObject):
    '''用于执行数据下载任务的工作线程对象'''
    progress = Signal(str)
    finished = Signal()
    failed = Signal(str)

    def __init__(self, json_data: Dict[str, Any], start_year: int, download_all: bool, selected_sources: Optional[list[str]] | None = None, main_window: Optional[_MainWindowProto] = None):
        super().__init__()
        self._json_data = json_data
        self._start_year = start_year
        self._download_all = download_all
        self._is_cancelled = False
        self._selected_sources = selected_sources or []
        self.main_window = main_window
        self._cancel_token = CancellationToken()

    def cancel(self):
        self._is_cancelled = True
        self._cancel_token.cancel()

    def run(self):
        try:
            # 延迟导入后端工厂，避免缺少第三方依赖导致 UI 启动失败
            try:
                from downloaders import DownloaderFactory  # type: ignore
                _backend_available = True
            except Exception as e:  # ModuleNotFoundError 等
                DownloaderFactory = None  # type: ignore
                _backend_available = False
                self.progress.emit(f"Backend not available: {e}. Running mock download...")

            sources = [
                "bea",
                "yf",
                "fred",
                "bls",
                "te",
                "ism",
                "fw"
                "dfm",
                "em",
                # "fs",
                "cin",
                "nyf"
                ] if self._download_all else list(self._selected_sources)
            if not sources:
                self.progress.emit("No sources selected. Nothing to do.")
                self.finished.emit()
                return

            for src in sources:
                if self._is_cancelled:
                    self.progress.emit("Cancelled by user.")
                    break
                if not _backend_available:
                    # 模拟下载进度
                    try:
                        import time
                        for i in range(5):
                            if self._is_cancelled:
                                break
                            self.progress.emit(f"{src}: mock step {i+1}/5...")
                            time.sleep(0.3)
                        self.progress.emit(f"{src} done (mock).")
                    except Exception as e:
                        self.progress.emit(f"{src} mock failed: {e}")
                    continue

                self.progress.emit(f"Creating downloader for: {src}...")
                downloader = DownloaderFactory.create_downloader(  # type: ignore[reportUnknownMemberType]
                    source=src,
                    json_data=self._json_data,
                    request_year=self._start_year,
                )
                if downloader is None:
                    self.progress.emit(f"Skip {src}: no downloader available.")
                    continue
                self.progress.emit(f"Downloading {src} data to local...")
                try:
                    # 优先判断 download_csv_check 是否被选中
                    if self.main_window and hasattr(self.main_window, "download_csv_check") and self.main_window.download_csv_check.isChecked():
                        self.progress.emit(f"Exporting {src} data to CSV...")
                        downloader.to_db(return_csv=True, cancel_token=self._cancel_token)
                    else:
                        downloader.to_db(return_csv=False, cancel_token=self._cancel_token)
                    self.progress.emit(f"{src} done.")
                except CancelledError:
                    self._is_cancelled = True
                    self.progress.emit(f"{src} cancelled.")
                    break
                except Exception as e:
                    self.progress.emit(f"{src} failed: {e}")
                    continue
        except Exception as e:
            self.failed.emit(str(e))
            return
        finally:
            self.finished.emit()


class UiFunctions():  # 删除:mainWindow
    def __init__(self, main_window: _MainWindowProto):
        self.main_window: _MainWindowProto = main_window
        self._dl_thread: Optional[QThread] = None
        self._worker: Optional[_DownloadWorker] = None
        # parallel executor refs
        self._parallel_exec = None
        self._cleanup_pending = False
        # wire buttons
        try:
            self.main_window.download_btn.clicked.connect(self.start_download)
            self.main_window.cancel_btn.clicked.connect(self.cancel_download)
            self.main_window.cancel_btn.setEnabled(False)
        except Exception:
            # best-effort wiring; ignore if widgets not built yet
            pass

        # 初始化时尝试从 .env 读取并填充输入框
        try:
            self.settings_api_load()
        except Exception:
            pass

    def set_color(self, widget: Any):
        current_color = widget.styleSheet().split(":")[1][1:]   # 当前的颜色
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            widget.setStyleSheet(f"background: {color.name()}")

    # ===================== Settings JSON 结构保护 =====================
    def _ensure_settings_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """确保 settings.json 的基础结构存在，防止 KeyError。
        返回修补后的字典（原地修改）。"""
        try:
            if 'recent_update_time' not in data:
                from datetime import date
                data['recent_update_time'] = str(date.today())
            one = data.setdefault('one_chart_settings', {})
            two = one.setdefault('first_data', {})
            one_second = one.setdefault('second_data', {})
            two.setdefault('data_name', '')
            two.setdefault('time_lags', 0)
            two.setdefault('color', '#90b6e7')
            one_second.setdefault('data_name', '')
            one_second.setdefault('time_lags', 0)
            one_second.setdefault('color', '#f39c12')
            four = data.setdefault('four_chart_settings', {})
            for key, default_color in zip(
                ['first_data','second_data','third_data','fourth_data'],
                ['#90b6e7','#f39c12','#2ecc71','#e74c3c']
            ):
                slot = four.setdefault(key, {})
                slot.setdefault('data_name','')
                slot.setdefault('time_lags',0)
                slot.setdefault('color', default_color)
            table = data.setdefault('table_settings', {})
            table.setdefault('table_name', [])
        except Exception:
            pass
        return data

    # ===================== CHART LINK TOGGLE =====================
    def on_connect_charts_changed(self, state):
        """主窗口复选框回调：勾选 -> 四图联动；取消 -> 取消联动。
        仅做健壮性最小实现：
          * X 轴联动（共用缩放/平移）
          * 十字线同步（可选，若 chart_functions 具备内部封装则调用其方法）
        """


        link = (state == 2)
        # 优先尝试调用 chart_functions 已存在的封装方法（如果后来添加了）
        try:
            if hasattr(self.main_window, 'chart_functions') and hasattr(self.main_window.chart_functions, 'link_four_charts'):
                self.main_window.chart_functions.link_four_charts(link)  # type: ignore[attr-defined]
                return
        except Exception:
            pass

        # 手动实现基础联动
        try:
            widgets: list[pg.PlotWidget] = []
            mapping = [
                (self.main_window.four_chart_one, "four_chart_one_plot"),
                (self.main_window.four_chart_two, "four_chart_two_plot"),
                (self.main_window.four_chart_three, "four_chart_three_plot"),
                (self.main_window.four_chart_four, "four_chart_four_plot"),
            ]
            for container, obj_name in mapping:
                try:
                    w = container.findChild(pg.PlotWidget, obj_name)
                    if w is not None:
                        widgets.append(w)
                except Exception:
                    continue
            if len(widgets) < 2:
                return
            if link:
                master_vb = widgets[0].getViewBox()
                for w in widgets[1:]:
                    vb = w.getViewBox()
                    vb.setXLink(master_vb)
                # 简单十字线同步：只处理主图鼠标事件广播 X 位置
                def sync_mouse(pos):
                    if not widgets[0].sceneBoundingRect().contains(pos):
                        return
                    mp = master_vb.mapSceneToView(pos)
                    x_val = mp.x()
                    for w in widgets:
                        try:
                            pi = w.getPlotItem()
                            # 查找十字线
                            # 由于十字线存放在 chart_functions.crosshairs 中，若存在则直接使用
                            cross = getattr(self.main_window, 'chart_functions', 'crosshairs', {}) if hasattr(self.main_window, 'chart_functions') else {}
                            key = w.objectName()
                            if key in cross:
                                v_line, h_line = cross[key]
                                v_line.setPos(x_val)
                        except Exception:
                            pass
                # 绑定到主图 scene（临时实现，不保存引用避免重复，多次勾选需刷新）
                try:
                    widgets[0].scene().sigMouseMoved.connect(sync_mouse)  # type: ignore[arg-type]
                except Exception:
                    pass
            else:
                for w in widgets:
                    vb = w.getViewBox()
                    vb.setXLink(None)
        except Exception:
            pass

    '''SETTINGS PAGE SLOTS METHODS'''
    def _env_file_path(self) -> str:
        base = os.path.abspath(os.path.dirname(__file__))
        return os.path.abspath(os.path.join(base, "..", ".env"))

    def settings_api_load(self):
        """从 .env 加载 API 值并填充到界面输入框。"""
        path = self._env_file_path()
        if not os.path.exists(path):
            return
        try:
            cfg = dotenv_values(path)
        except Exception as e:
            logging.error(f"Failed to load .env: {e}")
            return
        bea = (cfg.get("bea") or "").strip()
        fred = (cfg.get("fred") or "").strip()
        bls = (cfg.get("bls") or "").strip()
        try:
            self.main_window.bea_api.setText(bea)
            self.main_window.fred_api.setText(fred)
            self.main_window.bls_api.setText(bls)
            if bea or fred or bls:
                self.main_window.status_label.setText("Loaded API keys from .env")
                self.main_window.status_label.setStyleSheet("color: #90b6e7")
        except Exception:
            # 如果控件不可用则忽略
            pass

    def settings_api_save(self):
        # find whether exist .env file
        logging.info("settings_api_save invoked")
        path = self._env_file_path()

        # get api_text from line edit
        bea_api = self.main_window.bea_api.text()
        fred_api = self.main_window.fred_api.text()
        bls_api = self.main_window.bls_api.text()

        try:
            # 创建 .env 文件
            with open(path, 'w', encoding='utf-8') as f:
                # 写入基本的环境变量模板
                f.write(f'bea = "{bea_api}" \n')
                f.write(f'fred = "{fred_api}" \n')
                f.write(f'bls = "{bls_api}" ')
            self.main_window.status_label.setText("API key saved successfully")
            self.main_window.status_label.setStyleSheet("color: #90b6e7")
            logging.info(f".env file created successfully at path: {path}")

        except Exception as e:
            self.main_window.status_label.setText("FAILED to save API key, see log file")
            self.main_window.status_label.setStyleSheet("color: #fa88aa")
            logging.error(f"Failed to create .env file at path: {path}, since {e}")

    def download_all_checkbox_settings(self):
        checkbox_list = [
            self.main_window.bea,
            self.main_window.yf,
            self.main_window.fred,
            self.main_window.bls,
            self.main_window.te,
            self.main_window.cin,
            self.main_window.dfm,
            self.main_window.em,
            self.main_window.fs,
            self.main_window.fw,
            self.main_window.ism,
            self.main_window.nyf
        ]
        if bool(self.main_window.download_for_all_check.isChecked()):
            # 设置checkbox的逻辑
            for checkbox in checkbox_list:
                try:
                    checkbox.setChecked(False)
                    checkbox.setEnabled(False)
                except Exception:
                    pass

        else:
            for checkbox in checkbox_list:
                try:
                    checkbox.setEnabled(True)
                    checkbox.setChecked(False)
                except Exception:
                    pass


    def clear_logs(self):
        """仅清空界面日志窗口，保留磁盘日志文件。"""
        cleared = False
        try:
            if hasattr(self.main_window, "console_area") and self.main_window.console_area is not None:
                self.main_window.console_area.clear()
                cleared = True
        except Exception as e:
            logging.error(f"Failed to clear console text area: {e}")

        message = (
            "Console log window cleared. Log files remain unchanged."
            if cleared
            else "Console log window unavailable. Log files remain unchanged."
        )
        logging.info(message)

        try:
            self._append_console(message)
        except Exception:
            pass

    '''NOTE PAGE SLOTS METHODS'''
    def note_add_extra_page(self):
        '''点击后新建一个文档和对应的按钮，包括对命名格式的判断'''
        # get btn name from lineedit
        note_name= self.main_window.note_enter_passage_name.text()

        # illegal judgement
        if note_name == "":
            self.main_window.note_status_bar.setText("Please enter a note name")
            self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
            return

        illegal_chars = '\\/:*?"<>| '
        for char in illegal_chars:
            if char in note_name:
                self.main_window.note_status_bar.setText(
                    "\\ / : * ? \" < > |, space are invalid"
                )
                self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
                return
        if note_name == "note_instructions_btn" or note_name == "User_instructions":
            self.main_window.note_status_bar.setText("Name Conflict, change a name")
            self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
            return

        # check whether has duplication 防止命名重复
        layout = self.main_window.scrollAreaWidgetContents.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QPushButton) and widget.text() == note_name:
                    self.main_window.note_status_bar.setText("Name Conflict, change a name")
                    self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
                    return

        button_name = self.main_window.note_enter_passage_name.text()
        new_button = QPushButton(button_name)
        layout.insertWidget(0, new_button)          # 插入到第一个位置

        # create txt file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        note_dir = os.path.join(parent_dir, "note")
        if not os.path.exists(note_dir):   # create folder if not exist
            os.makedirs(note_dir)
        txt_file_path = os.path.join(note_dir, f"{button_name}.txt")
        with open(txt_file_path, "w") as file:
            file.write("")  # 写入空内容

        # update interface
        new_button.clicked.connect(
            lambda checked: self.note_btn_open_file_slot(button_name) # type: ignore
        )
        self.main_window.note_status_bar.setText("Create note successful")
        self.main_window.note_status_bar.setStyleSheet("color: #90b6e7")

    def note_delete_page(self):
        '''点击后删除文章对应的按钮'''
        note_name = self.main_window.note_enter_passage_name.text()
        layout = self.main_window.scrollAreaWidgetContents.layout()

        if not note_name:
            self.main_window.note_status_bar.setText("Please enter a note name")
            self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
            return

        if note_name == "note_instructions_btn" or note_name == "User_instructions" or note_name == "User instructions":
            self.main_window.note_status_bar.setText("This file cannot be deleted")
            self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
            return

        # 遍历布局中的所有控件来找到匹配的按钮
        found = False
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QPushButton) and widget.text() == note_name:
                    layout.removeWidget(widget)
                    widget.deleteLater()

                    # delete text file
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    parent_dir = os.path.dirname(current_dir)
                    note_dir = os.path.join(parent_dir, "note")   # folder path
                    txt_file_path = os.path.join(note_dir, f"{note_name}.txt")
                    if os.path.exists(txt_file_path):
                        os.remove(txt_file_path)

                    found = True
                    break

        if found:
            self.main_window.note_status_bar.setText("Delete note successful")
            self.main_window.note_status_bar.setStyleSheet("color: #90b6e7")
            self.main_window.plainTextEdit.clear()
            self.main_window.plainTextEdit.setReadOnly(True)
            self.main_window.save_text.setDisabled(True)

        else:
            self.main_window.note_status_bar.setText("Note does not exist")
            self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")

    def note_rename_page(self):
        '''重命名文章  rename the file'''
        note_name = self.main_window.note_enter_passage_name.text()
        layout = self.main_window.scrollAreaWidgetContents.layout()

        if not note_name:
            self.main_window.note_status_bar.setText("Please enter a note name")
            self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
            return

        if note_name == "note_instructions_btn" or note_name == "User_instructions" or note_name == "User_Instructions":
            self.main_window.note_status_bar.setText("Name Conflict, change a name")
            self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
            return

        found = False
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QPushButton) and widget.text() == note_name:
                    # 保存旧的objectName用于后续的信号重新连接
                    old_object_name = widget.objectName()

                    widget.setText("Enter and press any to finish")
                    widget.setStyleSheet('''
                        color : #90b6e7;
                        font-family : "Comfortaa", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                        font-weight : Bold;
                    ''')

                    # 创建LineEdit，输入新名称
                    line_edit = QLineEdit()
                    line_edit.setStyleSheet('''
                        color : white;
                        font-weight : Bold;
                        font-family : "Comfortaa", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                        font-size : 8px;
                        min-height : 15px;
                        max-height : 15px;
                    ''')
                    line_edit.setPlaceholderText("Enter new name here")
                    line_edit.setObjectName(f"rename_edit_{note_name}")
                    layout.insertWidget(i + 1, line_edit)

                    def finish_rename(le: QLineEdit = line_edit, btn: QPushButton = widget, old_name: str = old_object_name, idx: int = i):
                        new_name = le.text().strip()
                        if new_name:
                            illegal_chars = '\\/:*?"<>| '
                            is_valid = True
                            for char in illegal_chars:
                                if char in new_name:
                                    is_valid = False
                                    break

                            if is_valid and new_name != "note_instructions_btn":
                                duplicate = False
                                for j in range(layout.count()):
                                    item_check = layout.itemAt(j)
                                    if item_check and item_check.widget():
                                        check_widget = item_check.widget()
                                        if isinstance(check_widget, QPushButton) and check_widget.text() == new_name:
                                            duplicate = True
                                            break

                                if not duplicate:
                                    # 重命名文件
                                    current_dir = os.path.dirname(os.path.abspath(__file__))
                                    parent_dir = os.path.dirname(current_dir)
                                    note_dir = os.path.join(parent_dir, "note")
                                    origin_txt_file_path = os.path.join(note_dir, f"{old_name}.txt")
                                    changed_txt_file_path = os.path.join(note_dir, f"{new_name}.txt")

                                    if os.path.exists(origin_txt_file_path):
                                        os.rename(origin_txt_file_path, changed_txt_file_path)

                                    # 更新按钮的文本和objectName
                                    btn.setText(new_name)
                                    btn.setObjectName(new_name)  # 关键：更新objectName
                                    btn.setStyleSheet("color : white")

                                    # 重新连接按钮的点击信号
                                    try:
                                        # 先断开旧的连接
                                        btn.clicked.disconnect()
                                    except:
                                        pass  # 如果没有连接，忽略错误

                                    # 重新连接新的信号
                                    btn.clicked.connect(
                                        lambda checked: self.note_btn_open_file_slot(new_name)) # type: ignore

                                    self.main_window.note_status_bar.setText("Rename successful")
                                    self.main_window.note_status_bar.setStyleSheet("color: #90b6e7")

                                    layout.removeWidget(le)
                                    le.deleteLater()
                                else:
                                    self.main_window.note_status_bar.setText("Name Conflict, change a name")
                                    self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
                                    le.setFocus()
                            else:
                                self.main_window.note_status_bar.setText("\\ / : * ? \" < > |, space, nums are invalid")
                                self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
                                le.setFocus()
                        else:
                            self.main_window.note_status_bar.setText("Please enter a valid note name")
                            self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
                            le.setFocus()

                    # 连接LineEdit的编辑完成信号
                    line_edit.editingFinished.connect(finish_rename)

                    # 可选：也可以连接回车键信号
                    line_edit.returnPressed.connect(finish_rename)

                    found = True
                    break

        if not found:
            self.main_window.note_status_bar.setText("Note not found")
            self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")

    def note_btn_open_file_slot(self, file_name: str):
        # 传入打开的文件名称，所有新建的按钮均调用这个槽函数
        self.main_window.save_text.setDisabled(False)
        self.main_window.plainTextEdit.setReadOnly(False)  # 先设置允许编写
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        selected_note_dir = os.path.join(parent_dir, "note", f"{file_name}.txt")
        
        # 读取文件内容并显示在plainTextEdit控件中
        try:
            with open(selected_note_dir, 'r', encoding='utf-8') as file:
                content = file.read()
                self.main_window.plainTextEdit.setPlainText(content)
                self.main_window.note_update_label.setText(f"Current file name : {file_name}")
                self.main_window.note_label_notes.setText('Reminder : Remember to click "SAVE" button on the right hand side after you finish writing your notes.')
                self.main_window.note_label_notes.setStyleSheet("color: #ee5c88; margin-left : 20px")
        except FileNotFoundError:
            self.main_window.plainTextEdit.setPlainText("")
            logging.error(f"File {selected_note_dir} not found")
            return
        except Exception as e:
            self.main_window.plainTextEdit.setPlainText("")
            logging.error(f"Error reading file {selected_note_dir}: {str(e)}")
            return

    def note_open_instruction(self):
        # 打开instruction文件，仅用于一个按钮
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        selected_note_dir = os.path.join(parent_dir, "note", f"User_instructions.txt")
        try:
            with open(selected_note_dir, 'r', encoding='utf-8') as file:
                content = file.read()
                self.main_window.plainTextEdit.setPlainText(content)
        except FileNotFoundError:
            self.main_window.plainTextEdit.setPlainText("")
            logging.error(f"File {selected_note_dir} not found")
            return
        self.main_window.note_update_label.setText(f"Current file name : [Read Only] Notes Editor Instructions")
        self.main_window.plainTextEdit.setReadOnly(True)
        self.main_window.note_label_notes.setText(
            f'Reminder : Please read instructions carefully.'
        )
        self.main_window.note_label_notes.setStyleSheet("color: #ee5c88; margin-left : 20px")
        self.main_window.save_text.setDisabled(True)

    def note_save_file(self, file_name: str):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        selected_note_dir = os.path.join(parent_dir, "note", f"{file_name}.txt")

        try:
            file_content = self.main_window.plainTextEdit.toPlainText()
            with open(selected_note_dir, 'w', encoding='utf-8') as file:
                file.write(file_content)
            self.main_window.note_label_notes.setText(
                f'Note successfully saved!'
            )
            self.main_window.note_label_notes.setStyleSheet("color: #90b6e7; margin-left : 20px")

        except Exception as e:
            logging.error(f"Error: notes editor cannot save writing file, error is {e}")
            self.main_window.note_label_notes.setText(
                f'WARNING : THIS NOTE FAILED TO SAVE, PLEASE CHECK LOG FILE "doc/error.log" FILE!!!'
            )
            self.main_window.note_label_notes.setStyleSheet("color: #ee5c88; margin-left : 20px")

    '''ONE CHART PAGE SLOTS METHODS'''
    def open_settings_window(self, ui: Any, window: QWidget, name: str):
        # 先添加下拉框里面的所有选项
        # name 形参用于区分调用此槽方法的是哪个按钮
        combo_box_name: list[str] = self._get_sqlite_col_name()

        if name == "one" or name == "four":
            # 清空选项框
            try:
                ui.first_data_selection_box.clear()
                ui.second_data_selection_box.clear()
                if name != "one":
                    ui.third_data_selection_box.clear()
                    ui.fourth_data_selection_box.clear()
            except Exception:   # 如果没有控件，就pass
                pass

            # 添加数据名称
            try:
                ui.first_data_selection_box.addItems(combo_box_name)
                ui.second_data_selection_box.addItems(combo_box_name)
                if name != "one":
                    ui.third_data_selection_box.addItems(combo_box_name)
                    ui.fourth_data_selection_box.addItems(combo_box_name)
            except Exception:   # 如果没有控件，就pass
                pass

        if name == "one":
            try:
                existing_data: Dict[str, Any] = self.get_settings_from_json()
                ui.first_data_selection_box.setCurrentText(existing_data["one_chart_settings"]["first_data"]["data_name"])
                ui.second_data_selection_box.setCurrentText(existing_data["one_chart_settings"]["second_data"]["data_name"])
            except:
                pass

        if name == "four":
            try:
                existing_data: Dict[str, Any] = self.get_settings_from_json()
                ui.first_data_selection_box.setCurrentText(existing_data["four_chart_settings"]["first_data"]["data_name"])
                ui.second_data_selection_box.setCurrentText(existing_data["four_chart_settings"]["second_data"]["data_name"])
                ui.third_data_selection_box.setCurrentText(existing_data["four_chart_settings"]["third_data"]["data_name"])
                ui.fourth_data_selection_box.setCurrentText(existing_data["four_chart_settings"]["fourth_data"]["data_name"])
            except:
                pass

        if name == "table":
            try:
                # 下拉框显示当前已经显示的数据
                existing_data: Dict[str, Any] = self.get_settings_from_json()

                current_file_path = os.path.dirname(os.path.abspath(__file__))
                table_csv_folder_path = os.path.join(current_file_path, "..", "csv", "A_TABLE_DATA")
                ui.first_data_selection_box.clear()   # 先清除，再添加选项
                for file_name in os.listdir(table_csv_folder_path):
                    ui.first_data_selection_box.addItem(file_name)

                ui.first_data_selection_box.setCurrentText(existing_data["table_settings"]["table_name"])

            except:
                    pass

        # 打开窗口
        window.show()


    '''ONE CHART PAGE SETTINGS SLOTS METHODS'''

    def _get_json_settings_path(self)->str:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "settings.json")

    def get_settings_from_json(self)->Dict[str, Any]:
        '''内部方法，用户打开并读取json文件'''
        settings_file_path =  self._get_json_settings_path()

        # 读取现有设置文件（如果存在）
        try:
            if os.path.exists(settings_file_path):
                with open(settings_file_path, 'r', encoding='utf-8') as f:
                    existing_data: Dict[str, Any] = json.load(f)
            else:
                existing_data = {}
        except Exception as e:
            logging.error(f"Error in reading json settings file: {e}")
            existing_data = {}
        return self._ensure_settings_structure(existing_data)

    # ONE WINDOW
    def one_finish_settings(self, window: Any, widget: QWidget):
        '''确认按钮的槽函数'''
        # define variables
        first_data = window.first_data_selection_box.currentText()
        second_data = window.second_data_selection_box.currentText()

        first_lag  = window.first_time_lag.value()
        second_lag = window.second_time_lag.value()

        first_color = window.first_color_btn.styleSheet().split(":")[1][1:]
        second_color = window.second_color_btn.styleSheet().split(":")[1][1:]

        # 调用内部方法打开json文件
        existing_data : Dict[str, Any] = self.get_settings_from_json()

        existing_data["one_chart_settings"]["first_data"]["data_name"] = first_data
        # # 只有当第二条数据非空时才记录
        # if isinstance(second_data, str) and second_data.strip():
        existing_data["one_chart_settings"]["second_data"]["data_name"] = second_data

        existing_data["one_chart_settings"]["first_data"]["time_lags"] = first_lag
        existing_data["one_chart_settings"]["second_data"]["time_lags"] = second_lag

        existing_data["one_chart_settings"]["first_data"]["color"] = first_color
        existing_data["one_chart_settings"]["second_data"]["color"] = second_color
        
        # 获取 main_plot_widget 实例（PlotWidget）
        main_plot_widget = self.main_window.graph_widget_2.findChild(pg.PlotWidget, "main_plot_widget")
        if main_plot_widget is not None:
            # 如果之前存在右侧 viewbox 与第二条曲线，彻底移除，防止残留第三条曲线
            try:
                if hasattr(main_plot_widget, "_right_viewbox") and getattr(main_plot_widget, "_right_viewbox") is not None:  # type: ignore[attr-defined]
                    old_vb = getattr(main_plot_widget, "_right_viewbox")  # type: ignore[attr-defined]
                    # 移除旧的曲线项
                    for item in list(getattr(old_vb, 'addedItems', [])):
                        try:
                            old_vb.removeItem(item)
                        except Exception:
                            pass
                    # 从场景中摘除旧的 viewbox
                    try:
                        main_plot_widget.getPlotItem().scene().removeItem(old_vb)
                    except Exception:
                        pass
                # 隐藏右轴（会在需要时重新创建）
                try:
                    main_plot_widget.hideAxis('right')
                except Exception:
                    pass
                # 置空引用
                setattr(main_plot_widget, "_right_viewbox", None)
            except Exception:
                pass

            # 全量重置：移除旧 legend（连对象一起删除），保留十字线与 tooltip
            try:
                plot_item = main_plot_widget.getPlotItem()
                # 记录需保留的项目
                keep = set()
                try:
                    v_line, h_line = self.main_window.chart_functions.crosshairs.get('main_plot_widget', (None, None))
                except Exception:
                    v_line = h_line = None
                lbl = None
                try:
                    lbl = self.main_window.chart_functions.labels.get('main_plot_widget')
                except Exception:
                    pass
                keep.update([v_line, h_line, lbl])
                for it in list(plot_item.items):
                    if it not in keep:
                        try:
                            plot_item.removeItem(it)
                        except Exception:
                            pass
                # 移除旧 legend
                if plot_item.legend is not None:
                    try:
                        plot_item.scene().removeItem(plot_item.legend)
                    except Exception:
                        pass
                    try:
                        plot_item.legend = None  # type: ignore
                    except Exception:
                        pass
            except Exception:
                pass

            self.main_window.chart_functions.plot_data(
                data_name=first_data,
                color=[first_color],   # 这里必须是一个list
                widget=main_plot_widget
            )

            if isinstance(second_data, str) and second_data.strip():
                # 第二个数据
                dates, values = self.main_window.chart_functions._get_data_from_database(second_data)
                pen = pg.mkPen(color=second_color, width=2)
                # 获取plotItem
                plot_item = main_plot_widget.getPlotItem()

                # 创建右侧ViewBox
                font = pg.QtGui.QFont()
                font.setPixelSize(10)
                font.setFamilies(["Comfortaa"])
                # 使用自定义 ViewBox，使绘图区内部垂直拖动被自动还原，但允许轴区域控制 Y
                try:
                    from gui.chart_function import OnlyXWheelViewBox  # 延迟导入避免循环
                    right_viewbox = OnlyXWheelViewBox()
                except Exception:
                    right_viewbox = pg.ViewBox()
                plot_item.scene().addItem(right_viewbox)  # 添加到场景
                try:
                    right_viewbox.setMouseEnabled(x=True, y=True)
                except Exception:
                    pass
                # 保存引用，供下次清理
                setattr(main_plot_widget, "_right_viewbox", right_viewbox)

                # 链接右侧轴
                main_plot_widget.showAxis('right')
                right_axis = main_plot_widget.getAxis('right')
                right_axis.setTickFont(font)
                right_axis.linkToView(right_viewbox)
                right_axis.setLabel(second_data, color=second_color)

                # 仅链接 X 轴（时间轴），Y 轴保持独立以适配不同数值量级
                right_viewbox.setXLink(plot_item.vb)

            # 同步视图
                # 保存第二条数据备用（用于动态缩放）
                setattr(main_plot_widget, "_second_values", values)

                def update_views():
                    right_viewbox.setGeometry(plot_item.vb.sceneBoundingRect())
                    right_viewbox.linkedViewChanged(plot_item.vb, right_viewbox.XAxis)
                update_views()
                plot_item.vb.sigResized.connect(update_views)

                def _rescale_right_y():
                    # 右轴动态缩放：增加防抖、阈值与重入保护，避免缩放事件快速触发造成抖动
                    if getattr(main_plot_widget, '_right_rescaling', False):
                        return
                    try:
                        setattr(main_plot_widget, '_right_rescaling', True)
                        vals = getattr(main_plot_widget, '_second_values', [])
                        if not vals:
                            return
                        # 当前主视图的 X 范围（索引）
                        x_range = plot_item.vb.viewRange()[0]
                        x_min = max(0, int(math.floor(x_range[0])))
                        x_max = min(len(vals)-1, int(math.ceil(x_range[1])))
                        if x_max <= x_min:
                            x_max = min(len(vals)-1, x_min+1)

                        last_xrng = getattr(main_plot_widget, '_right_last_xrange', None)
                        cur_xrng = (x_min, x_max)
                        # 如果可见区间没有变化，则跳过
                        if last_xrng == cur_xrng:
                            return

                        sub = vals[x_min:x_max+1]
                        sub_clean = [v for v in sub if v is not None]
                        if not sub_clean:
                            return
                        v_min = min(sub_clean)
                        v_max = max(sub_clean)
                        if v_min == v_max:
                            pad = 0.5 if v_min == 0 else max(1e-6, abs(v_min) * 0.1)
                            v_min -= pad
                            v_max += pad
                        else:
                            span = v_max - v_min
                            pad = max(1e-9, span * 0.08)
                            v_min -= pad
                            v_max += pad

                        last_yrng = getattr(main_plot_widget, '_right_last_yrange', None)
                        # 阈值：若变化幅度很小则不更新，减少抖动
                        if last_yrng is not None:
                            old_min, old_max = last_yrng
                            # 计算相对变化
                            def rel_diff(a, b):
                                denom = max(1e-9, abs(a) + abs(b))
                                return abs(a - b) / denom
                            if rel_diff(v_min, old_min) < 0.01 and rel_diff(v_max, old_max) < 0.01:
                                setattr(main_plot_widget, '_right_last_xrange', cur_xrng)
                                return

                        # 真正更新 YRange（用 blockSignals 防止不必要的级联事件）
                        try:
                            right_viewbox.blockSignals(True)
                            right_viewbox.setYRange(v_min, v_max, padding=0)
                        finally:
                            right_viewbox.blockSignals(False)
                        setattr(main_plot_widget, '_right_last_xrange', cur_xrng)
                        setattr(main_plot_widget, '_right_last_yrange', (v_min, v_max))
                    except Exception:
                        pass
                    finally:
                        setattr(main_plot_widget, '_right_rescaling', False)

                # 主视图范围变化时（包括 Y 变化）触发重新计算右侧 Y
                plot_item.vb.sigRangeChanged.connect(lambda *_: _rescale_right_y())

                # 添加第二个曲线到右侧ViewBox
                second_curve = pg.PlotCurveItem(name=second_data)
                flash_date_buff = list(range(len(values)))
                # 根据 second_time_lag 将数据向左移动若干单位（保持长度不变，末尾以 nan 填充）
                try:
                    lag = int(second_lag) if isinstance(second_lag, int) or isinstance(second_lag, float) else int(second_lag)
                except Exception:
                    lag = 0
                if lag and lag > 0:
                    try:
                        shifted_values = [values[i + lag] if (i + lag) < len(values) else math.nan for i in range(len(values))]
                    except Exception:
                        shifted_values = values
                else:
                    shifted_values = values

                # 提供 name 供悬浮标签识别，并缓存日期列表
                try:
                    second_curve.setData(x=flash_date_buff, y=shifted_values, pen=pen, name=second_data)
                except Exception:
                    second_curve.setData(x=flash_date_buff, y=shifted_values, pen=pen)
                try:
                    setattr(second_curve, '_date_labels', dates)
                except Exception:
                    pass
                right_viewbox.addItem(second_curve)
                right_viewbox.setZValue(10)
                # 第二条曲线 legend 将在后面统一创建
                # 初始做一次右轴自适应
                try:
                    _rescale_right_y()
                except Exception:
                    pass
                # 立刻重建 legend（显示主+副两条），后面保存时再统一刷新一次确保一致
                try:
                    self.main_window.chart_functions.rebuild_legend(main_plot_widget)  # type: ignore[attr-defined]
                except Exception:
                    pass
            else:
                # 如果没有第二条数据，确保旧的右侧 viewbox 已移除
                try:
                    if hasattr(main_plot_widget, "_right_viewbox") and getattr(main_plot_widget, "_right_viewbox") is not None:  # type: ignore[attr-defined]
                        old_vb = getattr(main_plot_widget, "_right_viewbox")  # type: ignore[attr-defined]
                        for item in list(getattr(old_vb, 'addedItems', [])):
                            try:
                                old_vb.removeItem(item)
                            except Exception:
                                pass
                        main_plot_widget.getPlotItem().scene().removeItem(old_vb)
                        setattr(main_plot_widget, "_right_viewbox", None)
                        main_plot_widget.hideAxis('right')
                except Exception:
                    pass

        # 保存到json
        try:
            settings_path = self._get_json_settings_path()
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)
            # 统一重建 legend（先创建再手动添加，避免自动重复）
            try:
                plot_item = main_plot_widget.getPlotItem()
                legend = plot_item.legend
                if legend is None:
                    main_plot_widget.addLegend()
                    legend = plot_item.legend
                # 清空（若框架自动添加了主曲线条目则先清空）
                try:
                    legend.clear()  # type: ignore
                except Exception:
                    pass
                # 收集主 viewbox 曲线
                main_curves = [it for it in plot_item.listDataItems() if getattr(it, 'opts', {}).get('name')]
                added = set()
                for cv in main_curves:
                    nm = getattr(cv, 'opts', {}).get('name')
                    if nm and nm not in added:
                        try:
                            legend.addItem(cv, nm)
                            added.add(nm)
                        except Exception:
                            pass
                # 收集右侧 viewbox 曲线
                if hasattr(main_plot_widget, '_right_viewbox') and getattr(main_plot_widget, '_right_viewbox') is not None:  # type: ignore[attr-defined]
                    rvb = getattr(main_plot_widget, '_right_viewbox')  # type: ignore[attr-defined]
                    for it in list(getattr(rvb, 'addedItems', [])):
                        nm = getattr(getattr(it, 'opts', {}), 'get', lambda *_: None)('name') if hasattr(it, 'opts') else None
                        if not nm and hasattr(it, 'opts'):
                            nm = it.opts.get('name')  # type: ignore
                        if not nm and hasattr(it, 'name'):
                            try:
                                nm_try = it.name() if callable(it.name) else it.name
                                if isinstance(nm_try, str):
                                    nm = nm_try
                            except Exception:
                                pass
                        if nm and nm not in added:
                            try:
                                legend.addItem(it, nm)
                                added.add(nm)
                            except Exception:
                                pass
            except Exception:
                pass
        except Exception as e:
            logging.error(f"写入 one_chart settings.json 失败: {e}")

        # 关闭窗口
        try:
            widget.close()
        except Exception:
            pass

        # 如果 first_data 为空或仅空白，则展示占位提示
        try:
            if isinstance(first_data, str) and first_data.strip():
                self.main_window.title_label_2.setText(first_data)
            else:
                self.main_window.title_label_2.setText("Data name will be here")
        except Exception:
            # 若控件不存在或出错，忽略以保证健壮性
            pass

    def one_close_setting_window(self, window: Any, widget: QWidget):
        try:
            widget.close()
        except Exception:
            pass

    def one_reset_settings(self, window: Any):
        # 重置设置面板默认值
        window.first_color_btn.setStyleSheet(f"background-color: #90b6e7")
        window.second_color_btn.setStyleSheet(f"background-color: #ee5c88")
        window.first_time_lag.setValue(0)
        window.second_time_lag.setValue(0)
        window.first_data_selection_box.setCurrentIndex(0)
        window.second_data_selection_box.setCurrentIndex(0)


    # FOUR CHART SETTINGS
    def four_finish_settings(self, window: Any, widget: QWidget):
        first_data = window.first_data_selection_box.currentText()
        second_data = window.second_data_selection_box.currentText()
        third_data = window.third_data_selection_box.currentText()
        fourth_data = window.fourth_data_selection_box.currentText()

        first_color = window.first_color_btn.styleSheet().split(":")[1][1:]
        second_color = window.second_color_btn.styleSheet().split(":")[1][1:]
        third_color = window.third_color_btn.styleSheet().split(":")[1][1:]
        fourth_color = window.fourth_color_btn.styleSheet().split(":")[1][1:]

        # 调用内部方法打开json文件
        existing_data: Dict[str, Any] = self.get_settings_from_json()

        existing_data["four_chart_settings"]["first_data"]["data_name"] = first_data
        existing_data["four_chart_settings"]["second_data"]["data_name"] = second_data
        existing_data["four_chart_settings"]["third_data"]["data_name"] = third_data
        existing_data["four_chart_settings"]["fourth_data"]["data_name"] = fourth_data

        existing_data["four_chart_settings"]["first_data"]["color"] = first_color
        existing_data["four_chart_settings"]["second_data"]["color"] = second_color
        existing_data["four_chart_settings"]["third_data"]["color"] = third_color
        existing_data["four_chart_settings"]["fourth_data"]["color"] = fourth_color

        # 依次处理四个图表，四个内容是，图表号，控件名称，数据名称，颜色
        # 然后for循环遍历四个list，进行图表输出以及图表名称修改
        four_widgets = [
            ["first_data", "four_chart_one_plot", first_data, first_color],
            ["second_data", "four_chart_two_plot", second_data, second_color],
            ["third_data", "four_chart_three_plot", third_data, third_color],
            ["fourth_data", "four_chart_four_plot", fourth_data, fourth_color],
        ]
        for widget_list in four_widgets:
            index_name = widget_list[0]
            plot_widget_name = widget_list[1]
            data_name = widget_list[2]
            color_name = widget_list[3]

            # plot graphs
            plot_widget = getattr(self.main_window, plot_widget_name.replace("_plot", "")).findChild(pg.PlotWidget, plot_widget_name)
            if plot_widget is not None:
                self.main_window.chart_functions.plot_data(
                    data_name=data_name,
                    color=[color_name],
                    widget=plot_widget
                )
                plot_widget.enableAutoRange(axis='xy', enable=True)

            # change title of the chart 修改图表标签
            main_plot_widget_title = getattr(
                self.main_window, plot_widget_name.replace("_plot", "")
            ).findChild(
                QLabel, plot_widget_name.replace("_plot", "_plot_title")
            )
            if main_plot_widget_title is not None:
                main_plot_widget_title.setText(data_name.replace("_", " "))  # 修正：用各自的data_name

        # 写入json
        try:
            with open(self._get_json_settings_path(), 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error writing settings file: {e}")

        # 关闭窗口
        widget.close()

    def four_close_setting_window(self, window: Any, widget: QWidget):
        try:
            widget.close()
        except Exception:
            pass

    def four_reset_settings(self, window: Any):
        window.first_color_btn.setStyleSheet(f"background-color: #90b6e7")
        window.second_color_btn.setStyleSheet(f"background-color: #90b6e7")
        window.third_color_btn.setStyleSheet(f"background-color: #90b6e7")
        window.fourth_color_btn.setStyleSheet(f"background-color: #90b6e7")
        window.first_data_selection_box.setCurrentIndex(0)
        window.second_data_selection_box.setCurrentIndex(0)
        window.third_data_selection_box.setCurrentIndex(0)
        window.fourth_data_selection_box.setCurrentIndex(0)


    # TABLE SETTINGS
    def table_finish_settings(self, window: Any, widget: QWidget):
        table_data_name = window.first_data_selection_box.currentText()
        existing_data = self.get_settings_from_json()
        existing_data["table_settings"]["table_name"] = table_data_name
        current_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_path, "..", "csv", "A_TABLE_DATA", f"{table_data_name}", f"{table_data_name}.csv")

        # 读取csv文件
        table_data : pd.DataFrame = pd.read_csv(file_path)
        if table_data.empty:
            logging.error("Table data is empty.")
            return

        # 调用table_functions然后使用里面的函数写入table
        if window.stretch_table_check.isChecked():
            self.main_window.table_functions.show_table(table_data, stretch = True)
        else:
            self.main_window.table_functions.show_table(table_data, stretch = False)

        # 修改widget label名称
        self.main_window.table_title_label.setText(f"Current Table Name : {table_data_name}")


        try:
            with open(self._get_json_settings_path(), 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Failed to save settings, error: {e}")
        try:
            widget.close()
        except Exception:
            pass

    def table_close_setting_window(self, widget: QWidget):
        try:
            widget.close()
        except Exception:
            pass

    #获取 SQLite 列名称
    def _get_sqlite_col_name(self) -> list[str]:
        """获取 sqlite 数据库 Time_Series 表的列名 (除去第一列 date)。
        若数据库或表不存在，返回空列表并记录日志。"""
        try:
            current_file_path = os.path.dirname(os.path.abspath(__file__))
            sqlite_file_path = os.path.join(current_file_path, "..", "data.db")
            sqlite_file_path = os.path.abspath(sqlite_file_path)
            if not os.path.exists(sqlite_file_path):
                logging.error("Database file not found. Please download data first.")
                return []
            conn = sqlite3.connect(sqlite_file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Time_Series'")
            table_exists = cursor.fetchone()
            if not table_exists:
                conn.close()
                logging.error("Time_Series table not found in database. Please download data to create it.")
                return []
            cursor.execute("SELECT * FROM Time_Series LIMIT 0")
            column_names = [d[0] for d in cursor.description][1:]
            conn.close()
            return column_names
        except Exception as e:
            logging.error(f"Failed to get sqlite column names: {e}")
            try:
                conn.close()  # type: ignore
            except Exception:
                pass
            return []


    def _append_console(self, text: str):
        try:
            self.main_window.console_area.append(text)
        except Exception:
            pass
        try:
            logging.getLogger(__name__).info(text)
        except Exception:
            pass

    def _load_request_json(self) -> Optional[Dict[str, Any]]:
        try:
            req_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "request_id.json")
            with open(os.path.abspath(req_path), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load request_id.json: {e}")
            self._append_console(f"Failed to load request_id.json: {e}")
            return None

    def start_download(self):

        # 先检查是否点击了term and condition btn
        if not self.main_window.read_and_agree_check.isChecked():
            self._append_console("PLEASE READ AND AGREE TO THE TERMS AND CONDITIONS !!!")
            # 读取json path并修改内容
            existing_data: Dict[str, Any] = self.get_settings_from_json()
            existing_data["agree_to_terms"] = False
            try:
                with open(self._get_json_settings_path(), 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logging.error(f"Error writing settings file: {e}")
            return
        else:
            existing_data: Dict[str, Any] = self.get_settings_from_json()
            existing_data["agree_to_terms"] = True
            try:
                with open(self._get_json_settings_path(), 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logging.error(f"Error writing settings file: {e}")

        if self._dl_thread is not None or self._parallel_exec is not None:
            self._append_console("Download already running.")
            return
        json_data = self._load_request_json()
        if not isinstance(json_data, dict):
            return

        start_year = int(self.main_window.int_year_spinbox.value())
        sources: list[str]
        download_all_bool = False

        # all sources name 是所有已经存在的数据源
        all_sources_name = ["bea", "yf", "fred", "bls", "te", "ism", "fw", "dfm", "nyf", "cin", "em", "fs"]

        # 如果都下载，就直接sources = all sources name
        if bool(self.main_window.download_for_all_check.isChecked()):
            sources : list = all_sources_name
            download_all_bool = True
        # 否则，遍历list，然后再sources这个list当中添加选中的源
        else:
            sources = []
            for name in all_sources_name:
                w = getattr(self.main_window, name, None)
                try:
                    if w is not None and bool(w.isChecked()):
                        sources.append(name)
                except Exception:
                    pass
            if not sources:
                self._append_console("No source selected.")
                return

        parallel = False
        max_threads = 1
        try:
            parallel = bool(self.main_window.parallel_download_check.isChecked())
            max_threads = int(self.main_window.max_threads_spin.value())
        except Exception:
            pass

       
        if parallel:
            self._append_console(f"Start parallel download ({len(sources)} sources, threads={max_threads}) from year {start_year}...")
            # 使用标准的 Qt 线程模式处理并行下载
            self._worker = _DownloadWorker(
                json_data=json_data,
                start_year=start_year,
                download_all=download_all_bool,
                selected_sources=sources,
                main_window=self.main_window
            )
            self._dl_thread = QThread()
            self._worker.moveToThread(self._dl_thread)
            self._dl_thread.started.connect(self._worker.run)
            self._worker.progress.connect(self._append_console)
            self._worker.failed.connect(self._on_worker_failed)
            self._worker.finished.connect(self._schedule_cleanup)
            self._dl_thread.start()
        else:
            self._append_console(f"Start download from year {start_year}...")
            self._worker = _DownloadWorker(
                json_data=json_data,
                start_year=start_year,
                download_all=True if sources and len(sources) == 5 else False,
                selected_sources=sources,
                main_window = self.main_window
            )
            self._dl_thread = QThread()
            self._worker.moveToThread(self._dl_thread)
            self._dl_thread.started.connect(self._worker.run)
            self._worker.progress.connect(self._append_console)
            self._worker.failed.connect(self._on_worker_failed)
            self._worker.finished.connect(self._schedule_cleanup)
            self._dl_thread.start()
        self.main_window.download_btn.setEnabled(False)
        self.main_window.cancel_btn.setEnabled(True)
        
    def _schedule_cleanup(self) -> None:
        if self._cleanup_pending:
            return
        self._cleanup_pending = True
        try:
            QTimer.singleShot(0, self._cleanup_thread)
        except Exception as e:
            logging.error(f"Failed to schedule download cleanup: {e}")
            self._cleanup_thread()

    def _cleanup_thread(self):
        self._cleanup_pending = False
        self._parallel_exec = None
        thread = self._dl_thread
        worker = self._worker
        was_cancelled = bool(getattr(worker, "_is_cancelled", False)) if worker else False

        if worker is not None:
            try:
                worker.finished.disconnect(self._schedule_cleanup)
            except Exception:
                pass
            try:
                worker.deleteLater()
            except Exception:
                pass
        if thread is not None:
            cleanup_done = False

            def finalize_thread() -> None:
                nonlocal cleanup_done
                if cleanup_done:
                    return
                if thread.isRunning():
                    QTimer.singleShot(50, finalize_thread)
                    return
                cleanup_done = True
                try:
                    thread.finished.disconnect(finalize_thread)  # type: ignore[arg-type]
                except Exception:
                    pass
                try:
                    thread.deleteLater()
                except Exception:
                    pass

            if thread.isRunning():
                try:
                    thread.requestInterruption()
                except Exception:
                    pass
                thread.quit()
                try:
                    thread.finished.connect(finalize_thread)
                except Exception:
                    pass

                def force_terminate() -> None:
                    if cleanup_done:
                        return
                    if thread.isRunning():
                        logging.warning("Download thread did not exit in time; forcing termination.")
                        try:
                            thread.terminate()
                        except Exception as err:
                            logging.error(f"Failed to terminate download thread: {err}")
                    finalize_thread()

                QTimer.singleShot(5000, force_terminate)
            else:
                finalize_thread()
            self._dl_thread = None

        self._worker = None

        date_today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.main_window.download_btn.setEnabled(True)
        self.main_window.cancel_btn.setEnabled(False)
        if was_cancelled:
            self._append_console("Download cancelled.")
        else:
            self._append_console("ALL TASKS COMPLETE !!! (∠・ω< )⌒★")

        existing_data: Dict[str, Any] = self.get_settings_from_json()
        existing_data["recent_update_time"] = date_today

        self.main_window.table_update_label.setText(f"Recent Update Time : {date_today}")
        self.main_window.update_label_2.setText(f"Recent Update Time : {date_today}")
        self.main_window.four_update_label.setText(f"Recent Update Time : {date_today}")
        try:
            with open(self._get_json_settings_path(), 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error writing settings file: {e}")

    def cancel_download(self):
        did = False
        if self._worker is not None:
            self._worker.cancel()
            did = True
        if self._parallel_exec is not None:
            self._parallel_exec.cancel()
            did = True
        if did:
            self._append_console("Cancelling...")
        else:
            self._append_console("No running task to cancel.")

    def _on_worker_failed(self, msg: str):
        self._append_console(f"Error: {msg}")

























