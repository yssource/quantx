
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

    def OnWorking(self): # 供具体回测继承调用，在 运行 前执行一些操作
        result = self.basicx.GetStockDaily("sz", "000001", 20100101, 20171231)
        if not result.empty:
            print(result)

    def OnSuspend(self): # 供具体回测继承调用，在 暂停 前执行一些操作
        pass

    def OnContinue(self): # 供具体回测继承调用，在 继续 前执行一些操作
        pass

    def OnTerminal(self): # 供具体回测继承调用，在 停止 前执行一些操作
        pass
