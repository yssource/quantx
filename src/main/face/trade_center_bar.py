
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

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QCheckBox, QLabel, QToolBar

import config
import logger
import trader

class TradeBarItem(object):
    def __init__(self, flag, show, tips):
        self.flag = flag
        self.show = show
        self.tips = tips
        self.log_text = ""
        self.log_cate = "TradeBarItem"
        self.logger = logger.Logger()
        self.trader = trader.Trader()
        
        self.check_box = QCheckBox()
        self.check_box.setCheckable(True)
        self.check_box.setChecked(False)
        self.check_box.setFont(QFont("SimSun", 8, QFont.Bold))
        self.check_box.setText(show)
        self.check_box.setToolTip(tips)
        self.state_label = QLabel()
        self.state_label.setFont(QFont("SimSun", 8, QFont.Bold))
        self.state_label.setMinimumWidth(40)
        self.state_label.setMinimumHeight(17)
        self.state_label.setText("OFF")
        self.state_label.setStyleSheet("color:rgb(96,96,96);")
        self.state_label.setToolTip(tips)
        
        self.check_box.clicked.connect(self.HandleConnectEvent)

    def HandleConnectEvent(self):
        if self.check_box.isChecked() == True:
            if self.flag in self.trader.trader_dict.keys():
                self.trader.trader_dict[self.flag].Start()
            else:
                self.log_text = "交易服务 %s %s 尚未载入！" % (self.flag, self.show)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        else:
            if self.flag in self.trader.trader_dict.keys():
                self.trader.trader_dict[self.flag].Stop()
            else:
                self.log_text = "交易服务 %s %s 尚未载入！" % (self.flag, self.show)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

class TradeCenterBar(QToolBar):
    def __init__(self, parent):
        super(TradeCenterBar, self).__init__(parent)
        self.parent = parent
        self.config = config.Config()
        self.InitUserInterface()

    def __del__(self):
        pass

    def InitUserInterface(self):
        if self.config.cfg_main.trade_stock_ape_need == 1:
            self.bar_item_stock_ape = TradeBarItem(self.config.cfg_main.trade_stock_ape_flag, self.config.cfg_main.trade_stock_ape_show, self.config.cfg_main.trade_stock_ape_tips)
            self.addWidget(self.bar_item_stock_ape.check_box)
            self.addWidget(self.bar_item_stock_ape.state_label)
            self.addSeparator()
        
        if self.config.cfg_main.trade_future_np_ctp_need == 1:
            self.bar_item_future_np_ctp = TradeBarItem(self.config.cfg_main.trade_future_np_ctp_flag, self.config.cfg_main.trade_future_np_ctp_show, self.config.cfg_main.trade_future_np_ctp_tips)
            self.addWidget(self.bar_item_future_np_ctp.check_box)
            self.addWidget(self.bar_item_future_np_ctp.state_label)
            self.addSeparator()
