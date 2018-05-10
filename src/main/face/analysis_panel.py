
# -*- coding: utf-8 -*-

# Copyright (c) 2018-2018 the QuantX authors
# All rights reserved.
#
# The project sponsor and lead author is Xu Rendong.
# E-mail: xrd@ustc.edu, QQ: 277195007, WeChat: ustc_xrd
# You can get more information at https://xurendong.github.io
# For names of other contributors see the contributors file.
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

import time
import datetime
import operator
import threading
from datetime import datetime

from PyQt5.QtGui import QFont
from PyQt5.QtCore import QAbstractTableModel, QDateTime, QEvent, Qt, pyqtSignal
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QCheckBox, QComboBox, QDateTimeEdit, QDialog, QLabel, QLineEdit, QHeaderView
from PyQt5.QtWidgets import QMessageBox, QProgressBar, QPushButton, QRadioButton, QTableView, QTextEdit, QHBoxLayout, QVBoxLayout

import config
import define
import common
import logger
import analys
import basicx

class AnalysisPanel(QDialog):
    def __init__(self, parent):
        super(AnalysisPanel, self).__init__(parent)
        self.parent = parent
        self.log_text = ""
        self.log_cate = "AnalysisPanel"
        self.config = config.Config()
        self.logger = logger.Logger()
        self.basicx = basicx.BasicX()
        self.analysis_progress = 0
        self.get_quote_data_progress = 0
        self.getting = False
        self.suspend = False
        self.analysis_trading_day_list = [] # 存储交易日期date
        self.analysis_trading_day_dict = {} # 用于交易日数计算
        
        self.InitUserInterface()

    def __del__(self):
        pass

    def InitUserInterface(self):
        pass
