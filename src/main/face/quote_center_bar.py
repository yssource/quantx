
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

from datetime import datetime, timedelta

from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QCheckBox, QLabel, QToolBar

import config
import logger
import center
import trader

class QuoteBarItem(object):
    def __init__(self, flag, show, tips):
        self.flag = flag
        self.show = show
        self.tips = tips
        self.log_text = ""
        self.log_cate = "QuoteBarItem"
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
            if self.flag in self.trader.quoter_dict.keys():
                pass
                self.trader.quoter_dict[self.flag].Start()
            else:
                self.log_text = "行情服务 %s %s 尚未载入！" % (self.flag, self.show)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        else:
            if self.flag in self.trader.quoter_dict.keys():
                self.trader.quoter_dict[self.flag].Stop()
            else:
                self.log_text = "行情服务 %s %s 尚未载入！" % (self.flag, self.show)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

class QuoteCenterBar(QToolBar):
    def __init__(self, parent):
        super(QuoteCenterBar, self).__init__(parent)
        self.parent = parent
        self.log_text = ""
        self.log_cate = "QuoteCenterBar"
        self.config = config.Config()
        self.logger = logger.Logger()
        self.center = center.Center()
        self.InitUserInterface()

    def __del__(self):
        self.timer_check_quote_data.stop()
        del self.timer_check_quote_data

    def InitUserInterface(self):
        if self.config.cfg_main.quote_stock_ltb_need == 1:
            self.bar_item_stock_ltb = QuoteBarItem(self.config.cfg_main.quote_stock_ltb_flag, self.config.cfg_main.quote_stock_ltb_show, self.config.cfg_main.quote_stock_ltb_tips)
            self.addWidget(self.bar_item_stock_ltb.check_box)
            self.addWidget(self.bar_item_stock_ltb.state_label)
            self.addSeparator()
        
        if self.config.cfg_main.quote_stock_ltp_need == 1:
            self.bar_item_stock_ltp = QuoteBarItem(self.config.cfg_main.quote_stock_ltp_flag, self.config.cfg_main.quote_stock_ltp_show, self.config.cfg_main.quote_stock_ltp_tips)
            self.addWidget(self.bar_item_stock_ltp.check_box)
            self.addWidget(self.bar_item_stock_ltp.state_label)
            self.addSeparator()
        
        if self.config.cfg_main.quote_stock_tdf_need == 1:
            self.bar_item_stock_tdf = QuoteBarItem(self.config.cfg_main.quote_stock_tdf_flag, self.config.cfg_main.quote_stock_tdf_show, self.config.cfg_main.quote_stock_tdf_tips)
            self.addWidget(self.bar_item_stock_tdf.check_box)
            self.addWidget(self.bar_item_stock_tdf.state_label)
            self.addSeparator()
        
        if self.config.cfg_main.quote_future_np_need == 1:
            self.bar_item_future_np = QuoteBarItem(self.config.cfg_main.quote_future_np_flag, self.config.cfg_main.quote_future_np_show, self.config.cfg_main.quote_future_np_tips)
            self.addWidget(self.bar_item_future_np.check_box)
            self.addWidget(self.bar_item_future_np.state_label)
            self.addSeparator()
        
        self.timer_check_quote_data = QTimer()
        self.timer_check_quote_data.timeout.connect(self.OnCheckQuoteData)
        self.timer_check_quote_data.start(3000)

    def OnCheckQuoteData(self):
        timer = datetime.now()
        now_week = datetime.now().isoweekday()
        now_time = int(datetime.now().strftime("%H%M"))
        
        if self.config.cfg_main.quote_stock_ltb_need == 1:
            if self.bar_item_stock_ltb.check_box.isChecked() == True:
                if not (now_week == 7 or now_week == 6):
                    if (now_time >= 930 and now_time < 1130) or (now_time >= 1300 and now_time < 1500): # 只盘中时间检测
                        if (timer - self.center.update_timestamp_stock_ltb) > timedelta(seconds = 5):
                            time_span = timer - self.center.update_timestamp_stock_ltb
                            self.log_text = "股票类LTB行情 距上次数据更新时间已超过 %f 秒！" % time_span.total_seconds()
                            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "M")
                        # 指数类的目前先不管
        if self.config.cfg_main.quote_stock_ltp_need == 1:
            if self.bar_item_stock_ltp.check_box.isChecked() == True:
                if not (now_week == 7 or now_week == 6):
                    if (now_time >= 930 and now_time < 1130) or (now_time >= 1300 and now_time < 1500): # 只盘中时间检测
                        if (timer - self.center.update_timestamp_stock_ltp) > timedelta(seconds = 5):
                            time_span = timer - self.center.update_timestamp_stock_ltp
                            self.log_text = "股票类LTP行情 距上次数据更新时间已超过 %f 秒！" % time_span.total_seconds()
                            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "M")
                        # 指数类的目前先不管
        if self.config.cfg_main.quote_stock_tdf_need == 1:
            if self.bar_item_stock_tdf.check_box.isChecked() == True:
                if not (now_week == 7 or now_week == 6):
                    if (now_time >= 930 and now_time < 1130) or (now_time >= 1300 and now_time < 1500): # 只盘中时间检测
                        if (timer - self.center.update_timestamp_stock_tdf) > timedelta(seconds = 5):
                            time_span = timer - self.center.update_timestamp_stock_tdf
                            self.log_text = "股票类TDF行情 距上次数据更新时间已超过 %f 秒！" % time_span.total_seconds()
                            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "M")
                        # 指数类的目前先不管
        if self.config.cfg_main.quote_future_np_need == 1:
            if self.bar_item_future_np.check_box.isChecked() == True:
                if not (now_week == 7 or (now_week == 6 and now_time >= 230)):
                    if (now_time >= 900 and now_time < 1130) or (now_time >= 1300 and now_time < 1515) or (now_time >= 2100 and now_time <= 2359) or (now_time >= 0 and now_time < 230): # 只盘中时间检测
                        if (timer - self.center.update_timestamp_future_np) > timedelta(seconds = 5):
                            time_span = timer - self.center.update_timestamp_future_np
                            self.log_text = "期货类内盘行情 距上次数据更新时间已超过 %f 秒！" % time_span.total_seconds()
                            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "M")
