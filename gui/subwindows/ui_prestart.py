# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_prestart.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QSizePolicy, QWidget)
import gui.subwindows.sub_resources_rc

class Ui_Prestart_ui(object):
    def setupUi(self, Prestart_ui):
        if not Prestart_ui.objectName():
            Prestart_ui.setObjectName(u"Prestart_ui")
        Prestart_ui.setEnabled(True)
        Prestart_ui.resize(550, 300)
        self.horizontalLayout = QHBoxLayout(Prestart_ui)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(Prestart_ui)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(550, 300))
        self.widget.setMaximumSize(QSize(550, 300))
        self.widget.setStyleSheet(u"image: url(:/png/sub_resource/prestart.png);")

        self.horizontalLayout.addWidget(self.widget)


        self.retranslateUi(Prestart_ui)

        QMetaObject.connectSlotsByName(Prestart_ui)
    # setupUi

    def retranslateUi(self, Prestart_ui):
        Prestart_ui.setWindowTitle(QCoreApplication.translate("Prestart_ui", u"Prestart_ui", None))
    # retranslateUi

