'''
这里包括所有ui的控件槽函数
动画等函数在gui_animation文件中
'''

import os
import sys
import logging
import json
from typing import Optional, Dict, Any, Protocol

from gui import *
from concurrent.futures import ThreadPoolExecutor, Future
import subprocess

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
    # fw : Any
    # dfm : Any
    # em : Any
    # fs : Any
    # cin : Any
    # ism : Any
    # nyf : Any
    # parallel controls
    parallel_download_check: Any
    max_threads_spin: Any
    download_btn: Any
    cancel_btn: Any
    read_and_agree_check : Any


class _DownloadWorker(QObject):
    '''用于执行数据下载任务的工作线程对象'''
    progress = Signal(str)
    finished = Signal()
    failed = Signal(str)

    def __init__(self, json_data: Dict[str, Any], start_year: int, download_all: bool, selected_sources: Optional[list[str]] | None = None, main_window = None):
        super().__init__()
        self._json_data = json_data
        self._start_year = start_year
        self._download_all = download_all
        self._is_cancelled = False
        self._selected_sources = selected_sources or []
        self.main_window = main_window

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            # 延迟导入后端工厂，避免缺少第三方依赖导致 UI 启动失败
            try:
                from download import DownloaderFactory  # type: ignore
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
                # "fw",
                # "dfm",
                # "em",
                # "fs",
                # "cin",
                # "ism",
                # "nyf"
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
                self.progress.emit(f"Downloading {src} data to database...")
                try:
                    # 优先判断 download_csv_check 是否被选中
                    if self.main_window and hasattr(self.main_window, "download_csv_check") and self.main_window.download_csv_check.isChecked():
                        self.progress.emit(f"Exporting {src} data to CSV...")
                        downloader.to_db(return_csv=True)
                    else:
                        downloader.to_db(return_csv=False)
                    self.progress.emit(f"{src} done.")
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
        print("save")
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

    def clear_logs(self):
        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path, "..", "doc", "error.log")
        with open(path, 'w'):
            pass
        self._append_console("Log file cleared successfully")

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
        if note_name == "note_instructions_btn":
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

        if note_name == "note_instructions_btn" or note_name == "User_instructions":
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

        if note_name == "note_instructions_btn" or note_name == "User_instructions":
            self.main_window.note_status_bar.setText("Name Conflict, change a name")
            self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
            return

        found = False
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QPushButton) and widget.text() == note_name:
                    widget.setText("Enter and press any to finish")  # 将按钮名称修改为提示词
                    widget.setStyleSheet(
                        '''
                        color : #90b6e7;
                        font-family : "Comfortaa";
                        font-weight : Bold;
                        '''
                    )
                    
                    # 创建LineEdit，输入新名称
                    line_edit = QLineEdit()
                    line_edit.setStyleSheet(
                        '''
                        color : white;
                        font-weight : Bold;
                        font-family : "Comfortaa";
                        font-size : 8px;
                        min-height : 15px;
                        max-height : 15px;
                        '''
                    )
                    line_edit.setPlaceholderText("Enter new name here")
                    line_edit.setObjectName(f"rename_edit_{note_name}")
                    layout.insertWidget(i+1, line_edit)   # 放在按钮下面
                    

                    def finish_rename(le=line_edit, btn=widget, idx=i):
                        # 若是点击别的地方自动完成重命名
                        new_name = le.text().strip()
                        if new_name:
                            # 检查新名称是否合法 check validity
                            illegal_chars = '\\/:*?"<>| '
                            is_valid = True
                            for char in illegal_chars:
                                if char in new_name:
                                    is_valid = False
                                    break
                            
                            if is_valid and new_name != "note_instructions_btn":
                                # 检查是否有重名
                                duplicate = False
                                for j in range(layout.count()):
                                    item_check = layout.itemAt(j)
                                    if item_check and item_check.widget():
                                        check_widget = item_check.widget()
                                        if isinstance(check_widget, QPushButton) and check_widget.text() == new_name:
                                            duplicate = True
                                            break
                                
                                if not duplicate:
                                    btn.setText(new_name)
                                    btn.setStyleSheet("color : white")

                                    # rename text file
                                    current_dir = os.path.dirname(os.path.abspath(__file__))
                                    parent_dir = os.path.dirname(current_dir)
                                    note_dir = os.path.join(parent_dir, "note")  # folder path
                                    origin_txt_file_path = os.path.join(note_dir, f"{note_name}.txt")
                                    changed_txt_file_path = os.path.join(note_dir, f"{new_name}.txt")
                                    if os.path.exists(origin_txt_file_path):
                                        os.rename(origin_txt_file_path, changed_txt_file_path)

                                    self.main_window.note_status_bar.setText("Rename successful")
                                    self.main_window.note_status_bar.setStyleSheet("color: #90b6e7")
                                    # 只有在名称合法时才移除LineEdit
                                    layout.removeWidget(le)
                                    le.deleteLater()
                                else:
                                    self.main_window.note_status_bar.setText("Name Conflict, change a name")
                                    self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
                                    # 保持LineEdit不删除，让用户重新输入
                                    le.setFocus()
                            else:
                                self.main_window.note_status_bar.setText("\\ / : * ? \" < > |, space, nums are invalid")
                                self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
                                # 保持LineEdit不删除，让用户重新输入
                                le.setFocus()
                        else:
                            self.main_window.note_status_bar.setText("Please enter a valid note name")
                            self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")
                            # 保持LineEdit不删除，让用户重新输入
                            le.setFocus()
                    
                    # 连接LineEdit的编辑完成信号
                    line_edit.editingFinished.connect(lambda le=line_edit, btn=widget, idx=i: finish_rename(le, btn, idx))
                    
                    # 设置焦点到LineEdit
                    line_edit.setFocus()
                    
                    found = True

        if not found:
            self.main_window.note_status_bar.setText("Note does not exist")
            self.main_window.note_status_bar.setStyleSheet("color: #EE5C88")

    def note_btn_open_file_slot(self, file_name):
        # 传入打开的文件名称，所有新建的按钮均调用这个槽函数
        self.main_window.plainTextEdit.setReadOnly(False)  # 先设置允许编写
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        selected_note_dir = os.path.join(parent_dir, "note", f"{file_name}.txt")
        
        # 读取文件内容并显示在plainTextEdit控件中
        try:
            with open(selected_note_dir, 'r', encoding='utf-8') as file:
                content = file.read()
                self.main_window.plainTextEdit.setPlainText(content)
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
        self.main_window.plainTextEdit.setReadOnly(True)


    # ============ Download wiring ============
    def _append_console(self, text: str):
        try:
            self.main_window.console_area.append(text)
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
        if not self.main_window.read_and_agree_check.isChecked():
            self._append_console("PLEASE READ AND AGREE TO THE TERMS AND CONDITIONS !!!")
            return
        if self._dl_thread is not None or self._parallel_exec is not None:
            self._append_console("Download already running.")
            return
        json_data = self._load_request_json()
        if not isinstance(json_data, dict):
            return

        start_year = int(self.main_window.int_year_spinbox.value())
        # gather sources
        sources: list[str]
        if bool(self.main_window.download_for_all_check.isChecked()):
            sources = ["bea", "yf", "fred", "bls", "te"]
        else:
            sources = []
            for name in ("bea", "yf", "fred", "bls", "te"):
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
            # parallel executor
            self._append_console(f"Start parallel download ({len(sources)} sources, threads={max_threads}) from year {start_year}...")
            execu = _ParallelExecutor(json_data=json_data, start_year=start_year, sources=sources, max_threads=max_threads, main_window=self.main_window)
            self._parallel_exec = execu
            execu.progress.connect(self._append_console)
            execu.failed.connect(self._on_worker_failed)
            execu.finished.connect(self._cleanup_thread)
            execu.start()
        else:
            # fallback to existing single-thread worker
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
            self._worker.finished.connect(self._cleanup_thread)
            self._dl_thread.start()

        # 设置 UI 状态
        self.main_window.download_btn.setEnabled(False)
        self.main_window.cancel_btn.setEnabled(True)

    def _cleanup_thread(self):
        try:
            if self._dl_thread:
                self._dl_thread.quit()
                self._dl_thread.wait()
            # clear parallel exec
            self._parallel_exec = None
        finally:
            self._dl_thread = None
            self._worker = None
            self.main_window.download_btn.setEnabled(True)
            self.main_window.cancel_btn.setEnabled(False)
            self._append_console("ALL TASKS COMPLETE !!! (∠・ω< )⌒★")

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


class _ParallelExecutor(QObject):
    '''并行执行多个数据下载任务'''
    progress = Signal(str)
    finished = Signal()
    failed = Signal(str)

    # class-level annotations for type checkers
    _json_data: Dict[str, Any]
    _start_year: int
    _sources: list[str]
    _max_threads: int
    _canceled: bool
    _executor: Optional[ThreadPoolExecutor]
    _futures: list[Future[Any]]
    _timer: Optional[QTimer]
    _completed: int
    _procs: Dict[str, Any]

    def __init__(self, json_data: Dict[str, Any], start_year: int, sources: list[str], max_threads: int = 4, main_window=None):
        super().__init__()
        self._json_data = json_data
        self._start_year = start_year
        self._sources = sources
        self._max_threads = max(1, int(max_threads))
        self._canceled = False
        self._executor = None
        self._futures = []
        self._timer = None
        self._procs = {}
        self._completed = 0
        self.main_window = main_window  # 新增: 保存 main_window 引用
        try:
            QThreadPool.globalInstance().setMaxThreadCount(self._max_threads)
        except Exception:
            pass

    def cancel(self):
        self._canceled = True
        # 尝试取消未开始的任务并快速关闭线程池
        try:
            # 停止轮询，避免多次发射 finished
            if self._timer:
                try:
                    self._timer.stop()
                    self._timer.deleteLater()
                except Exception:
                    pass
                finally:
                    self._timer = None
            if self._executor is not None:
                for f in list(self._futures):
                    try:
                        f.cancel()
                    except Exception:
                        pass
                # 取消未开始的任务，不等待正在运行的任务
                self._executor.shutdown(wait=False, cancel_futures=True)
                # 强制终止已启动的子进程
                for src, p in list(self._procs.items()):
                    try:
                        if p.poll() is None:
                            p.kill()
                            self.progress.emit(f"Killed process for {src}")
                    except Exception:
                        pass
                self.progress.emit("Cancel requested: pending tasks will be skipped; running tasks will finish soon.")
        except Exception:
            pass
        # 立即通知上层做清理
        try:
            self.finished.emit()
        except Exception:
            pass

    def start(self):
        if not self._sources:
            self.finished.emit()
            return
        self.progress.emit(f"Queue {len(self._sources)} tasks...")
        self._executor = ThreadPoolExecutor(max_workers=self._max_threads, thread_name_prefix="md_dl")
        for src in self._sources:
            if self._canceled:
                break
            f = self._executor.submit(self._run_one, src)
            self._futures.append(f)
        # 如果在队列前就被取消且未提交任何任务
        if not self._futures:
            self.finished.emit()
        # 使用定时器轮询完成状态
        if self._futures:
            self._timer = QTimer(self)
            self._timer.setInterval(100)
            self._timer.timeout.connect(self._poll_futures)
            self._timer.start()

    def _poll_futures(self):
        try:
            total = len(self._futures)
            done = sum(1 for f in self._futures if f.done())
            if done >= total:
                if self._timer:
                    self._timer.stop()
                    self._timer.deleteLater()
                    self._timer = None
                try:
                    if self._executor:
                        # 已经在 cancel() 中尝试过 shutdown；此处确保资源回收
                        self._executor.shutdown(wait=False, cancel_futures=False)
                except Exception:
                    pass
                self.finished.emit()
        except Exception as e:
            self.failed.emit(str(e))

    def _run_one(self, src: str):
        try:
            if self._canceled:
                return
            # 子进程执行，以支持强制取消
            req_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "request_id.json")
            req_path = os.path.abspath(req_path)
            worker = os.path.abspath(os.path.join(os.path.dirname(req_path), "worker_run_source.py"))
            py = sys.executable
            if not os.path.exists(worker):
                self.progress.emit("worker_run_source.py not found")
                return
            args = [py, worker, req_path, str(self._start_year), src]
            # 新增: 判断是否需要导出 CSV
            export_csv = False
            if self.main_window and hasattr(self.main_window, "download_csv_check"):
                export_csv = self.main_window.download_csv_check.isChecked()
            if export_csv:
                args.append("--csv")
            # 启动子进程
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self._procs[src] = p  # Save the process reference for management
            # 读取输出
            if p.stdout is not None:
                for line in p.stdout:
                    if self._canceled:
                        break
                    self.progress.emit(f"{src}> {line.strip()}")
            code = p.wait()
            if code == 0:
                self.progress.emit(f"{src} done.")
            else:
                self.progress.emit(f"{src} failed with code {code}.")
        except Exception as e:
            self.failed.emit(str(e))



