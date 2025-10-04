# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QCheckBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QPlainTextEdit,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QSpinBox, QStackedWidget, QTableView, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1267, 792)
        MainWindow.setMinimumSize(QSize(1267, 792))
        MainWindow.setMaximumSize(QSize(2304, 1440))
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
"}\n"
"\n"
"\n"
"/*================================== ====*/\n"
"/*\u5168\u5c40checkbox\u6837\u5f0f \u591a\u9009\u6846*/\n"
"QCheckBox {\n"
"            spacing: 8px;    /*\u591a\u9009\u6846\u4e0e\u5b57\u4f53\u7684\u7a7a\u683c*/\n"
"            font-size: 11px;\n"
"        }\n"
"        \n"
"QCheckBox::indicator {\n"
"            width: 12px;\n"
"            height: 12px;\n"
"            border: 1px solid #555555;\n"
"            border-radius: 5px;\n"
"            background: #202023;\n"
"        }\n"
"        \n"
"QCheckBox::indicator:hover {\n"
"            border: 1px solid #ffffff;\n"
"        }\n"
"\n"
"        \n"
"QCheckBox::indicator:checked {\n"
" "
                        "           border: 1px solid #90b6e7;\n"
"            image: url(:/png/png/true.png);\n"
"        }\n"
"QCheckBox::indicator:disabled {\n"
"            border: 1px solid #454555;\n"
"            background: #454555;\n"
"        }\n"
"        \n"
"        QCheckBox::indicator:checked:disabled {\n"
"            background: #454555;\n"
"            border: 2px solid #454555;\n"
"        }\n"
"\n"
"\n"
"\n"
"/*================================== ====*/\n"
"/* SpinBox\u57fa\u672c\u6837\u5f0f */\n"
"        QSpinBox {\n"
"            padding: 0px;\n"
"            border: 1px solid #404043;\n"
"            border-radius: 5px;\n"
"            font-size: 12px;\n"
"        }\n"
"\n"
"        QSpinBox:hover {\n"
"            border: 1px solid #606063;\n"
"        }\n"
"        \n"
"        QSpinBox:focus {\n"
"            border: 1px solid #404043;\n"
"        }\n"
"        \n"
"        \n"
"        \n"
"        QSpinBox::up-button {\n"
"            subcontrol-origin: border;\n"
"            subcontrol-position: top right"
                        ";\n"
"            width: 20px;\n"
"            border-top-right-radius: 5px;\n"
"            background: #404043;\n"
"        }\n"
"        \n"
"        QSpinBox::up-button:hover {\n"
"            background: #606063;\n"
"        }\n"
"        \n"
"        QSpinBox::up-button:pressed {\n"
"            background: #404043;\n"
"        }\n"
"      \n"
"        \n"
"        QSpinBox::down-button {\n"
"            subcontrol-origin: border;\n"
"            subcontrol-position: bottom right;\n"
"            width: 20px;\n"
"            border-bottom-right-radius: 5px;\n"
"            background: #404043;\n"
"        }\n"
"        \n"
"        QSpinBox::down-button:hover {\n"
"            background: #606063;\n"
"        }\n"
"        \n"
"        QSpinBox::down-button:pressed {\n"
"            background: #404043;\n"
"        }\n"
"\n"
"\n"
"/*================================== ====*/\n"
"/* scroll bar*/\n"
" QScrollBar:vertical {\n"
"	border: none;\n"
"    background: #303030;\n"
"    width: 8px;\n"
"    margin: 2"
                        "1px 0 21px 0;\n"
"	border-radius: 0px;\n"
" }\n"
" QScrollBar::handle:vertical {	\n"
"	background: #90b6e7;\n"
"    min-height: 25px;\n"
"	border-radius: 4px\n"
" }\n"
"\n"
"\n"
"/*\u8bbe\u7f6e\u4e0a\u4e0b\u6ed1\u6761\u6309\u94ae*/\n"
" QScrollBar::add-line:vertical {\n"
"     border: none;\n"
"    background: #252526;\n"
"     height: 20px;\n"
"	border-bottom-left-radius: 4px;\n"
"    border-bottom-right-radius: 4px;\n"
"     subcontrol-position: bottom;\n"
"     subcontrol-origin: margin;\n"
" }\n"
" QScrollBar::sub-line:vertical {\n"
"	border: none;\n"
"    background: #252526;\n"
"     height: 20px;\n"
"	border-top-left-radius: 4px;\n"
"    border-top-right-radius: 4px;\n"
"     subcontrol-position: top;\n"
"     subcontrol-origin: margin;\n"
" }\n"
"\n"
"\n"
"/*\u9632\u6b62\u906e\u4f4f\u6ed1\u6761\u80cc\u666f\u989c\u8272*/\n"
" QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
"     background: none;\n"
" }\n"
" QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"     back"
                        "ground: none;\n"
" }\n"
"        \n"
"        \n"
"\n"
"\n"
"        \n"
"")
        self.style_sheet = QWidget(MainWindow)
        self.style_sheet.setObjectName(u"style_sheet")
        self.style_sheet.setStyleSheet(u"QWidget#header_bar {\n"
"background : #2b2e32;\n"
"border-bottom : 1px solid #181823;\n"
"}")
        self.verticalLayout_33 = QVBoxLayout(self.style_sheet)
        self.verticalLayout_33.setSpacing(0)
        self.verticalLayout_33.setObjectName(u"verticalLayout_33")
        self.verticalLayout_33.setContentsMargins(0, 0, 0, 0)
        self.header_bar = QWidget(self.style_sheet)
        self.header_bar.setObjectName(u"header_bar")
        self.header_bar.setMinimumSize(QSize(0, 25))
        self.header_bar.setMaximumSize(QSize(16777215, 25))
        self.header_bar.setStyleSheet(u"* {\n"
"font-family : \"Comfortaa\";\n"
"font-weight : Bold;\n"
"color : #90b6e7;\n"
"}")
        self.horizontalLayout_2 = QHBoxLayout(self.header_bar)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.header_text_and_icon = QWidget(self.header_bar)
        self.header_text_and_icon.setObjectName(u"header_text_and_icon")
        self.header_text_and_icon.setStyleSheet(u"background : transparent;")
        self.horizontalLayout_15 = QHBoxLayout(self.header_text_and_icon)
        self.horizontalLayout_15.setSpacing(10)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalLayout_15.setContentsMargins(8, 4, 2, 2)
        self.icon = QWidget(self.header_text_and_icon)
        self.icon.setObjectName(u"icon")
        self.icon.setMinimumSize(QSize(18, 18))
        self.icon.setMaximumSize(QSize(18, 18))
        self.icon.setStyleSheet(u"background-image: url(:/png/png/ico_small.png);\n"
"border-radius :5px;\n"
"")

        self.horizontalLayout_15.addWidget(self.icon)

        self.title_text = QLabel(self.header_text_and_icon)
        self.title_text.setObjectName(u"title_text")
        font = QFont()
        font.setFamilies([u"Comfortaa"])
        font.setPointSize(8)
        font.setBold(True)
        self.title_text.setFont(font)
        self.title_text.setStyleSheet(u"")

        self.horizontalLayout_15.addWidget(self.title_text)


        self.horizontalLayout_2.addWidget(self.header_text_and_icon)

        self.header_right_btn_container = QWidget(self.header_bar)
        self.header_right_btn_container.setObjectName(u"header_right_btn_container")
        self.header_right_btn_container.setStyleSheet(u"* {\n"
"background : transparent;\n"
"}\n"
"\n"
"QPushButton {\n"
"	background : #202023;\n"
"	border-radius : 7px\n"
"}\n"
"\n"
"QPushButton::hover {\n"
"	background : #454545;\n"
"}\n"
"QPushButton::pressed {\n"
"	background : #131317;\n"
"}")
        self.horizontalLayout_20 = QHBoxLayout(self.header_right_btn_container)
        self.horizontalLayout_20.setSpacing(6)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.horizontalLayout_20.setContentsMargins(0, 2, 10, 0)
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer_4)

        self.minimize_btn = QPushButton(self.header_right_btn_container)
        self.minimize_btn.setObjectName(u"minimize_btn")
        self.minimize_btn.setMinimumSize(QSize(20, 18))
        self.minimize_btn.setMaximumSize(QSize(20, 18))
        self.minimize_btn.setStyleSheet(u"image: url(:/svg/svg/minimize.svg);")

        self.horizontalLayout_20.addWidget(self.minimize_btn)

        self.window_btn = QPushButton(self.header_right_btn_container)
        self.window_btn.setObjectName(u"window_btn")
        self.window_btn.setMinimumSize(QSize(20, 18))
        self.window_btn.setMaximumSize(QSize(20, 18))
        self.window_btn.setStyleSheet(u"image: url(:/svg/svg/big_window.svg);\n"
"padding : 4px;\n"
"image-position : center;")

        self.horizontalLayout_20.addWidget(self.window_btn)

        self.close_btn = QPushButton(self.header_right_btn_container)
        self.close_btn.setObjectName(u"close_btn")
        self.close_btn.setMinimumSize(QSize(20, 18))
        self.close_btn.setMaximumSize(QSize(20, 18))
        self.close_btn.setStyleSheet(u"image: url(:/svg/svg/false.svg);")

        self.horizontalLayout_20.addWidget(self.close_btn)


        self.horizontalLayout_2.addWidget(self.header_right_btn_container)


        self.verticalLayout_33.addWidget(self.header_bar)

        self.self_sized_main_widget = QWidget(self.style_sheet)
        self.self_sized_main_widget.setObjectName(u"self_sized_main_widget")
        self.self_sized_main_widget.setMaximumSize(QSize(16777215, 16777215))
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
"\n"
"/*\u6bcf\u4e2a\u6309\u94ae\u7684\u6837\u5f0f\u5728\u8fd9\u91cc*/\n"
"/*\u4e0d\u662fchecked\uff0c\u5df2\u7ecf\u5220\u9664\u8fc7 \u9a8c\u8bc1\u4e86*/\n"
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
"QPushButton:pressed{\n"
"	background-color : #90b6e7;\n"
"	border-radius : 0;\n"
"	margin :0;\n"
"	border :0;\n"
"}\n"
"\n"
"\n"
"/*\u56fe\u7247\u6837\u5f0f*/\n"
"QPushButton#one_page_btn {\n"
"    icon: url(:/png/png/one.png);\n"
"    icon-size: 20px 20px;\n"
"}\n"
"QPushButton#one_page_btn:pressed {\n"
"    icon: url(:/png_press/png/one_press.png);\n"
"    icon-size: 20px 20px;\n"
"}\n"
"\n"
"QPushButton#four_page_btn {\n"
"    icon: url(:/png/png/four.png);\n"
"    icon-size: 20px 20px;\n"
"}\n"
"QPushButton#four_page_btn:pressed {\n"
"   "
                        " icon: url(:/png_press/png/four_press.png);\n"
"    icon-size: 20px 20px;\n"
"}\n"
"\n"
"QPushButton#table_btn {\n"
"    icon: url(:/png/png/table.png);\n"
"    icon-size: 20px 20px;\n"
"}\n"
"QPushButton#table_btn:pressed {\n"
"    icon: url(:/png_press/png/table_press.png);\n"
"    icon-size: 20px 20px;\n"
"}\n"
"\n"
"QPushButton#note_btn {\n"
"    icon: url(:/png/png/note_btn.png);\n"
"    icon-size: 20px 20px;\n"
"}\n"
"QPushButton#note_btn:pressed {\n"
"    icon: url(:/png_press/png/note_btn_press.png);\n"
"    icon-size: 20px 20px;\n"
"}\n"
"\n"
"QPushButton#settings_btn {\n"
"    icon: url(:/png/png/settings.png);\n"
"    icon-size: 20px 20px;\n"
"}\n"
"QPushButton#settings_btn:pressed {\n"
"    icon: url(:/png_press/png/settings_press.png);\n"
"    icon-size: 20px 20px;\n"
"}\n"
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
        self.one_page_btn.setStyleSheet(u"")

        self.left_up_four_frame.addWidget(self.one_page_btn)

        self.four_page_btn = QPushButton(self.left_box_frame)
        self.four_page_btn.setObjectName(u"four_page_btn")
        self.four_page_btn.setMinimumSize(QSize(0, 40))
        self.four_page_btn.setMaximumSize(QSize(70, 16777215))
        self.four_page_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self.four_page_btn.setStyleSheet(u"")

        self.left_up_four_frame.addWidget(self.four_page_btn)

        self.table_btn = QPushButton(self.left_box_frame)
        self.table_btn.setObjectName(u"table_btn")
        self.table_btn.setMinimumSize(QSize(0, 40))
        self.table_btn.setMaximumSize(QSize(60, 40))
        self.table_btn.setStyleSheet(u"")

        self.left_up_four_frame.addWidget(self.table_btn)

        self.note_btn = QPushButton(self.left_box_frame)
        self.note_btn.setObjectName(u"note_btn")
        self.note_btn.setMinimumSize(QSize(60, 40))
        self.note_btn.setMaximumSize(QSize(60, 40))
        self.note_btn.setStyleSheet(u"")

        self.left_up_four_frame.addWidget(self.note_btn)

        self.vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.left_up_four_frame.addItem(self.vertical_spacer)

        self.settings_btn = QPushButton(self.left_box_frame)
        self.settings_btn.setObjectName(u"settings_btn")
        self.settings_btn.setMinimumSize(QSize(0, 40))
        self.settings_btn.setMaximumSize(QSize(70, 40))
        self.settings_btn.setStyleSheet(u"")

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
        self.widget_2 = QWidget(self.page_one_container)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(0, 0))
        self.widget_2.setStyleSheet(u"* {\n"
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
"image:url(:/svg/svg/close_2.svg);\n"
"    background-repeat: no-repeat;\n"
"    background-position: center;\n"
"    border-radius: 10px;\n"
"	size:50%\n"
"}\n"
"")
        self.verticalLayout_35 = QVBoxLayout(self.widget_2)
        self.verticalLayout_35.setObjectName(u"verticalLayout_35")
        self.verticalSpacer_10 = QSpacerItem(0, 7, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_35.addItem(self.verticalSpacer_10)

        self.btn_and_text_container = QWidget(self.widget_2)
        self.btn_and_text_container.setObjectName(u"btn_and_text_container")
        self.btn_and_text_container.setMinimumSize(QSize(0, 65))
        self.btn_and_text_container.setMaximumSize(QSize(16777215, 65))
        self.btn_and_text_container.setStyleSheet(u"")
        self.horizontalLayout_21 = QHBoxLayout(self.btn_and_text_container)
        self.horizontalLayout_21.setSpacing(3)
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.horizontalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.text_container_3 = QWidget(self.btn_and_text_container)
        self.text_container_3.setObjectName(u"text_container_3")
        self.text_container_3.setMaximumSize(QSize(16777215, 40))
        self.verticalLayout_34 = QVBoxLayout(self.text_container_3)
        self.verticalLayout_34.setSpacing(6)
        self.verticalLayout_34.setObjectName(u"verticalLayout_34")
        self.verticalLayout_34.setContentsMargins(0, 0, 0, 0)
        self.title_label_2 = QLabel(self.text_container_3)
        self.title_label_2.setObjectName(u"title_label_2")
        self.title_label_2.setMaximumSize(QSize(16777215, 20))
        font1 = QFont()
        font1.setFamilies([u"Comfortaa"])
        font1.setPointSize(14)
        font1.setBold(True)
        self.title_label_2.setFont(font1)
        self.title_label_2.setStyleSheet(u"color: #ffffff; \n"
"margin-left : 7px; ")

        self.verticalLayout_34.addWidget(self.title_label_2)

        self.update_label_2 = QLabel(self.text_container_3)
        self.update_label_2.setObjectName(u"update_label_2")
        self.update_label_2.setMaximumSize(QSize(16777215, 12))
        self.update_label_2.setFont(font)
        self.update_label_2.setStyleSheet(u"margin-left : 10px; \n"
"color : #90b6e7;")

        self.verticalLayout_34.addWidget(self.update_label_2)


        self.horizontalLayout_21.addWidget(self.text_container_3)

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
"}\n"
"\n"
"QPushButton#one_set_preference {\n"
"    icon: url(:/png/png/set_preference.png);\n"
"    icon-size: 17px 17px;\n"
"}\n"
"QPushButton#one_set_preference:pressed {\n"
"    icon: url(:/png_press/png/set_preference_press.png);\n"
"    icon-size: 17px 17px;\n"
"}")
        self.btn_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.btn_frame.setFrameShadow(QFrame.Shadow.Plain)
        self.btn_frame.setLineWidth(0)
        self.horizontalLayout_22 = QHBoxLayout(self.btn_frame)
        self.horizontalLayout_22.setSpacing(0)
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalLayout_22.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_22.addItem(self.horizontalSpacer)

        self.one_set_preference = QPushButton(self.btn_frame)
        self.one_set_preference.setObjectName(u"one_set_preference")
        self.one_set_preference.setMaximumSize(QSize(25, 25))
        self.one_set_preference.setStyleSheet(u"")

        self.horizontalLayout_22.addWidget(self.one_set_preference)


        self.horizontalLayout_21.addWidget(self.btn_frame)

        self.horizontalSpacer_5 = QSpacerItem(10, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_21.addItem(self.horizontalSpacer_5)


        self.verticalLayout_35.addWidget(self.btn_and_text_container)

        self.verticalSpacer_9 = QSpacerItem(20, 7, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_35.addItem(self.verticalSpacer_9)

        self.graph_widget_2 = QWidget(self.widget_2)
        self.graph_widget_2.setObjectName(u"graph_widget_2")
        self.graph_widget_2.setStyleSheet(u"background-color : #262a2f;\n"
"border-radius:30px;\n"
"margin-left : 10px;\n"
"margin-right : 10px;")

        self.verticalLayout_35.addWidget(self.graph_widget_2)


        self.verticalLayout_4.addWidget(self.widget_2)

        self.stackedWidget.addWidget(self.page_one_container)
        self.page_table_container = QWidget()
        self.page_table_container.setObjectName(u"page_table_container")
        self.verticalLayout_8 = QVBoxLayout(self.page_table_container)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.text_and_btn = QWidget(self.page_table_container)
        self.text_and_btn.setObjectName(u"text_and_btn")
        self.text_and_btn.setMinimumSize(QSize(0, 82))
        self.text_and_btn.setMaximumSize(QSize(16777215, 82))
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
        self.verticalLayout_9.setSpacing(6)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.table_title_label = QLabel(self.text_container_2)
        self.table_title_label.setObjectName(u"table_title_label")
        self.table_title_label.setMaximumSize(QSize(16777215, 20))
        self.table_title_label.setFont(font1)
        self.table_title_label.setStyleSheet(u"color: #ffffff; \n"
"margin-left : 7px; ")

        self.verticalLayout_9.addWidget(self.table_title_label)

        self.table_update_label = QLabel(self.text_container_2)
        self.table_update_label.setObjectName(u"table_update_label")
        self.table_update_label.setMaximumSize(QSize(16777215, 12))
        self.table_update_label.setFont(font)
        self.table_update_label.setStyleSheet(u"margin-left : 9px; \n"
"color : #90b6e7;")

        self.verticalLayout_9.addWidget(self.table_update_label)


        self.horizontalLayout_6.addWidget(self.text_container_2)

        self.page_table_set_preference = QPushButton(self.text_and_btn)
        self.page_table_set_preference.setObjectName(u"page_table_set_preference")
        self.page_table_set_preference.setMaximumSize(QSize(25, 25))
        self.page_table_set_preference.setStyleSheet(u"QPushButton#page_table_set_preference {\n"
"    icon: url(:/png/png/set_preference.png);\n"
"    icon-size: 17px 17px;\n"
"}\n"
"QPushButton#page_table_set_preference:pressed {\n"
"    icon: url(:/png_press/png/set_preference_press.png);\n"
"    icon-size: 17px 17px;\n"
"}")

        self.horizontalLayout_6.addWidget(self.page_table_set_preference)

        self.horizontalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_2)


        self.verticalLayout_8.addWidget(self.text_and_btn)

        self.table_container = QWidget(self.page_table_container)
        self.table_container.setObjectName(u"table_container")
        self.table_container.setMaximumSize(QSize(16777215, 16777215))
        self.table_container.setStyleSheet(u"background-color : #262a2f;\n"
"border-radius:30px;\n"
"margin-left : 10px;\n"
"margin-right : 10px;")
        self.verticalLayout_10 = QVBoxLayout(self.table_container)
        self.verticalLayout_10.setSpacing(0)
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
        self.four_text_widget.setMinimumSize(QSize(0, 80))
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
"}\n"
"\n"
"\n"
"QPushButton#four_settings_button {\n"
"    icon: url(:/png/png/set_preference.png);\n"
"    icon-size: 17px 17px;\n"
"}\n"
"QPushButton#four_settings_button:pressed {\n"
"    icon: url(:/png_press/png/set_preference_press.png);\n"
"    icon-size: 17px 17px;\n"
"}\n"
"")
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
        self.four_title_label.setMaximumSize(QSize(16777215, 20))
        self.four_title_label.setFont(font1)
        self.four_title_label.setStyleSheet(u"color: #ffffff; \n"
"margin-left : 7px; ")

        self.verticalLayout_7.addWidget(self.four_title_label)

        self.four_update_label = QLabel(self.four_text_container)
        self.four_update_label.setObjectName(u"four_update_label")
        self.four_update_label.setMaximumSize(QSize(16777215, 12))
        self.four_update_label.setFont(font)
        self.four_update_label.setStyleSheet(u"margin-left : 8px; \n"
"color : #90b6e7;")

        self.verticalLayout_7.addWidget(self.four_update_label)


        self.horizontalLayout_5.addWidget(self.four_text_container)

        self.connect_charts = QCheckBox(self.four_text_widget)
        self.connect_charts.setObjectName(u"connect_charts")
        self.connect_charts.setMaximumSize(QSize(150, 16777215))
        font2 = QFont()
        font2.setFamilies([u"Comfortaa"])
        font2.setBold(True)
        self.connect_charts.setFont(font2)
        self.connect_charts.setStyleSheet(u"color:white;")

        self.horizontalLayout_5.addWidget(self.connect_charts)

        self.four_settings_button = QPushButton(self.four_text_widget)
        self.four_settings_button.setObjectName(u"four_settings_button")
        self.four_settings_button.setMaximumSize(QSize(25, 25))
        self.four_settings_button.setStyleSheet(u"")

        self.horizontalLayout_5.addWidget(self.four_settings_button)


        self.verticalLayout_3.addWidget(self.four_text_widget)

        self.chart_widget = QWidget(self.page_four_container)
        self.chart_widget.setObjectName(u"chart_widget")
        self.chart_widget.setMaximumSize(QSize(16777215, 16777215))
        self.chart_widget.setStyleSheet(u"")
        self.gridLayout = QGridLayout(self.chart_widget)
        self.gridLayout.setSpacing(8)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(10, 0, 10, 0)
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
        self.page_note_container = QWidget()
        self.page_note_container.setObjectName(u"page_note_container")
        self.page_note_container.setStyleSheet(u"QScrollBar:vertical {\n"
"	border: none;\n"
"    background: #ffffff;\n"
"    width: 17.5px;\n"
"    margin: 0;\n"
"	border-radius: 0px;\n"
" }\n"
"QScrollBar::handle:vertical {	\n"
"	background: #90b6e7;\n"
"	width :8px;\n"
"    min-height: 25px;\n"
"	border-radius: 4px\n"
" }\n"
"\n"
"\n"
"/*\u8bbe\u7f6e\u4e0a\u4e0b\u6309\u94ae*/\n"
" QScrollBar::add-line:vertical {\n"
"     border: none;\n"
"    background: transparent;\n"
"     height: 20px;\n"
"	border-bottom-left-radius: 4px;\n"
"    border-bottom-right-radius: 4px;\n"
"     subcontrol-position: bottom;\n"
"     subcontrol-origin: margin;\n"
" }\n"
" QScrollBar::sub-line:vertical {\n"
"	border: none;\n"
"    background: transparent;\n"
"     height: 20px;\n"
"	border-top-left-radius: 4px;\n"
"    border-top-right-radius: 4px;\n"
"     subcontrol-position: top;\n"
"     subcontrol-origin: margin;\n"
" }\n"
"\n"
"\n"
"/*\u9632\u6b62\u906e\u4f4f\u6ed1\u6761\u80cc\u666f\u989c\u8272*/\n"
" QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
" "
                        "    background: none;\n"
" }\n"
" QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"     background: none;\n"
" }\n"
"")
        self.horizontalLayout_7 = QHBoxLayout(self.page_note_container)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.note_list = QWidget(self.page_note_container)
        self.note_list.setObjectName(u"note_list")
        self.note_list.setMinimumSize(QSize(230, 0))
        self.note_list.setMaximumSize(QSize(230, 16777215))
        self.note_list.setStyleSheet(u"* {\n"
"background-color: #3e4146;\n"
"border : 0;\n"
"margin :0;\n"
"}\n"
"\n"
"\n"
"\n"
"/* scroll bar*/\n"
" QScrollBar:vertical {\n"
"	border: none;\n"
"    background: #303030;\n"
"    width: 8px;\n"
"    margin: 21px 0 21px 0;\n"
"	border-radius: 0px;\n"
" }\n"
" QScrollBar::handle:vertical {	\n"
"	background: #90b6e7;\n"
"    min-height: 25px;\n"
"	border-radius: 4px\n"
" }\n"
"\n"
"\n"
"/*\u8bbe\u7f6e\u4e0a\u4e0b\u6ed1\u6761\u6309\u94ae*/\n"
" QScrollBar::add-line:vertical {\n"
"     border: none;\n"
"    background: #252526;\n"
"     height: 20px;\n"
"	border-bottom-left-radius: 4px;\n"
"    border-bottom-right-radius: 4px;\n"
"     subcontrol-position: bottom;\n"
"     subcontrol-origin: margin;\n"
" }\n"
" QScrollBar::sub-line:vertical {\n"
"	border: none;\n"
"    background: #252526;\n"
"     height: 20px;\n"
"	border-top-left-radius: 4px;\n"
"    border-top-right-radius: 4px;\n"
"     subcontrol-position: top;\n"
"     subcontrol-origin: margin;\n"
" }\n"
"\n"
"\n"
"/*\u9632\u6b62\u906e\u4f4f\u6ed1"
                        "\u6761\u80cc\u666f\u989c\u8272*/\n"
" QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
"     background: none;\n"
" }\n"
" QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"     background: none;\n"
" }\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"/* scroll bar   horizontal \u9690\u85cf!!!!!*/\n"
" QScrollBar:horizontal {\n"
"	border: none;\n"
"    background: transparent;\n"
"    width: 0;\n"
" }\n"
" QScrollBar::handle:horizontal {	\n"
"	border: none;\n"
"    background: transparent;\n"
"    width: 0;\n"
" }\n"
"\n"
"\n"
" QScrollBar::add-line:horizontal {\n"
"     border: none;\n"
"    background: transparent;\n"
"    width: 0;\n"
" }\n"
" QScrollBar::sub-line:horizontal {\n"
"	border: none;\n"
"    background: transparent;\n"
"    width: 0;\n"
" }\n"
"\n"
"\n"
"/*\u9632\u6b62\u906e\u4f4f\u6ed1\u6761\u80cc\u666f\u989c\u8272*/\n"
" QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal {\n"
"     border: none;\n"
"    background: transparent;\n"
"    width: 0;\n"
""
                        " }\n"
" QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {\n"
"     border: none;\n"
"    background: transparent;\n"
"    width: 0;\n"
" }\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"/*\u8f93\u5165\u6761*/\n"
"QLineEdit {\n"
"        background-color: #33363a;\n"
"        border-radius : 2px;\n"
"	    max-height : 9px;\n"
"        border-bottom: 1px solid #90b6e7;\n"
"        padding: 5px;\n"
"    }\n"
"QLineEdit:focus {\n"
"		background-color: #454555;\n"
"        border-bottom: 1px solid #ffffff;\n"
"    }\n"
"")
        self.verticalLayout_15 = QVBoxLayout(self.note_list)
        self.verticalLayout_15.setSpacing(5)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(3, 0, 3, 0)
        self.note_list_text_container = QWidget(self.note_list)
        self.note_list_text_container.setObjectName(u"note_list_text_container")
        self.note_list_text_container.setMinimumSize(QSize(0, 70))
        self.note_list_text_container.setMaximumSize(QSize(16777215, 70))
        self.note_list_text_container.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.note_list_text_container.setStyleSheet(u"background : #3a3b43;")
        self.verticalLayout_17 = QVBoxLayout(self.note_list_text_container)
        self.verticalLayout_17.setSpacing(0)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.note_text_container_3 = QWidget(self.note_list_text_container)
        self.note_text_container_3.setObjectName(u"note_text_container_3")
        self.note_text_container_3.setMinimumSize(QSize(0, 70))
        self.note_text_container_3.setMaximumSize(QSize(16777215, 70))
        self.note_text_container_3.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalLayout_16 = QVBoxLayout(self.note_text_container_3)
        self.verticalLayout_16.setSpacing(5)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer_7 = QSpacerItem(20, 18, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_16.addItem(self.verticalSpacer_7)

        self.four_title_label_3 = QLabel(self.note_text_container_3)
        self.four_title_label_3.setObjectName(u"four_title_label_3")
        self.four_title_label_3.setMaximumSize(QSize(16777215, 18))
        font3 = QFont()
        font3.setFamilies([u"Comfortaa"])
        font3.setPointSize(10)
        font3.setBold(True)
        self.four_title_label_3.setFont(font3)
        self.four_title_label_3.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.four_title_label_3.setStyleSheet(u"color: #ffffff; \n"
"margin-left : 7px; ")
        self.four_title_label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_16.addWidget(self.four_title_label_3)

        self.four_update_label_3 = QLabel(self.note_text_container_3)
        self.four_update_label_3.setObjectName(u"four_update_label_3")
        self.four_update_label_3.setMaximumSize(QSize(16777215, 12))
        font4 = QFont()
        font4.setFamilies([u"Comfortaa"])
        font4.setPointSize(6)
        font4.setBold(True)
        self.four_update_label_3.setFont(font4)
        self.four_update_label_3.setStyleSheet(u"margin-left : 10px; \n"
"color : #90b6e7;")
        self.four_update_label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_16.addWidget(self.four_update_label_3)

        self.verticalSpacer_6 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_16.addItem(self.verticalSpacer_6)


        self.verticalLayout_17.addWidget(self.note_text_container_3)


        self.verticalLayout_15.addWidget(self.note_list_text_container)

        self.scrollArea = QScrollArea(self.note_list)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setStyleSheet(u"QPushButton {\n"
"	min-height : 50px;\n"
"	font-family : \"Comfortaa\";\n"
"	font-weight : Bold;\n"
"	color : white;\n"
"\n"
"}")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 224, 554))
        self.scrollAreaWidgetContents.setStyleSheet(u"* {\n"
"background:#3a3d43;\n"
"}\n"
"\n"
"QPushButton {\n"
"	background-color : #3e4146;\n"
"	border : 0;\n"
"	max-width : 230px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color : #515660;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"	background-color : #2b2e32;\n"
"}\n"
"")
        self.verticalLayout_18 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_18.setSpacing(2)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(0, 1, 0, 1)
        self.note_instructions_btn = QPushButton(self.scrollAreaWidgetContents)
        self.note_instructions_btn.setObjectName(u"note_instructions_btn")

        self.verticalLayout_18.addWidget(self.note_instructions_btn)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_18.addItem(self.verticalSpacer_8)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_15.addWidget(self.scrollArea)

        self.note_status_bar = QLabel(self.note_list)
        self.note_status_bar.setObjectName(u"note_status_bar")
        self.note_status_bar.setFont(font)
        self.note_status_bar.setStyleSheet(u"color : #90b6e7; padding-top : 4px;")
        self.note_status_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_15.addWidget(self.note_status_bar)

        self.note_enter_passage_name = QLineEdit(self.note_list)
        self.note_enter_passage_name.setObjectName(u"note_enter_passage_name")
        self.note_enter_passage_name.setMinimumSize(QSize(0, 26))
        self.note_enter_passage_name.setFont(font)
        self.note_enter_passage_name.setStyleSheet(u"color : white; ")

        self.verticalLayout_15.addWidget(self.note_enter_passage_name)

        self.note_add_del_container = QWidget(self.note_list)
        self.note_add_del_container.setObjectName(u"note_add_del_container")
        self.note_add_del_container.setMinimumSize(QSize(0, 60))
        self.note_add_del_container.setStyleSheet(u"* {\n"
"background : #3a3b43;\n"
"}\n"
"\n"
"/*\u6bcf\u4e2a\u6309\u94ae\u7684\u6837\u5f0f\u5728\u8fd9\u91cc*/\n"
"\n"
"QPushButton {\n"
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
"}\n"
"\n"
"\n"
"QPushButton#note_add_btn {\n"
"    icon: url(:/png/png/add_page.png);\n"
"    icon-size: 17px 17px;\n"
"}\n"
"QPushButton#note_add_btn:pressed {\n"
"    icon: url(:/png_press/png/add_page_press.png);\n"
"    icon-size: 17px 17px;\n"
"}\n"
"QPushButton#note_delete_btn {\n"
"    icon: url(:/png/png/delete.png);\n"
"    icon-size: 17px 17px;\n"
"}\n"
"QPushButton#note_delete_btn:pressed {\n"
"    icon: url(:/png_press/png/delete_press.png);\n"
"    icon-size: 17px 17px;\n"
"}\n"
"QPushButton#note_rename_btn {\n"
"    icon: url(:/png/png/rename.png);\n"
"    icon-size: 17px 17px;\n"
"}\n"
"QPushButton#note_rename_btn:pr"
                        "essed {\n"
"    icon: url(:/png_press/png/rename_press.png);\n"
"    icon-size: 17px 17px;\n"
"}\n"
"\n"
"")
        self.horizontalLayout_9 = QHBoxLayout(self.note_add_del_container)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.note_add_btn = QPushButton(self.note_add_del_container)
        self.note_add_btn.setObjectName(u"note_add_btn")
        self.note_add_btn.setMaximumSize(QSize(25, 25))
        self.note_add_btn.setStyleSheet(u"")

        self.horizontalLayout_9.addWidget(self.note_add_btn)

        self.note_rename_btn = QPushButton(self.note_add_del_container)
        self.note_rename_btn.setObjectName(u"note_rename_btn")
        self.note_rename_btn.setMaximumSize(QSize(25, 25))

        self.horizontalLayout_9.addWidget(self.note_rename_btn)

        self.note_delete_btn = QPushButton(self.note_add_del_container)
        self.note_delete_btn.setObjectName(u"note_delete_btn")
        self.note_delete_btn.setMaximumSize(QSize(25, 25))
        self.note_delete_btn.setStyleSheet(u"")

        self.horizontalLayout_9.addWidget(self.note_delete_btn)


        self.verticalLayout_15.addWidget(self.note_add_del_container)


        self.horizontalLayout_7.addWidget(self.note_list)

        self.content_area = QWidget(self.page_note_container)
        self.content_area.setObjectName(u"content_area")
        self.content_area.setMinimumSize(QSize(0, 0))
        self.verticalLayout_11 = QVBoxLayout(self.content_area)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.text_enter_container = QWidget(self.content_area)
        self.text_enter_container.setObjectName(u"text_enter_container")
        self.text_enter_container.setMinimumSize(QSize(0, 80))
        self.text_enter_container.setMaximumSize(QSize(16777215, 80))
        self.text_enter_container.setStyleSheet(u"QPushButton {\n"
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
"}\n"
"\n"
"QPushButton#save_text {\n"
"    icon: url(:/png/png/save_2.png);\n"
"    icon-size: 17px 17px;\n"
"}\n"
"QPushButton#save_text:pressed {\n"
"    icon: url(:/png_press/png/save_2_press.png);\n"
"    icon-size: 17px 17px;\n"
"}\n"
"")
        self.horizontalLayout_8 = QHBoxLayout(self.text_enter_container)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(-1, -1, -1, 9)
        self.note_text_container = QWidget(self.text_enter_container)
        self.note_text_container.setObjectName(u"note_text_container")
        self.note_text_container.setMaximumSize(QSize(16777215, 40))
        self.verticalLayout_12 = QVBoxLayout(self.note_text_container)
        self.verticalLayout_12.setSpacing(6)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.note_title_label = QLabel(self.note_text_container)
        self.note_title_label.setObjectName(u"note_title_label")
        self.note_title_label.setMaximumSize(QSize(16777215, 20))
        self.note_title_label.setFont(font1)
        self.note_title_label.setStyleSheet(u"color: #ffffff; \n"
"margin-left : 7px; ")

        self.verticalLayout_12.addWidget(self.note_title_label)

        self.note_update_label = QLabel(self.note_text_container)
        self.note_update_label.setObjectName(u"note_update_label")
        self.note_update_label.setMaximumSize(QSize(16777215, 12))
        self.note_update_label.setFont(font)
        self.note_update_label.setStyleSheet(u"margin-left : 10px; \n"
"color : #90b6e7;")

        self.verticalLayout_12.addWidget(self.note_update_label)


        self.horizontalLayout_8.addWidget(self.note_text_container)

        self.save_text = QPushButton(self.text_enter_container)
        self.save_text.setObjectName(u"save_text")
        self.save_text.setEnabled(False)
        self.save_text.setMaximumSize(QSize(25, 25))

        self.horizontalLayout_8.addWidget(self.save_text)

        self.horizontalSpacer_3 = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_3)


        self.verticalLayout_11.addWidget(self.text_enter_container)

        self.note_label_notes = QLabel(self.content_area)
        self.note_label_notes.setObjectName(u"note_label_notes")
        self.note_label_notes.setFont(font2)
        self.note_label_notes.setStyleSheet(u"color : #EE5C88; margin-left : 20px")

        self.verticalLayout_11.addWidget(self.note_label_notes)

        self.note_title_container = QWidget(self.content_area)
        self.note_title_container.setObjectName(u"note_title_container")
        self.verticalLayout_13 = QVBoxLayout(self.note_title_container)
        self.verticalLayout_13.setSpacing(0)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.text_edit_container = QWidget(self.note_title_container)
        self.text_edit_container.setObjectName(u"text_edit_container")
        self.text_edit_container.setStyleSheet(u"background-color : #262a2f;\n"
"border-radius:30px;\n"
"margin-left : 10px;\n"
"margin-right : 10px;")
        self.verticalLayout_14 = QVBoxLayout(self.text_edit_container)
        self.verticalLayout_14.setSpacing(25)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(25, 25, 25, 25)
        self.plainTextEdit = QPlainTextEdit(self.text_edit_container)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        self.plainTextEdit.setStyleSheet(u"color : white; \n"
"font-family : \"Comfortaa\";")
        self.plainTextEdit.setReadOnly(True)

        self.verticalLayout_14.addWidget(self.plainTextEdit)


        self.verticalLayout_13.addWidget(self.text_edit_container)


        self.verticalLayout_11.addWidget(self.note_title_container)


        self.horizontalLayout_7.addWidget(self.content_area)

        self.stackedWidget.addWidget(self.page_note_container)
        self.page_settings_container = QWidget()
        self.page_settings_container.setObjectName(u"page_settings_container")
        self.page_settings_container.setStyleSheet(u"QScrollBar:vertical {\n"
"	border: none;\n"
"    background: #ffffff;\n"
"    width: 17.5px;\n"
"    margin: 0;\n"
"	border-radius: 0px;\n"
" }\n"
"QScrollBar::handle:vertical {	\n"
"	background: #90b6e7;\n"
"	width :8px;\n"
"    min-height: 25px;\n"
"	border-radius: 4px\n"
" }\n"
"\n"
"\n"
"/*\u8bbe\u7f6e\u4e0a\u4e0b\u6309\u94ae*/\n"
" QScrollBar::add-line:vertical {\n"
"     border: none;\n"
"    background: transparent;\n"
"     height: 20px;\n"
"	border-bottom-left-radius: 4px;\n"
"    border-bottom-right-radius: 4px;\n"
"     subcontrol-position: bottom;\n"
"     subcontrol-origin: margin;\n"
" }\n"
" QScrollBar::sub-line:vertical {\n"
"	border: none;\n"
"    background: transparent;\n"
"     height: 20px;\n"
"	border-top-left-radius: 4px;\n"
"    border-top-right-radius: 4px;\n"
"     subcontrol-position: top;\n"
"     subcontrol-origin: margin;\n"
" }\n"
"\n"
"\n"
"/*\u9632\u6b62\u906e\u4f4f\u6ed1\u6761\u80cc\u666f\u989c\u8272*/\n"
" QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
" "
                        "    background: none;\n"
" }\n"
" QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"     background: none;\n"
" }\n"
"")
        self.verticalLayout_19 = QVBoxLayout(self.page_settings_container)
        self.verticalLayout_19.setSpacing(12)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(18, -1, 18, -1)
        self.setting_text_container = QWidget(self.page_settings_container)
        self.setting_text_container.setObjectName(u"setting_text_container")
        self.setting_text_container.setMinimumSize(QSize(0, 80))
        self.setting_text_container.setMaximumSize(QSize(16777215, 80))
        self.verticalLayout_22 = QVBoxLayout(self.setting_text_container)
        self.verticalLayout_22.setSpacing(0)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(0, 0, 0, 0)
        self.note_text_container_2 = QWidget(self.setting_text_container)
        self.note_text_container_2.setObjectName(u"note_text_container_2")
        self.note_text_container_2.setMaximumSize(QSize(16777215, 40))
        self.verticalLayout_21 = QVBoxLayout(self.note_text_container_2)
        self.verticalLayout_21.setSpacing(6)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.verticalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.note_title_label_2 = QLabel(self.note_text_container_2)
        self.note_title_label_2.setObjectName(u"note_title_label_2")
        self.note_title_label_2.setMaximumSize(QSize(16777215, 20))
        self.note_title_label_2.setFont(font1)
        self.note_title_label_2.setStyleSheet(u"color: #ffffff; \n"
"margin-left : 1px; ")

        self.verticalLayout_21.addWidget(self.note_title_label_2)

        self.note_update_label_2 = QLabel(self.note_text_container_2)
        self.note_update_label_2.setObjectName(u"note_update_label_2")
        self.note_update_label_2.setMaximumSize(QSize(16777215, 12))
        self.note_update_label_2.setFont(font)
        self.note_update_label_2.setStyleSheet(u"margin-left : 1px; \n"
"color : #90b6e7;")

        self.verticalLayout_21.addWidget(self.note_update_label_2)


        self.verticalLayout_22.addWidget(self.note_text_container_2)


        self.verticalLayout_19.addWidget(self.setting_text_container)

        self.setting_two_box_container = QWidget(self.page_settings_container)
        self.setting_two_box_container.setObjectName(u"setting_two_box_container")
        self.setting_two_box_container.setStyleSheet(u"QGroupBox {\n"
" border: 2px solid #2b2e32; \n"
"border-radius: 25px; \n"
"margin-top: 1ex; \n"
"padding-top: 0px; } \n"
"\n"
"QGroupBox::title { \n"
"subcontrol-origin: margin; \n"
"subcontrol-position: top center; \n"
"padding: 0 10px; \n"
"color : white; \n"
"margin-top: -0.5ex; /* \u5782\u76f4 */ \n"
"font-family: \"Comfortaa\"; \n"
"font-size: 14px; \n"
"font-weight: bold;\n"
" } \n"
"\n"
"")
        self.horizontalLayout_10 = QHBoxLayout(self.setting_two_box_container)
        self.horizontalLayout_10.setSpacing(12)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.api_group_box = QGroupBox(self.setting_two_box_container)
        self.api_group_box.setObjectName(u"api_group_box")
        self.api_group_box.setBaseSize(QSize(0, 0))
        self.api_group_box.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.api_group_box.setStyleSheet(u"* {\n"
"color :white;\n"
"font-family : \"Comfortaa\";\n"
"font-weight : Bold;\n"
"}\n"
"\n"
"QWidget{\n"
"	background: #2b2e32;\n"
"}")
        self.api_group_box.setFlat(False)
        self.api_group_box.setCheckable(False)
        self.verticalLayout_23 = QVBoxLayout(self.api_group_box)
        self.verticalLayout_23.setSpacing(0)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.verticalLayout_23.setContentsMargins(15, 12, 15, 12)
        self.setting_page_notify_text = QLabel(self.api_group_box)
        self.setting_page_notify_text.setObjectName(u"setting_page_notify_text")
        self.setting_page_notify_text.setMaximumSize(QSize(16777215, 30))
        self.setting_page_notify_text.setFont(font3)
        self.setting_page_notify_text.setStyleSheet(u"color : #90b6e7;")
        self.setting_page_notify_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_23.addWidget(self.setting_page_notify_text)

        self.enter_text_container = QWidget(self.api_group_box)
        self.enter_text_container.setObjectName(u"enter_text_container")
        self.enter_text_container.setMinimumSize(QSize(0, 0))
        self.enter_text_container.setStyleSheet(u"")
        self.horizontalLayout_14 = QHBoxLayout(self.enter_text_container)
        self.horizontalLayout_14.setSpacing(0)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.lapi_enter_container = QWidget(self.enter_text_container)
        self.lapi_enter_container.setObjectName(u"lapi_enter_container")
        self.lapi_enter_container.setStyleSheet(u"QLineEdit {\n"
"        background-color: #33363a;\n"
"        border-radius : 2px;\n"
"	    max-height : 9px;\n"
"        border-bottom: 1px solid #90b6e7;\n"
"        padding: 5px;\n"
"    }\n"
"QLineEdit:focus {\n"
"		background-color: #454555;\n"
"        border-bottom: 1px solid #ffffff;\n"
"    }")
        self.verticalLayout_25 = QVBoxLayout(self.lapi_enter_container)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.bea_api = QLineEdit(self.lapi_enter_container)
        self.bea_api.setObjectName(u"bea_api")
        self.bea_api.setEchoMode(QLineEdit.EchoMode.Password)

        self.verticalLayout_25.addWidget(self.bea_api)

        self.fred_api = QLineEdit(self.lapi_enter_container)
        self.fred_api.setObjectName(u"fred_api")
        self.fred_api.setEchoMode(QLineEdit.EchoMode.Password)

        self.verticalLayout_25.addWidget(self.fred_api)

        self.bls_api = QLineEdit(self.lapi_enter_container)
        self.bls_api.setObjectName(u"bls_api")
        self.bls_api.setEchoMode(QLineEdit.EchoMode.Password)

        self.verticalLayout_25.addWidget(self.bls_api)


        self.horizontalLayout_14.addWidget(self.lapi_enter_container)

        self.widget = QWidget(self.enter_text_container)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(150, 0))
        self.widget.setMaximumSize(QSize(16777215, 16777215))
        self.widget.setStyleSheet(u"QLabel {\n"
"max-height : 20px;\n"
"}")
        self.verticalLayout_24 = QVBoxLayout(self.widget)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.bea_label = QLabel(self.widget)
        self.bea_label.setObjectName(u"bea_label")
        self.bea_label.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_24.addWidget(self.bea_label)

        self.fred_label = QLabel(self.widget)
        self.fred_label.setObjectName(u"fred_label")
        self.fred_label.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_24.addWidget(self.fred_label)

        self.bls_label = QLabel(self.widget)
        self.bls_label.setObjectName(u"bls_label")
        self.bls_label.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_24.addWidget(self.bls_label)


        self.horizontalLayout_14.addWidget(self.widget)


        self.verticalLayout_23.addWidget(self.enter_text_container)

        self.api_btn_frame = QFrame(self.api_group_box)
        self.api_btn_frame.setObjectName(u"api_btn_frame")
        self.api_btn_frame.setMinimumSize(QSize(0, 45))
        self.api_btn_frame.setMaximumSize(QSize(16777215, 45))
        self.api_btn_frame.setStyleSheet(u"QPushButton {\n"
"	background : #202023;\n"
"	border-radius : 7px\n"
"}\n"
"\n"
"QPushButton::hover {\n"
"	background : #454545;\n"
"}\n"
"QPushButton::pressed {\n"
"	background : #202023;\n"
"}")
        self.api_btn_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.api_btn_frame.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLayout_11 = QHBoxLayout(self.api_btn_frame)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(20, -1, 20, -1)
        self.api_save_btn = QPushButton(self.api_btn_frame)
        self.api_save_btn.setObjectName(u"api_save_btn")
        self.api_save_btn.setMaximumSize(QSize(100, 70))

        self.horizontalLayout_11.addWidget(self.api_save_btn)

        self.status_label = QLabel(self.api_btn_frame)
        self.status_label.setObjectName(u"status_label")
        self.status_label.setMaximumSize(QSize(250, 16777215))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_11.addWidget(self.status_label)


        self.verticalLayout_23.addWidget(self.api_btn_frame)


        self.horizontalLayout_10.addWidget(self.api_group_box)

        self.other_group_box = QGroupBox(self.setting_two_box_container)
        self.other_group_box.setObjectName(u"other_group_box")
        self.other_group_box.setMinimumSize(QSize(330, 0))
        self.other_group_box.setStyleSheet(u"*{\n"
"border:0;\n"
"}\n"
"\n"
"QWidget{\n"
"	background: #2b2e32;\n"
"}\n"
"\n"
"")
        self.verticalLayout_26 = QVBoxLayout(self.other_group_box)
        self.verticalLayout_26.setSpacing(8)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.verticalLayout_26.setContentsMargins(15, 12, 15, 12)
        self.other_option_text = QLabel(self.other_group_box)
        self.other_option_text.setObjectName(u"other_option_text")
        self.other_option_text.setMinimumSize(QSize(0, 30))
        self.other_option_text.setMaximumSize(QSize(16777215, 30))
        self.other_option_text.setFont(font3)
        self.other_option_text.setStyleSheet(u"color:#90b6e7;\n"
"font-weight : Bold;")
        self.other_option_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_26.addWidget(self.other_option_text)

        self.basic_info_and_icon = QWidget(self.other_group_box)
        self.basic_info_and_icon.setObjectName(u"basic_info_and_icon")
        self.basic_info_and_icon.setMaximumSize(QSize(16777215, 110))
        self.horizontalLayout_13 = QHBoxLayout(self.basic_info_and_icon)
        self.horizontalLayout_13.setSpacing(0)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.info_container = QWidget(self.basic_info_and_icon)
        self.info_container.setObjectName(u"info_container")
        self.info_container.setMinimumSize(QSize(0, 0))
        self.info_container.setMaximumSize(QSize(16777215, 16777215))
        self.info_container.setStyleSheet(u"")
        self.horizontalLayout_17 = QHBoxLayout(self.info_container)
        self.horizontalLayout_17.setSpacing(0)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalLayout_17.setContentsMargins(0, 0, 30, 0)
        self.basic_version_info_text = QLabel(self.info_container)
        self.basic_version_info_text.setObjectName(u"basic_version_info_text")
        self.basic_version_info_text.setMinimumSize(QSize(0, 75))
        self.basic_version_info_text.setMaximumSize(QSize(16777215, 75))
        font5 = QFont()
        font5.setFamilies([u"Comfortaa"])
        font5.setPointSize(9)
        font5.setBold(True)
        self.basic_version_info_text.setFont(font5)
        self.basic_version_info_text.setStyleSheet(u"* {\n"
"font-family : \"Comfortaa\";\n"
"color:white;\n"
"margin-left :8px;\n"
"border:0;\n"
"margin-right:20px;\n"
"}")
        self.basic_version_info_text.setWordWrap(False)

        self.horizontalLayout_17.addWidget(self.basic_version_info_text)

        self.image_label = QLabel(self.info_container)
        self.image_label.setObjectName(u"image_label")
        self.image_label.setMinimumSize(QSize(75, 75))
        self.image_label.setMaximumSize(QSize(75, 75))
        self.image_label.setStyleSheet(u"background-image: url(:/png/png/ico.png);\n"
"")

        self.horizontalLayout_17.addWidget(self.image_label)


        self.horizontalLayout_13.addWidget(self.info_container)


        self.verticalLayout_26.addWidget(self.basic_info_and_icon)

        self.textEdit = QTextEdit(self.other_group_box)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setEnabled(True)
        self.textEdit.setMaximumSize(QSize(16777215, 16777215))
        font6 = QFont()
        font6.setFamilies([u"Comfortaa"])
        font6.setPointSize(12)
        self.textEdit.setFont(font6)
        self.textEdit.setStyleSheet(u"color:white; \n"
"font-famlily:\"Comfortaa\";\n"
"border :0;\n"
"background:#262a2f;\n"
"padding :5px;\n"
"\n"
"\n"
"")
        self.textEdit.setFrameShape(QFrame.Shape.NoFrame)
        self.textEdit.setFrameShadow(QFrame.Shadow.Plain)
        self.textEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.textEdit.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow)
        self.textEdit.setLineWrapColumnOrWidth(0)
        self.textEdit.setReadOnly(True)
        self.textEdit.setAcceptRichText(False)
        self.textEdit.setCursorWidth(0)

        self.verticalLayout_26.addWidget(self.textEdit)

        self.read_and_agree_check = QCheckBox(self.other_group_box)
        self.read_and_agree_check.setObjectName(u"read_and_agree_check")
        self.read_and_agree_check.setStyleSheet(u"* {\n"
"font-family : \"Comfortaa\"; \n"
"color : #EE5C88; \n"
"font-weight : Bold;\n"
"}")

        self.verticalLayout_26.addWidget(self.read_and_agree_check)


        self.horizontalLayout_10.addWidget(self.other_group_box)


        self.verticalLayout_19.addWidget(self.setting_two_box_container)

        self.group_box_container = QFrame(self.page_settings_container)
        self.group_box_container.setObjectName(u"group_box_container")
        self.group_box_container.setMinimumSize(QSize(0, 80))
        self.group_box_container.setStyleSheet(u"QGroupBox {\n"
"    border: 2px solid #303030;\n"
"    border-radius: 25px;\n"
"    margin-top: 1ex;\n"
"    padding-top: 0px; \n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    subcontrol-position: top center; \n"
"    padding: 0 10px;\n"
"	color : white;\n"
"    margin-top: -0.5ex; /* \u5782\u76f4 */\n"
"    font-family: \"Comfortaa\";\n"
"    font-size: 14px;              \n"
"    font-weight: bold; \n"
"}\n"
"\n"
"")
        self.group_box_container.setFrameShape(QFrame.Shape.NoFrame)
        self.group_box_container.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_20 = QVBoxLayout(self.group_box_container)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.download_data_box = QGroupBox(self.group_box_container)
        self.download_data_box.setObjectName(u"download_data_box")
        self.download_data_box.setMinimumSize(QSize(0, 200))
        self.download_data_box.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.download_data_box.setStyleSheet(u"QWidget{\n"
"	background: #2b2e32;\n"
"}\n"
"\n"
"")
        self.verticalLayout_28 = QVBoxLayout(self.download_data_box)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.verticalLayout_28.setContentsMargins(15, 12, 15, 12)
        self.download_text = QLabel(self.download_data_box)
        self.download_text.setObjectName(u"download_text")
        self.download_text.setMaximumSize(QSize(16777215, 30))
        self.download_text.setFont(font3)
        self.download_text.setStyleSheet(u"color : #90b6e7;")
        self.download_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_28.addWidget(self.download_text)

        self.download_container = QWidget(self.download_data_box)
        self.download_container.setObjectName(u"download_container")
        self.download_container.setStyleSheet(u"* {\n"
"font-family : \"Comfortaa\"; \n"
"font-weight : Bold;\n"
"}")
        self.horizontalLayout_16 = QHBoxLayout(self.download_container)
        self.horizontalLayout_16.setSpacing(12)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.download_option_container = QWidget(self.download_container)
        self.download_option_container.setObjectName(u"download_option_container")
        self.horizontalLayout_18 = QHBoxLayout(self.download_option_container)
        self.horizontalLayout_18.setSpacing(12)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.download_options = QWidget(self.download_option_container)
        self.download_options.setObjectName(u"download_options")
        self.download_options.setStyleSheet(u"* {\n"
"color : #777785; \n"
"}\n"
"")
        self.horizontalLayout_19 = QHBoxLayout(self.download_options)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.ts_data = QWidget(self.download_options)
        self.ts_data.setObjectName(u"ts_data")
        self.verticalLayout_29 = QVBoxLayout(self.ts_data)
        self.verticalLayout_29.setObjectName(u"verticalLayout_29")
        self.verticalLayout_29.setContentsMargins(0, 0, 0, 0)
        self.bea = QCheckBox(self.ts_data)
        self.bea.setObjectName(u"bea")
        self.bea.setEnabled(True)
        self.bea.setCheckable(True)

        self.verticalLayout_29.addWidget(self.bea)

        self.yf = QCheckBox(self.ts_data)
        self.yf.setObjectName(u"yf")
        self.yf.setEnabled(True)
        self.yf.setCheckable(True)

        self.verticalLayout_29.addWidget(self.yf)

        self.fred = QCheckBox(self.ts_data)
        self.fred.setObjectName(u"fred")
        self.fred.setEnabled(True)
        self.fred.setCheckable(True)

        self.verticalLayout_29.addWidget(self.fred)

        self.bls = QCheckBox(self.ts_data)
        self.bls.setObjectName(u"bls")
        self.bls.setEnabled(True)
        self.bls.setCheckable(True)

        self.verticalLayout_29.addWidget(self.bls)

        self.te = QCheckBox(self.ts_data)
        self.te.setObjectName(u"te")
        self.te.setEnabled(True)
        self.te.setCheckable(True)

        self.verticalLayout_29.addWidget(self.te)


        self.horizontalLayout_19.addWidget(self.ts_data)

        self.cs_data = QWidget(self.download_options)
        self.cs_data.setObjectName(u"cs_data")
        self.verticalLayout_31 = QVBoxLayout(self.cs_data)
        self.verticalLayout_31.setObjectName(u"verticalLayout_31")
        self.verticalLayout_31.setContentsMargins(0, 0, 0, 0)
        self.ism = QCheckBox(self.cs_data)
        self.ism.setObjectName(u"ism")
        self.ism.setEnabled(False)
        self.ism.setCheckable(True)

        self.verticalLayout_31.addWidget(self.ism)

        self.fw = QCheckBox(self.cs_data)
        self.fw.setObjectName(u"fw")
        self.fw.setEnabled(False)
        self.fw.setCheckable(True)

        self.verticalLayout_31.addWidget(self.fw)

        self.dfm = QCheckBox(self.cs_data)
        self.dfm.setObjectName(u"dfm")
        self.dfm.setEnabled(False)
        self.dfm.setCheckable(True)

        self.verticalLayout_31.addWidget(self.dfm)

        self.nyf = QCheckBox(self.cs_data)
        self.nyf.setObjectName(u"nyf")
        self.nyf.setEnabled(False)
        self.nyf.setCheckable(True)

        self.verticalLayout_31.addWidget(self.nyf)

        self.cin = QCheckBox(self.cs_data)
        self.cin.setObjectName(u"cin")
        self.cin.setEnabled(False)
        self.cin.setCheckable(True)

        self.verticalLayout_31.addWidget(self.cin)

        self.em = QCheckBox(self.cs_data)
        self.em.setObjectName(u"em")
        self.em.setEnabled(False)
        self.em.setCheckable(True)
        self.em.setChecked(False)

        self.verticalLayout_31.addWidget(self.em)

        self.fs = QCheckBox(self.cs_data)
        self.fs.setObjectName(u"fs")
        self.fs.setEnabled(False)
        self.fs.setCheckable(True)

        self.verticalLayout_31.addWidget(self.fs)


        self.horizontalLayout_19.addWidget(self.cs_data)


        self.horizontalLayout_18.addWidget(self.download_options)

        self.line = QFrame(self.download_option_container)
        self.line.setObjectName(u"line")
        self.line.setStyleSheet(u"")
        self.line.setFrameShadow(QFrame.Shadow.Plain)
        self.line.setLineWidth(1)
        self.line.setMidLineWidth(0)
        self.line.setFrameShape(QFrame.Shape.VLine)

        self.horizontalLayout_18.addWidget(self.line)

        self.download_confirm_container = QWidget(self.download_option_container)
        self.download_confirm_container.setObjectName(u"download_confirm_container")
        self.download_confirm_container.setStyleSheet(u"color : white; ")
        self.verticalLayout_32 = QVBoxLayout(self.download_confirm_container)
        self.verticalLayout_32.setSpacing(12)
        self.verticalLayout_32.setObjectName(u"verticalLayout_32")
        self.verticalLayout_32.setContentsMargins(0, 0, 0, 0)
        self.year_selection = QWidget(self.download_confirm_container)
        self.year_selection.setObjectName(u"year_selection")
        self.year_selection.setMaximumSize(QSize(16777215, 35))
        self.horizontalLayout_12 = QHBoxLayout(self.year_selection)
        self.horizontalLayout_12.setSpacing(6)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label = QLabel(self.year_selection)
        self.label.setObjectName(u"label")

        self.horizontalLayout_12.addWidget(self.label)

        self.int_year_spinbox = QSpinBox(self.year_selection)
        self.int_year_spinbox.setObjectName(u"int_year_spinbox")
        self.int_year_spinbox.setMinimumSize(QSize(0, 17))
        self.int_year_spinbox.setMaximumSize(QSize(16777215, 17))
        self.int_year_spinbox.setMinimum(2020)
        self.int_year_spinbox.setMaximum(2025)

        self.horizontalLayout_12.addWidget(self.int_year_spinbox)


        self.verticalLayout_32.addWidget(self.year_selection)

        self.download_csv_check = QCheckBox(self.download_confirm_container)
        self.download_csv_check.setObjectName(u"download_csv_check")

        self.verticalLayout_32.addWidget(self.download_csv_check)

        self.download_for_all_check = QCheckBox(self.download_confirm_container)
        self.download_for_all_check.setObjectName(u"download_for_all_check")
        self.download_for_all_check.setChecked(True)

        self.verticalLayout_32.addWidget(self.download_for_all_check)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_32.addItem(self.verticalSpacer_5)

        self.download_btn_container = QWidget(self.download_confirm_container)
        self.download_btn_container.setObjectName(u"download_btn_container")
        self.download_btn_container.setMinimumSize(QSize(0, 130))
        self.download_btn_container.setStyleSheet(u"QPushButton {\n"
"	min-height : 30px;\n"
"	border-radius : 9px\n"
"}\n"
"\n"
"/*download*/\n"
"QPushButton#download_btn {\n"
"	background : #202023;\n"
"}\n"
"QPushButton#download_btn::hover {\n"
"	background : #353542;\n"
"}\n"
"QPushButton#download_btn::pressed {\n"
"	background : #202023;\n"
"}\n"
"\n"
"\n"
"/*cancel*/\n"
"QPushButton#cancel_btn {\n"
"	background-color:#EE5C88;\n"
"	color : #252526;\n"
"}\n"
"QPushButton#cancel_btn::hover {\n"
"	background : #fa88aa;\n"
"}\n"
"QPushButton#cancel_btn::pressed {\n"
"	background : #EE5C88;\n"
"}\n"
"\n"
"\n"
"/*clear lags*/\n"
"QPushButton#clear_log_btn {\n"
"	background-color:#EE5C88;\n"
"	color : #252526;\n"
"}\n"
"QPushButton#clear_log_btn::hover {\n"
"	background : #fa88aa;\n"
"}\n"
"QPushButton#clear_log_btn::pressed {\n"
"	background : #EE5C88;\n"
"}")
        self.verticalLayout_27 = QVBoxLayout(self.download_btn_container)
        self.verticalLayout_27.setSpacing(12)
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.download_btn = QPushButton(self.download_btn_container)
        self.download_btn.setObjectName(u"download_btn")
        self.download_btn.setFont(font5)

        self.verticalLayout_27.addWidget(self.download_btn)

        self.cancel_btn = QPushButton(self.download_btn_container)
        self.cancel_btn.setObjectName(u"cancel_btn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setFont(font5)
        self.cancel_btn.setStyleSheet(u"")

        self.verticalLayout_27.addWidget(self.cancel_btn)

        self.clear_log_btn = QPushButton(self.download_btn_container)
        self.clear_log_btn.setObjectName(u"clear_log_btn")
        self.clear_log_btn.setFont(font5)
        self.clear_log_btn.setStyleSheet(u"")

        self.verticalLayout_27.addWidget(self.clear_log_btn)


        self.verticalLayout_32.addWidget(self.download_btn_container)

        self.parallel_opts_container = QWidget(self.download_confirm_container)
        self.parallel_opts_container.setObjectName(u"parallel_opts_container")
        self.horizontalLayout_parallel = QHBoxLayout(self.parallel_opts_container)
        self.horizontalLayout_parallel.setSpacing(8)
        self.horizontalLayout_parallel.setObjectName(u"horizontalLayout_parallel")
        self.horizontalLayout_parallel.setContentsMargins(0, 0, 0, 0)
        self.parallel_download_check = QCheckBox(self.parallel_opts_container)
        self.parallel_download_check.setObjectName(u"parallel_download_check")
        self.parallel_download_check.setChecked(True)

        self.horizontalLayout_parallel.addWidget(self.parallel_download_check)

        self.max_threads_label = QLabel(self.parallel_opts_container)
        self.max_threads_label.setObjectName(u"max_threads_label")

        self.horizontalLayout_parallel.addWidget(self.max_threads_label)

        self.max_threads_spin = QSpinBox(self.parallel_opts_container)
        self.max_threads_spin.setObjectName(u"max_threads_spin")
        self.max_threads_spin.setMinimumSize(QSize(40, 17))
        self.max_threads_spin.setMaximumSize(QSize(40, 17))
        self.max_threads_spin.setMinimum(1)
        self.max_threads_spin.setMaximum(8)
        self.max_threads_spin.setValue(4)

        self.horizontalLayout_parallel.addWidget(self.max_threads_spin)


        self.verticalLayout_32.addWidget(self.parallel_opts_container)


        self.horizontalLayout_18.addWidget(self.download_confirm_container)


        self.horizontalLayout_16.addWidget(self.download_option_container)

        self.consolecontainer = QWidget(self.download_container)
        self.consolecontainer.setObjectName(u"consolecontainer")
        self.consolecontainer.setMinimumSize(QSize(400, 0))
        self.consolecontainer.setStyleSheet(u"* {\n"
"border-radius : 20px; background :#202023; \n"
"}\n"
"")
        self.verticalLayout_30 = QVBoxLayout(self.consolecontainer)
        self.verticalLayout_30.setObjectName(u"verticalLayout_30")
        self.verticalLayout_30.setContentsMargins(13, 13, 13, 13)
        self.console_text = QLabel(self.consolecontainer)
        self.console_text.setObjectName(u"console_text")
        self.console_text.setStyleSheet(u"color:white; \n"
"font-family : \"Comfortaa\"; \n"
"font-weight : bold;\n"
"margin-left: 1px;")
        self.console_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_30.addWidget(self.console_text)

        self.console_area = QTextEdit(self.consolecontainer)
        self.console_area.setObjectName(u"console_area")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.console_area.sizePolicy().hasHeightForWidth())
        self.console_area.setSizePolicy(sizePolicy1)
        self.console_area.setStyleSheet(u"color:white; \n"
"font-famlily:\"Comfortaa\";\n"
"border :0;\n"
"background:transparent;\n"
"padding :5px;\n"
"")
        self.console_area.setReadOnly(True)

        self.verticalLayout_30.addWidget(self.console_area)


        self.horizontalLayout_16.addWidget(self.consolecontainer)


        self.verticalLayout_28.addWidget(self.download_container)


        self.verticalLayout_20.addWidget(self.download_data_box)


        self.verticalLayout_19.addWidget(self.group_box_container)

        self.stackedWidget.addWidget(self.page_settings_container)

        self.verticalLayout_2.addWidget(self.stackedWidget)

        self.author_name_and_time = QLabel(self.frame)
        self.author_name_and_time.setObjectName(u"author_name_and_time")
        self.author_name_and_time.setMaximumSize(QSize(16777215, 16777215))
        self.author_name_and_time.setFont(font2)
        self.author_name_and_time.setStyleSheet(u"color:#90b6e7;\n"
"font-family:\"Comfortaa\";\n"
"padding:3px;\n"
"border: 0;\n"
"font-size:10px;")
        self.author_name_and_time.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_2.addWidget(self.author_name_and_time)


        self.horizontalLayout.addWidget(self.frame)


        self.verticalLayout_33.addWidget(self.self_sized_main_widget)

        MainWindow.setCentralWidget(self.style_sheet)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Macro Dashboard", None))
        self.title_text.setText(QCoreApplication.translate("MainWindow", u"Macro Dashboard", None))
        self.minimize_btn.setText("")
        self.window_btn.setText("")
        self.close_btn.setText("")
#if QT_CONFIG(tooltip)
        self.one_page_btn.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.one_page_btn.setText("")
#if QT_CONFIG(tooltip)
        self.four_page_btn.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.four_page_btn.setText("")
#if QT_CONFIG(tooltip)
        self.table_btn.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.table_btn.setText("")
#if QT_CONFIG(tooltip)
        self.note_btn.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.note_btn.setText("")
#if QT_CONFIG(tooltip)
        self.settings_btn.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.settings_btn.setText("")
        self.title_label_2.setText(QCoreApplication.translate("MainWindow", u"Data name will be here", None))
        self.update_label_2.setText(QCoreApplication.translate("MainWindow", u"Recent Update Time : ", None))
        self.one_set_preference.setText("")
        self.table_title_label.setText(QCoreApplication.translate("MainWindow", u"Table : Selected Table Name", None))
        self.table_update_label.setText(QCoreApplication.translate("MainWindow", u"Recent Update Time : ", None))
        self.page_table_set_preference.setText("")
        self.four_title_label.setText(QCoreApplication.translate("MainWindow", u"Four Charts Interface", None))
        self.four_update_label.setText(QCoreApplication.translate("MainWindow", u"Recent Update Time : ", None))
        self.connect_charts.setText(QCoreApplication.translate("MainWindow", u" Connect Charts", None))
        self.four_settings_button.setText("")
#if QT_CONFIG(tooltip)
        self.note_list_text_container.setToolTip(QCoreApplication.translate("MainWindow", u"Feel free to write notes here ~", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.four_title_label_3.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.four_title_label_3.setText(QCoreApplication.translate("MainWindow", u"Feel Free to Write Notes", None))
        self.four_update_label_3.setText(QCoreApplication.translate("MainWindow", u"a place where store thoughts, or feelings", None))
        self.note_instructions_btn.setText(QCoreApplication.translate("MainWindow", u"Users Instructions", None))
        self.note_status_bar.setText(QCoreApplication.translate("MainWindow", u"Enter file name then click button", None))
        self.note_add_btn.setText("")
        self.note_rename_btn.setText("")
        self.note_delete_btn.setText("")
        self.note_title_label.setText(QCoreApplication.translate("MainWindow", u"Notes Editor", None))
        self.note_update_label.setText(QCoreApplication.translate("MainWindow", u"Current file name : [Read Only] Notes Editor Instructions", None))
#if QT_CONFIG(tooltip)
        self.save_text.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.save_text.setText("")
        self.note_label_notes.setText(QCoreApplication.translate("MainWindow", u"Reminder : Please read instructions carefully.", None))
        self.plainTextEdit.setPlainText(QCoreApplication.translate("MainWindow", u"\u2605\u2605 \u8fd9\u662f\u4e00\u4e2aNotes Editor\u754c\u9762\u7684\u4f7f\u7528\u8bf4\u660e\uff0c\u8bf7\u4e0d\u8981\u5220\u9664\u6b64\u6587\u6863\u3002\u2605\u2605\n"
"	\n"
"        \u672c\u6587\u6863\u7f16\u8f91\u5668\u7684\u6587\u4ef6\u50a8\u5b58\u76ee\u5f55\u4e3a \u8f6f\u4ef6\u8def\u5f84/note\uff08\u5373\u4e3a\u8f6f\u4ef6\u76ee\u5f55\u5f53\u4e2d\u7684note\u6587\u4ef6\u5939\uff09\uff0c\u5982\u9700\u64cd\u4f5c\u8bf7\u81ea\u884c\u5230\u6587\u4ef6\u5939\u4e0b\u9762\u8fdb\u884c\u64cd\u4f5c\uff0c\u6ce8\u610f\u4e0d\u8981\u5728\u8f6f\u4ef6\u8fd0\u884c\u7684\u65f6\u5019\u64cd\u4f5c\u6587\u4ef6\u5939\u3002	\n"
"\n"
"        \u53f3\u4e0a\u89d2\u7684\u6309\u94ae\u662f\u4fdd\u5b58\u6309\u94ae\u3002\u8bf7\u52a1\u5fc5\u5728\u6bcf\u6b21\u5199\u5b8c\u6587\u7ae0\u540e\u70b9\u51fb\u4fdd\u5b58\u6309\u94ae\uff0c\u811a\u672c\u5c06\u4f1a\u8bc6\u522b\u4e2d\u95f4\u6587\u672c\u7f16\u8f91\u533a\u7684\u6587\u672c\u5e76\u4f20\u5165\u5bf9\u5e94\u7684txt\u6587\u4ef6\u5f53\u4e2d\u3002\uff08\u81ea\u52a8\u4fdd\u5b58\u529f\u80fd\u4f1a\u5728\u540e"
                        "\u7eed\u66f4\u65b0\u4e2d\u52a0\u5165\uff09\n"
"        \u5de6\u4e0b\u89d2\u6709\u4e09\u4e2a\u6309\u94ae\uff0c\u6309\u987a\u5e8f\u4f9d\u6b21\u662f\uff1a\n"
"                \u65b0\u5efa\u7b14\u8bb0\uff0c\u7b14\u8bb0\u91cd\u547d\u540d\uff0c\u5220\u9664\u7b14\u8bb0\u3002\n"
"\n"
"        -- \u65b0\u5efa\u7b14\u8bb0\uff1a\n"
"	1. \u5148\u5728\u6700\u4e0b\u65b9\u7684\u8f93\u5165\u6846\u5185\u8f93\u5165\u7b14\u8bb0\u7684\u540d\u79f0\uff0c\u6ce8\u610f\u8bf7\u4e0d\u8981\u5728\u540d\u79f0\u5185\u5305\u62ec\u7a7a\u683c\uff0c\u4ee5\u53ca \\ / : * ? \\\" < > | \u8fd9\u4e9b\u7cfb\u7edf\u9ed8\u8ba4\u4e0d\u5141\u8bb8\u4f5c\u4e3a\u6587\u4ef6\u540d\u79f0\u7684\u5b57\u7b26\u3002\n"
"	2. \u70b9\u51fb\u5de6\u4e0b\u89d2\u7684 \u65b0\u5efa\u7b14\u8bb0 \u6309\u94ae\uff0c\u5373\u53ef\u5728\u5de6\u8fb9Notes Editor\u8fb9\u680f\u91cc\u770b\u5230\u5bf9\u5e94\u7684\u6309\u94ae\uff0c\u70b9\u51fb\u6309\u94ae\u5373\u53ef\u8fdb\u5165\u6587\u6863\u7f16\u8f91\u3002\n"
"        -- \u7b14\u8bb0\u91cd\u547d\u540d\uff1a\n"
"	1. \u5148\u5728\u6700\u4e0b"
                        "\u65b9\u8f93\u5165\u60f3\u8981\u66f4\u6539\u7684\u7b14\u8bb0\u7684\u540d\u79f0\uff0c\u6ce8\u610f\u5927\u5c0f\u5199\uff0c\u811a\u672c\u4f1a\u5c1d\u8bd5\u5339\u914d\u5bf9\u5e94\u7684\u6309\u94ae\u3002\n"
"	2. \u5f53\u5339\u914d\u6210\u529f\u540e\uff0c\u5bf9\u5e94\u7684\u6309\u94ae\u4e0b\u65b9\u5c06\u5f39\u51fa\u65b0\u7684\u8f93\u5165\u6846\uff0c\u8bf7\u5728\u65b0\u7684\u8f93\u5165\u6846\u5f53\u4e2d\u8f93\u5165\u65b0\u7684\u6587\u4ef6\u540d\uff0c\u6ce8\u610f\u4e0d\u8981\u4e0e\u5176\u4ed6\u6587\u4ef6\u91cd\u540d\u6216\u5c1d\u8bd5\u8f93\u5165\u975e\u6cd5\u5b57\u7b26\u3002\uff08\u6b64\u65f6\u6587\u4ef6\u5939\u4e0b\u9762\u7684txt\u6587\u6863\u6ca1\u6709\u6539\u540d\uff09\n"
"	3. \u4fee\u6539\u5b8c\u6210\u540e\uff0c\u6309\u4efb\u610f\u952e\u6216\u8005\u70b9\u51fb\u754c\u9762\u5185\u7684\u4efb\u610f\u5730\u65b9\u5373\u53ef\u5b8c\u6210\u4fee\u6539\uff0c\u811a\u672c\u4f1a\u81ea\u52a8\u4fee\u6539\u6587\u4ef6\u5939\u76ee\u5f55\u4e0b\u9762\u7684txt\u6587\u6863\u3002\n"
"        -- \u5220\u9664\u7b14\u8bb0\uff1a\n"
"	1. \u5728"
                        "\u6700\u4e0b\u65b9\u7684\u8f93\u5165\u6846\u5185\u8f93\u5165\u60f3\u8981\u5220\u9664\u7684\u7b14\u8bb0\u7684\u540d\u79f0\u3002\n"
"	2. \u70b9\u51fb \u5220\u9664 \u6309\u94ae\u3002\uff08\u6ce8\u610f\u5220\u9664\u65f6\u4e0d\u4f1a\u5f39\u51fa\u518d\u6b21\u786e\u8ba4\u7a97\u53e3\u4e14\u6587\u4ef6\u65e0\u6cd5\u590d\u539f\uff0c\u8bf7\u8c28\u614e\u5220\u9664\uff09\n"
"\n"
"        \u7f16\u8f91\u6846\u76ee\u524d\u6682\u65f6\u4e0d\u652f\u6301\u63d2\u5165\u56fe\u7247\u548c\u7f16\u8f91\u5b57\u4f53\u6837\u5f0f\uff0c\u540e\u7eed\u4f1a\u9010\u6b65\u66f4\u65b0\u5185\u5bb9\u3002\n"
"        \u795d\u4f7f\u7528\u6109\u5feb\uff01(\u2220\u30fb\u03c9< )\u2312\u2605  Love from Kitazaki Hinata\n"
"\n"
"------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
"\n"
"\u2605\u2605 This is the usage guide for the Notes Editor interface. Please do not delete this document. \u2605\u2605 \n"
"\n"
"        The file storage directory o"
                        "f this document editor is \"software path/note\" (which is the \"note\" folder within the software directory). If you need to operate, please do it directly in the folder. Be careful not to operate the folder while the software is running. \n"
"        \n"
"        The button on the upper right corner is the save button. Please make sure to click the save button after each time you finish writing the article. The script will recognize the text in the middle text editing area and transfer it to the corresponding txt file. (The automatic save function will be added in the subsequent updates.)\n"
"        On the lower left corner, there are three buttons in sequence:\n"
"                New note, Rename note, Delete note. \n"
"\n"
"        -- Create a new note:\n"
"        1. First, enter the name of the note in the bottom input box. Please make sure not to include spaces, as well as characters such as \\ / : * ? \" < > | which are system-prohibited for use as file names.\n"
"        2. Click the \"Create Note\" "
                        "button at the bottom left corner, and you will see the corresponding button in the Notes Editor sidebar on the left. Click the button to enter the document editing mode.\n"
"\n"
"        -- Rename a note:\n"
"        1. Enter the name of the note you want to change in the bottom input box. Pay attention to the case. The script will try to match the corresponding button.\n"
"        2. Once the match is successful, a new input box will appear below the corresponding button. Please enter the new file name in the new input box. Be sure not to have the same name as other files or input illegal characters. (At this time, the txt document under the folder has not been renamed)\n"
"        3. After the modification is completed, press any key or click anywhere on the interface to complete the modification. The script will automatically modify the txt document under the folder directory.\n"
"        -- Delete a note:\n"
"        1. Enter the name of the note you want to delete in the bottom input box.\n"
"        2. C"
                        "lick the \"Delete\" button. (Note that no confirmation window will pop up when deleting and the file cannot be restored. Please be cautious when deleting) \n"
"\n"
"        The edit box currently does not support inserting images or editing font styles. Updates will be gradually released in the future.\n"
"        Enjoy your use! (\u2220\u00b7\u03c9< )\u2312\u2605 Love from Kitazaki Hinata", None))
        self.note_title_label_2.setText(QCoreApplication.translate("MainWindow", u"Settings Panel", None))
        self.note_update_label_2.setText(QCoreApplication.translate("MainWindow", u"Set API // Download Data // About & Terms", None))
        self.api_group_box.setTitle("")
        self.setting_page_notify_text.setText(QCoreApplication.translate("MainWindow", u"Enter API key here and click \"Save\" button to save API key", None))
        self.bea_label.setText(QCoreApplication.translate("MainWindow", u"BEA API key : ", None))
        self.fred_label.setText(QCoreApplication.translate("MainWindow", u"FRED API key :", None))
        self.bls_label.setText(QCoreApplication.translate("MainWindow", u"BLS API key :", None))
        self.api_save_btn.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.status_label.setText(QCoreApplication.translate("MainWindow", u"Status will be displayed here", None))
        self.other_group_box.setTitle("")
        self.other_option_text.setText(QCoreApplication.translate("MainWindow", u"About & Terms", None))
        self.basic_version_info_text.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Macro Dashboard </p><p>Version: 0.9.00_beta</p><p>Copyright (c) 2025 Kitazaki-Hinata</p><p><br/></p></body></html>", None))
        self.image_label.setText("")
        self.textEdit.setDocumentTitle("")
        self.textEdit.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Comfortaa'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Microsoft YaHei UI'; font-size:9pt; font-weight:700;\">This software is designed for educational and reference purposes only; commercial use, redistribution for profit and claiming as own product are prohibited. </span></p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span"
                        " style=\" font-family:'Microsoft YaHei UI'; font-size:9pt;\">The software provides a dashboard for macroeconomic data learning and analysis.</span></p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Microsoft YaHei UI'; font-size:9pt;\">The source code is open and available under the MIT-Non Commercial (MIT-NC) License terms.</span></p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Microsoft YaHei UI'; font-size:9pt;\">Some UI elements (SVG and PNG icons, components) are sourced from [FAWZIUIUX]\uff1afawziuiux.com/#Home.  All rights belong to the original author.</span></p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Microsoft YaHei UI"
                        "'; font-size:9pt;\">Special thanks to : SeaStar, yuyoux7</span></p></body></html>", None))
        self.read_and_agree_check.setText(QCoreApplication.translate("MainWindow", u"I have read and agree to the Terms and Conditions.", None))
        self.download_data_box.setTitle("")
        self.download_text.setText(QCoreApplication.translate("MainWindow", u"Select data resources and download data", None))
        self.bea.setText(QCoreApplication.translate("MainWindow", u"BEA data API", None))
        self.yf.setText(QCoreApplication.translate("MainWindow", u"Yfinance API", None))
        self.fred.setText(QCoreApplication.translate("MainWindow", u"FRED data API", None))
        self.bls.setText(QCoreApplication.translate("MainWindow", u"BLS data API", None))
        self.te.setText(QCoreApplication.translate("MainWindow", u"TE data", None))
        self.ism.setText(QCoreApplication.translate("MainWindow", u"ISM", None))
        self.fw.setText(QCoreApplication.translate("MainWindow", u"CME FedWatch", None))
        self.dfm.setText(QCoreApplication.translate("MainWindow", u"Dallas Fed Manu.", None))
        self.nyf.setText(QCoreApplication.translate("MainWindow", u"NewYork Fed", None))
        self.cin.setText(QCoreApplication.translate("MainWindow", u"Infla. Nowcasting", None))
        self.em.setText(QCoreApplication.translate("MainWindow", u"CME EminiFuture", None))
        self.fs.setText(QCoreApplication.translate("MainWindow", u"Forex Swap", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Data Start Year", None))
        self.download_csv_check.setText(QCoreApplication.translate("MainWindow", u"Download csv", None))
        self.download_for_all_check.setText(QCoreApplication.translate("MainWindow", u"Download ALL data", None))
        self.download_btn.setText(QCoreApplication.translate("MainWindow", u"Download", None))
        self.cancel_btn.setText(QCoreApplication.translate("MainWindow", u"Cancel Download", None))
        self.clear_log_btn.setText(QCoreApplication.translate("MainWindow", u"Clear logs", None))
        self.parallel_download_check.setText(QCoreApplication.translate("MainWindow", u"Enable parallel downloads", None))
        self.max_threads_label.setText(QCoreApplication.translate("MainWindow", u"Max threads", None))
        self.console_text.setText(QCoreApplication.translate("MainWindow", u"Console & Logging Information", None))
        self.console_area.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Comfortaa'; font-size:9pt; font-weight:700; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.author_name_and_time.setText(QCoreApplication.translate("MainWindow", u"Love from : Kitazaki Hinata", None))
    # retranslateUi

