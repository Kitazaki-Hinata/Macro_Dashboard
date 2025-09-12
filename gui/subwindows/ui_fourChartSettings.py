# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_fourChartSettings.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)
import gui.subwindows.sub_resources_rc

class Ui_FourChartSettingsPanel(object):
    def setupUi(self, FourChartSettingsPanel):
        if not FourChartSettingsPanel.objectName():
            FourChartSettingsPanel.setObjectName(u"FourChartSettingsPanel")
        FourChartSettingsPanel.resize(575, 350)
        FourChartSettingsPanel.setMinimumSize(QSize(575, 350))
        FourChartSettingsPanel.setMaximumSize(QSize(575, 350))
        FourChartSettingsPanel.setStyleSheet(u"* {\n"
"background : #262a2f;\n"
"}\n"
"\n"
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
"            subcontrol-position: top right;\n"
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
"         "
                        "   subcontrol-origin: border;\n"
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
"        ")
        self.verticalLayout = QVBoxLayout(FourChartSettingsPanel)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.top_name_bar = QWidget(FourChartSettingsPanel)
        self.top_name_bar.setObjectName(u"top_name_bar")
        self.top_name_bar.setMaximumSize(QSize(16777215, 50))
        self.top_name_bar.setStyleSheet(u"* {\n"
"	background : #252526;\n"
"	font-family : \"Comfortaa\";\n"
"	color : white;\n"
"	border-bottom : 2px solid #90b6e7;\n"
"	font-weight : Bold;\n"
"}")
        self.verticalLayout_2 = QVBoxLayout(self.top_name_bar)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.top_name_bar)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setFamilies([u"Comfortaa"])
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setStyleSheet(u"border-bottom : 0 solid transparent;\n"
"padding-left : 3px;")

        self.verticalLayout_2.addWidget(self.label)


        self.verticalLayout.addWidget(self.top_name_bar)

        self.settings_panel = QWidget(FourChartSettingsPanel)
        self.settings_panel.setObjectName(u"settings_panel")
        self.settings_panel.setMaximumSize(QSize(16777215, 16777215))
        self.settings_panel.setStyleSheet(u"* {\n"
"color : white;\n"
"font-family : \"Comfortaa\";\n"
"font-weight : Bold;\n"
"}\n"
"\n"
"QComboBox {\n"
"        background-color: #33363a;\n"
"        border-radius : 2px;\n"
"	    max-height : 9px;\n"
"        border-bottom: 1px solid #90b6e7;\n"
"        padding: 5px;\n"
"    }\n"
"QComboBox:focus {\n"
"		background-color: #454555;\n"
"        border-bottom: 1px solid #ffffff;\n"
"    }\n"
"\n"
"")
        self.gridLayout = QGridLayout(self.settings_panel)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(15, -1, 15, -1)
        self.first_data_selection_box = QComboBox(self.settings_panel)
        self.first_data_selection_box.setObjectName(u"first_data_selection_box")
        self.first_data_selection_box.setEditable(True)
        self.first_data_selection_box.setMinimumContentsLength(0)

        self.gridLayout.addWidget(self.first_data_selection_box, 1, 1, 1, 1)

        self.second_color_btn = QPushButton(self.settings_panel)
        self.second_color_btn.setObjectName(u"second_color_btn")
        self.second_color_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.second_color_btn.setStyleSheet(u"background : #90b6e7")

        self.gridLayout.addWidget(self.second_color_btn, 2, 2, 1, 1)

        self.third_data_selection_box = QComboBox(self.settings_panel)
        self.third_data_selection_box.setObjectName(u"third_data_selection_box")
        self.third_data_selection_box.setEditable(True)

        self.gridLayout.addWidget(self.third_data_selection_box, 3, 1, 1, 1)

        self.fourth_data_selection_box = QComboBox(self.settings_panel)
        self.fourth_data_selection_box.setObjectName(u"fourth_data_selection_box")

        self.gridLayout.addWidget(self.fourth_data_selection_box, 4, 1, 1, 1)

        self.third_color_btn = QPushButton(self.settings_panel)
        self.third_color_btn.setObjectName(u"third_color_btn")
        self.third_color_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.third_color_btn.setStyleSheet(u"background : #90b6e7")

        self.gridLayout.addWidget(self.third_color_btn, 3, 2, 1, 1)

        self.first_data_title = QLabel(self.settings_panel)
        self.first_data_title.setObjectName(u"first_data_title")
        self.first_data_title.setMaximumSize(QSize(120, 16777215))

        self.gridLayout.addWidget(self.first_data_title, 1, 0, 1, 1)

        self.second_data_selection_box = QComboBox(self.settings_panel)
        self.second_data_selection_box.setObjectName(u"second_data_selection_box")
        self.second_data_selection_box.setEditable(True)

        self.gridLayout.addWidget(self.second_data_selection_box, 2, 1, 1, 1)

        self.line_color_title = QLabel(self.settings_panel)
        self.line_color_title.setObjectName(u"line_color_title")
        self.line_color_title.setMaximumSize(QSize(40, 16777215))
        self.line_color_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.line_color_title, 0, 2, 1, 1)

        self.third_data_title = QLabel(self.settings_panel)
        self.third_data_title.setObjectName(u"third_data_title")

        self.gridLayout.addWidget(self.third_data_title, 3, 0, 1, 1)

        self.widget = QWidget(self.settings_panel)
        self.widget.setObjectName(u"widget")

        self.gridLayout.addWidget(self.widget, 5, 1, 1, 1)

        self.second_data_title = QLabel(self.settings_panel)
        self.second_data_title.setObjectName(u"second_data_title")

        self.gridLayout.addWidget(self.second_data_title, 2, 0, 1, 1)

        self.first_color_btn = QPushButton(self.settings_panel)
        self.first_color_btn.setObjectName(u"first_color_btn")
        self.first_color_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.first_color_btn.setStyleSheet(u"background : #90b6e7")

        self.gridLayout.addWidget(self.first_color_btn, 1, 2, 1, 1)

        self.data_name_title = QLabel(self.settings_panel)
        self.data_name_title.setObjectName(u"data_name_title")
        self.data_name_title.setMaximumSize(QSize(16777215, 40))
        self.data_name_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.data_name_title, 0, 1, 1, 1)

        self.fourth_data_title = QLabel(self.settings_panel)
        self.fourth_data_title.setObjectName(u"fourth_data_title")

        self.gridLayout.addWidget(self.fourth_data_title, 4, 0, 1, 1)

        self.fourth_color_btn = QPushButton(self.settings_panel)
        self.fourth_color_btn.setObjectName(u"fourth_color_btn")
        self.fourth_color_btn.setStyleSheet(u"background : #90b6e7")

        self.gridLayout.addWidget(self.fourth_color_btn, 4, 2, 1, 1)


        self.verticalLayout.addWidget(self.settings_panel)

        self.ctrl_btn_container = QWidget(FourChartSettingsPanel)
        self.ctrl_btn_container.setObjectName(u"ctrl_btn_container")
        self.ctrl_btn_container.setMaximumSize(QSize(16777215, 40))
        self.ctrl_btn_container.setStyleSheet(u"QPushButton {\n"
"    background-position: center;\n"
"    background-repeat: no-repeat;\n"
"	background : #2a2f39;\n"
"	border-radius : 8px;\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"	background : #252526;\n"
"	margin :0;\n"
"}\n"
"QPushButton:pressed{\n"
"	background-color : #2a2f39;\n"
"	margin :0;\n"
"}\n"
"\n"
"\n"
"/*\u56fe\u7247\u6837\u5f0f*/\n"
"QPushButton#finish_btn {\n"
"    icon: url(:/png/sub_resource/accept.png);\n"
"    icon-size: 20px 20px;\n"
"}\n"
"QPushButton#cancel_btn {\n"
"    icon: url(:/png/sub_resource/cancel.png);\n"
"    icon-size: 20px 20px;\n"
"}\n"
"\n"
"")
        self.horizontalLayout = QHBoxLayout(self.ctrl_btn_container)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 15, 0)
        self.horizontalSpacer = QSpacerItem(495, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cancel_btn = QPushButton(self.ctrl_btn_container)
        self.cancel_btn.setObjectName(u"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(25, 25))
        self.cancel_btn.setMaximumSize(QSize(25, 25))

        self.horizontalLayout.addWidget(self.cancel_btn)

        self.finish_btn = QPushButton(self.ctrl_btn_container)
        self.finish_btn.setObjectName(u"finish_btn")
        self.finish_btn.setMinimumSize(QSize(25, 25))
        self.finish_btn.setMaximumSize(QSize(25, 25))

        self.horizontalLayout.addWidget(self.finish_btn)


        self.verticalLayout.addWidget(self.ctrl_btn_container)


        self.retranslateUi(FourChartSettingsPanel)

        QMetaObject.connectSlotsByName(FourChartSettingsPanel)
    # setupUi

    def retranslateUi(self, FourChartSettingsPanel):
        FourChartSettingsPanel.setWindowTitle(QCoreApplication.translate("FourChartSettingsPanel", u"Settings", None))
        self.label.setText(QCoreApplication.translate("FourChartSettingsPanel", u"Data Selection and Settings", None))
        self.second_color_btn.setText("")
        self.third_color_btn.setText("")
        self.first_data_title.setText(QCoreApplication.translate("FourChartSettingsPanel", u"First Chart", None))
        self.line_color_title.setText(QCoreApplication.translate("FourChartSettingsPanel", u"Color", None))
        self.third_data_title.setText(QCoreApplication.translate("FourChartSettingsPanel", u"Third Chart", None))
        self.second_data_title.setText(QCoreApplication.translate("FourChartSettingsPanel", u"Second Chart", None))
        self.first_color_btn.setText("")
        self.data_name_title.setText(QCoreApplication.translate("FourChartSettingsPanel", u"Data Name", None))
        self.fourth_data_title.setText(QCoreApplication.translate("FourChartSettingsPanel", u"Fourth Chart", None))
        self.fourth_color_btn.setText("")
        self.cancel_btn.setText("")
        self.finish_btn.setText("")
    # retranslateUi

