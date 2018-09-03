
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

import threading
from datetime import datetime, date

import define

class Singleton(object):
    objs = {}
    objs_locker = threading.Lock()

    def __new__(cls, *args, **kv):
        if cls in cls.objs:
            return cls.objs[cls]["obj"]
        
        cls.objs_locker.acquire()
        try:
            if cls in cls.objs:  # double check locking
                return cls.objs[cls]["obj"]
            obj = object.__new__(cls)
            cls.objs[cls] = {"obj": obj, "init": False}
            setattr(cls, "__init__", cls.decorate_init(cls.__init__))
        finally:
            cls.objs_locker.release()
        
        return cls.objs[cls]["obj"]

    @classmethod
    def decorate_init(cls, fn):
        def init_wrap(*args):
        #def init_wrap(*args, **kv): # 子类可以使用 __init__(self, **kwargs) 形式传参
            if not cls.objs[cls]["init"]:
                fn(*args)
                #fn(*args, **kv) # 子类可以使用 __init__(self, **kwargs) 形式传参
                cls.objs[cls]["init"] = True
            return
        
        return init_wrap

def GetDateShort():
    return datetime.now().strftime("%Y-%m-%d")

def GetTimeShort():
    return datetime.now().strftime("%H:%M:%S")

def TransDateIntToStr(int_date):
    year = int(int_date / 10000)
    month = int((int_date % 10000) / 100)
    day = int_date % 100
    return "%d-%d-%d" % (year, month, day)

def TransDateIntToDate(int_date):
    year = int(int_date / 10000)
    month = int((int_date % 10000) / 100)
    day = int_date % 100
    return date(year, month, day)

def TransTimeIntToStr(int_time):
    hour = int(int_time / 10000)
    minute = int((int_time % 10000) / 100)
    second = int_time % 100
    return "%d:%d:%d" % (hour, minute, second)

def PreTransStockTdfMarket(tmp_data): # TDF个股快照预处理
    try:
        src_data = tmp_data.astype(define.stock_tdf_market_s_type_src)
        src_data[5] = round(src_data[5] * 0.0001, 5) # Last uint32 最新价 /10000
        src_data[6] = round(src_data[6] * 0.0001, 5) # Open uint32 开盘价 /10000
        src_data[7] = round(src_data[7] * 0.0001, 5) # High uint32 最高价 /10000
        src_data[8] = round(src_data[8] * 0.0001, 5) # Low uint32 最低价 /10000
        src_data[9] = round(src_data[9] * 0.0001, 5) # Close uint32 收盘价 /10000
        src_data[10] = round(src_data[10] * 0.0001, 5) # PreClose uint32 昨收价 /10000
        src_data[12] = round(src_data[12] * 0.0001, 5) # Turnover int64 成交额 /10000
        src_data[13][0] = round(src_data[13][0] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][1] = round(src_data[13][1] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][2] = round(src_data[13][2] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][3] = round(src_data[13][3] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][4] = round(src_data[13][4] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][5] = round(src_data[13][5] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][6] = round(src_data[13][6] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][7] = round(src_data[13][7] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][8] = round(src_data[13][8] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][9] = round(src_data[13][9] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[15][0] = round(src_data[15][0] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][1] = round(src_data[15][1] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][2] = round(src_data[15][2] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][3] = round(src_data[15][3] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][4] = round(src_data[15][4] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][5] = round(src_data[15][5] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][6] = round(src_data[15][6] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][7] = round(src_data[15][7] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][8] = round(src_data[15][8] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][9] = round(src_data[15][9] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[17] = round(src_data[17] * 0.0001, 5) # HighLimit uint32 涨停价 /10000
        src_data[18] = round(src_data[18] * 0.0001, 5) # LowLimit uint32 跌停价 /10000
        src_data[21] = round(src_data[21] * 0.0001, 5) # WeightedAvgBidPrice uint32 加权平均委买价格 /10000
        src_data[22] = round(src_data[22] * 0.0001, 5) # WeightedAvgAskPrice uint32 加权平均委卖价格 /10000
        src_data[24] = round(src_data[24] * 0.0001, 5) # IOPV int32 IOPV 净值估值 /10000
        src_data[25] = round(src_data[25] * 0.0001, 5) # YieldRate int32 到期收益率 /10000
        src_data[26] = round(src_data[26] * 0.0001, 5) # PeRate_1 int32 市盈率 1 /10000
        src_data[27] = round(src_data[27] * 0.0001, 5) # PeRate_2 int32 市盈率 2 /10000
        return src_data
    except Exception as e:
        print("PreTransStockTdfMarket error:", e)

def PreTransIndexTdfMarket(tmp_data): # TDF指数快照预处理
    try:
        src_data = tmp_data.astype(define.stock_tdf_market_i_type_src)
        src_data[5] = round(src_data[5] * 0.0001, 5) # Last int32 最新指数 /10000
        src_data[6] = round(src_data[6] * 0.0001, 5) # Open int32 开盘指数 /10000
        src_data[7] = round(src_data[7] * 0.0001, 5) # High int32 最高指数 /10000
        src_data[8] = round(src_data[8] * 0.0001, 5) # Low int32 最低指数 /10000
        src_data[9] = round(src_data[9] * 0.0001, 5) # Close uint32 收盘指数 /10000
        src_data[10] = round(src_data[10] * 0.0001, 5) # PreClose int32 昨收指数 /10000
        src_data[12] = round(src_data[12] * 0.0001, 5) # Turnover int64 成交额 /10000
        return src_data
    except Exception as e:
        print("PreTransIndexTdfMarket error:", e)

def PreTransTransTdfMarket(tmp_data): # TDF逐笔成交预处理
    try:
        src_data = tmp_data.astype(define.stock_tdf_market_t_type_src)
        src_data[5] = round(src_data[5] * 0.0001, 5) # Price uint32 成交价 /10000
        src_data[7] = round(src_data[7] * 0.0001, 5) # Turnover int64 成交额 /10000
        return src_data
    except Exception as e:
        print("PreTransTransTdfMarket error:", e)

def PreTransStockLtbMarket(tmp_data): # LTB个股快照预处理
    try:
        src_data = tmp_data.astype(define.stock_ltb_market_s_type_src)
        src_data[5] = round(src_data[5] * 0.0001, 5) # Last uint32 最新价 /10000
        src_data[6] = round(src_data[6] * 0.0001, 5) # Open uint32 开盘价 /10000
        src_data[7] = round(src_data[7] * 0.0001, 5) # High uint32 最高价 /10000
        src_data[8] = round(src_data[8] * 0.0001, 5) # Low uint32 最低价 /10000
        src_data[9] = round(src_data[9] * 0.0001, 5) # Close uint32 收盘价 /10000
        src_data[10] = round(src_data[10] * 0.0001, 5) # PreClose uint32 昨收价 /10000
        src_data[12] = round(src_data[12] * 0.0001, 5) # Turnover int64 成交额 /10000
        src_data[13][0] = round(src_data[13][0] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][1] = round(src_data[13][1] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][2] = round(src_data[13][2] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][3] = round(src_data[13][3] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][4] = round(src_data[13][4] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][5] = round(src_data[13][5] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][6] = round(src_data[13][6] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][7] = round(src_data[13][7] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][8] = round(src_data[13][8] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][9] = round(src_data[13][9] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[15][0] = round(src_data[15][0] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][1] = round(src_data[15][1] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][2] = round(src_data[15][2] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][3] = round(src_data[15][3] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][4] = round(src_data[15][4] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][5] = round(src_data[15][5] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][6] = round(src_data[15][6] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][7] = round(src_data[15][7] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][8] = round(src_data[15][8] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][9] = round(src_data[15][9] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[17] = round(src_data[17] * 0.0001, 5) # HighLimit uint32 涨停价 /10000
        src_data[18] = round(src_data[18] * 0.0001, 5) # LowLimit uint32 跌停价 /10000
        src_data[20] = round(src_data[20] * 0.0001, 5) # IOPV int32 基金净值 /10000
        src_data[22] = round(src_data[22] * 0.0001, 5) # YieldToMaturity uint32 到期收益率 /10000
        src_data[23] = round(src_data[23] * 0.0001, 5) # AuctionPrice uint32 动态参考价格 /10000
        src_data[28] = round(src_data[28] * 0.0001, 5) # WeightedAvgBidPrice uint32 申买加权均价 /10000
        src_data[29] = round(src_data[29] * 0.0001, 5) # WeightedAvgOfferPrice uint32 申卖加权均价 /10000
        src_data[30] = round(src_data[30] * 0.0001, 5) # AltWeightedAvgBidPrice uint32 债券申买加权均价 /10000
        src_data[31] = round(src_data[31] * 0.0001, 5) # AltWeightedAvgOfferPrice uint32 债券申卖加权均价 /10000
        return src_data
    except Exception as e:
        print("PreTransStockLtbMarket error:", e)

def PreTransIndexLtbMarket(tmp_data): # LTB指数快照预处理
    try:
        src_data = tmp_data.astype(define.stock_ltb_market_i_type_src)
        src_data[5] = round(src_data[5] * 0.0001, 5) # Last int32 最新指数 /10000
        src_data[6] = round(src_data[6] * 0.0001, 5) # Open int32 开盘指数 /10000
        src_data[7] = round(src_data[7] * 0.0001, 5) # High int32 最高指数 /10000
        src_data[8] = round(src_data[8] * 0.0001, 5) # Low int32 最低指数 /10000
        src_data[9] = round(src_data[9] * 0.0001, 5) # Close uint32 收盘指数 /10000
        src_data[10] = round(src_data[10] * 0.0001, 5) # PreClose int32 昨收指数 /10000
        src_data[12] = round(src_data[12] * 0.0001, 5) # Turnover int64 成交额 /10000
        return src_data
    except Exception as e:
        print("PreTransIndexLtbMarket error:", e)

def PreTransTransLtbMarket(tmp_data): # LTB逐笔成交预处理
    try:
        src_data = tmp_data.astype(define.stock_ltb_market_t_type_src)
        src_data[5] = round(src_data[5] * 0.0001, 5) # Price uint32 成交价 /10000
        src_data[7] = round(src_data[7] * 0.0001, 5) # Turnover int64 成交额 /10000
        return src_data
    except Exception as e:
        print("PreTransTransLtbMarket error:", e)

def PreTransStockLtpMarket(tmp_data): # LTP个股快照预处理 //与 preTransStockTdfMarket 相同
    try:
        src_data = tmp_data.astype(define.stock_ltp_market_s_type_src)
        src_data[5] = round(src_data[5] * 0.0001, 5) # Last uint32 最新价 /10000
        src_data[6] = round(src_data[6] * 0.0001, 5) # Open uint32 开盘价 /10000
        src_data[7] = round(src_data[7] * 0.0001, 5) # High uint32 最高价 /10000
        src_data[8] = round(src_data[8] * 0.0001, 5) # Low uint32 最低价 /10000
        src_data[9] = round(src_data[9] * 0.0001, 5) # Close uint32 收盘价 /10000
        src_data[10] = round(src_data[10] * 0.0001, 5) # PreClose uint32 昨收价 /10000
        src_data[12] = round(src_data[12] * 0.0001, 5) # Turnover int64 成交额 /10000
        src_data[13][0] = round(src_data[13][0] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][1] = round(src_data[13][1] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][2] = round(src_data[13][2] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][3] = round(src_data[13][3] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][4] = round(src_data[13][4] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][5] = round(src_data[13][5] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][6] = round(src_data[13][6] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][7] = round(src_data[13][7] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][8] = round(src_data[13][8] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][9] = round(src_data[13][9] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[15][0] = round(src_data[15][0] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][1] = round(src_data[15][1] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][2] = round(src_data[15][2] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][3] = round(src_data[15][3] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][4] = round(src_data[15][4] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][5] = round(src_data[15][5] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][6] = round(src_data[15][6] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][7] = round(src_data[15][7] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][8] = round(src_data[15][8] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][9] = round(src_data[15][9] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[17] = round(src_data[17] * 0.0001, 5) # HighLimit uint32 涨停价 /10000
        src_data[18] = round(src_data[18] * 0.0001, 5) # LowLimit uint32 跌停价 /10000
        src_data[21] = round(src_data[21] * 0.0001, 5) # WeightedAvgBidPrice uint32 加权平均委买价格 /10000
        src_data[22] = round(src_data[22] * 0.0001, 5) # WeightedAvgAskPrice uint32 加权平均委卖价格 /10000
        src_data[24] = round(src_data[24] * 0.0001, 5) # IOPV int32 IOPV 净值估值 /10000
        src_data[25] = round(src_data[25] * 0.0001, 5) # YieldRate int32 到期收益率 /10000
        src_data[26] = round(src_data[26] * 0.0001, 5) # PeRate_1 int32 市盈率 1 /10000
        src_data[27] = round(src_data[27] * 0.0001, 5) # PeRate_2 int32 市盈率 2 /10000
        return src_data
    except Exception as e:
        print("PreTransStockLtpMarket error:", e)

def PreTransIndexLtpMarket(tmp_data): # LTP指数快照预处理 //与 preTransIndexTdfMarket 相同
    try:
        src_data = tmp_data.astype(define.stock_ltp_market_i_type_src)
        src_data[5] = round(src_data[5] * 0.0001, 5) # Last int32 最新指数 /10000
        src_data[6] = round(src_data[6] * 0.0001, 5) # Open int32 开盘指数 /10000
        src_data[7] = round(src_data[7] * 0.0001, 5) # High int32 最高指数 /10000
        src_data[8] = round(src_data[8] * 0.0001, 5) # Low int32 最低指数 /10000
        src_data[9] = round(src_data[9] * 0.0001, 5) # Close uint32 收盘指数 /10000
        src_data[10] = round(src_data[10] * 0.0001, 5) # PreClose int32 昨收指数 /10000
        src_data[12] = round(src_data[12] * 0.0001, 5) # Turnover int64 成交额 /10000
        return src_data
    except Exception as e:
        print("PreTransIndexLtpMarket error:", e)

def PreTransTransLtpMarket(tmp_data): # LTP逐笔成交预处理 //与 preTransTransTdfMarket 相同
    try:
        src_data = tmp_data.astype(define.stock_ltp_market_t_type_src)
        src_data[5] = round(src_data[5] * 0.0001, 5) # Price uint32 成交价 /10000
        src_data[7] = round(src_data[7] * 0.0001, 5) # Turnover int64 成交额 /10000
        return src_data
    except Exception as e:
        print("PreTransTransLtpMarket error:", e)

def PreTransStockHgtSgtMarket(tmp_data): # HGT/SGT个股快照预处理
    try:
        src_data = tmp_data.astype(define.stock_hgt_sgt_market_s_type_src)
        src_data[5] = round(src_data[5] * 0.0001, 5) # Last uint32 最新价 /10000
        src_data[6] = round(src_data[6] * 0.0001, 5) # Open uint32 开盘价 /10000
        src_data[7] = round(src_data[7] * 0.0001, 5) # High uint32 最高价 /10000
        src_data[8] = round(src_data[8] * 0.0001, 5) # Low uint32 最低价 /10000
        src_data[9] = round(src_data[9] * 0.0001, 5) # Close uint32 收盘价 /10000
        src_data[10] = round(src_data[10] * 0.0001, 5) # PreClose uint32 昨收价 /10000
        src_data[12] = round(src_data[12] * 0.0001, 5) # Turnover int64 成交额 /10000
        src_data[13][0] = round(src_data[13][0] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][1] = round(src_data[13][1] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][2] = round(src_data[13][2] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][3] = round(src_data[13][3] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][4] = round(src_data[13][4] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][5] = round(src_data[13][5] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][6] = round(src_data[13][6] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][7] = round(src_data[13][7] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][8] = round(src_data[13][8] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[13][9] = round(src_data[13][9] * 0.0001, 5) # AskPrice[10] uint32 申卖价 /10000
        src_data[15][0] = round(src_data[15][0] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][1] = round(src_data[15][1] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][2] = round(src_data[15][2] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][3] = round(src_data[15][3] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][4] = round(src_data[15][4] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][5] = round(src_data[15][5] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][6] = round(src_data[15][6] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][7] = round(src_data[15][7] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][8] = round(src_data[15][8] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[15][9] = round(src_data[15][9] * 0.0001, 5) # BidPrice[10] uint32 申买价 /10000
        src_data[17] = round(src_data[17] * 0.0001, 5) # HighLimit uint32 涨停价 /10000
        src_data[18] = round(src_data[18] * 0.0001, 5) # LowLimit uint32 跌停价 /10000
        return src_data
    except Exception as e:
        print("PreTransStockHgtSgtMarket error:", e)

def PreTransFutureMarket(tmp_data): # 期货内盘快照预处理
    try:
        src_data = tmp_data.astype(define.future_np_market_type_src)
        src_data[5] = round(src_data[5] * 0.0001, 5) # Last uint32 最新价 /10000
        src_data[6] = round(src_data[6] * 0.0001, 5) # Open uint32 开盘价 /10000
        src_data[7] = round(src_data[7] * 0.0001, 5) # High uint32 最高价 /10000
        src_data[8] = round(src_data[8] * 0.0001, 5) # Low uint32 最低价 /10000
        src_data[9] = round(src_data[9] * 0.0001, 5) # Close uint32 收盘价 /10000
        src_data[10] = round(src_data[10] * 0.0001, 5) # PreClose uint32 昨收价 /10000
        src_data[12] = round(src_data[12] * 0.0001, 5) # Turnover int64 成交额 /10000
        src_data[13][0] = round(src_data[13][0] * 0.0001, 5) # AskPrice[5] uint32 申卖价 /10000
        src_data[13][1] = round(src_data[13][1] * 0.0001, 5) # AskPrice[5] uint32 申卖价 /10000
        src_data[13][2] = round(src_data[13][2] * 0.0001, 5) # AskPrice[5] uint32 申卖价 /10000
        src_data[13][3] = round(src_data[13][3] * 0.0001, 5) # AskPrice[5] uint32 申卖价 /10000
        src_data[13][4] = round(src_data[13][4] * 0.0001, 5) # AskPrice[5] uint32 申卖价 /10000
        src_data[15][0] = round(src_data[15][0] * 0.0001, 5) # BidPrice[5] uint32 申买价 /10000
        src_data[15][1] = round(src_data[15][1] * 0.0001, 5) # BidPrice[5] uint32 申买价 /10000
        src_data[15][2] = round(src_data[15][2] * 0.0001, 5) # BidPrice[5] uint32 申买价 /10000
        src_data[15][3] = round(src_data[15][3] * 0.0001, 5) # BidPrice[5] uint32 申买价 /10000
        src_data[15][4] = round(src_data[15][4] * 0.0001, 5) # BidPrice[5] uint32 申买价 /10000
        src_data[17] = round(src_data[17] * 0.0001, 5) # HighLimit uint32 涨停价 /10000
        src_data[18] = round(src_data[18] * 0.0001, 5) # LowLimit uint32 跌停价 /10000
        src_data[19] = round(src_data[19] * 0.0001, 5) # Settle uint32 今日结算价 /10000
        src_data[20] = round(src_data[20] * 0.0001, 5) # PreSettle uint32 昨日结算价 /10000 
        src_data[23] = round(src_data[23] * 0.0001, 5) # Average uint32 均价 /10000
        src_data[24] = round(src_data[24] * 0.0001, 5) # UpDown int32 涨跌 /10000
        src_data[25] = round(src_data[25] * 0.0001, 5) # UpDownRate int32 涨跌幅度 /10000
        src_data[26] = round(src_data[26] * 0.0001, 5) # Swing int32 振幅 /10000
        src_data[27] = round(src_data[27] * 0.0001, 5) # Delta int32 今日虚实度 /10000
        src_data[28] = round(src_data[28] * 0.0001, 5) # PreDelta int32 昨日虚实度 /10000
        return src_data
    except Exception as e:
        print("PreTransFutureMarket error:", e)

def TransStrategyState(straState): # 策略状态
    if straState == 0:
        return "已加载"
    elif straState == 1:
        return "运行中"
    elif straState == 2:
        return "已暂停"
    elif straState == 3:
        return "已停止"
    elif straState == 4:
        return "已异常"
    else:
        return "未知！"

def TransSecurityCategory(category): #
    if category == 0:
        return "未知"
    elif category == 1:
        return "沪A主板"
    elif category == 2:
        return "深A主板"
    elif category == 3:
        return "深A中小板"
    elif category == 4:
        return "深A创业板"
    elif category == 5:
        return "沪ETF基金"
    elif category == 6:
        return "深ETF基金"
    elif category == 7:
        return "沪LOF基金"
    elif category == 8:
        return "深LOF基金"
    elif category == 9:
        return "沪分级子基金"
    elif category == 10:
        return "深分级子基金"
    elif category == 11:
        return "沪封闭式基金"
    elif category == 12:
        return "深封闭式基金"
    # 13, 14
    elif category == 15:
        return "沪固收基金"
    elif category == 16:
        return "深固收基金"
    else:
        return "？？？"

def TransSecuritySector(sector): #
    if sector == 1:
        return "主板"
    elif sector == 2:
        return "中小板"
    elif sector == 3:
        return "创业板"
    else:
        return "？？？"

def TransSecurityST(is_st): #
    if is_st == 0:
        return "否"
    elif is_st == 1:
        return "是"
    else:
        return "？"

def TransSecurityListState(list_state): #
    if list_state == 1:
        return "上市"
    elif list_state == 2:
        return "暂停"
    elif list_state == 3:
        return "终止"
    elif list_state == 4:
        return "其他"
    elif list_state == 5:
        return "交易"
    elif list_state == 6:
        return "停牌"
    elif list_state == 7:
        return "摘牌"
    else:
        return "？？"

def TransOrderStatus_STK(order_status): #
    if order_status == 0:
        return "尚未申报"
    elif order_status == 1:
        return "正在申报"
    elif order_status == 2:
        return "已报未成"
    elif order_status == 3:
        return "非法委托"
    elif order_status == 4:
        return "资金授权"
    elif order_status == 5:
        return "部分成交"
    elif order_status == 6:
        return "全部成交"
    elif order_status == 7:
        return "部成部撤"
    elif order_status == 8:
        return "全部撤单"
    elif order_status == 9:
        return "撤单未成"
    elif order_status == 10:
        return "人工申报"
    else:
        return "？？？"

def TransTradeStage_STK(trade_stage): #
    if trade_stage == 0:
        return "初始化"
    elif trade_stage == 1:
        return "交易中"
    elif trade_stage == 2:
        return "撤单中"
    elif trade_stage == 3:
        return "已完成"
    elif trade_stage == 4:
        return "有异常"
    elif trade_stage == 5:
        return "等资金"
    elif trade_stage == 6:
        return "等行情"
    elif trade_stage == 7:
        return "已涨停"
    elif trade_stage == 8:
        return "已跌停"
    elif trade_stage == 9:
        return "已终止"
    else:
        return "-"
