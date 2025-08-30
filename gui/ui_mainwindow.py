'''
主窗口的设置与控件信号
启动窗口请前往main.py文件
'''


from gui import *
from .ui_function import UiFunctions  # 修改: 添加对UiFunctions的导入

class mainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # create instances
        self.ui_functions = UiFunctions(self)

        # left menu btn signal connection
        self.one_page_btn.clicked.connect(self.left_bar_button_slot)
        self.four_page_btn.clicked.connect(self.left_bar_button_slot)
        self.table_btn.clicked.connect(self.left_bar_button_slot)
        self.note_btn.clicked.connect(self.left_bar_button_slot)
        self.settings_btn.clicked.connect(self.left_bar_button_slot)

        # settings signals
        # 点击api确认按钮保存输入的API
        self.api_save_btn.clicked.connect(self.ui_functions.settings_api_save)

        # set window gui
        self.setWindowIcon(QIcon(":/png/png/ico.png"))

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