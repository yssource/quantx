
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

import random
import threading

import define
import logger

class TWAP():
    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.trader = kwargs.get("trader", None)
        self.strategy = kwargs.get("strategy", "")
        self.log_type = kwargs.get("log_type", "")
        self.log_text = ""
        self.log_cate = "TWAP_%s" % self.strategy
        self.logger = logger.Logger()
        
        self.quote_data_dict = {}
        self.quote_data_locker = threading.Lock()

    def __del__(self):
        pass

    def OnQuoteStock(self, msg): # 行情触发 # 目前只订阅个股行情，不会有指数干扰
        try:
            self.quote_data_locker.acquire()
            self.quote_data_dict[msg.data[0].decode()] = msg.data
            self.quote_data_locker.release()
        except Exception as e:
            self.log_text = "函数 OnQuoteStock 异常！%s" % e
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, self.log_type)

    def OnTraderEvent(self, trader, ret_func, task_item): # 交易模块事件通知，供具体策略继承调用
        if ret_func == define.trade_placeorder_s_func:
            self.log_text = "%s %d：%s" % (trader, ret_func, task_item.order.order_id)
            self.logger.SendMessage("H", 2, self.log_cate, self.log_text, self.log_type)

    def TradeStart(self):
        self.log_text = "用户 执行 算法交易。"
        self.logger.SendMessage("H", 2, self.log_cate, self.log_text, self.log_type)

    def TradeSuspend(self):
        self.log_text = "用户 暂停 算法交易。"
        self.logger.SendMessage("H", 2, self.log_cate, self.log_text, self.log_type)

    def TradeContinue(self):
        self.log_text = "用户 继续 算法交易。"
        self.logger.SendMessage("H", 2, self.log_cate, self.log_text, self.log_type)

    def TradeStop(self):
        self.log_text = "用户 停止 算法交易。"
        self.logger.SendMessage("H", 2, self.log_cate, self.log_text, self.log_type)
