
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

import numpy as np
import pandas as pd

import logger
import basicx
import analysis_base

class Analysis_Stock_Volatility(analysis_base.AnalysisBase):
    def __init__(self):
        analysis_base.AnalysisBase.__init__(self, "Analysis_Stock_Volatility", "Stock_Volatility", "个股波动率检测")
        self.log_text = ""
        self.log_cate = "Analysis_Stock_Volatility"
        self.logger = logger.Logger()
        self.basicx = basicx.BasicX()
        self.testing = False
        self.suspend = False

    def OnWorking(self): # 供具体回测继承调用，在 运行 前执行一些操作
        self.testing = True

    def OnSuspend(self): # 供具体回测继承调用，在 暂停 前执行一些操作
        self.suspend = True

    def OnContinue(self): # 供具体回测继承调用，在 继续 前执行一些操作
        self.suspend = False

    def OnTerminal(self): # 供具体回测继承调用，在 停止 前执行一些操作
        self.testing = False
        self.suspend = False

    def OnBackTest(self, symbol_list, trading_day_list):
        self.columns = ["market", "symbol", "swing"]
        self.result = pd.DataFrame(columns = self.columns) # 空
        self.log_text = "回测 %s %s 开始 ..." % (self.analysis, self.analysis_introduction)
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "A")
        
        if len(trading_day_list) > 0:
            trading_day_s = trading_day_list[0]
            trading_day_e = trading_day_list[-1]
            self.date_s = trading_day_s.year * 10000 + trading_day_s.month * 100 + trading_day_s.day
            self.date_e = trading_day_e.year * 10000 + trading_day_e.month * 100 + trading_day_e.day
            self.total_task = 0
            self.finish_task = 0
            self.total_task = len(symbol_list)
            if self.total_task > 0:
                for item in symbol_list:
                    market = item["market"]
                    symbol = item["code"]
                    stock_daily = self.basicx.GetStockDaily(market, symbol, self.date_s, self.date_e)
                    if not stock_daily.empty:
                        stock_daily = self.basicx.MakeExRightsCalc(market, symbol, stock_daily, 1) # 1 向前除权；2 向后除权
                        stock_daily = stock_daily.ix[(stock_daily.high > 0.0) & (stock_daily.low > 0.0) & (stock_daily.open > 0.0), :]
                        if not stock_daily.empty:
                            stock_daily["spread"] = stock_daily["high"] - stock_daily["low"]
                            stock_daily["swing"] = stock_daily["spread"] / stock_daily["open"] * 100.0
                            #print(stock_daily[["date", "close", "change"]])
                            #print(market, symbol, stock_daily["swing"].mean())
                            self.result = self.result.append({"market":market, "symbol":symbol, "swing":stock_daily["swing"].mean()}, ignore_index = True)
                    if False == self.testing:
                        break
                    while True == self.suspend:
                        time.sleep(1.0)
                    self.finish_task += 1
                    self.SetAnalysisProgress(self.total_task, self.finish_task)
            else:
                self.log_text = "回测 %s %s 证券列表为空！" % (self.analysis, self.analysis_introduction)
                self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        else:
            self.log_text = "回测 %s %s 日期列表为空！" % (self.analysis, self.analysis_introduction)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        
        if not self.result.empty:
            print(self.result.sort_values(by = ["swing",], ascending = [0,]))
            self.log_text = "回测 %s %s 完成。" % (self.analysis, self.analysis_introduction)
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "A")
