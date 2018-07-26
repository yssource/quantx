
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

import config
import define
import common
import logger

import quotex
import tradex_stk_sy
import tradex_fue_as

class Trader(common.Singleton):
    def __init__(self):
        self.started = False
        self.log_text = ""
        self.log_cate = "Trader"
        self.quoter_dict = {}
        self.trader_dict = {}
        self.config = config.Config()
        self.logger = logger.Logger()
        self.cfg_main_file_path = define.CFG_FILE_PATH_MAIN

    def __del__(self):
        pass

    def StartService(self):
        if self.config.cfg_main.quote_stock_ltb_need == 1:
            self.log_text = "正在加载 股票类LTB行情数据 服务..."
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            quote_subs = {define.stock_ltb_market_s_func : (define.stock_ltb_market_s_func, define.stock_ltb_market_s_type, ""), 
                          define.stock_ltb_market_i_func : (define.stock_ltb_market_i_func, define.stock_ltb_market_i_type, ""),
                          define.stock_ltb_market_t_func : (define.stock_ltb_market_t_func, define.stock_ltb_market_t_type, "")}
            quoter = quotex.QuoteX(self, "股票类LTB行情", self.config.cfg_main.quote_stock_ltb_addr, self.config.cfg_main.quote_stock_ltb_port, quote_subs) # 股票类LTB快照
            self.quoter_dict[self.config.cfg_main.quote_stock_ltb_flag] = quoter
        
        if self.config.cfg_main.quote_stock_ltp_need == 1:
            self.log_text = "正在加载 股票类LTP行情数据 服务..."
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            quote_subs = {define.stock_ltp_market_s_func : (define.stock_ltp_market_s_func, define.stock_ltp_market_s_type, ""), 
                          define.stock_ltp_market_i_func : (define.stock_ltp_market_i_func, define.stock_ltp_market_i_type, ""),
                          define.stock_ltp_market_t_func : (define.stock_ltp_market_t_func, define.stock_ltp_market_t_type, "")}
            quoter = quotex.QuoteX(self, "股票类LTP行情", self.config.cfg_main.quote_stock_ltp_addr, self.config.cfg_main.quote_stock_ltp_port, quote_subs) # 股票类LTP快照
            self.quoter_dict[self.config.cfg_main.quote_stock_ltp_flag] = quoter
        
        if self.config.cfg_main.quote_stock_tdf_need == 1:
            self.log_text = "正在加载 股票类TDF行情数据 服务..."
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            quote_subs = {define.stock_tdf_market_s_func : (define.stock_tdf_market_s_func, define.stock_tdf_market_s_type, ""),
                          define.stock_tdf_market_i_func : (define.stock_tdf_market_i_func, define.stock_tdf_market_i_type, ""),
                          define.stock_tdf_market_t_func : (define.stock_tdf_market_t_func, define.stock_tdf_market_t_type, "")}
            quoter = quotex.QuoteX(self, "股票类TDF行情", self.config.cfg_main.quote_stock_tdf_addr, self.config.cfg_main.quote_stock_tdf_port, quote_subs) # 股票类TDF快照
            self.quoter_dict[self.config.cfg_main.quote_stock_tdf_flag] = quoter
        
        if self.config.cfg_main.quote_future_np_need == 1:
            self.log_text = "正在加载 期货类内盘行情数据 服务..."
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            quote_subs = {define.future_np_market_func : (define.future_np_market_func, define.future_np_market_type, "")}
            quoter = quotex.QuoteX(self, "期货类内盘行情", self.config.cfg_main.quote_future_np_addr, self.config.cfg_main.quote_future_np_port, quote_subs) # 期货类内盘快照
            self.quoter_dict[self.config.cfg_main.quote_future_np_flag] = quoter
        
        if self.config.cfg_main.trade_stock_ape_need == 1:
            self.log_text = "正在加载 股票类顶点交易 (同步) 服务..."
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            trader = tradex_stk_sy.TradeX_Stk_Sy(self, "股票类顶点交易(SY)", self.config.cfg_main.trade_stock_ape_flag, self.config.cfg_main.trade_stock_ape_save,
                     self.config.cfg_main.trade_stock_ape_addr, self.config.cfg_main.trade_stock_ape_port, self.config.cfg_main.user_username_ape, self.config.cfg_main.user_password_ape, self.config.cfg_main.user_gdh_sh_ape, self.config.cfg_main.user_gdh_sz_ape, self.config.cfg_main.user_asset_account_ape, 5)
            self.trader_dict[self.config.cfg_main.trade_stock_ape_flag] = trader
        
        if self.config.cfg_main.trade_future_np_ctp_need == 1:
            self.log_text = "正在加载 期货类内盘交易 (异步) 服务..."
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            trader = tradex_fue_as.TradeX_Fue_As(self, "期货类内盘交易(AS)", self.config.cfg_main.trade_future_np_ctp_flag, self.config.cfg_main.trade_future_np_ctp_save, 
                     self.config.cfg_main.trade_future_np_ctp_addr, self.config.cfg_main.trade_future_np_ctp_port, self.config.cfg_main.user_username_ctp, self.config.cfg_main.user_password_ctp, self.config.cfg_main.user_asset_account_ctp, 5)
            self.trader_dict[self.config.cfg_main.trade_future_np_ctp_flag] = trader

    def GetTrader(self, trader_flag):
        trader = None
        if trader_flag in self.trader_dict.keys():
            trader = self.trader_dict[trader_flag]
        return trader

    def OnQuoteReplyMsg(self, quote_name, reply_func, reply_code, reply_info):
        pass # TODO：更新用户界面信息

    def OnTradeReplyMsg(self, trade_name, reply_func, reply_code, reply_info):
        pass # TODO：更新用户界面信息

    def start(self):
        if self.started == False:
            self.StartService()
            self.started = True

    def stop(self):
        if self.started == True:
            for trader in self.trader_dict.values():
                trader.Stop()
            for quoter in self.quoter_dict.values():
                quoter.Stop()
            self.started = False
