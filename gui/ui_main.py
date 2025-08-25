# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QStackedWidget,
    QTabWidget, QTableView, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(960, 600)
        MainWindow.setMinimumSize(QSize(960, 600))
        MainWindow.setStyleSheet(u"* {\n"
"	background-color: #33363a;\n"
"}\n"
"\n"
"QToolTip {\n"
"    /* \u8bbe\u7f6e\u63d0\u793a\u6846color */\n"
"    background-color: #ffffff;\n"
"	font-family : \"Comfortaa\";\n"
"    background-image: none;\n"
"    color: #90b6e7;\n"
"    border: 0;\n"
"    border-top-left-radius: 5px;\n"
"    border-bottom-right-radius: 5px;\n"
"    padding: 2px;\n"
"}")
        self.style_sheet = QWidget(MainWindow)
        self.style_sheet.setObjectName(u"style_sheet")
        self.style_sheet.setStyleSheet(u"")
        self.horizontalLayout_2 = QHBoxLayout(self.style_sheet)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.self_sized_main_widget = QWidget(self.style_sheet)
        self.self_sized_main_widget.setObjectName(u"self_sized_main_widget")
        self.self_sized_main_widget.setStyleSheet(u"")
        self.horizontalLayout = QHBoxLayout(self.self_sized_main_widget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.left_box_frame = QFrame(self.self_sized_main_widget)
        self.left_box_frame.setObjectName(u"left_box_frame")
        self.left_box_frame.setMaximumSize(QSize(70, 16777215))
        self.left_box_frame.setStyleSheet(u"* {\n"
"	background-color : #252526;\n"
"	padding:0;\n"
"	margin:0;\n"
"	border:0;\n"
"}\n"
"\n"
"/*\u6bcf\u4e2a\u6309\u94ae\u7684\u6837\u5f0f\u5728\u8fd9\u91cc*/\n"
"\n"
"QPushButton {\n"
"    background-position: center;\n"
"    background-repeat: no-repeat;\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"	background-color : #33363a;\n"
"	border-radius : 0;\n"
"	margin :0;\n"
"	border :0;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"	background-color : #90b6e7;\n"
"	border-radius : 0;\n"
"	border-left:2px solid white;\n"
"	margin :0;\n"
"	border :0;\n"
"}\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"")
        self.left_box_frame.setLineWidth(0)
        self.left_up_four_frame = QVBoxLayout(self.left_box_frame)
        self.left_up_four_frame.setSpacing(0)
        self.left_up_four_frame.setObjectName(u"left_up_four_frame")
        self.left_up_four_frame.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.left_up_four_frame.addItem(self.verticalSpacer)

        self.one_page_btn = QPushButton(self.left_box_frame)
        self.one_page_btn.setObjectName(u"one_page_btn")
        self.one_page_btn.setMinimumSize(QSize(0, 40))
        self.one_page_btn.setMaximumSize(QSize(70, 40))
        self.one_page_btn.setStyleSheet(u"icon: url(:/png/png/one.png);\n"
"icon-size: 20px 20px;")

        self.left_up_four_frame.addWidget(self.one_page_btn)

        self.four_page_btn = QPushButton(self.left_box_frame)
        self.four_page_btn.setObjectName(u"four_page_btn")
        self.four_page_btn.setMinimumSize(QSize(0, 40))
        self.four_page_btn.setMaximumSize(QSize(70, 16777215))
        self.four_page_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self.four_page_btn.setStyleSheet(u"icon: url(:/png/png/four.png);\n"
"icon-size: 20px 20px;")

        self.left_up_four_frame.addWidget(self.four_page_btn)

        self.table_btn = QPushButton(self.left_box_frame)
        self.table_btn.setObjectName(u"table_btn")
        self.table_btn.setMinimumSize(QSize(0, 40))
        self.table_btn.setMaximumSize(QSize(60, 40))
        self.table_btn.setStyleSheet(u"icon: url(:/png/png/table.png);\n"
"icon-size: 20px 20px;")

        self.left_up_four_frame.addWidget(self.table_btn)

        self.note_btn = QPushButton(self.left_box_frame)
        self.note_btn.setObjectName(u"note_btn")
        self.note_btn.setMinimumSize(QSize(60, 40))
        self.note_btn.setMaximumSize(QSize(60, 40))
        self.note_btn.setStyleSheet(u"icon: url(:/png/png/note_btn.png);\n"
"icon-size: 20px 20px;")

        self.left_up_four_frame.addWidget(self.note_btn)

        self.vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.left_up_four_frame.addItem(self.vertical_spacer)

        self.settings_btn = QPushButton(self.left_box_frame)
        self.settings_btn.setObjectName(u"settings_btn")
        self.settings_btn.setMinimumSize(QSize(0, 40))
        self.settings_btn.setMaximumSize(QSize(70, 40))
        self.settings_btn.setStyleSheet(u"icon: url(:/png/png/settings.png);\n"
"icon-size: 20px 20px;")

        self.left_up_four_frame.addWidget(self.settings_btn)

        self.verticalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.left_up_four_frame.addItem(self.verticalSpacer_2)

        self.four_page_btn.raise_()
        self.table_btn.raise_()
        self.note_btn.raise_()
        self.settings_btn.raise_()
        self.one_page_btn.raise_()

        self.verticalLayout.addWidget(self.left_box_frame)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.frame = QFrame(self.self_sized_main_widget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.frame)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setStyleSheet(u"")
        self.page_one_container = QWidget()
        self.page_one_container.setObjectName(u"page_one_container")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.page_one_container.sizePolicy().hasHeightForWidth())
        self.page_one_container.setSizePolicy(sizePolicy)
        self.page_one_container.setStyleSheet(u"background-color: #2a2f39;")
        self.verticalLayout_4 = QVBoxLayout(self.page_one_container)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.tab_window = QTabWidget(self.page_one_container)
        self.tab_window.setObjectName(u"tab_window")
        self.tab_window.setEnabled(True)
        font = QFont()
        font.setFamilies([u"Comfortaa"])
        font.setBold(True)
        self.tab_window.setFont(font)
        self.tab_window.setAcceptDrops(False)
        self.tab_window.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.tab_window.setAutoFillBackground(False)
        self.tab_window.setStyleSheet(u"* {\n"
"	background-color : #33363a;\n"
"	font-family : \"Comfortaa\";\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"    background-color: #2a2f39;\n"
"	color: #90b6e7;\n"
"    padding: 3px 2px;\n"
"	padding-left : 12px;\n"
"	padding-right:12px;\n"
"	border-radius:9px;\n"
"}\n"
"\n"
"QTabBar::tab:hover {\n"
"    background-color: #90b6e7;\n"
"    color: #252526;\n"
"}\n"
"\n"
"QTabWidget::pane{\n"
"	\n"
"}\n"
"\n"
"\n"
"\n"
"QTabBar::close-button {\n"
"    /* \u8bbe\u7f6e\u80cc\u666f\u56fe\u7247\uff0c\u4e0d\u91cd\u590d */\n"
"	image:url(:svg/svg/close_2.svg);\n"
"    background-repeat: no-repeat;\n"
"    background-position: center;\n"
"    border-radius: 10px;\n"
"	size:50%\n"
"}\n"
"")
        self.tab_window.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_window.setTabShape(QTabWidget.TabShape.Rounded)
        self.tab_window.setElideMode(Qt.TextElideMode.ElideNone)
        self.tab_window.setUsesScrollButtons(True)
        self.tab_window.setDocumentMode(True)
        self.tab_window.setTabsClosable(True)
        self.tab_window.setMovable(True)
        self.tab_window.setTabBarAutoHide(False)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_5 = QVBoxLayout(self.tab)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalSpacer_3 = QSpacerItem(0, 7, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_5.addItem(self.verticalSpacer_3)

        self.btn_and_text_container = QWidget(self.tab)
        self.btn_and_text_container.setObjectName(u"btn_and_text_container")
        self.btn_and_text_container.setMaximumSize(QSize(16777215, 40))
        self.btn_and_text_container.setStyleSheet(u"")
        self.horizontalLayout_3 = QHBoxLayout(self.btn_and_text_container)
        self.horizontalLayout_3.setSpacing(3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.text_container = QWidget(self.btn_and_text_container)
        self.text_container.setObjectName(u"text_container")
        self.text_container.setMaximumSize(QSize(16777215, 40))
        self.verticalLayout_6 = QVBoxLayout(self.text_container)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.title_label = QLabel(self.text_container)
        self.title_label.setObjectName(u"title_label")
        self.title_label.setMaximumSize(QSize(16777215, 18))
        font1 = QFont()
        font1.setFamilies([u"Comfortaa"])
        font1.setPointSize(14)
        font1.setBold(True)
        self.title_label.setFont(font1)
        self.title_label.setStyleSheet(u"color: #ffffff; \n"
"margin-left : 7px; ")

        self.verticalLayout_6.addWidget(self.title_label)

        self.update_label = QLabel(self.text_container)
        self.update_label.setObjectName(u"update_label")
        self.update_label.setMaximumSize(QSize(16777215, 12))
        font2 = QFont()
        font2.setFamilies([u"Comfortaa"])
        font2.setPointSize(8)
        font2.setBold(True)
        self.update_label.setFont(font2)
        self.update_label.setStyleSheet(u"margin-left : 10px; \n"
"color : #90b6e7;")

        self.verticalLayout_6.addWidget(self.update_label)


        self.horizontalLayout_3.addWidget(self.text_container)

        self.btn_frame = QFrame(self.btn_and_text_container)
        self.btn_frame.setObjectName(u"btn_frame")
        self.btn_frame.setMaximumSize(QSize(100, 16777215))
        self.btn_frame.setStyleSheet(u"QPushButton {\n"
"	background-color : #252526;\n"
"	border-radius : 9px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color : #33363a;\n"
"	border-radius : 9px;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color : #90b6e7;\n"
"	border-radius : 9px;\n"
"}")
        self.btn_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.btn_frame.setFrameShadow(QFrame.Shadow.Plain)
        self.btn_frame.setLineWidth(0)
        self.horizontalLayout_4 = QHBoxLayout(self.btn_frame)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.one_add_page = QPushButton(self.btn_frame)
        self.one_add_page.setObjectName(u"one_add_page")
        self.one_add_page.setMaximumSize(QSize(25, 25))
        self.one_add_page.setStyleSheet(u" * {	\n"
"	image: url(:svg/svg/add_page.svg);\n"
" 	padding : 4px;\n"
"}\n"
"")

        self.horizontalLayout_4.addWidget(self.one_add_page)

        self.one_set_preference = QPushButton(self.btn_frame)
        self.one_set_preference.setObjectName(u"one_set_preference")
        self.one_set_preference.setMaximumSize(QSize(25, 25))
        self.one_set_preference.setStyleSheet(u" image: url(:svg/svg/set_preference.svg);\n"
" padding : 4px;")

        self.horizontalLayout_4.addWidget(self.one_set_preference)


        self.horizontalLayout_3.addWidget(self.btn_frame)

        self.horizontalSpacer = QSpacerItem(10, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.verticalLayout_5.addWidget(self.btn_and_text_container)

        self.verticalSpacer_4 = QSpacerItem(20, 7, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_5.addItem(self.verticalSpacer_4)

        self.graph_widget = QWidget(self.tab)
        self.graph_widget.setObjectName(u"graph_widget")
        self.graph_widget.setStyleSheet(u"background-color : #262a2f;\n"
"border-radius:30px;\n"
"margin-left : 10px;\n"
"margin-right : 10px;")

        self.verticalLayout_5.addWidget(self.graph_widget)

        self.tab_window.addTab(self.tab, "")

        self.verticalLayout_4.addWidget(self.tab_window)

        self.stackedWidget.addWidget(self.page_one_container)
        self.page_table_container = QWidget()
        self.page_table_container.setObjectName(u"page_table_container")
        self.verticalLayout_8 = QVBoxLayout(self.page_table_container)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.text_and_btn = QWidget(self.page_table_container)
        self.text_and_btn.setObjectName(u"text_and_btn")
        self.text_and_btn.setMinimumSize(QSize(0, 82))
        self.text_and_btn.setMaximumSize(QSize(16777215, 16777215))
        self.text_and_btn.setStyleSheet(u"QPushButton {\n"
"	background-color : #252526;\n"
"	border-radius : 9px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color : #33363a;\n"
"	border-radius : 9px;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color : #90b6e7;\n"
"	border-radius : 9px;\n"
"}")
        self.horizontalLayout_6 = QHBoxLayout(self.text_and_btn)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.text_container_2 = QWidget(self.text_and_btn)
        self.text_container_2.setObjectName(u"text_container_2")
        self.text_container_2.setMinimumSize(QSize(0, 0))
        self.text_container_2.setMaximumSize(QSize(16777215, 40))
        self.verticalLayout_9 = QVBoxLayout(self.text_container_2)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.title_label_2 = QLabel(self.text_container_2)
        self.title_label_2.setObjectName(u"title_label_2")
        self.title_label_2.setMaximumSize(QSize(16777215, 18))
        self.title_label_2.setFont(font1)
        self.title_label_2.setStyleSheet(u"color: #ffffff; \n"
"margin-left : 7px; ")

        self.verticalLayout_9.addWidget(self.title_label_2)

        self.update_label_2 = QLabel(self.text_container_2)
        self.update_label_2.setObjectName(u"update_label_2")
        self.update_label_2.setMaximumSize(QSize(16777215, 12))
        self.update_label_2.setFont(font2)
        self.update_label_2.setStyleSheet(u"margin-left : 10px; \n"
"color : #90b6e7;")

        self.verticalLayout_9.addWidget(self.update_label_2)


        self.horizontalLayout_6.addWidget(self.text_container_2)

        self.page_table_set_preference = QPushButton(self.text_and_btn)
        self.page_table_set_preference.setObjectName(u"page_table_set_preference")
        self.page_table_set_preference.setMaximumSize(QSize(25, 25))
        self.page_table_set_preference.setStyleSheet(u" image: url(:svg/svg/set_preference.svg);\n"
" padding : 4px;")

        self.horizontalLayout_6.addWidget(self.page_table_set_preference)

        self.horizontalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_2)


        self.verticalLayout_8.addWidget(self.text_and_btn)

        self.table_container = QWidget(self.page_table_container)
        self.table_container.setObjectName(u"table_container")
        self.table_container.setMaximumSize(QSize(16777215, 16777215))
        self.table_container.setStyleSheet(u"background-color : #252526;\n"
"border-radius:30px;\n"
"margin-left : 10px;\n"
"margin-right : 10px;")
        self.verticalLayout_10 = QVBoxLayout(self.table_container)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.tableView = QTableView(self.table_container)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setStyleSheet(u"")

        self.verticalLayout_10.addWidget(self.tableView)


        self.verticalLayout_8.addWidget(self.table_container)

        self.stackedWidget.addWidget(self.page_table_container)
        self.page_four_container = QWidget()
        self.page_four_container.setObjectName(u"page_four_container")
        self.verticalLayout_3 = QVBoxLayout(self.page_four_container)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.four_text_widget = QWidget(self.page_four_container)
        self.four_text_widget.setObjectName(u"four_text_widget")
        self.four_text_widget.setMaximumSize(QSize(16777215, 80))
        self.four_text_widget.setStyleSheet(u"QPushButton {\n"
"	background-color : #252526;\n"
"	border-radius : 9px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color : #33363a;\n"
"	border-radius : 9px;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color : #90b6e7;\n"
"	border-radius : 9px;\n"
"}")
        self.horizontalLayout_5 = QHBoxLayout(self.four_text_widget)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 32, 0)
        self.four_text_container = QWidget(self.four_text_widget)
        self.four_text_container.setObjectName(u"four_text_container")
        self.four_text_container.setMaximumSize(QSize(16777215, 40))
        self.verticalLayout_7 = QVBoxLayout(self.four_text_container)
        self.verticalLayout_7.setSpacing(6)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(4, 0, 0, 0)
        self.four_title_label = QLabel(self.four_text_container)
        self.four_title_label.setObjectName(u"four_title_label")
        self.four_title_label.setMaximumSize(QSize(16777215, 18))
        self.four_title_label.setFont(font1)
        self.four_title_label.setStyleSheet(u"color: #ffffff; \n"
"margin-left : 7px; ")

        self.verticalLayout_7.addWidget(self.four_title_label)

        self.four_update_label = QLabel(self.four_text_container)
        self.four_update_label.setObjectName(u"four_update_label")
        self.four_update_label.setMaximumSize(QSize(16777215, 12))
        self.four_update_label.setFont(font2)
        self.four_update_label.setStyleSheet(u"margin-left : 10px; \n"
"color : #90b6e7;")

        self.verticalLayout_7.addWidget(self.four_update_label)


        self.horizontalLayout_5.addWidget(self.four_text_container)

        self.connect_charts = QCheckBox(self.four_text_widget)
        self.connect_charts.setObjectName(u"connect_charts")
        self.connect_charts.setMaximumSize(QSize(150, 16777215))
        self.connect_charts.setFont(font)
        self.connect_charts.setStyleSheet(u"color:white;")

        self.horizontalLayout_5.addWidget(self.connect_charts)

        self.four_settings_button = QPushButton(self.four_text_widget)
        self.four_settings_button.setObjectName(u"four_settings_button")
        self.four_settings_button.setMaximumSize(QSize(25, 25))
        self.four_settings_button.setStyleSheet(u" image: url(:svg/svg/set_preference.svg);\n"
" padding : 4px;")

        self.horizontalLayout_5.addWidget(self.four_settings_button)


        self.verticalLayout_3.addWidget(self.four_text_widget)

        self.chart_widget = QWidget(self.page_four_container)
        self.chart_widget.setObjectName(u"chart_widget")
        self.chart_widget.setMaximumSize(QSize(16777215, 16777215))
        self.chart_widget.setStyleSheet(u"")
        self.gridLayout = QGridLayout(self.chart_widget)
        self.gridLayout.setSpacing(8)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(15, 0, 15, 0)
        self.four_chart_one = QWidget(self.chart_widget)
        self.four_chart_one.setObjectName(u"four_chart_one")
        self.four_chart_one.setStyleSheet(u"QWidget {\n"
"	background-color : #262a2f ;\n"
"	border-radius:20px;\n"
"}")

        self.gridLayout.addWidget(self.four_chart_one, 0, 0, 1, 1)

        self.four_chart_two = QWidget(self.chart_widget)
        self.four_chart_two.setObjectName(u"four_chart_two")
        self.four_chart_two.setStyleSheet(u"QWidget {\n"
"	background-color : #262a2f ;\n"
"	border-radius:20px;\n"
"}")

        self.gridLayout.addWidget(self.four_chart_two, 0, 1, 1, 1)

        self.four_chart_three = QWidget(self.chart_widget)
        self.four_chart_three.setObjectName(u"four_chart_three")
        self.four_chart_three.setStyleSheet(u"QWidget {\n"
"	background-color : #262a2f ;\n"
"	border-radius:20px;\n"
"}")

        self.gridLayout.addWidget(self.four_chart_three, 1, 0, 1, 1)

        self.four_chart_four = QWidget(self.chart_widget)
        self.four_chart_four.setObjectName(u"four_chart_four")
        self.four_chart_four.setStyleSheet(u"QWidget {\n"
"	background-color : #262a2f ;\n"
"	border-radius:20px;\n"
"}")

        self.gridLayout.addWidget(self.four_chart_four, 1, 1, 1, 1)


        self.verticalLayout_3.addWidget(self.chart_widget)

        self.stackedWidget.addWidget(self.page_four_container)

        self.verticalLayout_2.addWidget(self.stackedWidget)

        self.author_name = QLabel(self.frame)
        self.author_name.setObjectName(u"author_name")
        self.author_name.setFont(font)
        self.author_name.setStyleSheet(u"color:#90b6e7;\n"
"font-family:\"Comfortaa\";\n"
"padding:3px;\n"
"border: 0;\n"
"font-size:10px;")
        self.author_name.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_2.addWidget(self.author_name)


        self.horizontalLayout.addWidget(self.frame)


        self.horizontalLayout_2.addWidget(self.self_sized_main_widget)

        MainWindow.setCentralWidget(self.style_sheet)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(1)
        self.tab_window.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Macro Data Dashboard", None))
#if QT_CONFIG(tooltip)
        self.one_page_btn.setToolTip(QCoreApplication.translate("MainWindow", u"One Chart Interface", None))
#endif // QT_CONFIG(tooltip)
        self.one_page_btn.setText("")
#if QT_CONFIG(tooltip)
        self.four_page_btn.setToolTip(QCoreApplication.translate("MainWindow", u"Four Charts Interface", None))
#endif // QT_CONFIG(tooltip)
        self.four_page_btn.setText("")
#if QT_CONFIG(tooltip)
        self.table_btn.setToolTip(QCoreApplication.translate("MainWindow", u"Non Time Series Tables", None))
#endif // QT_CONFIG(tooltip)
        self.table_btn.setText("")
#if QT_CONFIG(tooltip)
        self.note_btn.setToolTip(QCoreApplication.translate("MainWindow", u"Notes", None))
#endif // QT_CONFIG(tooltip)
        self.note_btn.setText("")
#if QT_CONFIG(tooltip)
        self.settings_btn.setToolTip(QCoreApplication.translate("MainWindow", u"Settings", None))
#endif // QT_CONFIG(tooltip)
        self.settings_btn.setText("")
#if QT_CONFIG(tooltip)
        self.tab_window.setToolTip(QCoreApplication.translate("MainWindow", u"Tab pages", None))
#endif // QT_CONFIG(tooltip)
        self.title_label.setText(QCoreApplication.translate("MainWindow", u"Data name will be here", None))
        self.update_label.setText(QCoreApplication.translate("MainWindow", u"Recent Update Time : 2025-08-01", None))
        self.one_add_page.setText("")
        self.one_set_preference.setText("")
        self.tab_window.setTabText(self.tab_window.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Tab Box 1", None))
        self.title_label_2.setText(QCoreApplication.translate("MainWindow", u"Table : Selected Table Name", None))
        self.update_label_2.setText(QCoreApplication.translate("MainWindow", u"Recent Update Time : 2025-08-01", None))
        self.page_table_set_preference.setText("")
        self.four_title_label.setText(QCoreApplication.translate("MainWindow", u"Four Charts Interface", None))
        self.four_update_label.setText(QCoreApplication.translate("MainWindow", u"Recent Update Time : 2025-08-01", None))
        self.connect_charts.setText(QCoreApplication.translate("MainWindow", u" Connect Charts", None))
        self.four_settings_button.setText("")
        self.author_name.setText(QCoreApplication.translate("MainWindow", u"Love from : Kitazaki Hinata", None))
    # retranslateUi

