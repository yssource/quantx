
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

import logger
import strategy_base

class Strategy_Test_01(strategy_base.StrategyBase):
    def __init__(self):
        strategy_base.StrategyBase.__init__(self, "Strategy_Test_01", "Test_01", "测试_01")
        self.beat_calc = BeatCalc(self)

class BeatCalc():
    def __init__(self, parent):
        self.parent = parent
        self.calc_wait = 3
        self.logger = logger.Logger()

    def MakeCalc(self):
        self.log_cate = "Strategy_Test_01"
        self.log_text = "Strategy_Test_01"
        self.logger.SendMessage("D", 0, self.log_cate, self.log_text, "M")
