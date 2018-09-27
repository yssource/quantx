
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

import os
import re
import threading
from datetime import datetime

import numpy as np
import pandas as pd
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QTextEdit, QHBoxLayout, QVBoxLayout

import common
import dbm_mssql
import dbm_mysql

pd.set_option("max_colwidth", 200)
pd.set_option("display.width", 500)

DEF_EVENT_TEXT_INFO_PRINT = 1001

class CapitalItem(object):
    def __init__(self, **kwargs):
        self.inners = kwargs.get("inners", 0) # 内部代码
        self.market = kwargs.get("market", "") #֤ 证券市场
        self.code = kwargs.get("code", "") # 证券代码
        self.name = kwargs.get("name", "") # 证券名称
        self.end_date = kwargs.get("end_date", 0) # 截止日期
        self.total_shares = kwargs.get("total_shares", -1) # 总股本
        self.circu_shares = kwargs.get("circu_shares", -1) # 流通股本(A股)

    def SetEndDate(self, date): # 截止日期
        if date != None:
            self.end_date = date.year * 10000 + date.month * 100 + date.day

class ExRightsItem(object):
    def __init__(self, **kwargs):
        self.inners = kwargs.get("inners", 0) # 内部代码
        self.market = kwargs.get("market", "") #֤ 证券市场
        self.code = kwargs.get("code", "") # 证券代码
        self.date = kwargs.get("date", 0) # 除权除息日期
        self.muler = 0.0 # 乘数
        self.adder = 0.0 # 加数
        self.sg = 0.0 # 送股比率，每股
        self.pg = 0.0 # 配股比率，每股
        self.price = 0.0 # 配股价
        self.bonus = 0.0 # 现金红利

class IndustryItem(object):
    def __init__(self, **kwargs):
        self.standard = kwargs.get("standard", 0) # 行业划分标准
        self.industry = kwargs.get("industry", 0) # 所属行业
        self.industry_code_1 = kwargs.get("industry_code_1", "") # 一级行业代码
        self.industry_name_1 = kwargs.get("industry_name_1", "") # 一级行业名称
        self.industry_code_2 = kwargs.get("industry_code_2", "") # 二级行业代码
        self.industry_name_2 = kwargs.get("industry_name_2", "") # 二级行业名称
        self.industry_code_3 = kwargs.get("industry_code_3", "") # 三级行业代码
        self.industry_name_3 = kwargs.get("industry_name_3", "") # 三级行业名称
        self.industry_code_4 = kwargs.get("industry_code_4", "") # 四级行业代码
        self.industry_name_4 = kwargs.get("industry_name_4", "") # 四级行业名称
        self.inners = kwargs.get("inners", 0) # 证券内部编码
        self.market = kwargs.get("market", "") # 证券市场
        self.code = kwargs.get("code", "") # 证券代码
        self.name = kwargs.get("name", "") # 证券名称
        self.info_date = kwargs.get("info_date", 0) # 信息发布日期

    def SetInfoDate(self, date):
        if date != None:
            self.info_date = date.year * 10000 + date.month * 100 + date.day

    def SetIndustryCodeName_HK(self, classification, code, name):
        if classification == 1:
            self.industry_code_1 = "%d" % code
            self.industry_name_1 = name
        elif classification == 2:
            self.industry_code_2 = "%d" % code
            self.industry_name_2 = name
        elif classification == 3:
            self.industry_code_3 = "%d" % code
            self.industry_name_3 = name
        elif classification == 4:
            self.industry_code_4 = "%d" % code
            self.industry_name_4 = name

class PreQuoteStkItem(object):
    def __init__(self, **kwargs):
        self.inners = kwargs.get("inners", 0) # 内部代码
        self.market = kwargs.get("market", "")
        self.code = kwargs.get("code", "")
        self.name = kwargs.get("name", "")
        self.category = kwargs.get("category", 0)
        self.open = kwargs.get("open", 0.0)
        self.high = kwargs.get("high", 0.0)
        self.low = kwargs.get("low", 0.0)
        self.close = kwargs.get("close", 0.0)
        self.pre_close = kwargs.get("pre_close", 0.0)
        self.volume = kwargs.get("volume", 0) # 成交量，股
        self.turnover = kwargs.get("turnover", 0.0) # 成交额，元
        self.trade_count = kwargs.get("trade_count", 0) # 成交笔数
        self.quote_date = kwargs.get("quote_date", 0) # YYYYMMDD
        self.quote_time = kwargs.get("quote_time", 0) # HHMMSSmmm 精度：毫秒

    def SetCategory(self, category, symbol):
        if category == 1: # A股
            self.category = 1
        elif category == 62: # ETF基金 # 测试显示ETF基金的证券类别也全部被标记为 8 的
            self.category = 2
        elif category == 8: # 开放式基金
            if symbol[0:2] == "51" or symbol[0:3] == "159": # ETF基金
                self.category = 2
            elif symbol[0:3] == "502" or symbol[0:3] == "150": # 分级基金
                self.category = 3
            else: # 普通开放式基金
                self.category = 4

    def SetCategory_HK(self, category, symbol):
        if category == 3: # H股
            self.category = 21 # 港股个股
        elif category == 4: # 大盘(指数)
            self.category = 22 # 港股指数
        elif category == 51: # 港股
            self.category = 21 # 港股个股
        elif category == 52: # 合订证券
            self.category = 21 # 港股个股
        elif category == 53: # 红筹股
            self.category = 21 # 港股个股
        elif category == 62: # ETF基金
            self.category = 23 # 港股ETF基金

    def SetQuoteDate(self, date):
        if date != None:
            self.quote_date = date.year * 10000 + date.month * 100 + date.day

    def SetQuoteTime(self, time):
        if time != None:
            self.quote_time = time.hour * 10000000 + time.minute * 100000 + time.second * 1000 + time.microsecond / 1000

class PreQuoteFueItem(object):
    def __init__(self, **kwargs):
        self.inners = kwargs.get("inners", 0) # 内部代码
        self.market = kwargs.get("market", "")
        self.code = kwargs.get("code", "")
        self.open = kwargs.get("open", 0.0)
        self.high = kwargs.get("high", 0.0)
        self.low = kwargs.get("low", 0.0)
        self.close = kwargs.get("close", 0.0)
        self.settle = kwargs.get("settle", 0.0)
        self.pre_close = kwargs.get("pre_close", 0.0)
        self.pre_settle = kwargs.get("pre_settle", 0.0)
        self.volume = kwargs.get("volume", 0) # 成交量，手
        self.turnover = kwargs.get("turnover", 0.0) # 成交额，元
        self.open_interest = kwargs.get("open_interest", 0) # 持仓量，手
        self.chg_open_interest = kwargs.get("chg_open_interest", 0) # 持仓量变化，手
        self.basis_value = kwargs.get("basis_value", 0.0) # 基差
        self.main_flag = kwargs.get("main_flag", 0) # 主力标志
        self.quote_date = kwargs.get("quote_date", 0) # YYYYMMDD
        self.quote_time = kwargs.get("quote_time", 0) # HHMMSSmmm 精度：毫秒

    def SetQuoteDate(self, date):
        if date != None:
            self.quote_date = date.year * 10000 + date.month * 100 + date.day

    def SetQuoteTime(self, time):
        if time != None:
            self.quote_time = time.hour * 10000000 + time.minute * 100000 + time.second * 1000 + time.microsecond / 1000

class SecurityInfoItem(object):
    def __init__(self, **kwargs):
        self.inners = kwargs.get("inners", 0) # 内部代码
        self.company = kwargs.get("company", 0) # 公司代码
        self.market = kwargs.get("market", "") #֤ 证券市场
        self.code = kwargs.get("code", "") # 证券代码
        self.name = kwargs.get("name", "") # 证券名称
        self.category = kwargs.get("category", 0) # 证券类别
        self.sector = kwargs.get("sector", 0) # 上市板块
        self.is_st = kwargs.get("is_st", 0) # 是否ST股
        self.trade_unit = kwargs.get("trade_unit", 0) # 买卖单位
        self.min_price_chg = kwargs.get("min_price_chg", 0.0) # 最小变动价格
        self.list_state = kwargs.get("list_state", 0) # 上市状态
        self.list_date = kwargs.get("list_date", 0) # 上市日期

    # 0 ：未知
    # 1 ：沪A主板
    # 2 ：深A主板
    # 3 ：深A中小板
    # 4 ：深A创业板
    # 5 ：沪ETF基金
    # 6 ：深ETF基金
    # 7 ：沪LOF基金
    # 8 ：深LOF基金
    # 9 ：沪分级子基金
    # 10：深分级子基金
    # 11：沪封闭式基金
    # 12：深封闭式基金
    # 13：沪ST股
    # 14：深ST股
    # 15：沪固收基金
    # 16：深固收基金

    def SetFlag_LB(self, category, market, symbol, sector): # 证券类别
        if market == 83: # 上海，SH
            if category == 1: # A股
                if sector == 1: # 主板
                    self.category = 1 # 沪A主板
            elif category == 8: # 开放式基金
                if symbol[0:2] == "51": # ETF基金
                    if symbol[0:3] == "511": # 固收基金
                        self.category = 15 # 沪固收基金
                    else: # 512XXX、513XXX、518XXX
                        self.category = 5 # 沪ETF基金
                elif symbol[0:2] == "50": # LOF基金(普通开放式) # 其501和502中的502为分级母基金
                    self.category = 7 # 沪LOF基金
            elif category == 13: # 投资基金
                if symbol[0:3] == "502": # 分级子基金
                    self.category = 9 # 沪分级子基金
                elif symbol[0:3] == "505": # 封闭式基金 # 目前只有一个505888嘉实元和
                    self.category = 11 # 沪封闭式基金
            elif category == 62: # ETF基金 # 测试显示ETF基金的证券类别全部被标记为 8 而非 62
                self.category = 5 # 沪ETF基金
        elif market == 90: # 深圳，SZ
            if category == 1: # A股
                if sector == 1: # 主板
                    self.category = 2 # 深A主板
                elif sector == 2: # 中小企业板
                    self.category = 3 # 深A中小板
                elif sector == 6: # 创业板
                    self.category = 4 # 深A创业板
            elif category == 8: # 开放式基金
                if symbol[0:3] == "159": # ETF基金
                    if symbol[0:4] == "1590": # 固收基金
                        self.category = 16 # 深固收基金
                    else: # 1599XX
                        self.category = 6 # 深ETF基金
                elif symbol[0:2] == "16": # LOF基金(普通开放式) # 含分级母基金
                    self.category = 8 # 深LOF基金
            elif category == 13: # 投资基金
                if symbol[0:3] == "150": # 分级子基金
                    self.category = 10 # 深分级子基金
                elif symbol[0:3] == "184": # 封闭式基金 # 目前只有一个184801鹏华万科
                    self.category = 12 # 深封闭式基金
            elif category == 62: # ETF基金 # 测试显示ETF基金的证券类别全部被标记为 8 而非 62
                self.category = 6 # 深ETF基金
        elif market == 72: # 港股，HK
            if category == 3: # H股
                self.category = 21 # 港股个股
            elif category == 4: # 大盘(指数)
                self.category = 22 # 港股指数
            elif category == 51: # 港股
                self.category = 21 # 港股个股
            elif category == 52: # 合订证券
                self.category = 21 # 港股个股
            elif category == 53: # 红筹股
                self.category = 21 # 港股个股
            elif category == 62: # ETF基金
                self.category = 23 # 港股ETF基金

    def SetFlag_BK(self, sector): # 上市板块
        if sector == 1: # 主板
            self.sector = 1
        elif sector == 2: # 中小企业板
            self.sector = 2
        elif sector == 6: # 创业板
            self.sector = 3

    # *   ：退市警示
    # S   ：还没完成股改
    # N   ：上市首日新股
    # ST  ：连续两年亏损
    # SST ：连续两年亏损，还没完成股改
    # *ST ：连续三年亏损，退市风险预警
    # S*ST：连续三年亏损，还没完成股改，退市风险预警
    # NST ：经过重组或股改重新恢复上市的ST股
    # XR  ：表示已经除权，购买这样的股票不再享有分红的权利
    # XD  ：表示已经除息，购买这样的股票不再享有派息的权利
    # DR  ：表示除权除息，购买这样的股票不再享有送股派息的权利

    def SetFlag_ST(self, symbol): # 是否ST股
        if symbol[0:1].upper() == "*" or symbol[0:2].upper() == "ST" or symbol[0:3].upper() == "SST" or symbol[0:3].upper() == "*ST" or symbol[0:3].upper() == "NST" or symbol[0:4].upper() == "S*ST": # 为ST类股
            self.is_st = 1

    def SetFlag_ZT(self, state): # 上市状态
        if state == 1: # 上市
            self.list_state = 1
        elif state == 3: # 暂停
            self.list_state = 2
        elif state == 5: # 终止
            self.list_state = 3
        elif state == 9: # 其他
            self.list_state = 4
        elif state == 10: # 交易
            self.list_state = 5
        elif state == 11: # 停牌
            self.list_state = 6
        elif state == 12: # 摘牌
            self.list_state = 7

    def SetListDate(self, date): # 上市日期
        if date != None:
            self.list_date = date.year * 10000 + date.month * 100 + date.day

class TingPaiStockItem(object):
    def __init__(self, **kwargs):
        self.inners = kwargs.get("inners", 0) # 内部代码
        self.market = kwargs.get("market", "")
        self.code = kwargs.get("code", "")
        self.name = kwargs.get("name", "")
        self.category = kwargs.get("category", 0)
        self.tp_date = kwargs.get("tp_date", datetime(1900, 1, 1)) # 停牌日期
        self.tp_time = kwargs.get("tp_time", "") # 停牌时间
        self.tp_reason = kwargs.get("tp_reason", "") # 停牌原因
        self.tp_statement = kwargs.get("tp_statement", 0) # 停牌事项说明
        self.tp_term = kwargs.get("tp_term", "") # 停牌期限
        self.fp_date = kwargs.get("fp_date", datetime(1900, 1, 1)) # 复牌日期
        self.fp_time = kwargs.get("fp_time", "") # 复牌时间
        self.fp_statement = kwargs.get("fp_statement", 0) # 复牌事项说明
        self.update_time = kwargs.get("update_time", datetime(1900, 1, 1))

    def SetCategory(self, category, symbol):
        if category == 1: # A股
            self.category = 1
        elif category == 62: # ETF基金 # 测试显示ETF基金的证券类别也全部被标记为 8 的
            self.category = 2
        elif category == 8: # 开放式基金
            if symbol[0:2] == "51" or symbol[0:3] == "159": # ETF基金
                self.category = 2
            elif symbol[0:3] == "502" or symbol[0:3] == "150": # 分级基金
                self.category = 3
            else: # 普通开放式基金
                self.category = 4

class TradingDayItem(object):
    def __init__(self, **kwargs):
        self.natural_date = kwargs.get("natural_date", 0) # 日期
        self.market = kwargs.get("market", 0) #֤ 证券市场，72、83、89
        self.trading_day = kwargs.get("trading_day", 0) # 是否交易
        self.week_end = kwargs.get("week_end", 0) # 是否周末
        self.month_end = kwargs.get("month_end", 0) # 是否月末
        self.quarter_end = kwargs.get("quarter_end", 0) # 是否季末
        self.year_end = kwargs.get("year_end", 0) # 是否年末

    def SetNaturalDate(self, date):
        if date != None:
            self.natural_date = date.year * 10000 + date.month * 100 + date.day

class ExchangeRateItem(object):
    def __init__(self, **kwargs):
        self.base_money = kwargs.get("base_money", "") #֤ 基础货币
        self.price = kwargs.get("price", 0.0) # 汇率价格
        self.exchange_money = kwargs.get("exchange_money", "") #֤ 汇兑货币
        self.quote_type = kwargs.get("quote_type", 0) # 标价方式
        self.end_date = kwargs.get("end_date", 0) # 截止日期

    def SetEndDate(self, date): # 截止日期
        if date != None:
            self.end_date = date.year * 10000 + date.month * 100 + date.day

class ComponentHsggtItem(object):
    def __init__(self, **kwargs):
        self.inners = kwargs.get("inners", 0) # 内部代码
        self.market = kwargs.get("market", "")
        self.code = kwargs.get("code", "")
        self.name = kwargs.get("name", "")
        self.category = kwargs.get("category", 0)
        self.comp_type = kwargs.get("comp_type", 0) # 成分类别
        self.update_time = kwargs.get("update_time", datetime(1900, 1, 1))

    def SetCategory(self, category, symbol):
        if category == 1: # A股
            self.category = 1
        elif category == 3: # H股
            self.category = 21 # 港股个股
        elif category == 51: # 港股
            self.category = 21 # 港股个股
        elif category == 52: # 合订证券
            self.category = 21 # 港股个股
        elif category == 53: # 红筹股
            self.category = 21 # 港股个股

class DataMaker_Capital():
    def __init__(self, parent = None):
        self.parent = parent
        self.capital_dict = {}
        self.count_zgb_none = 0 # 总股本缺失
        self.count_ltgb_none = 0 # 流通股本缺失
        self.count_zgb_zero = 0 # 总股本为零
        self.count_ltgb_zero = 0 # 流通股本为零
        self.count_zgb_ltgb = 0 # 全流通计数
        self.count_jzrq_none = 0 # 截止日期缺失

    def SendMessage(self, text_info):
        if self.parent != None:
            self.parent.SendMessage(text_info)

    def CheckStockGuBen(self):
        for item in self.capital_dict.values():
            if item.total_shares == -1:
                self.count_zgb_none += 1
                self.SendMessage("总股本缺失：%s %s" % (item.market, item.code))
            elif item.total_shares == 0:
                self.count_zgb_zero += 1
                self.SendMessage("总股本为零：%s %s" % (item.market, item.code))
            if item.circu_shares == -1:
                self.count_ltgb_none += 1
                self.SendMessage("流通股本缺失：%s %s" % (item.market, item.code))
            elif item.circu_shares == 0:
                self.count_ltgb_zero += 1
                self.SendMessage("流通股本为零：%s %s" % (item.market, item.code))
            if item.total_shares == item.circu_shares:
                self.count_zgb_ltgb += 1
            if item.end_date == 0:
                self.count_jzrq_none += 1
        self.SendMessage("总计：%s" % len(self.capital_dict))
        self.SendMessage("总股本缺失：%s" % self.count_zgb_none)
        self.SendMessage("总股本为零：%s" % self.count_zgb_zero)
        self.SendMessage("流通股本缺失：%s" % self.count_ltgb_none)
        self.SendMessage("流通股本为零：%s" % self.count_ltgb_zero)
        self.SendMessage("全流通股票：%s" % self.count_zgb_ltgb)
        self.SendMessage("截止日期缺失：%s" % self.count_jzrq_none)

    def PullData_Capital(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_Capital 数据库 dbm 尚未连接！")
            return
        # 证券市场：83 上海证券交易所、90 深圳证券交易所
        # 证券类别：1 A股
        # 上市板块：1 主板、2 中小企业板、6 创业板
        # 查询字段：SecuMain：证券内部编码、证券代码、证券简称、证券市场
        # 查询字段：LC_ShareStru：截止日期、总股本(股)、已上市流通A股(股)
        # 唯一约束：SecuMain = InnerCode、LC_ShareStru = CompanyCode & EndDate
        sql = "SELECT SecuMain.InnerCode, SecuMain.SecuCode, SecuMain.SecuAbbr, SecuMain.SecuMarket, LC_ShareStru.EndDate, LC_ShareStru.TotalShares, LC_ShareStru.AFloatListed \
               FROM SecuMain INNER JOIN LC_ShareStru \
               ON SecuMain.CompanyCode = LC_ShareStru.CompanyCode \
               WHERE (SecuMain.SecuMarket = 83 OR SecuMain.SecuMarket = 90) \
                   AND (SecuMain.SecuCategory = 1) \
                   AND (SecuMain.ListedSector = 1 OR SecuMain.ListedSector = 2 OR SecuMain.ListedSector = 6) \
                   AND CAST(LC_ShareStru.CompanyCode AS nvarchar) + CAST(LC_ShareStru.EndDate AS nvarchar) IN \
                       ( \
                           SELECT CAST(CompanyCode AS nvarchar) + CAST(MAX(EndDate) AS nvarchar) \
                           FROM LC_ShareStru \
                           GROUP BY CompanyCode \
                       ) \
               ORDER BY SecuMain.SecuMarket ASC, SecuMain.SecuCode ASC"
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (InnerCode, SecuCode, SecuAbbr, SecuMarket, EndDate, TotalShares, AFloatListed) in result_list:
                if not SecuCode[0] == "X": # 排除未上市的新股
                    stock_market = ""
                    if SecuMarket == 83:
                        stock_market = "SH"
                    elif SecuMarket == 90:
                        stock_market = "SZ"
                    capital_item = CapitalItem(inners = InnerCode, market = stock_market, code = SecuCode, name = SecuAbbr)
                    capital_item.SetEndDate(EndDate) # 截止日期
                    if TotalShares != None:
                        capital_item.total_shares = TotalShares
                    if AFloatListed != None:
                        capital_item.circu_shares = AFloatListed
                    self.capital_dict[InnerCode] = capital_item
                    #print(InnerCode, SecuCode, SecuAbbr, SecuMarket, EndDate, TotalShares, AFloatListed)
            self.SendMessage("获取 股本结构 成功。总计 %d 个。" % len(result_list))
            self.CheckStockGuBen()
        else:
            self.SendMessage("获取 股本结构 失败！")

    def SaveData_Capital(self, dbm, table_name, save_path):
        capital_keys = list(self.capital_dict.keys())
        capital_keys.sort()
        capital_dict_list = [self.capital_dict[key] for key in capital_keys]
        total_record_num = len(capital_dict_list)
        values_list = []
        for i in range(total_record_num):
            str_date = common.TransDateIntToStr(capital_dict_list[i].end_date)
            values_list.append((capital_dict_list[i].inners, capital_dict_list[i].market, capital_dict_list[i].code, capital_dict_list[i].name, str_date, capital_dict_list[i].total_shares, capital_dict_list[i].circu_shares))
        columns = ["inners", "market", "code", "name", "end_date", "total_shares", "circu_shares"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values_list) > 0:
            result = pd.DataFrame(data = values_list, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("本地保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))
        if dbm != None:
            sql = "CREATE TABLE `%s` (" % table_name + \
                  "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                  "`inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码'," + \
                  "`market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，SH、SZ'," + \
                  "`code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码'," + \
                  "`name` varchar(32) DEFAULT '' COMMENT '证券名称'," + \
                  "`end_date` date NOT NULL COMMENT '截止日期'," + \
                  "`total_shares` bigint(64) DEFAULT '0' COMMENT '总股本，股'," + \
                  "`circu_shares` bigint(64) DEFAULT '0' COMMENT '流通股本，股，A股'," + \
                  "PRIMARY KEY (`id`)," + \
                  "UNIQUE KEY `idx_market_code_end_date` (`market`,`code`,`end_date`)" + \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            if dbm.TruncateOrCreateTable(table_name, sql) == True:
                sql = "INSERT INTO %s" % table_name + "(inners, market, code, name, end_date, total_shares, circu_shares) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                total_record_num, save_record_success, save_record_failed = dbm.BatchInsert(values_list, sql)
                self.SendMessage("远程入库：总记录 %d，入库记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))
            else:
                self.SendMessage("远程入库：初始化数据库表 %s 失败！" % table_name)

class DataMaker_Capital_HK():
    def __init__(self, parent = None):
        self.parent = parent
        self.capital_dict = {}
        self.count_zgb_none = 0 # 总股本缺失
        self.count_ltgb_none = 0 # 流通股本缺失
        self.count_zgb_zero = 0 # 总股本为零
        self.count_ltgb_zero = 0 # 流通股本为零
        self.count_zgb_ltgb = 0 # 全流通计数
        self.count_jzrq_none = 0 # 截止日期缺失

    def SendMessage(self, text_info):
        if self.parent != None:
            self.parent.SendMessage(text_info)

    def CheckStockGuBen(self):
        for item in self.capital_dict.values():
            if item.total_shares == -1:
                self.count_zgb_none += 1
                self.SendMessage("总股本缺失：%s %s" % (item.market, item.code))
            elif item.total_shares == 0:
                self.count_zgb_zero += 1
                self.SendMessage("总股本为零：%s %s" % (item.market, item.code))
            if item.circu_shares == -1:
                self.count_ltgb_none += 1
                self.SendMessage("流通股本缺失：%s %s" % (item.market, item.code))
            elif item.circu_shares == 0:
                self.count_ltgb_zero += 1
                self.SendMessage("流通股本为零：%s %s" % (item.market, item.code))
            if item.total_shares == item.circu_shares:
                self.count_zgb_ltgb += 1
            if item.end_date == 0:
                self.count_jzrq_none += 1
        self.SendMessage("总计：%s" % len(self.capital_dict))
        self.SendMessage("总股本缺失：%s" % self.count_zgb_none)
        self.SendMessage("总股本为零：%s" % self.count_zgb_zero)
        self.SendMessage("流通股本缺失：%s" % self.count_ltgb_none)
        self.SendMessage("流通股本为零：%s" % self.count_ltgb_zero)
        self.SendMessage("全流通股票：%s" % self.count_zgb_ltgb)
        self.SendMessage("截止日期缺失：%s" % self.count_jzrq_none)

    def PullData_Capital_HK(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_Capital_HK 数据库 dbm 尚未连接！")
            return
        # 证券市场：72 香港联交所
        # 证券类别：3 H股、51 港股、52 合订证券、53 红筹股
        # 上市状态：1 上市、3 暂停
        # 查询字段：HK_SecuMain：证券内部编码、证券代码、证券简称、证券市场
        # 查询字段：HK_ShareStru：截止日期、实收股数(股)、已上市(股)
        # 唯一约束：HK_SecuMain = InnerCode、HK_ShareStru = CompanyCode & EndDate
        sql = "SELECT HK_SecuMain.InnerCode, HK_SecuMain.SecuCode, HK_SecuMain.SecuAbbr, HK_SecuMain.SecuMarket, HK_ShareStru.EndDate, HK_ShareStru.PaidUpSharesComShare, HK_ShareStru.ListedShares \
               FROM HK_SecuMain INNER JOIN HK_ShareStru \
               ON HK_SecuMain.CompanyCode = HK_ShareStru.CompanyCode \
               WHERE (HK_SecuMain.SecuMarket = 72) \
                   AND (HK_SecuMain.SecuCategory = 3 OR HK_SecuMain.SecuCategory = 51 OR HK_SecuMain.SecuCategory = 52 OR HK_SecuMain.SecuCategory = 53) \
                   AND (HK_SecuMain.ListedSector = 1 OR HK_SecuMain.ListedSector = 3) \
                   AND CAST(HK_ShareStru.CompanyCode AS nvarchar) + CAST(HK_ShareStru.EndDate AS nvarchar) IN \
                       ( \
                           SELECT CAST(CompanyCode AS nvarchar) + CAST(MAX(EndDate) AS nvarchar) \
                           FROM HK_ShareStru \
                           GROUP BY CompanyCode \
                       ) \
               ORDER BY HK_SecuMain.SecuMarket ASC, HK_SecuMain.SecuCode ASC"
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (InnerCode, SecuCode, SecuAbbr, SecuMarket, EndDate, PaidUpSharesComShare, ListedShares) in result_list:
                if not SecuCode[0] == "N": # 排除未上市的新股
                    stock_market = "HK"
                    capital_item = CapitalItem(inners = InnerCode, market = stock_market, code = SecuCode, name = SecuAbbr)
                    capital_item.SetEndDate(EndDate) # 截止日期
                    if PaidUpSharesComShare != None:
                        capital_item.total_shares = PaidUpSharesComShare
                    if ListedShares != None:
                        capital_item.circu_shares = ListedShares
                    self.capital_dict[InnerCode] = capital_item
                    #print(InnerCode, SecuCode, SecuAbbr, SecuMarket, EndDate, PaidUpSharesComShare, ListedShares)
            self.SendMessage("获取 股本结构-HK 成功。总计 %d 个。" % len(result_list))
            self.CheckStockGuBen()
        else:
            self.SendMessage("获取 股本结构-HK 失败！")

    def SaveData_Capital_HK(self, dbm, table_name, save_path):
        capital_keys = list(self.capital_dict.keys())
        capital_keys.sort()
        capital_dict_list = [self.capital_dict[key] for key in capital_keys]
        total_record_num = len(capital_dict_list)
        values_list = []
        for i in range(total_record_num):
            str_date = common.TransDateIntToStr(capital_dict_list[i].end_date)
            values_list.append((capital_dict_list[i].inners, capital_dict_list[i].market, capital_dict_list[i].code, capital_dict_list[i].name, str_date, capital_dict_list[i].total_shares, capital_dict_list[i].circu_shares))
        columns = ["inners", "market", "code", "name", "end_date", "total_shares", "circu_shares"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values_list) > 0:
            result = pd.DataFrame(data = values_list, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("本地保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))
        if dbm != None:
            sql = "CREATE TABLE `%s` (" % table_name + \
                  "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                  "`inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码'," + \
                  "`market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，HK'," + \
                  "`code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码'," + \
                  "`name` varchar(32) DEFAULT '' COMMENT '证券名称'," + \
                  "`end_date` date NOT NULL COMMENT '截止日期'," + \
                  "`total_shares` bigint(64) DEFAULT '0' COMMENT '总股本，股'," + \
                  "`circu_shares` bigint(64) DEFAULT '0' COMMENT '流通股本，股，普通股'," + \
                  "PRIMARY KEY (`id`)," + \
                  "UNIQUE KEY `idx_market_code_end_date` (`market`,`code`,`end_date`)" + \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            if dbm.TruncateOrCreateTable(table_name, sql) == True:
                sql = "INSERT INTO %s" % table_name + "(inners, market, code, name, end_date, total_shares, circu_shares) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                total_record_num, save_record_success, save_record_failed = dbm.BatchInsert(values_list, sql)
                self.SendMessage("远程入库：总记录 %d，入库记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))
            else:
                self.SendMessage("远程入库：初始化数据库表 %s 失败！" % table_name)

class DataMaker_ExRights():
    def __init__(self, parent = None):
        self.parent = parent
        self.exrights_dict_sh = {}
        self.exrights_dict_sz = {}

    def SendMessage(self, text_info):
        if self.parent != None:
            self.parent.SendMessage(text_info)

    def PullData_Stock(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_Stock 数据库 dbm 尚未连接！")
            return
        # 证券市场：83 上海证券交易所、90 深圳证券交易所
        # 证券类别：1 A股、8 开放式基金、62 ETF基金
        # 上市板块：1 主板、2 中小企业板、6 创业板
        # 查询字段：SecuMain：证券内部编码、证券代码、证券市场、证券类别、上市板块
        # 唯一约束：SecuMain = InnerCode
        sql = "SELECT SecuMain.InnerCode, SecuMain.SecuCode, SecuMain.SecuMarket, SecuMain.SecuCategory, SecuMain.ListedSector \
               FROM SecuMain \
               WHERE (SecuMain.SecuMarket = 83 OR SecuMain.SecuMarket = 90) \
                   AND (SecuMain.SecuCategory = 1 OR SecuMain.SecuCategory = 8 OR SecuMain.SecuCategory = 62) \
               ORDER BY SecuMain.SecuCode ASC"
        result_list = dbm.ExecQuery(sql)
        stock_count_sh = 0
        stock_count_sz = 0
        if result_list != None:
            for (InnerCode, SecuCode, SecuMarket, SecuCategory, ListedSector) in result_list:
                #print(InnerCode, SecuCode, SecuMarket, SecuCategory, ListedSector)
                if SecuMarket == 83:
                    stock_count_sh += 1
                    self.exrights_dict_sh[SecuCode] = {}
                elif SecuMarket == 90:
                    stock_count_sz += 1
                    self.exrights_dict_sz[SecuCode] = {}
            self.SendMessage("获取证券列表成功。上证 %d 个，深证 %d 个。" % (stock_count_sh, stock_count_sz))
        else:
            self.SendMessage("获取证券列表失败！")

    def PullData_PeiGu(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_PeiGu 数据库 dbm 尚未连接！")
            return
        # 证券市场：83 上海证券交易所、90 深圳证券交易所
        # 证券类别：1 A股、8 开放式基金、62 ETF基金
        # 上市板块：1 主板、2 中小企业板、6 创业板
        # 查询字段：SecuMain：证券内部编码、证券代码、证券市场、证券类别、上市板块
        # 查询字段：LC_ASharePlacement：除权日、实际配股比例(10配X)、每股配股价格(元)
        # 唯一约束：SecuMain = InnerCode、LC_ASharePlacement = InnerCode, InitialInfoPublDate
        sql = "SELECT SecuMain.InnerCode, SecuMain.SecuCode, SecuMain.SecuMarket, SecuMain.SecuCategory, SecuMain.ListedSector, \
                      LC_ASharePlacement.ExRightDate, LC_ASharePlacement.ActualPlaRatio, LC_ASharePlacement.PlaPrice \
               FROM SecuMain INNER JOIN LC_ASharePlacement \
               ON SecuMain.InnerCode = LC_ASharePlacement.InnerCode \
               WHERE (SecuMain.SecuMarket = 83 OR SecuMain.SecuMarket = 90) \
                   AND (SecuMain.SecuCategory = 1 OR SecuMain.SecuCategory = 8 OR SecuMain.SecuCategory = 62) \
                   AND LC_ASharePlacement.ExRightDate IS NOT NULL \
               ORDER BY SecuMain.SecuCode ASC, LC_ASharePlacement.ExRightDate ASC"
        result_list = dbm.ExecQuery(sql)
        datas_count_sh = 0
        datas_count_sz = 0
        if result_list != None:
            for (InnerCode, SecuCode, SecuMarket, SecuCategory, ListedSector, ExRightDate, ActualPlaRatio, PlaPrice) in result_list:
                #print(InnerCode, SecuCode, SecuMarket, SecuCategory, ListedSector, ExRightDate, ActualPlaRatio, PlaPrice)
                #print(InnerCode, SecuCode, ExRightDate, ActualPlaRatio, PlaPrice)
                date = ExRightDate.year * 10000 + ExRightDate.month * 100 + ExRightDate.day
                if SecuMarket == 83:
                    market = "SH"
                    datas_count_sh += 1
                    if not SecuCode in self.exrights_dict_sh.keys():
                        self.exrights_dict_sh[SecuCode] = {}
                    exrights_item_dict = self.exrights_dict_sh[SecuCode]
                    if date in exrights_item_dict.keys():
                        exrights_item = exrights_item_dict[date]
                        if ActualPlaRatio != None:
                            exrights_item.pg = float(ActualPlaRatio) / 10.0
                        if PlaPrice != None:
                            exrights_item.price = float(PlaPrice)
                    else:
                        exrights_item = ExRightsItem(inners = InnerCode, market = market, code = SecuCode, date = date)
                        if ActualPlaRatio != None:
                            exrights_item.pg = float(ActualPlaRatio) / 10.0
                        if PlaPrice != None:
                            exrights_item.price = float(PlaPrice)
                        exrights_item_dict[date] = exrights_item
                elif SecuMarket == 90:
                    market = "SZ"
                    datas_count_sz += 1
                    if not SecuCode in self.exrights_dict_sz.keys():
                        self.exrights_dict_sz[SecuCode] = {}
                    exrights_item_dict = self.exrights_dict_sz[SecuCode]
                    if date in exrights_item_dict.keys():
                        exrights_item = exrights_item_dict[date]
                        if ActualPlaRatio != None:
                            exrights_item.pg = float(ActualPlaRatio) / 10.0
                        if PlaPrice != None:
                            exrights_item.price = float(PlaPrice)
                    else:
                        exrights_item = ExRightsItem(inners = InnerCode, market = market, code = SecuCode, date = date)
                        if ActualPlaRatio != None:
                            exrights_item.pg = float(ActualPlaRatio) / 10.0
                        if PlaPrice != None:
                            exrights_item.price = float(PlaPrice)
                        exrights_item_dict[date] = exrights_item
            self.SendMessage("获取配股数据成功。上证 %d 个，深证 %d 个。" % (datas_count_sh, datas_count_sz))
        else:
            self.SendMessage("获取配股数据失败！")

    def PullData_FenHong(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_FenHong 数据库 dbm 尚未连接！")
            return
        # 证券市场：83 上海证券交易所、90 深圳证券交易所
        # 证券类别：1 A股、8 开放式基金、62 ETF基金
        # 上市板块：1 主板、2 中小企业板、6 创业板
        # 查询字段：SecuMain：证券内部编码、证券代码、证券市场、证券类别、上市板块
        # 查询字段：LC_Dividend：是否分红、除权除息日、送股比例(10送X)、转增股比例(10转增X)、派现(含税/人民币元)
        # 唯一约束：SecuMain = InnerCode、LC_Dividend = InnerCode, EndDate
        sql = "SELECT SecuMain.InnerCode, SecuMain.SecuCode, SecuMain.SecuMarket, SecuMain.SecuCategory, SecuMain.ListedSector, \
                      LC_Dividend.IfDividend, LC_Dividend.ExDiviDate, LC_Dividend.BonusShareRatio, LC_Dividend.TranAddShareRaio, LC_Dividend.CashDiviRMB \
               FROM SecuMain INNER JOIN LC_Dividend \
               ON SecuMain.InnerCode = LC_Dividend.InnerCode \
               WHERE (SecuMain.SecuMarket = 83 OR SecuMain.SecuMarket = 90) \
                   AND (SecuMain.SecuCategory = 1 OR SecuMain.SecuCategory = 8 OR SecuMain.SecuCategory = 62) \
                   AND LC_Dividend.ExDiviDate IS NOT NULL \
               ORDER BY SecuMain.SecuCode ASC, LC_Dividend.ExDiviDate ASC"
        result_list = dbm.ExecQuery(sql)
        datas_count_sh = 0
        datas_count_sz = 0
        if result_list != None:
            for (InnerCode, SecuCode, SecuMarket, SecuCategory, ListedSector, IfDividend, ExDiviDate, BonusShareRatio, TranAddShareRaio, CashDiviRMB) in result_list:
                #print(InnerCode, SecuCode, SecuMarket, SecuCategory, ListedSector, IfDividend, ExDiviDate, BonusShareRatio, TranAddShareRaio, CashDiviRMB)
                #print(InnerCode, SecuCode, IfDividend, ExDiviDate, BonusShareRatio, TranAddShareRaio, CashDiviRMB)
                date = ExDiviDate.year * 10000 + ExDiviDate.month * 100 + ExDiviDate.day
                if SecuMarket == 83:
                    market = "SH"
                    datas_count_sh += 1
                    if not SecuCode in self.exrights_dict_sh.keys():
                        self.exrights_dict_sh[SecuCode] = {}
                    exrights_item_dict = self.exrights_dict_sh[SecuCode]
                    if date in exrights_item_dict.keys():
                        exrights_item = exrights_item_dict[date]
                        if BonusShareRatio != None:
                            exrights_item.sg += float(BonusShareRatio) / 10.0
                        if TranAddShareRaio != None:
                            exrights_item.sg += float(TranAddShareRaio) / 10.0
                        if CashDiviRMB != None:
                            exrights_item.bonus += float(CashDiviRMB) / 10.0
                    else:
                        exrights_item = ExRightsItem(inners = InnerCode, market = market, code = SecuCode, date = date)
                        if BonusShareRatio != None:
                            exrights_item.sg += float(BonusShareRatio) / 10.0
                        if TranAddShareRaio != None:
                            exrights_item.sg += float(TranAddShareRaio) / 10.0
                        if CashDiviRMB != None:
                            exrights_item.bonus += float(CashDiviRMB) / 10.0
                        exrights_item_dict[date] = exrights_item
                elif SecuMarket == 90:
                    market = "SZ"
                    datas_count_sz += 1
                    if not SecuCode in self.exrights_dict_sz.keys():
                        self.exrights_dict_sz[SecuCode] = {}
                    exrights_item_dict = self.exrights_dict_sz[SecuCode]
                    if date in exrights_item_dict.keys():
                        exrights_item = exrights_item_dict[date]
                        if BonusShareRatio != None:
                            exrights_item.sg += float(BonusShareRatio) / 10.0
                        if TranAddShareRaio != None:
                            exrights_item.sg += float(TranAddShareRaio) / 10.0
                        if CashDiviRMB != None:
                            exrights_item.bonus += float(CashDiviRMB) / 10.0
                    else:
                        exrights_item = ExRightsItem(inners = InnerCode, market = market, code = SecuCode, date = date)
                        if BonusShareRatio != None:
                            exrights_item.sg += float(BonusShareRatio) / 10.0
                        if TranAddShareRaio != None:
                            exrights_item.sg += float(TranAddShareRaio) / 10.0
                        if CashDiviRMB != None:
                            exrights_item.bonus += float(CashDiviRMB) / 10.0
                        exrights_item_dict[date] = exrights_item
            self.SendMessage("获取分红数据成功。上证 %d 个，深证 %d 个。" % (datas_count_sh, datas_count_sz))
        else:
            self.SendMessage("获取分红数据失败！")

    def CalcMulerAdder(self):
        for value_dict in self.exrights_dict_sh.values():
            for value_item in value_dict.values():
                value_item.muler = 1.0 + value_item.sg + value_item.pg
                value_item.adder = 0.0 - value_item.bonus + value_item.pg * value_item.price
        for value_dict in self.exrights_dict_sz.values():
            for value_item in value_dict.values():
                value_item.muler = 1.0 + value_item.sg + value_item.pg
                value_item.adder = 0.0 - value_item.bonus + value_item.pg * value_item.price

    def SaveData_ExRights(self, dbm, table_name, save_path):
        record_list_temp = []
        exrights_keys_sh = list(self.exrights_dict_sh.keys())
        exrights_keys_sz = list(self.exrights_dict_sz.keys())
        exrights_keys_sh.sort()
        exrights_keys_sz.sort()
        exrights_item_dict_list_sh = [self.exrights_dict_sh[key] for key in exrights_keys_sh]
        exrights_item_dict_list_sz = [self.exrights_dict_sz[key] for key in exrights_keys_sz]
        for exrights_item_dict in exrights_item_dict_list_sh:
            exrights_item_keys = list(exrights_item_dict.keys())
            exrights_item_keys.sort()
            exrights_item_list = [exrights_item_dict[key] for key in exrights_item_keys]
            record_list_temp.extend(exrights_item_list)
            #for exrights_item in exrights_item_list:
            #    print(exrights_item.inners, exrights_item.market, exrights_item.code, exrights_item.date, \
            #          exrights_item.muler, exrights_item.adder, exrights_item.sg, exrights_item.pg, exrights_item.price, exrights_item.bonus)
        for exrights_item_dict in exrights_item_dict_list_sz:
            exrights_item_keys = list(exrights_item_dict.keys())
            exrights_item_keys.sort()
            exrights_item_list = [exrights_item_dict[key] for key in exrights_item_keys]
            record_list_temp.extend(exrights_item_list)
            #for exrights_item in exrights_item_list:
            #    print(exrights_item.inners, exrights_item.market, exrights_item.code, exrights_item.date, \
            #          exrights_item.muler, exrights_item.adder, exrights_item.sg, exrights_item.pg, exrights_item.price, exrights_item.bonus)
        total_record_num = len(record_list_temp)
        values_list = []
        for i in range(total_record_num):
            str_date = common.TransDateIntToStr(record_list_temp[i].date)
            values_list.append((record_list_temp[i].inners, record_list_temp[i].market, record_list_temp[i].code, str_date, record_list_temp[i].muler, record_list_temp[i].adder, record_list_temp[i].sg, record_list_temp[i].pg, record_list_temp[i].price, record_list_temp[i].bonus))
        columns = ["inners", "market", "code", "date", "muler", "adder", "sg", "pg", "price", "bonus"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values_list) > 0:
            result = pd.DataFrame(data = values_list, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("本地保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))
        if dbm != None:
            sql = "CREATE TABLE `%s` (" % table_name + \
                  "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                  "`inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码'," + \
                  "`market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，SH、SZ'," + \
                  "`code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码'," + \
                  "`date` date NOT NULL COMMENT '除权除息日期'," + \
                  "`muler` float(16,7) DEFAULT '0.0000000' COMMENT '乘数'," + \
                  "`adder` float(16,7) DEFAULT '0.0000000' COMMENT '加数'," + \
                  "`sg` float(16,7) DEFAULT '0.0000000' COMMENT '送股比率，每股，非百分比'," + \
                  "`pg` float(16,7) DEFAULT '0.0000000' COMMENT '配股比率，每股，非百分比'," + \
                  "`price` float(10,3) DEFAULT '0.000' COMMENT '配股价，元'," + \
                  "`bonus` float(16,7) DEFAULT '0.0000000' COMMENT '现金红利，每股，元'," + \
                  "PRIMARY KEY (`id`)," + \
                  "UNIQUE KEY `idx_market_code_date` (`market`,`code`,`date`)" + \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            if dbm.TruncateOrCreateTable(table_name, sql) == True:
                sql = "INSERT INTO %s" % table_name + "(inners, market, code, date, muler, adder, sg, pg, price, bonus) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                total_record_num, save_record_success, save_record_failed = dbm.BatchInsert(values_list, sql)
                self.SendMessage("远程入库：总记录 %d，入库记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))
            else:
                self.SendMessage("远程入库：初始化数据库表 %s 失败！" % table_name)

class DataMaker_Industry():
    def __init__(self, parent = None):
        self.parent = parent
        self.industry_list = []

    def SendMessage(self, text_info):
        if self.parent != None:
            self.parent.SendMessage(text_info)

    def PullData_Industry(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_Industry 数据库 dbm 尚未连接！")
            return
        self.industry_list = []
        # 证券市场：83 上海证券交易所、90 深圳证券交易所
        # 证券类别：1 A股
        # 上市板块：1 主板、2 中小企业板、6 创业板
        # 查询字段：SecuMain：证券内部编码、证券代码、证券简称、证券市场
        # 查询字段：LC_ExgIndustry：信息发布日期、行业划分标准、所属行业、是否执行、
        #                           一级行业代码、一级行业名称、二级行业代码、二级行业名称、三级行业代码、三级行业名称、四级行业代码、四级行业名称
        # 唯一约束：SecuMain = InnerCode、LC_ExgIndustry = CompanyCode & InfoPublDate & Standard & Industry & IfPerformed
        sql = "SELECT SecuMain.InnerCode, SecuMain.SecuCode, SecuMain.SecuAbbr, SecuMain.SecuMarket, \
                      LC_ExgIndustry.InfoPublDate, LC_ExgIndustry.Standard, LC_ExgIndustry.Industry, LC_ExgIndustry.IfPerformed, \
                      LC_ExgIndustry.FirstIndustryCode, LC_ExgIndustry.FirstIndustryName, LC_ExgIndustry.SecondIndustryCode, LC_ExgIndustry.SecondIndustryName, \
                      LC_ExgIndustry.ThirdIndustryCode, LC_ExgIndustry.ThirdIndustryName, LC_ExgIndustry.FourthIndustryCode, LC_ExgIndustry.FourthIndustryName \
               FROM SecuMain INNER JOIN LC_ExgIndustry \
               ON SecuMain.CompanyCode = LC_ExgIndustry.CompanyCode \
               WHERE (SecuMain.SecuMarket = 83 OR SecuMain.SecuMarket = 90) \
                   AND (SecuMain.SecuCategory = 1) \
                   AND (SecuMain.ListedSector = 1 OR SecuMain.ListedSector = 2 OR SecuMain.ListedSector = 6) \
                   AND (LC_ExgIndustry.IfPerformed = 1) \
               ORDER BY LC_ExgIndustry.Standard ASC, LC_ExgIndustry.Industry ASC, \
                        LC_ExgIndustry.FirstIndustryCode ASC, LC_ExgIndustry.SecondIndustryCode ASC, LC_ExgIndustry.ThirdIndustryCode ASC, LC_ExgIndustry.FourthIndustryCode ASC"
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (InnerCode, SecuCode, SecuAbbr, SecuMarket, InfoPublDate, Standard, Industry, IfPerformed, FirstIndustryCode, FirstIndustryName, SecondIndustryCode, SecondIndustryName, ThirdIndustryCode, ThirdIndustryName, FourthIndustryCode, FourthIndustryName) in result_list:
                stock_market = ""
                if SecuMarket == 83:
                    stock_market = "SH"
                elif SecuMarket == 90:
                    stock_market = "SZ"
                industry_item = IndustryItem(standard = Standard, industry = Industry, inners = InnerCode, market = stock_market, code = SecuCode, name = SecuAbbr, 
                                    industry_code_1 = FirstIndustryCode, industry_name_1 = FirstIndustryName, industry_code_2 = SecondIndustryCode, industry_name_2 = SecondIndustryName, 
                                    industry_code_3 = ThirdIndustryCode, industry_name_3 = ThirdIndustryName, industry_code_4 = FourthIndustryCode, industry_name_4 = FourthIndustryName)
                industry_item.SetInfoDate(InfoPublDate) #
                self.industry_list.append(industry_item)
                #print(InnerCode, SecuCode, SecuAbbr, SecuMarket, InfoPublDate, Standard, Industry, IfPerformed, FirstIndustryCode, FirstIndustryName, SecondIndustryCode, SecondIndustryName, ThirdIndustryCode, ThirdIndustryName, FourthIndustryCode, FourthIndustryName)
            self.SendMessage("获取 行业划分 成功。总计 %d 个。" % len(result_list))
        else:
            self.SendMessage("获取 行业划分 失败！")

    def SaveData_Industry(self, dbm, table_name, save_path):
        total_record_num = len(self.industry_list)
        values_list = []
        for i in range(total_record_num):
            str_date = common.TransDateIntToStr(self.industry_list[i].info_date)
            values_list.append((self.industry_list[i].standard, self.industry_list[i].industry, 
                                self.industry_list[i].industry_code_1, self.industry_list[i].industry_name_1, self.industry_list[i].industry_code_2, self.industry_list[i].industry_name_2, 
                                self.industry_list[i].industry_code_3, self.industry_list[i].industry_name_3, self.industry_list[i].industry_code_4, self.industry_list[i].industry_name_4, 
                                self.industry_list[i].inners, self.industry_list[i].market, self.industry_list[i].code, self.industry_list[i].name, str_date))
        columns = ["standard", "industry", "industry_code_1", "industry_name_1", "industry_code_2", "industry_name_2", 
                   "industry_code_3", "industry_name_3", "industry_code_4", "industry_name_4", "inners", "market", "code", "name", "info_date"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values_list) > 0:
            result = pd.DataFrame(data = values_list, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("本地保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))
        if dbm != None:
            sql = "CREATE TABLE `%s` (" % table_name + \
                  "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                  "`standard` int(32) NOT NULL DEFAULT '0' COMMENT '行业划分标准'," + \
                  "`industry` int(32) NOT NULL DEFAULT '0' COMMENT '所属行业'," + \
                  "`industry_code_1` varchar(32) DEFAULT '' COMMENT '一级行业代码'," + \
                  "`industry_name_1` varchar(100) DEFAULT '' COMMENT '一级行业名称'," + \
                  "`industry_code_2` varchar(32) DEFAULT '' COMMENT '二级行业代码'," + \
                  "`industry_name_2` varchar(100) DEFAULT '' COMMENT '二级行业名称'," + \
                  "`industry_code_3` varchar(32) DEFAULT '' COMMENT '三级行业代码'," + \
                  "`industry_name_3` varchar(100) DEFAULT '' COMMENT '三级行业名称'," + \
                  "`industry_code_4` varchar(32) DEFAULT '' COMMENT '四级行业代码'," + \
                  "`industry_name_4` varchar(100) DEFAULT '' COMMENT '四级行业名称'," + \
                  "`inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码'," + \
                  "`market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，SH、SZ'," + \
                  "`code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码'," + \
                  "`name` varchar(32) DEFAULT '' COMMENT '证券名称'," + \
                  "`info_date` date NOT NULL COMMENT '信息日期'," + \
                  "PRIMARY KEY (`id`)," + \
                  "UNIQUE KEY `idx_standard_industry_market_code_info_date` (`standard`,`industry`,`market`,`code`,`info_date`)" + \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            if dbm.TruncateOrCreateTable(table_name, sql) == True:
                sql = "INSERT INTO %s" % table_name + "(standard, industry, industry_code_1, industry_name_1, industry_code_2, industry_name_2, industry_code_3, industry_name_3, industry_code_4, industry_name_4, inners, market, code, name, info_date) \
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                total_record_num, save_record_success, save_record_failed = dbm.BatchInsert(values_list, sql)
                self.SendMessage("远程入库：总记录 %d，入库记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))
            else:
                self.SendMessage("远程入库：初始化数据库表 %s 失败！" % table_name)

class DataMaker_Industry_HK():
    def __init__(self, parent = None):
        self.parent = parent
        self.industry_list = []
        self.industry_dict = {}

    def SendMessage(self, text_info):
        if self.parent != None:
            self.parent.SendMessage(text_info)

    def PullData_Industry_HK(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_Industry_HK 数据库 dbm 尚未连接！")
            return
        self.industry_dict = {}
        # 证券市场：72 香港联交所
        # 证券类别：3 H股、51 港股、52 合订证券、53 红筹股
        # 上市状态：1 上市、3 暂停
        # 查询字段：HK_SecuMain：证券内部编码、证券代码、证券简称、证券市场
        # 查询字段：HK_ExgIndustry：公司内码、行业划分标准、生效日期
        # 查询字段：HK_IndustryCategory：行业编码、行业名称、行业级别
        # 唯一约束：HK_SecuMain = InnerCode、HK_ExgIndustry = CompanyCode & Standard & IndustryNum & ExcuteDate、HK_IndustryCategory = Standard & IndustryNum & ExcuteDate
        sql = "SELECT HK_SecuMain.InnerCode, HK_SecuMain.SecuCode, HK_SecuMain.SecuAbbr, HK_SecuMain.SecuMarket, \
                      HK_ExgIndustry.CompanyCode, HK_ExgIndustry.Standard, HK_ExgIndustry.ExcuteDate, \
                      HK_IndustryCategory.IndustryNum, HK_IndustryCategory.IndustryName, HK_IndustryCategory.Classification \
               FROM HK_ExgIndustry INNER JOIN HK_SecuMain ON HK_SecuMain.CompanyCode = HK_ExgIndustry.CompanyCode \
                                   INNER JOIN HK_IndustryCategory ON HK_ExgIndustry.IndustryNum = HK_IndustryCategory.IndustryNum \
               WHERE (HK_SecuMain.SecuMarket = 72) \
                   AND (HK_SecuMain.SecuCategory = 3 OR HK_SecuMain.SecuCategory = 51 OR HK_SecuMain.SecuCategory = 52 OR HK_SecuMain.SecuCategory = 53) \
                   AND (HK_SecuMain.ListedSector = 1 OR HK_SecuMain.ListedSector = 3) \
                   AND (HK_ExgIndustry.IfExecuted = 1 AND HK_IndustryCategory.IfExecuted = 1) \
               ORDER BY HK_ExgIndustry.CompanyCode ASC, HK_ExgIndustry.Standard ASC, HK_IndustryCategory.Classification ASC, HK_ExgIndustry.IndustryNum ASC"
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (InnerCode, SecuCode, SecuAbbr, SecuMarket, CompanyCode, Standard, ExcuteDate, IndustryNum, IndustryName, Classification) in result_list:
                stock_market = "HK"
                key = "%d%d" % (CompanyCode, Standard)
                # 结果根据 Classification 排序，所以 industry 为分类标准中最高级的行业分类
                if not key in self.industry_dict.keys():
                    industry_item = IndustryItem(standard = Standard, industry = IndustryNum, inners = InnerCode, market = stock_market, code = SecuCode, name = SecuAbbr)
                    industry_item.SetInfoDate(ExcuteDate) #
                    industry_item.SetIndustryCodeName_HK(Classification, IndustryNum, IndustryName)
                    self.industry_dict[key] = industry_item
                else:
                    industry_item = self.industry_dict[key]
                    industry_item.SetIndustryCodeName_HK(Classification, IndustryNum, IndustryName)
                #print(InnerCode, SecuCode, SecuAbbr, SecuMarket, CompanyCode, Standard, ExcuteDate, IndustryNum, IndustryName, Classification)
            self.SendMessage("获取 行业划分-HK 成功。总计 %d 个。" % len(result_list))
        else:
            self.SendMessage("获取 行业划分-HK 失败！")

    def SaveData_Industry_HK(self, dbm, table_name, save_path):
        industry_keys = list(self.industry_dict.keys())
        industry_keys.sort()
        self.industry_list = [self.industry_dict[key] for key in industry_keys]
        total_record_num = len(self.industry_list)
        values_list = []
        for i in range(total_record_num):
            str_date = common.TransDateIntToStr(self.industry_list[i].info_date)
            values_list.append((self.industry_list[i].standard, self.industry_list[i].industry, 
                                self.industry_list[i].industry_code_1, self.industry_list[i].industry_name_1, self.industry_list[i].industry_code_2, self.industry_list[i].industry_name_2, 
                                self.industry_list[i].industry_code_3, self.industry_list[i].industry_name_3, self.industry_list[i].industry_code_4, self.industry_list[i].industry_name_4, 
                                self.industry_list[i].inners, self.industry_list[i].market, self.industry_list[i].code, self.industry_list[i].name, str_date))
        columns = ["standard", "industry", "industry_code_1", "industry_name_1", "industry_code_2", "industry_name_2", 
                   "industry_code_3", "industry_name_3", "industry_code_4", "industry_name_4", "inners", "market", "code", "name", "info_date"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values_list) > 0:
            result = pd.DataFrame(data = values_list, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("本地保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))
        if dbm != None:
            sql = "CREATE TABLE `%s` (" % table_name + \
                  "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                  "`standard` int(32) NOT NULL DEFAULT '0' COMMENT '行业划分标准'," + \
                  "`industry` int(32) NOT NULL DEFAULT '0' COMMENT '所属行业'," + \
                  "`industry_code_1` varchar(32) DEFAULT '' COMMENT '一级行业代码'," + \
                  "`industry_name_1` varchar(100) DEFAULT '' COMMENT '一级行业名称'," + \
                  "`industry_code_2` varchar(32) DEFAULT '' COMMENT '二级行业代码'," + \
                  "`industry_name_2` varchar(100) DEFAULT '' COMMENT '二级行业名称'," + \
                  "`industry_code_3` varchar(32) DEFAULT '' COMMENT '三级行业代码'," + \
                  "`industry_name_3` varchar(100) DEFAULT '' COMMENT '三级行业名称'," + \
                  "`industry_code_4` varchar(32) DEFAULT '' COMMENT '四级行业代码'," + \
                  "`industry_name_4` varchar(100) DEFAULT '' COMMENT '四级行业名称'," + \
                  "`inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码'," + \
                  "`market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，HK'," + \
                  "`code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码'," + \
                  "`name` varchar(32) DEFAULT '' COMMENT '证券名称'," + \
                  "`info_date` date NOT NULL COMMENT '信息日期'," + \
                  "PRIMARY KEY (`id`)," + \
                  "UNIQUE KEY `idx_standard_industry_market_code_info_date` (`standard`,`industry`,`market`,`code`,`info_date`)" + \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            if dbm.TruncateOrCreateTable(table_name, sql) == True:
                sql = "INSERT INTO %s" % table_name + "(standard, industry, industry_code_1, industry_name_1, industry_code_2, industry_name_2, industry_code_3, industry_name_3, industry_code_4, industry_name_4, inners, market, code, name, info_date) \
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                total_record_num, save_record_success, save_record_failed = dbm.BatchInsert(values_list, sql)
                self.SendMessage("远程入库：总记录 %d，入库记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))
            else:
                self.SendMessage("远程入库：初始化数据库表 %s 失败！" % table_name)

class DataMaker_PreQuoteStk():
    def __init__(self, parent = None):
        self.parent = parent
        self.quote_data_list = []

    def SendMessage(self, text_info):
        if self.parent != None:
            self.parent.SendMessage(text_info)

    def TransTimeIntToStr(self, str_date, int_time):
        hour = int(int_time / 10000000)
        minute = int((int_time % 10000000) / 100000)
        second = int((int_time % 100000) / 1000)
        microsecond = int_time % 1000
        return "%s %d:%d:%d.%d" % (str_date, hour, minute, second, microsecond)

    def PullData_PreQuoteStk(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_PreQuoteStk 数据库 dbm 尚未连接！")
            return
        pre_date = ""
        now_date = datetime.now().strftime("%Y-%m-%d")
        # 证券市场：83 沪深交易所
        # 查询字段：QT_TradingDayNew：日期、是否交易日、证券市场
        # 唯一约束：QT_TradingDayNew = Date、SecuMarket
        sql = "SELECT MAX(TradingDate) \
               FROM QT_TradingDayNew \
               WHERE QT_TradingDayNew.SecuMarket = 83 \
                   AND QT_TradingDayNew.TradingDate < '%s' \
                   AND QT_TradingDayNew.IfTradingDay = 1" % now_date
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (TradingDate,) in result_list:
                pre_date = TradingDate.strftime("%Y-%m-%d")
        if pre_date == "":
            self.SendMessage("获取 上一交易日期 失败！")
            return
        else:
            self.SendMessage("获取 上一交易日期 成功。%s" % pre_date)
        self.quote_data_list = []
        # 证券市场：83 上海证券交易所、90 深圳证券交易所
        # 证券类别：1 A股、8 开放式基金、62 ETF基金
        # 上市板块：1 主板、2 中小企业板、6 创业板
        # 查询字段：SecuMain：证券内部编码、证券代码、证券简称、证券类别、证券市场
        # 查询字段：QT_DailyQuote：交易日、昨收盘、今开盘、最高价、最低价、收盘价、成交量、成交金额、成交笔数、更新时间
        # 唯一约束：SecuMain = InnerCode、QT_DailyQuote = InnerCode & TradingDay
        sql = "SELECT SecuMain.InnerCode, SecuMain.SecuCode, SecuMain.SecuAbbr, SecuMain.SecuCategory, SecuMain.SecuMarket, \
                      QT_DailyQuote.TradingDay, QT_DailyQuote.PrevClosePrice, QT_DailyQuote.OpenPrice, QT_DailyQuote.HighPrice, QT_DailyQuote.LowPrice, QT_DailyQuote.ClosePrice, \
                      QT_DailyQuote.TurnoverVolume, QT_DailyQuote.TurnoverValue, QT_DailyQuote.TurnoverDeals, QT_DailyQuote.XGRQ \
               FROM SecuMain INNER JOIN QT_DailyQuote \
               ON SecuMain.InnerCode = QT_DailyQuote.InnerCode \
               WHERE (SecuMain.SecuMarket = 83 OR SecuMain.SecuMarket = 90) \
                   AND (SecuMain.SecuCategory = 1 OR SecuMain.SecuCategory = 8 OR SecuMain.SecuCategory = 62) \
                   AND (SecuMain.ListedSector = 1 OR SecuMain.ListedSector = 2 OR SecuMain.ListedSector = 6) \
                   AND QT_DailyQuote.TradingDay = '%s' \
               ORDER BY SecuMain.SecuMarket ASC, SecuMain.SecuCode ASC" % pre_date
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, TradingDay, PrevClosePrice, OpenPrice, HighPrice, LowPrice, ClosePrice, TurnoverVolume, TurnoverValue, TurnoverDeals, XGRQ) in result_list:
                stock_name = SecuAbbr.replace(" ", "")
                stock_market = ""
                if SecuMarket == 83:
                    stock_market = "SH"
                elif SecuMarket == 90:
                    stock_market = "SZ"
                pre_quote_stk_item = PreQuoteStkItem(inners = InnerCode, market = stock_market, code = SecuCode, name = stock_name, open = OpenPrice, high = HighPrice, low = LowPrice, close = ClosePrice, pre_close = PrevClosePrice, volume = TurnoverVolume, turnover = TurnoverValue, trade_count = TurnoverDeals)
                pre_quote_stk_item.SetCategory(SecuCategory, SecuCode) #
                pre_quote_stk_item.SetQuoteDate(TradingDay) #
                pre_quote_stk_item.SetQuoteTime(XGRQ) #
                self.quote_data_list.append(pre_quote_stk_item)
                #print(InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, TradingDay, PrevClosePrice, OpenPrice, HighPrice, LowPrice, ClosePrice, TurnoverVolume, TurnoverValue, TurnoverDeals, XGRQ)
                #print(pre_quote_stk_item.code, pre_quote_stk_item.category, pre_quote_stk_item.quote_date, pre_quote_stk_item.quote_time, XGRQ, XGRQ.hour, XGRQ.minute, XGRQ.second, XGRQ.microsecond)
            self.SendMessage("获取 股票行情 成功。总计 %d 个。" % len(result_list))
        else:
            self.SendMessage("获取 股票行情 失败！")

    def SaveData_PreQuoteStk(self, dbm, table_name, save_path):
        total_record_num = len(self.quote_data_list)
        values_list = []
        for i in range(total_record_num):
            str_date = common.TransDateIntToStr(self.quote_data_list[i].quote_date)
            str_time = self.TransTimeIntToStr(str_date, self.quote_data_list[i].quote_time)
            values_list.append((self.quote_data_list[i].inners, self.quote_data_list[i].market, self.quote_data_list[i].code, self.quote_data_list[i].name, self.quote_data_list[i].category, 
                                self.quote_data_list[i].open, self.quote_data_list[i].high, self.quote_data_list[i].low, self.quote_data_list[i].close, self.quote_data_list[i].pre_close, 
                                self.quote_data_list[i].volume, self.quote_data_list[i].turnover, self.quote_data_list[i].trade_count, str_date, str_time))
        columns = ["inners", "market", "code", "name", "category", "open", "high", "low", "close", "pre_close", "volume", "turnover", "trade_count", "quote_date", "quote_time"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values_list) > 0:
            result = pd.DataFrame(data = values_list, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("本地保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))
        if dbm != None:
            sql = "CREATE TABLE `%s` (" % table_name + \
                  "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                  "`inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码'," + \
                  "`market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，SH、SZ'," + \
                  "`code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码'," + \
                  "`name` varchar(32) DEFAULT '' COMMENT '证券名称'," + \
                  "`category` int(8) DEFAULT '0' COMMENT '证券类别，详见说明'," + \
                  "`open` float(16,4) DEFAULT '0.0000' COMMENT '开盘价'," + \
                  "`high` float(16,4) DEFAULT '0.0000' COMMENT '最高价'," + \
                  "`low` float(16,4) DEFAULT '0.0000' COMMENT '最低价'," + \
                  "`close` float(16,4) DEFAULT '0.0000' COMMENT '收盘价'," + \
                  "`pre_close` float(16,4) DEFAULT '0.0000' COMMENT '昨收价'," + \
                  "`volume` bigint(64) DEFAULT '0' COMMENT '成交量，股'," + \
                  "`turnover` double(64,2) DEFAULT '0.00' COMMENT '成交额，元'," + \
                  "`trade_count` int(32) DEFAULT '0' COMMENT '成交笔数'," + \
                  "`quote_date` date DEFAULT NULL COMMENT '行情日期，2015-12-31'," + \
                  "`quote_time` datetime(6) DEFAULT NULL COMMENT '行情时间'," + \
                  "PRIMARY KEY (`id`)," + \
                  "UNIQUE KEY `idx_market_code` (`market`,`code`)" + \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            if dbm.TruncateOrCreateTable(table_name, sql) == True:
                sql = "INSERT INTO %s" % table_name + "(inners, market, code, name, category, open, high, low, close, pre_close, volume, turnover, trade_count, quote_date, quote_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                total_record_num, save_record_success, save_record_failed = dbm.BatchInsert(values_list, sql)
                self.SendMessage("远程入库：总记录 %d，入库记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))
            else:
                self.SendMessage("远程入库：初始化数据库表 %s 失败！" % table_name)

class DataMaker_PreQuoteFue():
    def __init__(self, parent = None):
        self.parent = parent
        self.quote_data_list = []

    def SendMessage(self, text_info):
        if self.parent != None:
            self.parent.SendMessage(text_info)

    def TransTimeIntToStr(self, str_date, int_time):
        hour = int(int_time / 10000000)
        minute = int((int_time % 10000000) / 100000)
        second = int((int_time % 100000) / 1000)
        microsecond = int_time % 1000
        return "%s %d:%d:%d.%d" % (str_date, hour, minute, second, microsecond)

    def PullData_PreQuoteFue(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_PreQuoteFue 数据库 dbm 尚未连接！")
            return
        pre_date = ""
        now_date = datetime.now().strftime("%Y-%m-%d")
        # 证券市场：83 沪深交易所
        # 查询字段：QT_TradingDayNew：日期、是否交易日、证券市场
        # 唯一约束：QT_TradingDayNew = Date、SecuMarket
        sql = "SELECT MAX(TradingDate) \
               FROM QT_TradingDayNew \
               WHERE QT_TradingDayNew.SecuMarket = 83 \
                   AND QT_TradingDayNew.TradingDate < '%s' \
                   AND QT_TradingDayNew.IfTradingDay = 1" % now_date
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (TradingDate,) in result_list:
                pre_date = TradingDate.strftime("%Y-%m-%d")
        if pre_date == "":
            self.SendMessage("获取 上一交易日期 失败！")
            return
        else:
            self.SendMessage("获取 上一交易日期 成功。%s" % pre_date)
        self.quote_data_list = []
        # 合约市场：20 中国金融期货交易所
        # 查询字段：Fut_TradingQuote：交易日期、合约内部编码、交易所代码、合约代码、开盘价、最高价、最低价、收盘价、结算价、前收盘、前结算、成交量、成交金额、持仓量、持仓量变化、基差、更新时间
        # 唯一约束：Fut_TradingQuote = ContractInnerCode & TradingDay
        sql = "SELECT TradingDay, ContractInnerCode, ExchangeCode, ContractCode, OpenPrice, HighPrice, LowPrice, ClosePrice, SettlePrice, \
                      PrevClosePrice, PrevSettlePrice, TurnoverVolume, TurnoverValue, OpenInterest, ChangeOfOpenInterest, BasisValue, UpdateTime \
               FROM Fut_TradingQuote \
               WHERE ExchangeCode = 20 AND TradingDay = '%s' \
               ORDER BY ExchangeCode ASC, ContractCode ASC" % pre_date
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (TradingDay, ContractInnerCode, ExchangeCode, ContractCode, OpenPrice, HighPrice, LowPrice, ClosePrice, SettlePrice, PrevClosePrice, PrevSettlePrice, TurnoverVolume, TurnoverValue, OpenInterest, ChangeOfOpenInterest, BasisValue, UpdateTime) in result_list:
                future_market = ""
                if ExchangeCode == 10:
                    future_market = "SHFE" # 上期
                elif ExchangeCode == 13:
                    future_market = "DCE" # 大商
                elif ExchangeCode == 15:
                    future_market = "CZCE" # 郑商
                elif ExchangeCode == 20:
                    future_market = "CFFEX" # 中金
                pre_quote_fue_item = PreQuoteFueItem(inners = ContractInnerCode, market = future_market, code = ContractCode, open = OpenPrice, high = HighPrice, low = LowPrice, close = ClosePrice, settle = SettlePrice, 
                                                     pre_close = PrevClosePrice, pre_settle = PrevSettlePrice, volume = TurnoverVolume, turnover = TurnoverValue, open_interest = OpenInterest, chg_open_interest = ChangeOfOpenInterest, basis_value = BasisValue)
                pre_quote_fue_item.SetQuoteDate(TradingDay) #
                pre_quote_fue_item.SetQuoteTime(UpdateTime) #
                self.quote_data_list.append(pre_quote_fue_item)
                #print(TradingDay, ContractInnerCode, ExchangeCode, ContractCode, OpenPrice, HighPrice, LowPrice, ClosePrice, SettlePrice, PrevClosePrice, PrevSettlePrice, TurnoverVolume, TurnoverValue, OpenInterest, ChangeOfOpenInterest, BasisValue, UpdateTime)
            self.SendMessage("获取 期货行情 成功。总计 %d 个。" % len(result_list))
        else:
            self.SendMessage("获取 期货行情 失败！")

    def SaveData_PreQuoteFue(self, dbm, table_name, save_path):
        total_record_num = len(self.quote_data_list)
        values_list = []
        for i in range(total_record_num):
            str_date = common.TransDateIntToStr(self.quote_data_list[i].quote_date)
            str_time = self.TransTimeIntToStr(str_date, self.quote_data_list[i].quote_time)
            values_list.append((self.quote_data_list[i].inners, self.quote_data_list[i].market, self.quote_data_list[i].code, 
                                self.quote_data_list[i].open, self.quote_data_list[i].high, self.quote_data_list[i].low, self.quote_data_list[i].close, self.quote_data_list[i].settle, self.quote_data_list[i].pre_close, self.quote_data_list[i].pre_settle, 
                                self.quote_data_list[i].volume, self.quote_data_list[i].turnover, self.quote_data_list[i].open_interest, self.quote_data_list[i].chg_open_interest, self.quote_data_list[i].basis_value, self.quote_data_list[i].main_flag, str_date, str_time))
        columns = ["inners", "market", "code", "open", "high", "low", "close", "settle", "pre_close", "pre_settle", "volume", "turnover", "open_interest", "chg_open_interest", "basis_value", "main_flag", "quote_date", "quote_time"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values_list) > 0:
            result = pd.DataFrame(data = values_list, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("本地保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))
        if dbm != None:
            sql = "CREATE TABLE `%s` (" % table_name + \
                  "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                  "`inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码'," + \
                  "`market` varchar(32) NOT NULL DEFAULT '' COMMENT '合约市场，详见说明'," + \
                  "`code` varchar(32) NOT NULL DEFAULT '' COMMENT '合约代码'," + \
                  "`open` float(16,4) DEFAULT '0.0000' COMMENT '开盘价'," + \
                  "`high` float(16,4) DEFAULT '0.0000' COMMENT '最高价'," + \
                  "`low` float(16,4) DEFAULT '0.0000' COMMENT '最低价'," + \
                  "`close` float(16,4) DEFAULT '0.0000' COMMENT '收盘价'," + \
                  "`settle` float(16,4) DEFAULT '0.0000' COMMENT '结算价'," + \
                  "`pre_close` float(16,4) DEFAULT '0.0000' COMMENT '昨收价'," + \
                  "`pre_settle` float(16,4) DEFAULT '0.0000' COMMENT '昨结价'," + \
                  "`volume` bigint(64) DEFAULT '0' COMMENT '成交量，手'," + \
                  "`turnover` double(64,2) DEFAULT '0.00' COMMENT '成交额，元'," + \
                  "`open_interest` bigint(64) DEFAULT '0' COMMENT '持仓量，手'," + \
                  "`chg_open_interest` bigint(64) DEFAULT '0' COMMENT '持仓量变化，手'," + \
                  "`basis_value` float(16,4) DEFAULT '0.0000' COMMENT '基差'," + \
                  "`main_flag` int(8) DEFAULT '0' COMMENT '主力标志，1 是、0 否'," + \
                  "`quote_date` date DEFAULT NULL COMMENT '行情日期，2015-12-31'," + \
                  "`quote_time` datetime(6) DEFAULT NULL COMMENT '行情时间'," + \
                  "PRIMARY KEY (`id`)," + \
                  "UNIQUE KEY `idx_market_code` (`market`,`code`)" + \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            if dbm.TruncateOrCreateTable(table_name, sql) == True:
                sql = "INSERT INTO %s" % table_name + "(inners, market, code, open, high, low, close, settle, pre_close, pre_settle, volume, turnover, open_interest, chg_open_interest, basis_value, main_flag, quote_date, quote_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                total_record_num, save_record_success, save_record_failed = dbm.BatchInsert(values_list, sql)
                self.SendMessage("远程入库：总记录 %d，入库记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))
            else:
                self.SendMessage("远程入库：初始化数据库表 %s 失败！" % table_name)

class DataMaker_PreQuoteStk_HK():
    def __init__(self, parent = None):
        self.parent = parent
        self.quote_data_list = []

    def SendMessage(self, text_info):
        if self.parent != None:
            self.parent.SendMessage(text_info)

    def TransTimeIntToStr(self, str_date, int_time):
        hour = int(int_time / 10000000)
        minute = int((int_time % 10000000) / 100000)
        second = int((int_time % 100000) / 1000)
        microsecond = int_time % 1000
        return "%s %d:%d:%d.%d" % (str_date, hour, minute, second, microsecond)

    def PullData_PreQuoteStk_HK(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_PreQuoteStk_HK 数据库 dbm 尚未连接！")
            return
        pre_date = ""
        now_date = datetime.now().strftime("%Y-%m-%d")
        # 证券市场：72 香港联交所
        # 查询字段：QT_TradingDayNew：日期、是否交易日、证券市场
        # 唯一约束：QT_TradingDayNew = Date、SecuMarket
        sql = "SELECT MAX(TradingDate) \
               FROM QT_TradingDayNew \
               WHERE QT_TradingDayNew.SecuMarket = 72 \
                   AND QT_TradingDayNew.TradingDate < '%s' \
                   AND QT_TradingDayNew.IfTradingDay = 1" % now_date
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (TradingDate,) in result_list:
                pre_date = TradingDate.strftime("%Y-%m-%d")
        if pre_date == "":
            self.SendMessage("获取 上一交易日期 失败！")
            return
        else:
            self.SendMessage("获取 上一交易日期 成功。%s" % pre_date)
        self.quote_data_list = []
        # 证券市场：72 香港联交所
        # 证券类别：3 H股、4 大盘(指数)、51 港股、52 合订证券、53 红筹股、62 ETF基金
        # 过滤排除：10 其他、20 衍生权证、21 股本权证、25 牛熊证、55 优先股、60 基金、61 信托基金、64 杠杆及反向产品、65 债务证券、69 美国证券、71 普通预托证券
        # 上市状态：1 上市、3 暂停
        # 查询字段：HK_SecuMain：证券内部编码、证券代码、证券简称、证券类别、证券市场
        # 查询字段：QT_HKDailyQuote：交易日、昨收盘、今开盘、最高价、最低价、收盘价、成交量、成交金额、更新时间
        # 唯一约束：SecuMain = InnerCode、QT_DailyQuote = InnerCode & TradingDay
        sql = "SELECT HK_SecuMain.InnerCode, HK_SecuMain.SecuCode, HK_SecuMain.SecuAbbr, HK_SecuMain.SecuCategory, HK_SecuMain.SecuMarket, \
                      QT_HKDailyQuote.TradingDay, QT_HKDailyQuote.PrevClosePrice, QT_HKDailyQuote.OpenPrice, QT_HKDailyQuote.HighPrice, QT_HKDailyQuote.LowPrice, QT_HKDailyQuote.ClosePrice, \
                      QT_HKDailyQuote.TurnoverVolume, QT_HKDailyQuote.TurnoverValue, QT_HKDailyQuote.XGRQ \
               FROM HK_SecuMain INNER JOIN QT_HKDailyQuote \
               ON HK_SecuMain.InnerCode = QT_HKDailyQuote.InnerCode \
               WHERE (HK_SecuMain.SecuMarket = 72) \
                   AND (HK_SecuMain.SecuCategory = 3 OR HK_SecuMain.SecuCategory = 4 OR HK_SecuMain.SecuCategory = 51 OR HK_SecuMain.SecuCategory = 52 OR HK_SecuMain.SecuCategory = 53 OR HK_SecuMain.SecuCategory = 62) \
                   AND (HK_SecuMain.ListedSector = 1 OR HK_SecuMain.ListedSector = 3) \
                   AND QT_HKDailyQuote.TradingDay = '%s' \
               ORDER BY HK_SecuMain.SecuMarket ASC, HK_SecuMain.SecuCode ASC" % pre_date
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, TradingDay, PrevClosePrice, OpenPrice, HighPrice, LowPrice, ClosePrice, TurnoverVolume, TurnoverValue, XGRQ) in result_list:
                stock_name = SecuAbbr.replace(" ", "")
                stock_market = "HK"
                pre_quote_stk_item = PreQuoteStkItem(inners = InnerCode, market = stock_market, code = SecuCode, name = stock_name, open = OpenPrice, high = HighPrice, low = LowPrice, close = ClosePrice, pre_close = PrevClosePrice, volume = TurnoverVolume, turnover = TurnoverValue)
                pre_quote_stk_item.SetCategory_HK(SecuCategory, SecuCode) #
                pre_quote_stk_item.SetQuoteDate(TradingDay) #
                pre_quote_stk_item.SetQuoteTime(XGRQ) #
                self.quote_data_list.append(pre_quote_stk_item)
                #print(InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, TradingDay, PrevClosePrice, OpenPrice, HighPrice, LowPrice, ClosePrice, TurnoverVolume, TurnoverValue, XGRQ)
                #print(pre_quote_stk_item.code, pre_quote_stk_item.category, pre_quote_stk_item.quote_date, pre_quote_stk_item.quote_time, XGRQ, XGRQ.hour, XGRQ.minute, XGRQ.second, XGRQ.microsecond)
            self.SendMessage("获取 股票行情-HK 成功。总计 %d 个。" % len(result_list))
        else:
            self.SendMessage("获取 股票行情-HK 失败！")

    def SaveData_PreQuoteStk_HK(self, dbm, table_name, save_path):
        total_record_num = len(self.quote_data_list)
        values_list = []
        for i in range(total_record_num):
            str_date = common.TransDateIntToStr(self.quote_data_list[i].quote_date)
            str_time = self.TransTimeIntToStr(str_date, self.quote_data_list[i].quote_time)
            values_list.append((self.quote_data_list[i].inners, self.quote_data_list[i].market, self.quote_data_list[i].code, self.quote_data_list[i].name, self.quote_data_list[i].category, 
                                self.quote_data_list[i].open, self.quote_data_list[i].high, self.quote_data_list[i].low, self.quote_data_list[i].close, self.quote_data_list[i].pre_close, 
                                self.quote_data_list[i].volume, self.quote_data_list[i].turnover, self.quote_data_list[i].trade_count, str_date, str_time))
        columns = ["inners", "market", "code", "name", "category", "open", "high", "low", "close", "pre_close", "volume", "turnover", "trade_count", "quote_date", "quote_time"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values_list) > 0:
            result = pd.DataFrame(data = values_list, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("本地保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))
        if dbm != None:
            sql = "CREATE TABLE `%s` (" % table_name + \
                  "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                  "`inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码'," + \
                  "`market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，HK'," + \
                  "`code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码'," + \
                  "`name` varchar(32) DEFAULT '' COMMENT '证券名称'," + \
                  "`category` int(8) DEFAULT '0' COMMENT '证券类别，详见说明'," + \
                  "`open` float(16,4) DEFAULT '0.0000' COMMENT '开盘价'," + \
                  "`high` float(16,4) DEFAULT '0.0000' COMMENT '最高价'," + \
                  "`low` float(16,4) DEFAULT '0.0000' COMMENT '最低价'," + \
                  "`close` float(16,4) DEFAULT '0.0000' COMMENT '收盘价'," + \
                  "`pre_close` float(16,4) DEFAULT '0.0000' COMMENT '昨收价'," + \
                  "`volume` bigint(64) DEFAULT '0' COMMENT '成交量，股'," + \
                  "`turnover` double(64,2) DEFAULT '0.00' COMMENT '成交额，元'," + \
                  "`trade_count` int(32) DEFAULT '0' COMMENT '成交笔数'," + \
                  "`quote_date` date DEFAULT NULL COMMENT '行情日期，2015-12-31'," + \
                  "`quote_time` datetime(6) DEFAULT NULL COMMENT '行情时间'," + \
                  "PRIMARY KEY (`id`)," + \
                  "UNIQUE KEY `idx_market_code` (`market`,`code`)" + \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            if dbm.TruncateOrCreateTable(table_name, sql) == True:
                sql = "INSERT INTO %s" % table_name + "(inners, market, code, name, category, open, high, low, close, pre_close, volume, turnover, trade_count, quote_date, quote_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                total_record_num, save_record_success, save_record_failed = dbm.BatchInsert(values_list, sql)
                self.SendMessage("远程入库：总记录 %d，入库记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))
            else:
                self.SendMessage("远程入库：初始化数据库表 %s 失败！" % table_name)

class DataMaker_SecurityInfo():
    def __init__(self, parent = None):
        self.parent = parent
        self.security_dict = {}
        self.count_sh = 0
        self.count_sz = 0
        self.count_lb_1 = 0
        self.count_lb_2 = 0
        self.count_lb_3 = 0
        self.count_lb_4 = 0
        self.count_lb_5 = 0
        self.count_lb_6 = 0
        self.count_lb_7 = 0
        self.count_lb_8 = 0
        self.count_lb_9 = 0
        self.count_lb_10 = 0
        self.count_lb_11 = 0
        self.count_lb_12 = 0
        # 13, 14
        self.count_lb_15 = 0
        self.count_lb_16 = 0
        self.count_bk_1 = 0
        self.count_bk_2 = 0
        self.count_bk_3 = 0
        self.count_st_1 = 0
        self.count_ssrq = 0

    def SendMessage(self, text_info):
        if self.parent != None:
            self.parent.SendMessage(text_info)

    def CheckStockList(self):
        for item in self.security_dict.values():
            if item.market == "SH":
                self.count_sh += 1
            elif item.market == "SZ":
                self.count_sz += 1
            else:
                self.SendMessage("市场异常：%s %s %s" % (item.market, item.code, item.name))
            if item.category == 1:
                self.count_lb_1 += 1
            elif item.category == 2:
                self.count_lb_2 += 1
            elif item.category == 3:
                self.count_lb_3 += 1
            elif item.category == 4:
                self.count_lb_4 += 1
            elif item.category == 5:
                self.count_lb_5 += 1
            elif item.category == 6:
                self.count_lb_6 += 1
            elif item.category == 7:
                self.count_lb_7 += 1
            elif item.category == 8:
                self.count_lb_8 += 1
            elif item.category == 9:
                self.count_lb_9 += 1
            elif item.category == 10:
                self.count_lb_10 += 1
            elif item.category == 11:
                self.count_lb_11 += 1
            elif item.category == 12:
                self.count_lb_12 += 1
            # 13, 14
            elif item.category == 15:
                self.count_lb_15 += 1
            elif item.category == 16:
                self.count_lb_16 += 1
            else:
                self.SendMessage("分类异常：%s %s %s" % (item.market, item.code, item.name))
            if item.sector == 1:
                self.count_bk_1 += 1
            elif item.sector == 2:
                self.count_bk_2 += 1
            elif item.sector == 3:
                self.count_bk_3 += 1
            else:
                self.SendMessage("板块异常：%s %s %s" % (item.market, item.code, item.name))
            if item.is_st == 1:
                self.count_st_1 += 1
            if item.list_date == 0:
                self.count_ssrq += 1
        self.SendMessage("证券总计：%d" % len(self.security_dict))
        self.SendMessage("上海证券：%d" % self.count_sh)
        self.SendMessage("深圳证券：%d" % self.count_sz)
        self.SendMessage("沪A主板：%d" % self.count_lb_1)
        self.SendMessage("深A主板：%d" % self.count_lb_2)
        self.SendMessage("深A中小板：%d" % self.count_lb_3)
        self.SendMessage("深A创业板：%d" % self.count_lb_4)
        self.SendMessage("沪ETF基金：%d" % self.count_lb_5)
        self.SendMessage("深ETF基金：%d" % self.count_lb_6)
        self.SendMessage("沪LOF基金：%d" % self.count_lb_7)
        self.SendMessage("深LOF基金：%d" % self.count_lb_8)
        self.SendMessage("沪分级子基金：%d" % self.count_lb_9)
        self.SendMessage("深分级子基金：%d" % self.count_lb_10)
        self.SendMessage("沪封闭式基金：%d" % self.count_lb_11)
        self.SendMessage("深封闭式基金：%d" % self.count_lb_12)
        # 13, 14
        self.SendMessage("沪固收基金：%d" % self.count_lb_15)
        self.SendMessage("深固收基金：%d" % self.count_lb_16)
        self.SendMessage("主板板块：%d" % self.count_bk_1)
        self.SendMessage("中小板块：%d" % self.count_bk_2)
        self.SendMessage("创业板块：%d" % self.count_bk_3)
        self.SendMessage("ST类股票：%d" % self.count_st_1)
        self.SendMessage("无上市日：%d" % self.count_ssrq)

    def PullData_SecurityInfo(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_SecurityInfo 数据库 dbm 尚未连接！")
            return
        # 证券市场：83 上海证券交易所、90 深圳证券交易所
        # 证券类别：1 A股、8 开放式基金、13 投资基金、62 ETF基金
        # 上市板块：1 主板、2 中小企业板、6 创业板
        # 上市状态：1 上市、3 暂停、9 其他
        # 查询字段：SecuMain：证券内部编码、公司代码、证券代码、证券简称、证券市场、证券类别、上市日期、上市板块、上市状态
        # 唯一约束：SecuMain = InnerCode
        sql = "SELECT InnerCode, CompanyCode, SecuCode, SecuAbbr, SecuMarket, SecuCategory, ListedDate, ListedSector, ListedState \
               FROM SecuMain \
               WHERE (SecuMain.SecuMarket = 83 OR SecuMain.SecuMarket = 90) \
                   AND (SecuMain.SecuCategory = 1 OR SecuMain.SecuCategory = 8 OR SecuMain.SecuCategory = 13 OR SecuMain.SecuCategory = 62) \
                   AND (SecuMain.ListedState = 1 OR SecuMain.ListedState = 3 OR SecuMain.ListedState = 9) \
               ORDER BY SecuMarket ASC, SecuCode ASC"
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (InnerCode, CompanyCode, SecuCode, SecuAbbr, SecuMarket, SecuCategory, ListedDate, ListedSector, ListedState) in result_list:
                stock_name = SecuAbbr.replace(" ", "")
                stock_market = ""
                if SecuMarket == 83:
                    stock_market = "SH"
                elif SecuMarket == 90:
                    stock_market = "SZ"
                security_info_item = SecurityInfoItem(inners = InnerCode, company = CompanyCode, market = stock_market, code = SecuCode, name = stock_name)
                security_info_item.SetFlag_LB(SecuCategory, SecuMarket, SecuCode, ListedSector) # 证券类别
                security_info_item.SetFlag_BK(ListedSector) # 上市板块
                security_info_item.SetFlag_ST(stock_name) # 是否ST股
                security_info_item.SetFlag_ZT(ListedState) # 上市状态
                security_info_item.SetListDate(ListedDate) # 上市日期
                self.security_dict[InnerCode] = security_info_item
                #print(InnerCode, CompanyCode, SecuCode, SecuAbbr, SecuMarket, SecuCategory, ListedDate, ListedSector, ListedState)
            self.SendMessage("获取 证券信息 成功。总计 %d 个。" % len(result_list))
            self.CheckStockList()
        else:
            self.SendMessage("获取 证券信息 失败！")

    def SaveData_SecurityInfo(self, dbm, table_name, save_path):
        security_keys = list(self.security_dict.keys())
        security_keys.sort()
        security_dict_list = [self.security_dict[key] for key in security_keys]
        total_record_num = len(security_dict_list)
        values_list = []
        for i in range(total_record_num):
            str_date = common.TransDateIntToStr(security_dict_list[i].list_date)
            values_list.append((security_dict_list[i].inners, security_dict_list[i].company, security_dict_list[i].market, security_dict_list[i].code, security_dict_list[i].name, security_dict_list[i].category, security_dict_list[i].sector, security_dict_list[i].is_st, security_dict_list[i].list_state, str_date))
        columns = ["inners", "company", "market", "code", "name", "category", "sector", "is_st", "list_state", "list_date"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values_list) > 0:
            result = pd.DataFrame(data = values_list, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("本地保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))
        if dbm != None:
            sql = "CREATE TABLE `%s` (" % table_name + \
                  "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                  "`inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码'," + \
                  "`company` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '公司代码'," + \
                  "`market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，HK'," + \
                  "`code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码'," + \
                  "`name` varchar(32) DEFAULT '' COMMENT '证券名称'," + \
                  "`category` int(8) DEFAULT '0' COMMENT '证券类别，详见说明'," + \
                  "`sector` int(8) DEFAULT '0' COMMENT '上市板块，详见说明'," + \
                  "`is_st` int(8) DEFAULT '0' COMMENT '是否ST股，0:否、1:是'," + \
                  "`list_state` int(8) DEFAULT '0' COMMENT '上市状态，详见说明'," + \
                  "`list_date` date COMMENT '上市日期'," + \
                  "PRIMARY KEY (`id`)," + \
                  "UNIQUE KEY `idx_inners` (`inners`)," + \
                  "UNIQUE KEY `idx_company` (`company`)," + \
                  "UNIQUE KEY `idx_market_code` (`market`,`code`)" + \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            if dbm.TruncateOrCreateTable(table_name, sql) == True:
                sql = "INSERT INTO %s" % table_name + "(inners, company, market, code, name, category, sector, is_st, list_state, list_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                total_record_num, save_record_success, save_record_failed = dbm.BatchInsert(values_list, sql)
                self.SendMessage("远程入库：总记录 %d，入库记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))
            else:
                self.SendMessage("远程入库：初始化数据库表 %s 失败！" % table_name)

class DataMaker_SecurityInfo_HK():
    def __init__(self, parent = None):
        self.parent = parent
        self.security_dict = {}
        self.min_price_chg_dict = {}
        self.count_lb_21 = 0
        self.count_lb_22 = 0
        self.count_lb_23 = 0
        self.count_bk_1 = 0
        self.count_bk_2 = 0
        self.count_bk_3 = 0
        self.count_mpc = 0
        self.count_ssrq = 0

    def SendMessage(self, text_info):
        if self.parent != None:
            self.parent.SendMessage(text_info)

    def CheckStockList(self):
        for item in self.security_dict.values():
            if item.category == 21:
                self.count_lb_21 += 1
                if item.min_price_chg <= 0.0:
                    self.count_mpc += 1
            elif item.category == 22:
                self.count_lb_22 += 1
            elif item.category == 23:
                self.count_lb_23 += 1
            else:
                self.SendMessage("分类异常：%s %s %s" % (item.market, item.code, item.name))
            if item.sector == 1:
                self.count_bk_1 += 1
            elif item.sector == 2:
                self.count_bk_2 += 1
            elif item.sector == 3:
                self.count_bk_3 += 1
            else:
                self.SendMessage("板块异常：%s %s %s" % (item.market, item.code, item.name))
            if item.list_date == 0:
                self.count_ssrq += 1
        self.SendMessage("证券总计：%d" % len(self.security_dict))
        self.SendMessage("港股个股：%d" % self.count_lb_21)
        self.SendMessage("港股指数：%d" % self.count_lb_22)
        self.SendMessage("港股ETF基金：%d" % self.count_lb_23)
        self.SendMessage("主板板块：%d" % self.count_bk_1)
        self.SendMessage("中小板块：%d" % self.count_bk_2)
        self.SendMessage("创业板块：%d" % self.count_bk_3)
        self.SendMessage("无最小变动价格个股：%d" % self.count_mpc)
        self.SendMessage("无上市日：%d" % self.count_ssrq)

    def PullData_SecurityInfo_HK(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_SecurityInfo_HK 数据库 dbm 尚未连接！")
            return
        pre_date = ""
        now_date = datetime.now().strftime("%Y-%m-%d")
        # 证券市场：72 香港联交所
        # 查询字段：QT_TradingDayNew：日期、是否交易日、证券市场
        # 唯一约束：QT_TradingDayNew = Date、SecuMarket
        sql = "SELECT MAX(TradingDate) \
               FROM QT_TradingDayNew \
               WHERE QT_TradingDayNew.SecuMarket = 72 \
                   AND QT_TradingDayNew.TradingDate < '%s' \
                   AND QT_TradingDayNew.IfTradingDay = 1" % now_date
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (TradingDate,) in result_list:
                pre_date = TradingDate.strftime("%Y-%m-%d")
        if pre_date == "":
            self.SendMessage("获取 上一交易日期 失败！")
            return
        else:
            self.SendMessage("获取 上一交易日期 成功。%s" % pre_date)
        self.min_price_chg_dict = {}
        # 证券市场：72 香港联交所
        # 证券类别：3 H股、51 港股、52 合订证券、53 红筹股（排除 4 大盘指数 和 62 ETF基金）
        # 上市状态：1 上市、3 暂停
        # 查询字段：HK_SecuMain：证券内部编码、证券代码、证券简称、证券类别、证券市场
        # 查询字段：QT_HKDailyQuoteIndex：交易日、最小变动价格
        # 唯一约束：SecuMain = InnerCode、QT_HKDailyQuoteIndex = InnerCode & TradingDay
        sql = "SELECT HK_SecuMain.InnerCode, HK_SecuMain.SecuCode, HK_SecuMain.SecuAbbr, HK_SecuMain.SecuCategory, HK_SecuMain.SecuMarket, \
               QT_HKDailyQuoteIndex.TradingDay, CAST(QT_HKDailyQuoteIndex.MinPriceChg AS decimal(8,4)) \
               FROM HK_SecuMain INNER JOIN QT_HKDailyQuoteIndex \
               ON HK_SecuMain.InnerCode = QT_HKDailyQuoteIndex.InnerCode \
               WHERE (HK_SecuMain.SecuMarket = 72) \
                   AND (HK_SecuMain.SecuCategory = 3 OR HK_SecuMain.SecuCategory = 51 OR HK_SecuMain.SecuCategory = 52 OR HK_SecuMain.SecuCategory = 53) \
                   AND (HK_SecuMain.ListedState = 1 OR HK_SecuMain.ListedState = 3) \
                   AND QT_HKDailyQuoteIndex.TradingDay = '%s' \
               ORDER BY HK_SecuMain.SecuMarket ASC, HK_SecuMain.SecuCode ASC" % pre_date
        # 注意以上查询语句中，需要将 money 类型的 MinPriceChg 字段精度转换到 4 位，不然查询结果只会保留 2 位
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, TradingDay, MinPriceChg) in result_list:
                if MinPriceChg != None:
                    self.min_price_chg_dict[InnerCode] = MinPriceChg
                #print(InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, TradingDay, MinPriceChg)
            self.SendMessage("获取 上一交易日最小变动价格 成功。总计 %d 个。" % len(result_list))
        else:
            self.SendMessage("获取 上一交易最小变动价格 失败！")
        # 证券市场：72 香港联交所
        # 证券类别：3 H股、4 大盘(指数)、51 港股、52 合订证券、53 红筹股、62 ETF基金
        # 过滤排除：10 其他、20 衍生权证、21 股本权证、25 牛熊证、55 优先股、60 基金、61 信托基金、64 杠杆及反向产品、65 债务证券、69 美国证券、71 普通预托证券
        # 上市状态：1 上市、3 暂停
        # 查询字段：HK_SecuMain：证券内部编码、公司代码、证券代码、证券简称、证券市场、证券类别、上市日期、上市板块、上市状态、买卖单位
        # 唯一约束：HK_SecuMain = InnerCode
        sql = "SELECT InnerCode, CompanyCode, SecuCode, SecuAbbr, SecuMarket, SecuCategory, ListedDate, ListedSector, ListedState, TradingUnit \
               FROM HK_SecuMain \
               WHERE (HK_SecuMain.SecuMarket = 72) \
                   AND (HK_SecuMain.SecuCategory = 3 OR HK_SecuMain.SecuCategory = 4 OR HK_SecuMain.SecuCategory = 51 OR HK_SecuMain.SecuCategory = 52 OR HK_SecuMain.SecuCategory = 53 OR HK_SecuMain.SecuCategory = 62) \
                   AND (HK_SecuMain.ListedState = 1 OR HK_SecuMain.ListedState = 3) \
               ORDER BY SecuMarket ASC, SecuCode ASC"
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (InnerCode, CompanyCode, SecuCode, SecuAbbr, SecuMarket, SecuCategory, ListedDate, ListedSector, ListedState, TradingUnit) in result_list:
                stock_name = SecuAbbr.replace(" ", "")
                stock_market = "HK"
                security_info_item = SecurityInfoItem(inners = InnerCode, company = CompanyCode, market = stock_market, code = SecuCode, name = stock_name)
                security_info_item.SetFlag_LB(SecuCategory, SecuMarket, SecuCode, ListedSector) # 证券类别
                security_info_item.SetFlag_BK(ListedSector) # 上市板块
                security_info_item.SetFlag_ZT(ListedState) # 上市状态
                security_info_item.SetListDate(ListedDate) # 上市日期
                if TradingUnit != None:
                    security_info_item.trade_unit = int(TradingUnit) # 买卖单位
                if InnerCode in self.min_price_chg_dict.keys():
                    security_info_item.min_price_chg = self.min_price_chg_dict[InnerCode] # 最小变动价格
                self.security_dict[InnerCode] = security_info_item
                #print(InnerCode, CompanyCode, SecuCode, SecuAbbr, SecuMarket, SecuCategory, ListedDate, ListedSector, ListedState, TradingUnit)
            self.SendMessage("获取 证券信息-HK 成功。总计 %d 个。" % len(result_list))
            self.CheckStockList()
        else:
            self.SendMessage("获取 证券信息-HK 失败！")

    def SaveData_SecurityInfo_HK(self, dbm, table_name, save_path):
        security_keys = list(self.security_dict.keys())
        security_keys.sort()
        security_dict_list = [self.security_dict[key] for key in security_keys]
        total_record_num = len(security_dict_list)
        values_list = []
        for i in range(total_record_num):
            str_date = common.TransDateIntToStr(security_dict_list[i].list_date)
            values_list.append((security_dict_list[i].inners, security_dict_list[i].company, security_dict_list[i].market, security_dict_list[i].code, security_dict_list[i].name, security_dict_list[i].category, security_dict_list[i].sector, security_dict_list[i].trade_unit, security_dict_list[i].min_price_chg, security_dict_list[i].list_state, str_date))
        columns = ["inners", "company", "market", "code", "name", "category", "sector", "trade_unit", "min_price_chg", "list_state", "list_date"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values_list) > 0:
            result = pd.DataFrame(data = values_list, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("本地保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))
        if dbm != None:
            sql = "CREATE TABLE `%s` (" % table_name + \
                  "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                  "`inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码'," + \
                  "`company` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '公司代码'," + \
                  "`market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，SH、SZ'," + \
                  "`code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码'," + \
                  "`name` varchar(32) DEFAULT '' COMMENT '证券名称'," + \
                  "`category` int(8) DEFAULT '0' COMMENT '证券类别，详见说明'," + \
                  "`sector` int(8) DEFAULT '0' COMMENT '上市板块，详见说明'," + \
                  "`trade_unit` int(8) DEFAULT '0' COMMENT '买卖单位，股/手'," + \
                  "`min_price_chg` float(8,4) DEFAULT '0.0000' COMMENT '最小变动价格'," + \
                  "`list_state` int(8) DEFAULT '0' COMMENT '上市状态，详见说明'," + \
                  "`list_date` date COMMENT '上市日期'," + \
                  "PRIMARY KEY (`id`)," + \
                  "UNIQUE KEY `idx_inners` (`inners`)," + \
                  "KEY `idx_company` (`company`) USING BTREE," + \
                  "UNIQUE KEY `idx_market_code` (`market`,`code`)" + \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            if dbm.TruncateOrCreateTable(table_name, sql) == True:
                sql = "INSERT INTO %s" % table_name + "(inners, company, market, code, name, category, sector, trade_unit, min_price_chg, list_state, list_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                total_record_num, save_record_success, save_record_failed = dbm.BatchInsert(values_list, sql)
                self.SendMessage("远程入库：总记录 %d，入库记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))
            else:
                self.SendMessage("远程入库：初始化数据库表 %s 失败！" % table_name)

class DataMaker_TingPaiStock():
    def __init__(self, parent = None):
        self.parent = parent
        self.ting_pai_stock_list = []

    def SendMessage(self, text_info):
        if self.parent != None:
            self.parent.SendMessage(text_info)

    def PullData_TingPaiStock(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_TingPaiStock 数据库 dbm 尚未连接！")
            return
        self.ting_pai_stock_list = []
        now_date = datetime.now().strftime("%Y-%m-%d")
        # 证券市场：83 上海证券交易所、90 深圳证券交易所
        # 证券类别：1 A股、8 开放式基金、62 ETF基金
        # 上市板块：1 主板、2 中小企业板、6 创业板
        # 查询字段：SecuMain：证券内部编码、证券代码、证券简称、证券类别、证券市场
        # 查询字段：LC_SuspendResumption：停牌日期、停牌时间、停牌原因、停牌事项说明、停牌期限、复牌日期、复牌时间、复牌事项说明、更新时间
        # 唯一约束：SecuMain = InnerCode、LC_SuspendResumption = InnerCode & SuspendDate & SuspendTime
        sql = "SELECT SecuMain.InnerCode, SecuMain.SecuCode, SecuMain.SecuAbbr, SecuMain.SecuCategory, SecuMain.SecuMarket, \
                      LC_SuspendResumption.SuspendDate, LC_SuspendResumption.SuspendTime, LC_SuspendResumption.SuspendReason, LC_SuspendResumption.SuspendStatement, LC_SuspendResumption.SuspendTerm, \
                      LC_SuspendResumption.ResumptionDate, LC_SuspendResumption.ResumptionTime, LC_SuspendResumption.ResumptionStatement, LC_SuspendResumption.UpdateTime \
               FROM SecuMain INNER JOIN LC_SuspendResumption \
               ON SecuMain.InnerCode = LC_SuspendResumption.InnerCode \
               WHERE (SecuMain.SecuMarket = 83 OR SecuMain.SecuMarket = 90) \
                   AND (SecuMain.SecuCategory = 1 OR SecuMain.SecuCategory = 8 OR SecuMain.SecuCategory = 62) \
                   AND (SecuMain.ListedSector = 1 OR SecuMain.ListedSector = 2 OR SecuMain.ListedSector = 6) \
                   AND (LC_SuspendResumption.ResumptionDate = '1900-01-01' OR LC_SuspendResumption.ResumptionDate > '%s') \
               ORDER BY SecuMain.SecuMarket ASC, SecuMain.SecuCode ASC" % now_date # 复牌日期 1900-01-01 的为长期停牌
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, SuspendDate, SuspendTime, SuspendReason, SuspendStatement, SuspendTerm, ResumptionDate, ResumptionTime, ResumptionStatement, UpdateTime) in result_list:
                stock_name = SecuAbbr.replace(" ", "")
                stock_market = ""
                if SecuMarket == 83:
                    stock_market = "SH"
                elif SecuMarket == 90:
                    stock_market = "SZ"
                ting_pai_stock_item = TingPaiStockItem(inners = InnerCode, market = stock_market, code = SecuCode, name = stock_name, tp_date = SuspendDate, tp_time = SuspendTime, tp_reason = SuspendReason, tp_statement = SuspendStatement, tp_term = SuspendTerm, fp_date = ResumptionDate, fp_time = ResumptionTime, fp_statement = ResumptionStatement, update_time = UpdateTime)
                ting_pai_stock_item.SetCategory(SecuCategory, SecuCode) #
                self.ting_pai_stock_list.append(ting_pai_stock_item)
                #print(InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, SuspendDate, SuspendTime, SuspendReason, SuspendStatement, SuspendTerm, ResumptionDate, ResumptionTime, ResumptionStatement, UpdateTime)
                #print(SecuCode, SecuAbbr, SecuMarket, SuspendDate, ResumptionDate, SuspendReason)
            self.SendMessage("获取 今日停牌股票数据 成功。总计 %d 个。%s" % (len(result_list), now_date))
        else:
            self.SendMessage("获取 今日停牌股票数据 失败！")

    def SaveData_TingPaiStock(self, dbm, table_name, save_path):
        total_record_num = len(self.ting_pai_stock_list)
        values_list = []
        for i in range(total_record_num):
            str_date_tp = self.ting_pai_stock_list[i].tp_date.strftime("%Y-%m-%d")
            str_date_fp = self.ting_pai_stock_list[i].fp_date.strftime("%Y-%m-%d")
            str_date_up = self.ting_pai_stock_list[i].update_time.strftime("%Y-%m-%d")
            values_list.append((self.ting_pai_stock_list[i].inners, self.ting_pai_stock_list[i].market, self.ting_pai_stock_list[i].code, self.ting_pai_stock_list[i].name, self.ting_pai_stock_list[i].category, 
                                str_date_tp, self.ting_pai_stock_list[i].tp_time, self.ting_pai_stock_list[i].tp_reason, self.ting_pai_stock_list[i].tp_statement, self.ting_pai_stock_list[i].tp_term, 
                                str_date_fp, self.ting_pai_stock_list[i].fp_time, self.ting_pai_stock_list[i].fp_statement, str_date_up))
        columns = ["inners", "market", "code", "name", "category", "tp_date", "tp_time", "tp_reason", "tp_statement", "tp_term", "fp_date", "fp_time", "fp_statement", "update_time"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values_list) > 0:
            result = pd.DataFrame(data = values_list, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("本地保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))
        if dbm != None:
            sql = "CREATE TABLE `%s` (" % table_name + \
                  "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                  "`inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码'," + \
                  "`market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，SH、SZ'," + \
                  "`code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码'," + \
                  "`name` varchar(32) DEFAULT '' COMMENT '证券名称'," + \
                  "`category` int(8) DEFAULT '0' COMMENT '证券类别，详见说明'," + \
                  "``tp_date` datetime(6) DEFAULT NULL COMMENT '停牌日期'," + \
                  "``tp_time` varchar(30) DEFAULT '' COMMENT '停牌时间'," + \
                  "``tp_reason` varchar(110) DEFAULT '' COMMENT '停牌原因'," + \
                  "``tp_statement` int(8) DEFAULT '0' COMMENT '停牌事项说明，详见说明'," + \
                  "``tp_term` varchar(60) DEFAULT '' COMMENT '停牌期限'," + \
                  "``fp_date` datetime(6) DEFAULT NULL COMMENT '复牌日期'," + \
                  "``fp_time` varchar(30) DEFAULT '' COMMENT '复牌时间'," + \
                  "``fp_statement` varchar(110) DEFAULT '' COMMENT '复牌事项说明'," + \
                  "``update_time` datetime(6) DEFAULT NULL COMMENT '更新时间'," + \
                  "PRIMARY KEY (`id`)," + \
                  "UNIQUE KEY `idx_market_code` (`market`,`code`)" + \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            if dbm.TruncateOrCreateTable(table_name, sql) == True:
                sql = "INSERT INTO %s" % table_name + "(inners, market, code, name, category, tp_date, tp_time, tp_reason, tp_statement, tp_term, fp_date, fp_time, fp_statement, update_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                total_record_num, save_record_success, save_record_failed = dbm.BatchInsert(values_list, sql)
                self.SendMessage("远程入库：总记录 %d，入库记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))
            else:
                self.SendMessage("远程入库：初始化数据库表 %s 失败！" % table_name)

class DataMaker_TradingDay():
    def __init__(self, parent = None):
        self.parent = parent
        self.trading_day_list = []

    def SendMessage(self, text_info):
        if self.parent != None:
            self.parent.SendMessage(text_info)

    def PullData_TradingDay(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_TradingDay 数据库 dbm 尚未连接！")
            return
        self.trading_day_list = []
        # 证券市场：72、83 沪深交易所、89
        # 查询字段：QT_TradingDayNew：日期、是否交易日、证券市场、是否周末、是否月末、是否季末、是否年末
        # 唯一约束：QT_TradingDayNew = Date、SecuMarket
        sql = "SELECT TradingDate, IfTradingDay, SecuMarket, IfWeekEnd, IfMonthEnd, IfQuarterEnd, IfYearEnd \
               FROM QT_TradingDayNew \
               ORDER BY TradingDate ASC, SecuMarket ASC" # WHERE QT_TradingDayNew.SecuMarket = 83 \
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (TradingDate, IfTradingDay, SecuMarket, IfWeekEnd, IfMonthEnd, IfQuarterEnd, IfYearEnd) in result_list:
                trading_day = 0 if 2 == IfTradingDay else 1
                week_end = 0 if 2 == IfWeekEnd else 1
                month_end = 0 if 2 == IfMonthEnd else 1
                quarter_end = 0 if 2 == IfQuarterEnd else 1
                year_end = 0 if 2 == IfYearEnd else 1
                trading_day_item = TradingDayItem(market = SecuMarket, trading_day = trading_day, week_end = week_end, month_end = month_end, quarter_end = quarter_end, year_end = year_end)
                trading_day_item.SetNaturalDate(TradingDate) #
                self.trading_day_list.append(trading_day_item)
                #print(TradingDate, IfTradingDay, SecuMarket, IfWeekEnd, IfMonthEnd, IfQuarterEnd, IfYearEnd)
            self.SendMessage("获取 交易日期 成功。总计 %d 个。" % len(result_list))
        else:
            self.SendMessage("获取 交易日期 失败！")

    def SaveData_TradingDay(self, dbm, table_name, save_path):
        total_record_num = len(self.trading_day_list)
        values_list = []
        for i in range(total_record_num):
            str_date = common.TransDateIntToStr(self.trading_day_list[i].natural_date)
            values_list.append((str_date, self.trading_day_list[i].market, self.trading_day_list[i].trading_day, self.trading_day_list[i].week_end, self.trading_day_list[i].month_end, self.trading_day_list[i].quarter_end, self.trading_day_list[i].year_end))
        columns = ["natural_date", "market", "trading_day", "week_end", "month_end", "quarter_end", "year_end"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values_list) > 0:
            result = pd.DataFrame(data = values_list, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("本地保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))
        if dbm != None:
            sql = "CREATE TABLE `%s` (" % table_name + \
                  "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                  "``natural_date` date NOT NULL COMMENT '日期'," + \
                  "``market` int(4) unsigned NOT NULL DEFAULT '0' COMMENT '证券市场，72、83、89'," + \
                  "`trading_day` int(1) DEFAULT '0' COMMENT '是否交易'," + \
                  "``week_end` int(1) DEFAULT '0' COMMENT '是否周末'," + \
                  "``month_end` int(1) DEFAULT '0' COMMENT '是否月末'," + \
                  "``quarter_end` int(1) DEFAULT '0' COMMENT '是否季末'," + \
                  "``year_end` int(1) DEFAULT '0' COMMENT '是否年末'," + \
                  "PRIMARY KEY (`id`)," + \
                  "UNIQUE KEY `idx_natural_date_market` (`natural_date`,`market`)" + \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            if dbm.TruncateOrCreateTable(table_name, sql) == True:
                sql = "INSERT INTO %s" % table_name + "(natural_date, market, trading_day, week_end, month_end, quarter_end, year_end) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                total_record_num, save_record_success, save_record_failed = dbm.BatchInsert(values_list, sql)
                self.SendMessage("远程入库：总记录 %d，入库记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))
            else:
                self.SendMessage("远程入库：初始化数据库表 %s 失败！" % table_name)

class DataMaker_ExchangeRate():
    def __init__(self, parent = None):
        self.parent = parent
        self.exchange_rate_list = []

    def SendMessage(self, text_info):
        if self.parent != None:
            self.parent.SendMessage(text_info)

    def PullData_ExchangeRate(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_ExchangeRate 数据库 dbm 尚未连接！")
            return
        self.exchange_rate_list = []
        now_date = datetime.now().strftime("%Y-%m-%d")
        # 币种选择：1000 美元、1100 港元
        # 数据期间：5 日
        # 查询字段：ED_RMBBaseEXchangeRate：截止日期、币种选择、标价方式、期末价
        # 唯一约束：ED_RMBBaseEXchangeRate = EndDate、DataReportPeriod、Currency
        sql = "SELECT EndDate, Currency, QuotationType, CAST(PeriodEndPrice AS decimal(8,4)) \
               FROM ED_RMBBaseEXchangeRate \
               WHERE (Currency = 1000 OR Currency = 1100) \
                   AND (DataReportPeriod = 5) \
                   AND (EndDate = '%s')" % now_date
        # 注意以上查询语句中，需要将 money 类型的 PeriodEndPrice 字段精度转换到 4 位，不然查询结果只会保留 2 位
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (EndDate, Currency, QuotationType, PeriodEndPrice) in result_list:
                exchange_money = ""
                if 1000 == Currency:
                    exchange_money = "USD"
                elif 1100 == Currency:
                    exchange_money = "HKD"
                exchange_rate_item = ExchangeRateItem(base_money = "RMB", price = PeriodEndPrice, exchange_money = exchange_money, quote_type = QuotationType)
                exchange_rate_item.SetEndDate(EndDate) # 截止日期
                self.exchange_rate_list.append(exchange_rate_item)
                #print(InnerCode, SecuCode, SecuAbbr, SecuMarket, EndDate, TotalShares, AFloatListed)
            self.SendMessage("获取 基础汇率 成功。总计 %d 个。" % len(result_list))
        else:
            self.SendMessage("获取 基础汇率 失败！")

    def SaveData_ExchangeRate(self, dbm, table_name, save_path):
        total_record_num = len(self.exchange_rate_list)
        values_list = []
        for i in range(total_record_num):
            str_date = common.TransDateIntToStr(self.exchange_rate_list[i].end_date)
            values_list.append((self.exchange_rate_list[i].base_money, self.exchange_rate_list[i].price, self.exchange_rate_list[i].exchange_money, self.exchange_rate_list[i].quote_type, str_date))
        columns = ["base_money", "price", "exchange_money", "quote_type", "end_date"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values_list) > 0:
            result = pd.DataFrame(data = values_list, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("本地保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))
        if dbm != None:
            sql = "CREATE TABLE `%s` (" % table_name + \
                  "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                  "`base_money` varchar(8) NOT NULL DEFAULT '' COMMENT '基础货币，RMB'," + \
                  "`price` float(16,4) NOT NULL DEFAULT '0.0000' COMMENT '汇率价格，人民币元 / 100外币'," + \
                  "`exchange_money` varchar(8) NOT NULL DEFAULT '' COMMENT '汇兑货币，USD、HKD'," + \
                  "`quote_type` int(8) DEFAULT '0' COMMENT '标价方式，1 直接、2 间接'," + \
                  "`end_date` date NOT NULL COMMENT '截止日期'," + \
                  "PRIMARY KEY (`id`)," + \
                  "UNIQUE KEY `idx_base_money_exchange_money_end_date` (`base_money`,`exchange_money`,`end_date`)" + \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            if dbm.TruncateOrCreateTable(table_name, sql) == True:
                sql = "INSERT INTO %s" % table_name + "(base_money, price, exchange_money, quote_type, end_date) VALUES (%s, %s, %s, %s, %s)"
                total_record_num, save_record_success, save_record_failed = dbm.BatchInsert(values_list, sql)
                self.SendMessage("远程入库：总记录 %d，入库记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))
            else:
                self.SendMessage("远程入库：初始化数据库表 %s 失败！" % table_name)

class DataMaker_ComponentHSGGT():
    def __init__(self, parent = None):
        self.parent = parent
        self.component_hsggt_list = []

    def SendMessage(self, text_info):
        if self.parent != None:
            self.parent.SendMessage(text_info)

    def PullData_ComponentHSGGT(self, dbm):
        if dbm == None:
            self.SendMessage("PullData_ComponentHSGGT 数据库 dbm 尚未连接！")
            return
        self.component_hsggt_list = []
        # 成分类别：1 沪港通、2 沪股通、3 深股通、4 深港通
        # 成分标志：1 是成分股
        # 查询字段：SecuMain：证券内部编码、证券代码、证券简称、证券类别、证券市场
        # 查询字段：HK_SecuMain：证券内部编码、证券代码、证券简称、证券类别、证券市场
        # 查询字段：LC_ZHSCComponent：成分股类别、更新时间
        # 唯一约束：SecuMain = InnerCode、HK_SecuMain = InnerCode、LC_ZHSCComponent = CompType & InnerCode & InDate
        sql = "SELECT HK_SecuMain.InnerCode, HK_SecuMain.SecuCode, HK_SecuMain.SecuAbbr, HK_SecuMain.SecuCategory, HK_SecuMain.SecuMarket, LC_SHSCComponent.CompType, LC_SHSCComponent.UpdateTime \
               FROM HK_SecuMain INNER JOIN LC_SHSCComponent \
               ON HK_SecuMain.InnerCode = LC_SHSCComponent.InnerCode \
               WHERE LC_SHSCComponent.CompType = 1 AND LC_SHSCComponent.Flag = 1 \
               ORDER BY HK_SecuMain.SecuCode ASC"
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, CompType, UpdateTime) in result_list:
                stock_name = SecuAbbr.replace(" ", "")
                stock_market = ""
                if SecuMarket == 72:
                    stock_market = "HK"
                component_hsggt_item = ComponentHsggtItem(inners = InnerCode, market = stock_market, code = SecuCode, name = stock_name, comp_type = CompType, update_time = UpdateTime)
                component_hsggt_item.SetCategory(SecuCategory, SecuCode) #
                self.component_hsggt_list.append(component_hsggt_item)
                #print(InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, CompType, UpdateTime)
            self.SendMessage("获取 沪港通成分 成功。总计 %d 个。" % len(result_list))
        else:
            self.SendMessage("获取 沪港通成分 失败！")
        sql = "SELECT SecuMain.InnerCode, SecuMain.SecuCode, SecuMain.SecuAbbr, SecuMain.SecuCategory, SecuMain.SecuMarket, LC_SHSCComponent.CompType, LC_SHSCComponent.UpdateTime \
               FROM SecuMain INNER JOIN LC_SHSCComponent \
               ON SecuMain.InnerCode = LC_SHSCComponent.InnerCode \
               WHERE LC_SHSCComponent.CompType = 2 AND LC_SHSCComponent.Flag = 1 \
               ORDER BY SecuMain.SecuCode ASC"
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, CompType, UpdateTime) in result_list:
                stock_name = SecuAbbr.replace(" ", "")
                stock_market = ""
                if SecuMarket == 83:
                    stock_market = "SH"
                elif SecuMarket == 90:
                    stock_market = "SZ"
                component_hsggt_item = ComponentHsggtItem(inners = InnerCode, market = stock_market, code = SecuCode, name = stock_name, comp_type = CompType, update_time = UpdateTime)
                component_hsggt_item.SetCategory(SecuCategory, SecuCode) #
                self.component_hsggt_list.append(component_hsggt_item)
                #print(InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, CompType, UpdateTime)
            self.SendMessage("获取 沪股通成分 成功。总计 %d 个。" % len(result_list))
        else:
            self.SendMessage("获取 沪股通成分 失败！")
        sql = "SELECT HK_SecuMain.InnerCode, HK_SecuMain.SecuCode, HK_SecuMain.SecuAbbr, HK_SecuMain.SecuCategory, HK_SecuMain.SecuMarket, LC_ZHSCComponent.CompType, LC_ZHSCComponent.UpdateTime \
               FROM HK_SecuMain INNER JOIN LC_ZHSCComponent \
               ON HK_SecuMain.InnerCode = LC_ZHSCComponent.InnerCode \
               WHERE LC_ZHSCComponent.CompType = 4 AND LC_ZHSCComponent.Flag = 1 \
               ORDER BY HK_SecuMain.SecuCode ASC"
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, CompType, UpdateTime) in result_list:
                stock_name = SecuAbbr.replace(" ", "")
                stock_market = ""
                if SecuMarket == 72:
                    stock_market = "HK"
                component_hsggt_item = ComponentHsggtItem(inners = InnerCode, market = stock_market, code = SecuCode, name = stock_name, comp_type = CompType, update_time = UpdateTime)
                component_hsggt_item.SetCategory(SecuCategory, SecuCode) #
                self.component_hsggt_list.append(component_hsggt_item)
                #print(InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, CompType, UpdateTime)
            self.SendMessage("获取 深港通成分 成功。总计 %d 个。" % len(result_list))
        else:
            self.SendMessage("获取 深港通成分 失败！")
        sql = "SELECT SecuMain.InnerCode, SecuMain.SecuCode, SecuMain.SecuAbbr, SecuMain.SecuCategory, SecuMain.SecuMarket, LC_ZHSCComponent.CompType, LC_ZHSCComponent.UpdateTime \
               FROM SecuMain INNER JOIN LC_ZHSCComponent \
               ON SecuMain.InnerCode = LC_ZHSCComponent.InnerCode \
               WHERE LC_ZHSCComponent.CompType = 3 AND LC_ZHSCComponent.Flag = 1 \
               ORDER BY SecuMain.SecuCode ASC"
        result_list = dbm.ExecQuery(sql)
        if result_list != None:
            for (InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, CompType, UpdateTime) in result_list:
                stock_name = SecuAbbr.replace(" ", "")
                stock_market = ""
                if SecuMarket == 83:
                    stock_market = "SH"
                elif SecuMarket == 90:
                    stock_market = "SZ"
                component_hsggt_item = ComponentHsggtItem(inners = InnerCode, market = stock_market, code = SecuCode, name = stock_name, comp_type = CompType, update_time = UpdateTime)
                component_hsggt_item.SetCategory(SecuCategory, SecuCode) #
                self.component_hsggt_list.append(component_hsggt_item)
                #print(InnerCode, SecuCode, SecuAbbr, SecuCategory, SecuMarket, CompType, UpdateTime)
            self.SendMessage("获取 深股通成分 成功。总计 %d 个。" % len(result_list))
        else:
            self.SendMessage("获取 深股通成分 失败！")

    def SaveData_ComponentHSGGT(self, dbm, table_name, save_path):
        total_record_num = len(self.component_hsggt_list)
        values_list = []
        for i in range(total_record_num):
            values_list.append((self.component_hsggt_list[i].inners, self.component_hsggt_list[i].market, self.component_hsggt_list[i].code, self.component_hsggt_list[i].name, self.component_hsggt_list[i].category, 
                                self.component_hsggt_list[i].comp_type, self.component_hsggt_list[i].update_time.strftime("%Y-%m-%d")))
        columns = ["inners", "market", "code", "name", "category", "comp_type", "update_time"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values_list) > 0:
            result = pd.DataFrame(data = values_list, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("本地保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))
        if dbm != None:
            sql = "CREATE TABLE `%s` (" % table_name + \
                  "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                  "`inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码'," + \
                  "`market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，SH、SZ、HK'," + \
                  "`code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码'," + \
                  "`name` varchar(32) DEFAULT '' COMMENT '证券名称'," + \
                  "`category` int(8) DEFAULT '0' COMMENT '证券类别，详见说明'," + \
                  "`comp_type` int(8) DEFAULT '0' COMMENT '成分类别，详见说明'," + \
                  "`update_time` datetime(6) DEFAULT NULL COMMENT '更新时间'," + \
                  "PRIMARY KEY (`id`)," + \
                  "UNIQUE KEY `idx_market_code_comp_type` (`market`,`code`,`comp_type`)" + \
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            if dbm.TruncateOrCreateTable(table_name, sql) == True:
                sql = "INSERT INTO %s" % table_name + "(inners, market, code, name, category, comp_type, update_time) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                total_record_num, save_record_success, save_record_failed = dbm.BatchInsert(values_list, sql)
                self.SendMessage("远程入库：总记录 %d，入库记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))
            else:
                self.SendMessage("远程入库：初始化数据库表 %s 失败！" % table_name)

class BasicDataMaker(QDialog):
    def __init__(self, **kwargs):
        super(BasicDataMaker, self).__init__()
        self.folder = kwargs.get("folder", "") # 数据文件缓存
        self.tb_trading_day = "trading_day"
        self.tb_industry_data = "industry_data"
        self.tb_industry_data_hk = "industry_data_hk"
        self.tb_security_info = "security_info"
        self.tb_security_info_hk = "security_info_hk"
        self.tb_capital_data = "capital_data"
        self.tb_capital_data_hk = "capital_data_hk"
        self.tb_ex_rights_data = "ex_rights_data"
        self.tb_ting_pai_stock = "tod_ting_pai"
        self.tb_pre_quote_stk = "pre_quote_stk"
        self.tb_pre_quote_fue = "pre_quote_fue"
        self.tb_pre_quote_stk_hk = "pre_quote_stk_hk"
        self.tb_exchange_rate = "exchange_rate"
        self.tb_component_hsggt = "component_hsggt"
        
        self.mssql_host = "0.0.0.0"
        self.mssql_port = 0
        self.mssql_user = "user"
        self.mssql_password = "123456"
        self.mssql_database = "test"
        self.mssql_charset = "utf8"
        
        self.mysql_host = "0.0.0.0"
        self.mysql_port = 0
        self.mysql_user = "user"
        self.mysql_passwd = "123456"
        self.mysql_database = "test"
        self.mysql_charset = "utf8"
        
        self.dbm_jydb = None
        self.dbm_financial = None
        
        self.text_info_list = []
        self.text_info_index = 0
        self.flag_data_make = False # 手动点击就不用锁了
        self.flag_use_database = False
        
        if self.folder != "":
            self.folder_financial = self.folder + "/financial" # 可能路径含中文
            self.folder_quotedata = self.folder + "/quotedata" # 可能路径含中文
            self.folder_quotedata_stock = self.folder_quotedata + "/stock"
            self.folder_quotedata_stock_daily = self.folder_quotedata_stock + "/daily"
            self.folder_quotedata_stock_kline_1_m = self.folder_quotedata_stock + "/kline_1_m"
            if not os.path.exists(self.folder_financial):
                os.makedirs(self.folder_financial)
            # 下面已包含 folder_quotedata 和 folder_quotedata_stock 文件夹创建
            if not os.path.exists(self.folder_quotedata_stock_daily):
                os.makedirs(self.folder_quotedata_stock_daily)
            if not os.path.exists(self.folder_quotedata_stock_kline_1_m):
                os.makedirs(self.folder_quotedata_stock_kline_1_m)
        
        self.InitUserInterface()

    def __del__(self):
        pass

    def event(self, event):
        if event.type() == DEF_EVENT_TEXT_INFO_PRINT:
            self.OnTextInfoPrint()
        return QDialog.event(self, event)

    def OnTextInfoPrint(self):
        text_info_count = len(self.text_info_list)
        if text_info_count > self.text_info_index:
            for i in range(self.text_info_index, text_info_count):
                self.text_edit_text_info.append(self.text_info_list[i])
            self.text_edit_text_info.moveCursor(QTextCursor.End)
            self.text_info_index = text_info_count #

    def SendMessage(self, text_info):
        self.text_info_list.append(text_info)
        QApplication.postEvent(self, QEvent(DEF_EVENT_TEXT_INFO_PRINT))

    def SetMsSQL(self, **kwargs):
        self.mssql_host = kwargs.get("host", "0.0.0.0")
        self.mssql_port = kwargs.get("port", "0")
        self.mssql_user = kwargs.get("user", "user")
        self.mssql_password = kwargs.get("password", "123456")
        self.mssql_database = kwargs.get("database", "test")
        self.mssql_charset = kwargs.get("charset", "utf8")

    def SetMySQL(self, **kwargs):
        self.mysql_host = kwargs.get("host", "0.0.0.0")
        self.mysql_port = kwargs.get("port", 0)
        self.mysql_user = kwargs.get("user", "user")
        self.mysql_passwd = kwargs.get("passwd", "123456")
        self.mysql_db = kwargs.get("db", "test")
        self.mysql_charset = kwargs.get("charset", "utf8")
        self.flag_use_database = True #

    def ConnectDB(self):
        self.DisconnectDB() #
        try:
            self.dbm_jydb = dbm_mssql.DBM_MsSQL(host = self.mssql_host, port = self.mssql_port, user = self.mssql_user, password = self.mssql_password, database = self.mssql_database, charset = self.mssql_charset)
            if self.dbm_jydb.Start() == True:
                self.SendMessage("数据库 jydb 连接完成。")
            else:
                self.dbm_jydb = None
                self.SendMessage("数据库 jydb 连接失败！")
            if self.flag_use_database == True:
                self.dbm_financial = dbm_mysql.DBM_MySQL(host = self.mysql_host, port = self.mysql_port, user = self.mysql_user, passwd = self.mysql_passwd, db = self.mysql_db, charset = self.mysql_charset)
                if self.dbm_financial.Connect() == True:
                    self.SendMessage("数据库 financial 连接完成。")
                else:
                    self.dbm_financial = None
                    self.SendMessage("数据库 financial 连接失败！")
            else:
                self.SendMessage("不使用数据库 financial 保存基础数据。")
        except Exception as e:
            self.dbm_jydb = None
            self.dbm_financial = None
            self.SendMessage("建立数据库连接发生异常！%s" % e)

    def DisconnectDB(self):
        try:
            if self.dbm_jydb != None:
                self.dbm_jydb.Stop()
                self.dbm_jydb = None
                self.SendMessage("数据库 jydb 连接断开！")
            if self.flag_use_database == True:
                if self.dbm_financial != None:
                    self.dbm_financial.Disconnect()
                    self.dbm_financial = None
                    self.SendMessage("数据库 financial 连接断开！")
        except Exception as e:
            self.SendMessage("断开数据库连接发生异常！%s" % e)

    def InitUserInterface(self):
        self.setWindowTitle("基础数据生成")
        self.resize(390, 600)
        self.setFont(QFont("SimSun", 9))
        
        self.text_edit_text_info = QTextEdit()
        self.text_edit_text_info.setLineWrapMode(QTextEdit.NoWrap) # 不自动换行
        
        self.button_connect_db = QPushButton("数据库连接")
        self.button_connect_db.setFont(QFont("SimSun", 9))
        self.button_connect_db.setStyleSheet("color:black")
        self.button_connect_db.setFixedWidth(70)
        
        self.button_disconnect_db = QPushButton("数据库断开")
        self.button_disconnect_db.setFont(QFont("SimSun", 9))
        self.button_disconnect_db.setStyleSheet("color:black")
        self.button_disconnect_db.setFixedWidth(70)
        
        self.button_capital = QPushButton("股本结构")
        self.button_capital.setFont(QFont("SimSun", 9))
        self.button_capital.setStyleSheet("color:blue")
        self.button_capital.setFixedWidth(70)
        
        self.button_capital_hk = QPushButton("股本结构-HK")
        self.button_capital_hk.setFont(QFont("SimSun", 9))
        self.button_capital_hk.setStyleSheet("color:blue")
        self.button_capital_hk.setFixedWidth(85)
        
        self.button_exrights = QPushButton("除权数据")
        self.button_exrights.setFont(QFont("SimSun", 9))
        self.button_exrights.setStyleSheet("color:blue")
        self.button_exrights.setFixedWidth(70)
        
        self.button_industry = QPushButton("行业划分")
        self.button_industry.setFont(QFont("SimSun", 9))
        self.button_industry.setStyleSheet("color:blue")
        self.button_industry.setFixedWidth(70)
        
        self.button_industry_hk = QPushButton("行业划分-HK")
        self.button_industry_hk.setFont(QFont("SimSun", 9))
        self.button_industry_hk.setStyleSheet("color:blue")
        self.button_industry_hk.setFixedWidth(85)
        
        self.button_pre_quote_stk = QPushButton("股票行情")
        self.button_pre_quote_stk.setFont(QFont("SimSun", 9))
        self.button_pre_quote_stk.setStyleSheet("color:blue")
        self.button_pre_quote_stk.setFixedWidth(70)
        
        self.button_pre_quote_fue = QPushButton("期货行情")
        self.button_pre_quote_fue.setFont(QFont("SimSun", 9))
        self.button_pre_quote_fue.setStyleSheet("color:blue")
        self.button_pre_quote_fue.setFixedWidth(85)
        
        self.button_pre_quote_stk_hk = QPushButton("股票行情-HK")
        self.button_pre_quote_stk_hk.setFont(QFont("SimSun", 9))
        self.button_pre_quote_stk_hk.setStyleSheet("color:blue")
        self.button_pre_quote_stk_hk.setFixedWidth(85)
        
        self.button_security_info = QPushButton("证券信息")
        self.button_security_info.setFont(QFont("SimSun", 9))
        self.button_security_info.setStyleSheet("color:blue")
        self.button_security_info.setFixedWidth(70)
        
        self.button_security_info_hk = QPushButton("证券信息-HK")
        self.button_security_info_hk.setFont(QFont("SimSun", 9))
        self.button_security_info_hk.setStyleSheet("color:blue")
        self.button_security_info_hk.setFixedWidth(85)
        
        self.button_ting_pai_stock = QPushButton("当日停牌")
        self.button_ting_pai_stock.setFont(QFont("SimSun", 9))
        self.button_ting_pai_stock.setStyleSheet("color:blue")
        self.button_ting_pai_stock.setFixedWidth(70)
        
        self.button_trading_day = QPushButton("交易日期")
        self.button_trading_day.setFont(QFont("SimSun", 9))
        self.button_trading_day.setStyleSheet("color:blue")
        self.button_trading_day.setFixedWidth(85)
        
        self.button_exchange_rate = QPushButton("基础汇率")
        self.button_exchange_rate.setFont(QFont("SimSun", 9))
        self.button_exchange_rate.setStyleSheet("color:blue")
        self.button_exchange_rate.setFixedWidth(85)
        
        self.button_component_hsggt = QPushButton("港通成分")
        self.button_component_hsggt.setFont(QFont("SimSun", 9))
        self.button_component_hsggt.setStyleSheet("color:blue")
        self.button_component_hsggt.setFixedWidth(85)
        
        self.h_box_layout_database = QHBoxLayout()
        self.h_box_layout_database.setContentsMargins(-1, -1, -1, -1)
        self.h_box_layout_database.addStretch(1)
        self.h_box_layout_database.addWidget(self.button_connect_db)
        self.h_box_layout_database.addStretch(1)
        self.h_box_layout_database.addWidget(self.button_disconnect_db)
        self.h_box_layout_database.addStretch(1)
        
        self.h_box_layout_buttons_1 = QHBoxLayout()
        self.h_box_layout_buttons_1.setContentsMargins(-1, -1, -1, -1)
        self.h_box_layout_buttons_1.addStretch(1)
        self.h_box_layout_buttons_1.addWidget(self.button_capital)
        self.h_box_layout_buttons_1.addStretch(1)
        self.h_box_layout_buttons_1.addWidget(self.button_exrights)
        self.h_box_layout_buttons_1.addStretch(1)
        self.h_box_layout_buttons_1.addWidget(self.button_industry)
        self.h_box_layout_buttons_1.addStretch(1)
        self.h_box_layout_buttons_1.addWidget(self.button_pre_quote_stk)
        self.h_box_layout_buttons_1.addStretch(1)
        self.h_box_layout_buttons_1.addWidget(self.button_security_info)
        self.h_box_layout_buttons_1.addStretch(1)
        self.h_box_layout_buttons_1.addWidget(self.button_ting_pai_stock)
        self.h_box_layout_buttons_1.addStretch(1)
        
        self.h_box_layout_buttons_2 = QHBoxLayout()
        self.h_box_layout_buttons_2.setContentsMargins(-1, -1, -1, -1)
        self.h_box_layout_buttons_2.addStretch(1)
        self.h_box_layout_buttons_2.addWidget(self.button_capital_hk)
        self.h_box_layout_buttons_2.addStretch(1)
        self.h_box_layout_buttons_2.addWidget(self.button_industry_hk)
        self.h_box_layout_buttons_2.addStretch(1)
        self.h_box_layout_buttons_2.addWidget(self.button_pre_quote_stk_hk)
        self.h_box_layout_buttons_2.addStretch(1)
        self.h_box_layout_buttons_2.addWidget(self.button_security_info_hk)
        self.h_box_layout_buttons_2.addStretch(1)
        
        self.h_box_layout_buttons_3 = QHBoxLayout()
        self.h_box_layout_buttons_3.setContentsMargins(-1, -1, -1, -1)
        self.h_box_layout_buttons_3.addStretch(1)
        self.h_box_layout_buttons_3.addWidget(self.button_pre_quote_fue)
        self.h_box_layout_buttons_3.addStretch(1)
        self.h_box_layout_buttons_3.addWidget(self.button_exchange_rate)
        self.h_box_layout_buttons_3.addStretch(1)
        self.h_box_layout_buttons_3.addWidget(self.button_component_hsggt)
        self.h_box_layout_buttons_3.addStretch(1)
        self.h_box_layout_buttons_3.addWidget(self.button_trading_day)
        self.h_box_layout_buttons_3.addStretch(1)
        
        self.h_box_layout_text_info = QHBoxLayout()
        self.h_box_layout_text_info.setContentsMargins(-1, -1, -1, -1)
        self.h_box_layout_text_info.addWidget(self.text_edit_text_info)
        
        self.v_box_layout = QVBoxLayout()
        self.v_box_layout.setContentsMargins(-1, -1, -1, -1)
        self.v_box_layout.addLayout(self.h_box_layout_text_info)
        self.v_box_layout.addLayout(self.h_box_layout_database)
        self.v_box_layout.addLayout(self.h_box_layout_buttons_1)
        self.v_box_layout.addLayout(self.h_box_layout_buttons_2)
        self.v_box_layout.addLayout(self.h_box_layout_buttons_3)
        
        self.setLayout(self.v_box_layout)
        
        self.button_connect_db.clicked.connect(self.ConnectDB)
        self.button_disconnect_db.clicked.connect(self.DisconnectDB)
        self.button_capital.clicked.connect(self.OnButtonCapital)
        self.button_capital_hk.clicked.connect(self.OnButtonCapital_HK)
        self.button_exrights.clicked.connect(self.OnButtonExRights)
        self.button_industry.clicked.connect(self.OnButtonIndustry)
        self.button_industry_hk.clicked.connect(self.OnButtonIndustry_HK)
        self.button_pre_quote_stk.clicked.connect(self.OnButtonPreQuoteStk)
        self.button_pre_quote_fue.clicked.connect(self.OnButtonPreQuoteFue)
        self.button_pre_quote_stk_hk.clicked.connect(self.OnButtonPreQuoteStk_HK)
        self.button_security_info.clicked.connect(self.OnButtonSecurityInfo)
        self.button_security_info_hk.clicked.connect(self.OnButtonSecurityInfo_HK)
        self.button_ting_pai_stock.clicked.connect(self.OnButtonTingPaiStock)
        self.button_trading_day.clicked.connect(self.OnButtonTradingDay)
        self.button_exchange_rate.clicked.connect(self.OnButtonExchangeRate)
        self.button_component_hsggt.clicked.connect(self.OnButtonComponentHSGGT)

    def Thread_Capital(self, data_type):
        if self.flag_data_make == False:
            self.flag_data_make = True
            try:
                self.SendMessage("\n# -------------------- %s -------------------- #" % data_type)
                save_path = "%s/%s" % (self.folder_financial, self.tb_capital_data)
                data_maker_capital = DataMaker_Capital(self)
                data_maker_capital.PullData_Capital(self.dbm_jydb)
                data_maker_capital.SaveData_Capital(self.dbm_financial, self.tb_capital_data, save_path)
                self.SendMessage("# -------------------- %s -------------------- #" % data_type)
            except Exception as e:
                self.SendMessage("生成 %s 发生异常！%s" % (data_type, e))
            self.flag_data_make = False #
        else:
            self.SendMessage("正在生成数据，请等待...")

    def Thread_Capital_HK(self, data_type):
        if self.flag_data_make == False:
            self.flag_data_make = True
            try:
                self.SendMessage("\n# -------------------- %s -------------------- #" % data_type)
                save_path = "%s/%s" % (self.folder_financial, self.tb_capital_data_hk)
                data_maker_capital = DataMaker_Capital_HK(self)
                data_maker_capital.PullData_Capital_HK(self.dbm_jydb)
                data_maker_capital.SaveData_Capital_HK(self.dbm_financial, self.tb_capital_data_hk, save_path)
                self.SendMessage("# -------------------- %s -------------------- #" % data_type)
            except Exception as e:
                self.SendMessage("生成 %s 发生异常！%s" % (data_type, e))
            self.flag_data_make = False #
        else:
            self.SendMessage("正在生成数据，请等待...")

    def Thread_ExRights(self, data_type):
        if self.flag_data_make == False:
            self.flag_data_make = True
            try:
                self.SendMessage("\n# -------------------- %s -------------------- #" % data_type)
                save_path = "%s/%s" % (self.folder_financial, self.tb_ex_rights_data)
                data_maker_exrights = DataMaker_ExRights(self)
                data_maker_exrights.PullData_Stock(self.dbm_jydb)
                data_maker_exrights.PullData_PeiGu(self.dbm_jydb)
                data_maker_exrights.PullData_FenHong(self.dbm_jydb)
                data_maker_exrights.CalcMulerAdder()
                data_maker_exrights.SaveData_ExRights(self.dbm_financial, self.tb_ex_rights_data, save_path)
                self.SendMessage("# -------------------- %s -------------------- #" % data_type)
            except Exception as e:
                self.SendMessage("生成 %s 发生异常！%s" % (data_type, e))
            self.flag_data_make = False #
        else:
            self.SendMessage("正在生成数据，请等待...")

    def Thread_Industry(self, data_type):
        if self.flag_data_make == False:
            self.flag_data_make = True
            try:
                self.SendMessage("\n# -------------------- %s -------------------- #" % data_type)
                save_path = "%s/%s" % (self.folder_financial, self.tb_industry_data)
                data_maker_industry = DataMaker_Industry(self)
                data_maker_industry.PullData_Industry(self.dbm_jydb)
                data_maker_industry.SaveData_Industry(self.dbm_financial, self.tb_industry_data, save_path)
                self.SendMessage("# -------------------- %s -------------------- #" % data_type)
            except Exception as e:
                self.SendMessage("生成 %s 发生异常！%s" % (data_type, e))
            self.flag_data_make = False #
        else:
            self.SendMessage("正在生成数据，请等待...")

    def Thread_Industry_HK(self, data_type):
        if self.flag_data_make == False:
            self.flag_data_make = True
            try:
                self.SendMessage("\n# -------------------- %s -------------------- #" % data_type)
                save_path = "%s/%s" % (self.folder_financial, self.tb_industry_data_hk)
                data_maker_industry = DataMaker_Industry_HK(self)
                data_maker_industry.PullData_Industry_HK(self.dbm_jydb)
                data_maker_industry.SaveData_Industry_HK(self.dbm_financial, self.tb_industry_data_hk, save_path)
                self.SendMessage("# -------------------- %s -------------------- #" % data_type)
            except Exception as e:
                self.SendMessage("生成 %s 发生异常！%s" % (data_type, e))
            self.flag_data_make = False #
        else:
            self.SendMessage("正在生成数据，请等待...")

    def Thread_PreQuoteStk(self, data_type):
        if self.flag_data_make == False:
            self.flag_data_make = True
            try:
                self.SendMessage("\n# -------------------- %s -------------------- #" % data_type)
                save_path = "%s/%s" % (self.folder_financial, self.tb_pre_quote_stk)
                data_maker_pre_quote_stk = DataMaker_PreQuoteStk(self)
                data_maker_pre_quote_stk.PullData_PreQuoteStk(self.dbm_jydb)
                data_maker_pre_quote_stk.SaveData_PreQuoteStk(self.dbm_financial, self.tb_pre_quote_stk, save_path)
                self.SendMessage("# -------------------- %s -------------------- #" % data_type)
            except Exception as e:
                self.SendMessage("生成 %s 发生异常！%s" % (data_type, e))
            self.flag_data_make = False #
        else:
            self.SendMessage("正在生成数据，请等待...")

    def Thread_PreQuoteFue(self, data_type):
        if self.flag_data_make == False:
            self.flag_data_make = True
            try:
                self.SendMessage("\n# -------------------- %s -------------------- #" % data_type)
                save_path = "%s/%s" % (self.folder_financial, self.tb_pre_quote_fue)
                data_maker_pre_quote_fue = DataMaker_PreQuoteFue(self)
                data_maker_pre_quote_fue.PullData_PreQuoteFue(self.dbm_jydb)
                data_maker_pre_quote_fue.SaveData_PreQuoteFue(self.dbm_financial, self.tb_pre_quote_fue, save_path)
                self.SendMessage("# -------------------- %s -------------------- #" % data_type)
            except Exception as e:
                self.SendMessage("生成 %s 发生异常！%s" % (data_type, e))
            self.flag_data_make = False #
        else:
            self.SendMessage("正在生成数据，请等待...")

    def Thread_PreQuoteStk_HK(self, data_type):
        if self.flag_data_make == False:
            self.flag_data_make = True
            try:
                self.SendMessage("\n# -------------------- %s -------------------- #" % data_type)
                save_path = "%s/%s" % (self.folder_financial, self.tb_pre_quote_stk_hk)
                data_maker_pre_quote_stk = DataMaker_PreQuoteStk_HK(self)
                data_maker_pre_quote_stk.PullData_PreQuoteStk_HK(self.dbm_jydb)
                data_maker_pre_quote_stk.SaveData_PreQuoteStk_HK(self.dbm_financial, self.tb_pre_quote_stk_hk, save_path)
                self.SendMessage("# -------------------- %s -------------------- #" % data_type)
            except Exception as e:
                self.SendMessage("生成 %s 发生异常！%s" % (data_type, e))
            self.flag_data_make = False #
        else:
            self.SendMessage("正在生成数据，请等待...")

    def Thread_SecurityInfo(self, data_type):
        if self.flag_data_make == False:
            self.flag_data_make = True
            try:
                self.SendMessage("\n# -------------------- %s -------------------- #" % data_type)
                save_path = "%s/%s" % (self.folder_financial, self.tb_security_info)
                data_maker_security_info = DataMaker_SecurityInfo(self)
                data_maker_security_info.PullData_SecurityInfo(self.dbm_jydb)
                data_maker_security_info.SaveData_SecurityInfo(self.dbm_financial, self.tb_security_info, save_path)
                self.SendMessage("# -------------------- %s -------------------- #" % data_type)
            except Exception as e:
                self.SendMessage("生成 %s 发生异常！%s" % (data_type, e))
            self.flag_data_make = False #
        else:
            self.SendMessage("正在生成数据，请等待...")

    def Thread_SecurityInfo_HK(self, data_type):
        if self.flag_data_make == False:
            self.flag_data_make = True
            try:
                self.SendMessage("\n# -------------------- %s -------------------- #" % data_type)
                save_path = "%s/%s" % (self.folder_financial, self.tb_security_info_hk)
                data_maker_security_info_hk = DataMaker_SecurityInfo_HK(self)
                data_maker_security_info_hk.PullData_SecurityInfo_HK(self.dbm_jydb)
                data_maker_security_info_hk.SaveData_SecurityInfo_HK(self.dbm_financial, self.tb_security_info_hk, save_path)
                self.SendMessage("# -------------------- %s -------------------- #" % data_type)
            except Exception as e:
                self.SendMessage("生成 %s 发生异常！%s" % (data_type, e))
            self.flag_data_make = False #
        else:
            self.SendMessage("正在生成数据，请等待...")

    def Thread_TingPaiStock(self, data_type):
        if self.flag_data_make == False:
            self.flag_data_make = True
            try:
                self.SendMessage("\n# -------------------- %s -------------------- #" % data_type)
                save_path = "%s/%s" % (self.folder_financial, self.tb_ting_pai_stock)
                data_maker_ting_pai_stock = DataMaker_TingPaiStock(self)
                data_maker_ting_pai_stock.PullData_TingPaiStock(self.dbm_jydb)
                data_maker_ting_pai_stock.SaveData_TingPaiStock(self.dbm_financial, self.tb_ting_pai_stock, save_path)
                self.SendMessage("# -------------------- %s -------------------- #" % data_type)
            except Exception as e:
                self.SendMessage("生成 %s 发生异常！%s" % (data_type, e))
            self.flag_data_make = False #
        else:
            self.SendMessage("正在生成数据，请等待...")

    def Thread_TradingDay(self, data_type):
        if self.flag_data_make == False:
            self.flag_data_make = True
            try:
                self.SendMessage("\n# -------------------- %s -------------------- #" % data_type)
                save_path = "%s/%s" % (self.folder_financial, self.tb_trading_day)
                data_maker_trading_day = DataMaker_TradingDay(self)
                data_maker_trading_day.PullData_TradingDay(self.dbm_jydb)
                data_maker_trading_day.SaveData_TradingDay(self.dbm_financial, self.tb_trading_day, save_path)
                self.SendMessage("# -------------------- %s -------------------- #" % data_type)
            except Exception as e:
                self.SendMessage("生成 %s 发生异常！%s" % (data_type, e))
            self.flag_data_make = False #
        else:
            self.SendMessage("正在生成数据，请等待...")

    def Thread_ExchangeRate(self, data_type):
        if self.flag_data_make == False:
            self.flag_data_make = True
            try:
                self.SendMessage("\n# -------------------- %s -------------------- #" % data_type)
                save_path = "%s/%s" % (self.folder_financial, self.tb_exchange_rate)
                data_maker_exchange_rate = DataMaker_ExchangeRate(self)
                data_maker_exchange_rate.PullData_ExchangeRate(self.dbm_jydb)
                data_maker_exchange_rate.SaveData_ExchangeRate(self.dbm_financial, self.tb_exchange_rate, save_path)
                self.SendMessage("# -------------------- %s -------------------- #" % data_type)
            except Exception as e:
                self.SendMessage("生成 %s 发生异常！%s" % (data_type, e))
            self.flag_data_make = False #
        else:
            self.SendMessage("正在生成数据，请等待...")

    def Thread_ComponentHSGGT(self, data_type):
        if self.flag_data_make == False:
            self.flag_data_make = True
            try:
                self.SendMessage("\n# -------------------- %s -------------------- #" % data_type)
                save_path = "%s/%s" % (self.folder_financial, self.tb_component_hsggt)
                data_maker_component_hsggt = DataMaker_ComponentHSGGT(self)
                data_maker_component_hsggt.PullData_ComponentHSGGT(self.dbm_jydb)
                data_maker_component_hsggt.SaveData_ComponentHSGGT(self.dbm_financial, self.tb_component_hsggt, save_path)
                self.SendMessage("# -------------------- %s -------------------- #" % data_type)
            except Exception as e:
                self.SendMessage("生成 %s 发生异常！%s" % (data_type, e))
            self.flag_data_make = False #
        else:
            self.SendMessage("正在生成数据，请等待...")

    def OnButtonCapital(self):
        self.thread_make_data = threading.Thread(target = self.Thread_Capital, args = ("股本结构",))
        self.thread_make_data.start()

    def OnButtonCapital_HK(self):
        self.thread_make_data = threading.Thread(target = self.Thread_Capital_HK, args = ("股本结构-HK",))
        self.thread_make_data.start()

    def OnButtonExRights(self):
        self.thread_make_data = threading.Thread(target = self.Thread_ExRights, args = ("除权数据",))
        self.thread_make_data.start()

    def OnButtonIndustry(self):
        self.thread_make_data = threading.Thread(target = self.Thread_Industry, args = ("行业划分",))
        self.thread_make_data.start()

    def OnButtonIndustry_HK(self):
        self.thread_make_data = threading.Thread(target = self.Thread_Industry_HK, args = ("行业划分-HK",))
        self.thread_make_data.start()

    def OnButtonPreQuoteStk(self):
        self.thread_make_data = threading.Thread(target = self.Thread_PreQuoteStk, args = ("股票行情",))
        self.thread_make_data.start()

    def OnButtonPreQuoteFue(self):
        self.thread_make_data = threading.Thread(target = self.Thread_PreQuoteFue, args = ("期货行情",))
        self.thread_make_data.start()

    def OnButtonPreQuoteStk_HK(self):
        self.thread_make_data = threading.Thread(target = self.Thread_PreQuoteStk_HK, args = ("股票行情-HK",))
        self.thread_make_data.start()

    def OnButtonSecurityInfo(self):
        self.thread_make_data = threading.Thread(target = self.Thread_SecurityInfo, args = ("证券信息",))
        self.thread_make_data.start()

    def OnButtonSecurityInfo_HK(self):
        self.thread_make_data = threading.Thread(target = self.Thread_SecurityInfo_HK, args = ("证券信息-HK",))
        self.thread_make_data.start()

    def OnButtonTingPaiStock(self):
        self.thread_make_data = threading.Thread(target = self.Thread_TingPaiStock, args = ("当日停牌",))
        self.thread_make_data.start()

    def OnButtonTradingDay(self):
        self.thread_make_data = threading.Thread(target = self.Thread_TradingDay, args = ("交易日期",))
        self.thread_make_data.start()

    def OnButtonExchangeRate(self):
        self.thread_make_data = threading.Thread(target = self.Thread_ExchangeRate, args = ("基础汇率",))
        self.thread_make_data.start()

    def OnButtonComponentHSGGT(self):
        self.thread_make_data = threading.Thread(target = self.Thread_ComponentHSGGT, args = ("港通成分",))
        self.thread_make_data.start()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    basic_data_maker = BasicDataMaker(folder = "../data")
    basic_data_maker.SetMsSQL(host = "10.0.7.80", port = "1433", user = "user", password = "user", database = "JYDB_NEW", charset = "GBK")
    basic_data_maker.SetMySQL(host = "10.0.7.53", port = 3306, user = "user", passwd = "user", db = "financial", charset = "utf8")
    basic_data_maker.show()
    sys.exit(app.exec_())
