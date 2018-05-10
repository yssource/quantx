
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

import sys
import traceback
import threading
from datetime import datetime

from pubsub import pub

import config
import define
import common

class AnalysisInfo(object):
    def __init__(self):
        self.analysis = ""
        self.module = None
        self.classer = None
        self.instance = None
        
        self.name = ""
        self.introduction = ""
        self.file_path = ""
        self.state_locker = threading.Lock()
        self.state = define.USER_CTRL_LOAD

class StrategyInfo(object):
    def __init__(self):
        self.strategy = ""
        self.module = None
        self.classer = None
        self.instance = None
        
        self.name = ""
        self.introduction = ""
        self.file_path = ""
        self.state_locker = threading.Lock()
        self.state = define.USER_CTRL_LOAD

class DataCenter(object):
    def __init__(self):
        self.stock_snapshot_ltb = {}
        self.index_snapshot_ltb = {}
        self.trans_ltb = {}
        self.stock_snapshot_ltp = {}
        self.index_snapshot_ltp = {}
        self.trans_ltp = {}
        self.stock_snapshot_tdf = {}
        self.index_snapshot_tdf = {}
        self.trans_tdf = {}
        self.future_snapshot_np = {}
        
        self.strategies = {}
        self.strategies_locker = threading.Lock()

class Center(common.Singleton):
    class DataMsg(object): # 用于直接发送时和 pub.sendMessage 格式的统一
        def __init__(self, quote_data):
            self.data = quote_data

    def __init__(self):
        self.data = DataCenter()
        self.config = config.Config()
        
        self.quote_sub_locker_stock_ltb = threading.Lock()
        self.quote_sub_locker_index_ltb = threading.Lock()
        self.quote_sub_locker_trans_ltb = threading.Lock()
        self.quote_sub_locker_stock_ltp = threading.Lock()
        self.quote_sub_locker_index_ltp = threading.Lock()
        self.quote_sub_locker_trans_ltp = threading.Lock()
        self.quote_sub_locker_stock_tdf = threading.Lock()
        self.quote_sub_locker_index_tdf = threading.Lock()
        self.quote_sub_locker_trans_tdf = threading.Lock()
        self.quote_sub_locker_future_np = threading.Lock()
        
        self.quote_sub_dict_stock_ltb = {}
        self.quote_sub_dict_index_ltb = {}
        self.quote_sub_dict_trans_ltb = {}
        self.quote_sub_dict_stock_ltp = {}
        self.quote_sub_dict_index_ltp = {}
        self.quote_sub_dict_trans_ltp = {}
        self.quote_sub_dict_stock_tdf = {}
        self.quote_sub_dict_index_tdf = {}
        self.quote_sub_dict_trans_tdf = {}
        self.quote_sub_dict_future_np = {}
        
        self.update_timestamp_stock_ltb = datetime.now() # 股票个股
        self.update_timestamp_index_ltb = datetime.now() # 股票指数
        self.update_timestamp_trans_ltb = datetime.now() # 股票逐笔
        self.update_timestamp_stock_ltp = datetime.now() # 股票个股
        self.update_timestamp_index_ltp = datetime.now() # 股票指数
        self.update_timestamp_trans_ltp = datetime.now() # 股票逐笔
        self.update_timestamp_stock_tdf = datetime.now() # 股票个股
        self.update_timestamp_index_tdf = datetime.now() # 股票指数
        self.update_timestamp_trans_tdf = datetime.now() # 股票逐笔
        self.update_timestamp_future_np = datetime.now() # 期货内盘

    def RegQuoteSub(self, strategy, quote_func, quote_type):
        if quote_type == "stock_ltb":
            self.quote_sub_locker_stock_ltb.acquire()
            self.quote_sub_dict_stock_ltb[strategy] = quote_func
            self.quote_sub_locker_stock_ltb.release()
            return
        if quote_type == "index_ltb":
            self.quote_sub_locker_index_ltb.acquire()
            self.quote_sub_dict_index_ltb[strategy] = quote_func
            self.quote_sub_locker_index_ltb.release()
            return
        if quote_type == "trans_ltb":
            self.quote_sub_locker_trans_ltb.acquire()
            self.quote_sub_dict_trans_ltb[strategy] = quote_func
            self.quote_sub_locker_trans_ltb.release()
            return
        if quote_type == "stock_ltp":
            self.quote_sub_locker_stock_ltp.acquire()
            self.quote_sub_dict_stock_ltp[strategy] = quote_func
            self.quote_sub_locker_stock_ltp.release()
            return
        if quote_type == "index_ltp":
            self.quote_sub_locker_index_ltp.acquire()
            self.quote_sub_dict_index_ltp[strategy] = quote_func
            self.quote_sub_locker_index_ltp.release()
            return
        if quote_type == "trans_ltp":
            self.quote_sub_locker_trans_ltp.acquire()
            self.quote_sub_dict_trans_ltp[strategy] = quote_func
            self.quote_sub_locker_trans_ltp.release()
            return
        if quote_type == "stock_tdf":
            self.quote_sub_locker_stock_tdf.acquire()
            self.quote_sub_dict_stock_tdf[strategy] = quote_func
            self.quote_sub_locker_stock_tdf.release()
            return
        if quote_type == "index_tdf":
            self.quote_sub_locker_index_tdf.acquire()
            self.quote_sub_dict_index_tdf[strategy] = quote_func
            self.quote_sub_locker_index_tdf.release()
            return
        if quote_type == "trans_tdf":
            self.quote_sub_locker_trans_tdf.acquire()
            self.quote_sub_dict_trans_tdf[strategy] = quote_func
            self.quote_sub_locker_trans_tdf.release()
            return
        if quote_type == "future_np":
            self.quote_sub_locker_future_np.acquire()
            self.quote_sub_dict_future_np[strategy] = quote_func
            self.quote_sub_locker_future_np.release()
            return

    def DelQuoteSub(self, strategy, quote_type):
        if quote_type == "stock_ltb":
            if strategy in self.quote_sub_dict_stock_ltb.keys():
                self.quote_sub_locker_stock_ltb.acquire()
                del self.quote_sub_dict_stock_ltb[strategy]
                self.quote_sub_locker_stock_ltb.release()
            return
        if quote_type == "index_ltb":
            if strategy in self.quote_sub_dict_index_ltb.keys():
                self.quote_sub_locker_index_ltb.acquire()
                del self.quote_sub_dict_index_ltb[strategy]
                self.quote_sub_locker_index_ltb.release()
            return
        if quote_type == "trans_ltb":
            if strategy in self.quote_sub_dict_trans_ltb.keys():
                self.quote_sub_locker_trans_ltb.acquire()
                del self.quote_sub_dict_trans_ltb[strategy]
                self.quote_sub_locker_trans_ltb.release()
            return
        if quote_type == "stock_ltp":
            if strategy in self.quote_sub_dict_stock_ltp.keys():
                self.quote_sub_locker_stock_ltp.acquire()
                del self.quote_sub_dict_stock_ltp[strategy]
                self.quote_sub_locker_stock_ltp.release()
            return
        if quote_type == "index_ltp":
            if strategy in self.quote_sub_dict_index_ltp.keys():
                self.quote_sub_locker_index_ltp.acquire()
                del self.quote_sub_dict_index_ltp[strategy]
                self.quote_sub_locker_index_ltp.release()
            return
        if quote_type == "trans_ltp":
            if strategy in self.quote_sub_dict_trans_ltp.keys():
                self.quote_sub_locker_trans_ltp.acquire()
                del self.quote_sub_dict_trans_ltp[strategy]
                self.quote_sub_locker_trans_ltp.release()
            return
        if quote_type == "stock_tdf":
            if strategy in self.quote_sub_dict_stock_tdf.keys():
                self.quote_sub_locker_stock_tdf.acquire()
                del self.quote_sub_dict_stock_tdf[strategy]
                self.quote_sub_locker_stock_tdf.release()
            return
        if quote_type == "index_tdf":
            if strategy in self.quote_sub_dict_index_tdf.keys():
                self.quote_sub_locker_index_tdf.acquire()
                del self.quote_sub_dict_index_tdf[strategy]
                self.quote_sub_locker_index_tdf.release()
            return
        if quote_type == "trans_tdf":
            if strategy in self.quote_sub_dict_trans_tdf.keys():
                self.quote_sub_locker_trans_tdf.acquire()
                del self.quote_sub_dict_trans_tdf[strategy]
                self.quote_sub_locker_trans_tdf.release()
            return
        if quote_type == "future_np":
            if strategy in self.quote_sub_dict_future_np.keys():
                self.quote_sub_locker_future_np.acquire()
                del self.quote_sub_dict_future_np[strategy]
                self.quote_sub_locker_future_np.release()
            return

    def UpdateSnapshot(self, data_type, tmp_data):
        try:
            if data_type == define.stock_ltb_market_s_func:
                str_code = tmp_data[0].decode() # 600000, 000001
                src_data = common.PreTransStockLtbMarket(tmp_data) # 部分数值转换
                self.data.stock_snapshot_ltb[str_code] = src_data
                self.update_timestamp_stock_ltb = datetime.now()
                pub.sendMessage("center.quote.stock_ltb", msg = src_data)
                self.quote_sub_locker_stock_ltb.acquire()
                for strategy, quote_func in self.quote_sub_dict_stock_ltb.items():
                    quote_func(self.DataMsg(src_data))
                self.quote_sub_locker_stock_ltb.release()
            elif data_type == define.stock_ltb_market_i_func:
                str_code = tmp_data[0].decode() # 399001, 000001
                src_data = common.PreTransIndexLtbMarket(tmp_data) # 部分数值转换
                self.data.index_snapshot_ltb[str_code] = src_data
                self.update_timestamp_index_ltb = datetime.now()
                pub.sendMessage("center.quote.index_ltb", msg = src_data)
                self.quote_sub_locker_index_ltb.acquire()
                for strategy, quote_func in self.quote_sub_dict_index_ltb.items():
                    quote_func(self.DataMsg(src_data))
                self.quote_sub_locker_index_ltb.release()
            elif data_type == define.stock_ltb_market_t_func:
                str_code = tmp_data[0].decode()
                src_data = common.PreTransTransLtbMarket(tmp_data) # 部分数值转换
                self.data.trans_ltb[str_code] = src_data
                self.update_timestamp_trans_ltb = datetime.now()
                pub.sendMessage("center.quote.trans_ltb", msg = src_data)
                self.quote_sub_locker_trans_ltb.acquire()
                for strategy, quote_func in self.quote_sub_dict_trans_ltb.items():
                    quote_func(self.DataMsg(src_data))
                self.quote_sub_locker_trans_ltb.release()
            elif data_type == define.stock_ltp_market_s_func:
                str_code = tmp_data[0].decode() # 600000, 000001
                src_data = common.PreTransStockLtpMarket(tmp_data) # 部分数值转换
                self.data.stock_snapshot_ltp[str_code] = src_data
                self.update_timestamp_stock_ltp = datetime.now()
                pub.sendMessage("center.quote.stock_ltp", msg = src_data)
                self.quote_sub_locker_stock_ltp.acquire()
                for strategy, quote_func in self.quote_sub_dict_stock_ltp.items():
                    quote_func(self.DataMsg(src_data))
                self.quote_sub_locker_stock_ltp.release()
            elif data_type == define.stock_ltp_market_i_func:
                str_code = tmp_data[0].decode() # 399001, 000001
                src_data = common.PreTransIndexLtpMarket(tmp_data) # 部分数值转换
                self.data.index_snapshot_ltp[str_code] = src_data
                self.update_timestamp_index_ltp = datetime.now()
                pub.sendMessage("center.quote.index_ltp", msg = src_data)
                self.quote_sub_locker_index_ltp.acquire()
                for strategy, quote_func in self.quote_sub_dict_index_ltp.items():
                    quote_func(self.DataMsg(src_data))
                self.quote_sub_locker_index_ltp.release()
            elif data_type == define.stock_ltp_market_t_func:
                str_code = tmp_data[0].decode()
                src_data = common.PreTransTransLtpMarket(tmp_data) # 部分数值转换
                self.data.trans_ltp[str_code] = src_data
                self.update_timestamp_trans_ltp = datetime.now()
                pub.sendMessage("center.quote.trans_ltp", msg = src_data)
                self.quote_sub_locker_trans_ltp.acquire()
                for strategy, quote_func in self.quote_sub_dict_trans_ltp.items():
                    quote_func(self.DataMsg(src_data))
                self.quote_sub_locker_trans_ltp.release()
            elif data_type == define.stock_tdf_market_s_func:
                str_code = tmp_data[0].decode() # 600000, 000001
                src_data = common.PreTransStockTdfMarket(tmp_data) # 部分数值转换
                self.data.stock_snapshot_tdf[str_code] = src_data
                self.update_timestamp_stock_tdf = datetime.now()
                pub.sendMessage("center.quote.stock_tdf", msg = src_data)
                self.quote_sub_locker_stock_tdf.acquire()
                for strategy, quote_func in self.quote_sub_dict_stock_tdf.items():
                    quote_func(self.DataMsg(src_data))
                self.quote_sub_locker_stock_tdf.release()
            elif data_type == define.stock_tdf_market_i_func:
                str_code = tmp_data[0].decode() # 399001, 999999
                src_data = common.PreTransIndexTdfMarket(tmp_data) # 部分数值转换
                self.data.index_snapshot_tdf[str_code] = src_data
                self.update_timestamp_index_tdf = datetime.now()
                pub.sendMessage("center.quote.index_tdf", msg = src_data)
                self.quote_sub_locker_index_tdf.acquire()
                for strategy, quote_func in self.quote_sub_dict_index_tdf.items():
                    quote_func(self.DataMsg(src_data))
                self.quote_sub_locker_index_tdf.release()
            elif data_type == define.stock_tdf_market_t_func:
                str_code = tmp_data[0].decode()
                src_data = common.PreTransTransTdfMarket(tmp_data) #部分数值转换
                self.data.trans_tdf[str_code] = src_data
                self.update_timestamp_trans_tdf = datetime.now()
                pub.sendMessage("center.quote.trans_tdf", msg = src_data)
                self.quote_sub_locker_trans_tdf.acquire()
                for strategy, quote_func in self.quote_sub_dict_trans_tdf.items():
                    quote_func(self.DataMsg(src_data))
                self.quote_sub_locker_trans_tdf.release()
            elif data_type == define.future_np_market_func:
                str_code = tmp_data[0].decode() # IF1806, IF1809
                src_data = common.PreTransFutureMarket(tmp_data) # 部分数值转换
                self.data.future_snapshot_np[str_code] = src_data
                self.update_timestamp_future_np = datetime.now()
                pub.sendMessage("center.quote.future_np", msg = src_data)
                self.quote_sub_locker_future_np.acquire()
                for strategy, quote_func in self.quote_sub_dict_future_np.items():
                    quote_func(self.DataMsg(src_data))
                self.quote_sub_locker_future_np.release()
        except Exception as e:
            print("UpdateSnapshot Error:", e)
            traceback.print_exc()
            info = sys.exc_info()
            print("UpdateSnapshot Error:", info[0], info[1])
