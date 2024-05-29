# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'item.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class Ui_Item(object):
    def setupUi(self, Item):
        if not Item.objectName():
            Item.setObjectName(u"Item")
        Item.resize(329, 65)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Item.sizePolicy().hasHeightForWidth())
        Item.setSizePolicy(sizePolicy)
        Item.setMinimumSize(QSize(0, 65))
        self.verticalLayout = QVBoxLayout(Item)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.background = ClickBubblingGroupBox(Item)
        self.background.setObjectName(u"background")
        self.horizontalLayout = QHBoxLayout(self.background)
        self.horizontalLayout.setSpacing(8)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 2, 10, 2)
        self.light = QLabel(self.background)
        self.light.setObjectName(u"light")
        self.light.setPixmap(QPixmap(u":/res/empty_bullet.png"))

        self.horizontalLayout.addWidget(self.light)

        self.thumbnail = ThumbnailLabel(self.background)
        self.thumbnail.setObjectName(u"thumbnail")
        self.thumbnail.setMinimumSize(QSize(70, 25))
        self.thumbnail.setMaximumSize(QSize(60, 40))
        self.thumbnail.setPixmap(QPixmap(u":/res/no_thumb.png"))
        self.thumbnail.setScaledContents(False)
        self.thumbnail.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.thumbnail)

        self.details = QLabel(self.background)
        self.details.setObjectName(u"details")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.details.sizePolicy().hasHeightForWidth())
        self.details.setSizePolicy(sizePolicy1)
        self.details.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.details.setWordWrap(True)

        self.horizontalLayout.addWidget(self.details)

        self.btn_find_node = QPushButton(self.background)
        self.btn_find_node.setObjectName(u"btn_find_node")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.btn_find_node.sizePolicy().hasHeightForWidth())
        self.btn_find_node.setSizePolicy(sizePolicy2)
        self.btn_find_node.setMaximumSize(QSize(40, 28))
        self.btn_find_node.setIconSize(QSize(18, 18))

        self.horizontalLayout.addWidget(self.btn_find_node)


        self.verticalLayout.addWidget(self.background)


        self.retranslateUi(Item)

        QMetaObject.connectSlotsByName(Item)
    # setupUi

    def retranslateUi(self, Item):
        Item.setWindowTitle(QCoreApplication.translate("Item", u"Form", None))
        self.background.setTitle("")
        self.light.setText("")
        self.thumbnail.setText("")
        self.details.setText(QCoreApplication.translate("Item", u"content", None))
        self.btn_find_node.setText(QCoreApplication.translate("Item", u"find", None))
    # retranslateUi

from .clickbubbling_groupbox import ClickBubblingGroupBox
from .thumbnail_label import ThumbnailLabel
from . import resources_rc
