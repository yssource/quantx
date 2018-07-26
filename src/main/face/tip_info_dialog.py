
# -*- coding: utf-8 -*-

# Copyright (c) 2018-2018 the QuantX authors
# All rights reserved.
#
# The project sponsor and lead author is Xu Rendong.
# E-mail: xrd@ustc.edu, QQ: 277195007, WeChat: ustc_xrd
# See the contributors file for names of other contributors.
#
# Commercial use of this code in source and binary forms is
# governed by a LGPL v3 license. You may get a copy from the
# root directory. Or else you should get a specific written 
# permission from the project author.
#
# Individual and educational use of this code in source and
# binary forms is governed by a 3-clause BSD license. You may
# get a copy from the root directory. Certainly welcome you
# to contribute code of all sorts.
#
# Be sure to retain the above copyright notice and conditions.

from pubsub import pub
from PyQt5.QtGui import QFont, QTextOption
from PyQt5.QtCore import QPoint, QRect, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QDialog, QDialogButtonBox, QSizePolicy, QSpacerItem, QTextEdit, QWidget, QVBoxLayout

class TipInfoDialog(QDialog):
    def __init__(self, parent):
        super(TipInfoDialog, self).__init__(parent)
        self.parent = parent
        self.is_show = False
        self.point = QPoint()
        self.InitUserInterface()

    def __del__(self):
        pass

    def InitUserInterface(self):
        win_size_x = 395
        win_size_y = 90 # 两行文字，110 三行文字
        self.resize(win_size_x, win_size_y)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        
        self.widget = QWidget()
        self.widget.setGeometry(QRect(0, 0, win_size_x, win_size_y))
        
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("SimSun", 10))
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.text_edit.document().setDefaultTextOption(QTextOption(Qt.AlignCenter))
        
        self.button_box = QDialogButtonBox(self.widget)
        self.button_box.setStandardButtons(QDialogButtonBox.Ok)
        self.button_box.button(QDialogButtonBox.Ok).setText("已  阅")
        self.button_box.setCenterButtons(True)
        self.button_box.accepted.connect(self.OnButtonClose)
        
        self.v_box = QVBoxLayout()
        self.v_box.setContentsMargins(5, 5, 5, 5)
        self.spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.v_box.addWidget(self.text_edit)
        self.v_box.addItem(self.spacer)
        self.v_box.addWidget(self.button_box)
        self.setLayout(self.v_box)
        
        self.timer_show = QTimer()
        self.timer_stay = QTimer()
        self.timer_hide = QTimer()
        
        self.timer_show.timeout.connect(self.OnTimerShow)
        self.timer_stay.timeout.connect(self.OnTimerStay)
        self.timer_hide.timeout.connect(self.OnTimerHide)
        
        pub.subscribe(self.OnTipInfoMessage, "tip.info.message")

    def OnTipInfoMessage(self, msg):
        self.ShowMessage(msg)

    def ShowMessage(self, msg):
        if self.is_show == True:
            self.OnButtonClose()
        
        self.rect_desktop = QApplication.desktop().availableGeometry()
        self.desktop_height = self.rect_desktop.height()
        self.point.setX(self.rect_desktop.width() - self.width())
        self.point.setY(self.rect_desktop.height() - self.height())
        
        self.move(self.point.x(), self.desktop_height)
        
        self.text_edit.clear()
        self.text_edit.append(msg)
        
        self.transparent = 0.9
        self.setWindowOpacity(self.transparent)
        
        self.show()
        
        self.is_show = True
        
        self.timer_show.start(10)

    def OnTimerShow(self):
        self.desktop_height -= 1
        self.move(self.point.x(), self.desktop_height)
        if self.desktop_height <= self.point.y():
            self.timer_show.stop()
            self.timer_stay.start(8000)

    def OnTimerStay(self):
        self.timer_stay.stop()
        self.timer_hide.start(100)

    def OnTimerHide(self):
        self.transparent -= 0.05
        if self.transparent <= 0.0:
            self.timer_hide.stop()
            self.is_show = False
            self.close()
        else:
            self.setWindowOpacity(self.transparent)

    def OnButtonClose(self):
        self.timer_show.stop()
        self.timer_stay.stop()
        self.timer_hide.stop()
        self.is_show = False
        self.close()
