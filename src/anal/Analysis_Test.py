
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

import time

import logger
import basicx
import analysis_base

class Analysis_Test(analysis_base.AnalysisBase):
    def __init__(self):
        analysis_base.AnalysisBase.__init__(self, "Analysis_Test", "Test", "测试")
        self.log_text = ""
        self.log_cate = "Analysis_Test"
        self.logger = logger.Logger()
        self.basicx = basicx.BasicX()
        self.testing = False
        self.suspend = False

    def OnWorking(self): # 供具体回测继承调用，在 运行 前执行一些操作
        self.testing = True
        result = self.basicx.GetStockDaily("sz", "000001", 20100101, 20171231)
        if not result.empty:
            print(result)

    def OnSuspend(self): # 供具体回测继承调用，在 暂停 前执行一些操作
        self.suspend = True

    def OnContinue(self): # 供具体回测继承调用，在 继续 前执行一些操作
        self.suspend = False

    def OnTerminal(self): # 供具体回测继承调用，在 停止 前执行一些操作
        self.testing = False
        self.suspend = False

    def OnBackTest(self, symbol_list, trading_day_list, trade_fees):
        self.total_task = 100
        self.finish_task = 0
        self.logger.SendMessage("I", 1, self.log_cate, "开始数据分析 ...", "A")
        while self.testing == True and self.finish_task < self.total_task:
            time.sleep(0.25)
            if self.suspend == True:
                continue
            self.finish_task += 1
            self.SetAnalysisProgress(self.total_task, self.finish_task)
        if self.testing == False:
            self.logger.SendMessage("I", 1, self.log_cate, "数据分析终止！", "A")
        else:
            self.logger.SendMessage("I", 1, self.log_cate, "数据分析完成。", "A")
