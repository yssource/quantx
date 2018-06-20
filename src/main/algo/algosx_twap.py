
# -*- coding: utf-8 -*-

import random
import threading

import define
import logger

class OriginalOrder(object):
    def __init__(self, **kwargs):
        self.symbol = kwargs.get("symbol", "") # 证券代码
        self.exchange = kwargs.get("exchange", "") # 交易所，SH：上交所，SZ：深交所
        self.entr_type = kwargs.get("entr_type", 0) # 委托方式，1：限价，2：市价
        self.exch_side = kwargs.get("exch_side", 0) # 交易类型，1：买入，2：卖出
        self.price = kwargs.get("price", 0.0) # 委托价格
        self.amount = kwargs.get("amount", 0) # 委托数量
        
        self.need_trade = False
        self.position_total = 0
        self.position_can_sell = 0
        
        self.filled_qty = 0 # 成交数量
        self.cancel_qty = 0 # 撤单数量
        self.order_status = 0 # 委托状态

    def ToString(self):
        return "symbol：%s, " % self.symbol + \
               "exchange：%s, " % self.exchange + \
               "entr_type：%d, " % self.entr_type + \
               "exch_side：%d, " % self.exch_side + \
               "price：%f, " % self.price + \
               "amount：%d, " % self.amount + \
               "position_total：%d, " % self.position_total + \
               "position_can_sell：%d" % self.position_can_sell

class TWAP():
    def __init__(self, **kwargs):
        self.trader = kwargs.get("trader", None)
        self.strategy = kwargs.get("strategy", "")
        self.log_type = kwargs.get("log_type", "")
        self.log_text = ""
        self.log_cate = "TWAP_%s" % self.strategy
        self.logger = logger.Logger()
        
        self.quote_data_dict = {}
        self.quote_data_locker = threading.Lock()
        
        self.DEF_TRADE_STATUS_INITIAL = 0
        self.DEF_TRADE_STATUS_RUNNING = 1
        self.DEF_TRADE_STATUS_SUSPEND = 2
        self.DEF_TRADE_STATUS_STOPPED = 3
        self.DEF_TRADE_STATUS_FINISH  = 4
        self.DEF_TRADE_STATUS_ERROR   = 5
        self.trade_status = self.DEF_TRADE_STATUS_INITIAL
        
        self.original_order_list = []
        self.original_order_dict = {}

    def __del__(self):
        pass

    def PrintTradeParameters(self):
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
