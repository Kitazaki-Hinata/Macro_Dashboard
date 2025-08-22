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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QStackedWidget, QTabWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(831, 472)
        MainWindow.setStyleSheet(u"background-color: #33363a;")
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
"	margin :0;\n"
"	border :0;\n"
"}\n"
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
        self.one_page_btn.setStyleSheet(u"background-image: url(./assets/svg/one.svg);\n"
"background-position : center;\n"
"background-repeat : no-repeat;")

        self.left_up_four_frame.addWidget(self.one_page_btn)

        self.four_page_btn = QPushButton(self.left_box_frame)
        self.four_page_btn.setObjectName(u"four_page_btn")
        self.four_page_btn.setMinimumSize(QSize(0, 40))
        self.four_page_btn.setMaximumSize(QSize(70, 40))
        self.four_page_btn.setStyleSheet(u"background-image: url(./assets/svg/four.svg);\n"
"background-position : center;\n"
"background-repeat : no-repeat;")

        self.left_up_four_frame.addWidget(self.four_page_btn)

        self.table_btn = QPushButton(self.left_box_frame)
        self.table_btn.setObjectName(u"table_btn")
        self.table_btn.setMinimumSize(QSize(0, 40))
        self.table_btn.setMaximumSize(QSize(60, 40))
        self.table_btn.setStyleSheet(u"background-image: url(./assets/svg/table.svg);\n"
"background-position : center;\n"
"background-repeat : no-repeat;")

        self.left_up_four_frame.addWidget(self.table_btn)

        self.note_btn = QPushButton(self.left_box_frame)
        self.note_btn.setObjectName(u"note_btn")
        self.note_btn.setMinimumSize(QSize(60, 40))
        self.note_btn.setMaximumSize(QSize(60, 40))
        self.note_btn.setStyleSheet(u"background-image: url(./assets/svg/notebtn2.svg);\n"
"background-position : center;\n"
"background-repeat : no-repeat;\n"
"")

        self.left_up_four_frame.addWidget(self.note_btn)

        self.vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.left_up_four_frame.addItem(self.vertical_spacer)

        self.settings = QPushButton(self.left_box_frame)
        self.settings.setObjectName(u"settings")
        self.settings.setMinimumSize(QSize(0, 40))
        self.settings.setMaximumSize(QSize(70, 40))
        self.settings.setStyleSheet(u"background-image: url(./assets/svg/settings.svg);\n"
"background-position : center;\n"
"background-repeat : no-repeat;\n"
"")

        self.left_up_four_frame.addWidget(self.settings)

        self.verticalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.left_up_four_frame.addItem(self.verticalSpacer_2)

        self.four_page_btn.raise_()
        self.table_btn.raise_()
        self.note_btn.raise_()
        self.settings.raise_()
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
        self.tabWidget = QTabWidget(self.page_one_container)
        self.tabWidget.setObjectName(u"tabWidget")
        font = QFont()
        font.setFamilies([u"Comfortaa"])
        font.setBold(True)
        self.tabWidget.setFont(font)
        self.tabWidget.setStyleSheet(u"* {\n"
"	background-color : #33363a;\n"
"	font-family : \"Comfortaa\";\n"
"	border : 0;\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"    background-color: #2a2f39;\n"
"	color: #90b6e7;\n"
"    padding: 6px 12px;\n"
"	border-radius : 10px;\n"
"}\n"
"\n"
"QTabBar::tab:hover {\n"
"    background-color: #90b6e7;\n"
"    color: #252526;\n"
"	border-radius : 0;\n"
"	border-radius : 10px;\n"
"}\n"
"\n"
"QTabWidget::pane{\n"
"	\n"
"}")
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.North)
        self.tabWidget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabWidget.setIconSize(QSize(30, 10))
        self.tabWidget.setElideMode(Qt.TextElideMode.ElideNone)
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabBarAutoHide(False)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget.addTab(self.tab_2, "")

        self.verticalLayout_4.addWidget(self.tabWidget)

        self.stackedWidget.addWidget(self.page_one_container)
        self.page_four_container = QWidget()
        self.page_four_container.setObjectName(u"page_four_container")
        self.verticalLayout_3 = QVBoxLayout(self.page_four_container)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
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

        self.stackedWidget.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Macro Data Dashboard", None))
        self.one_page_btn.setText("")
        self.four_page_btn.setText("")
        self.table_btn.setText("")
        self.note_btn.setText("")
        self.settings.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Tab Box 1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Tab 2", None))
        self.author_name.setText(QCoreApplication.translate("MainWindow", u"Love from : Kitazaki Hinata", None))
    # retranslateUi

