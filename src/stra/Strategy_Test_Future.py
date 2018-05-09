
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

from math import ceil, floor

import logger
import center
import strategy_base

class Strategy_Test_Future(strategy_base.StrategyBase):
    def __init__(self):
        strategy_base.StrategyBase.__init__(self, "Strategy_Test_Future", "Test_Future", "行情测试")
        self.log_cate = "Strategy_Test_Future"
        self.beat_calc = BeatCalc(self)
        
        self.subscribe = False # 行情订阅标志
        self.center = center.Center()

        self.symbol_f = "IF1806"
        self.price_round_f = 1 # 股指期货价格需精确到小数点后一位，且为 0.2 的整数倍

    def OnWorking(self): # 供具体策略继承调用，在 运行 前执行一些操作
        if self.subscribe == False:
            self.center.RegQuoteSub(self.strategy, self.OnQuoteFuture, "future_np")
            self.subscribe = True

    def OnSuspend(self): # 供具体策略继承调用，在 暂停 前执行一些操作
        pass

    def OnContinue(self): # 供具体策略继承调用，在 继续 前执行一些操作
        pass

    def OnTerminal(self): # 供具体策略继承调用，在 停止 前执行一些操作
        if self.subscribe == True:
            self.center.DelQuoteSub(self.strategy, "future_np")
            self.subscribe = False

    def OnQuoteFuture(self, msg): # 行情触发
        try:
            str_code = str(msg[0])
            if str_code == self.symbol_f:
                price_m_s1 = round(msg["AskPrice"][0], self.price_round_f) # 卖一价
                price_m_b1 = round(msg["BidPrice"][0], self.price_round_f) # 买一价
                quote_time = int(floor(msg["QuoteTime"] / 1000.0)) # 行情时间，HHMMSS
                self.log_text = "%s：%s：%f, %f, %d" % (self.strategy, str_code, price_m_s1, price_m_b1, quote_time)
                self.logger.SendMessage("D", 0, self.log_cate, self.log_text, "T")
        except Exception as e:
            self.log_text = "%s：函数 OnQuoteFuture 异常！%s" % (self.strategy, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "M")

class BeatCalc():
    def __init__(self, parent):
        self.parent = parent
        self.calc_wait = 3
        self.logger = logger.Logger()

    def MakeCalc(self):
        self.log_cate = "Strategy_Test_Future"
        self.log_text = "Strategy_Test_Future"
        #self.logger.SendMessage("D", 0, self.log_cate, self.log_text, "M")
