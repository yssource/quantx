
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

import os
import re
import time
import math
import threading
from datetime import datetime, date

import numpy as np
import pandas as pd

try: import logger
except: pass
import dbm_mongo
import dbm_mysql

pd.set_option("max_colwidth", 200)
pd.set_option("display.width", 500)

DEF_INIT_KLINE_ITEM_LOW = 99999.0

class Version(object):
    def __init__(self):
        self.major     = "major"
        self.minor     = "minor"
        self.revision  = "revision"
        self.build     = "build"
        self.name      = "name         BasicX"
        self.version   = "version      V0.1.0-Beta Build 20180515"
        self.author    = "author       Xu Rendong"
        self.developer = "developer    Developed by the X-Lab."
        self.company   = "company      X-Lab (Shanghai) Co., Ltd."
        self.copyright = "copyright    Copyright 2018-2018 X-Lab All Rights Reserved."
        self.homeurl   = "homeurl      http://www.xlab.com"
        self.data = [0, 1, 0, 20180515, "", "", "", "", "", "", ""]
        self.columns = ["version"]
        self.index = [self.major, self.minor, self.revision, self.build, self.name, self.version, self.author, self.developer, self.company, self.copyright, self.homeurl]
        self.version_df = pd.DataFrame(data = self.data, columns = self.columns, index = self.index)

class Security(object):
    def __init__(self, **kwargs):
        self.inners = kwargs.get("inners", 0) # 内部代码
        self.company = kwargs.get("company", 0) # 公司代码
        self.market = kwargs.get("market", "") # ֤证券市场
        self.code = kwargs.get("code", "") # 证券代码
        self.name = kwargs.get("name", "") # 证券名称
        self.category = kwargs.get("category", 0) # 证券类别
        self.sector = kwargs.get("sector", 0) # 上市板块
        self.is_st = kwargs.get("is_st", 0) # 是否ST股
        self.list_state = kwargs.get("list_state", 0) # 上市状态
        self.list_date = kwargs.get("list_date", 0) # 上市日期

class ExRights(object):
    def __init__(self, **kwargs):
        self.inners = kwargs.get("inners", 0) # 内部代码
        self.market = kwargs.get("market", "") #֤ 证券市场
        self.code = kwargs.get("code", "") # 证券代码
        self.date = kwargs.get("date", 0) # 除权除息日期
        self.muler = kwargs.get("muler", 0.0) # 乘数
        self.adder = kwargs.get("adder", 0.0) # 加数
        self.sg = kwargs.get("sg", 0.0) # 送股比率，每股
        self.pg = kwargs.get("pg", 0.0) # 配股比率，每股
        self.price = kwargs.get("price", 0.0) # 配股价
        self.bonus = kwargs.get("bonus", 0.0) # 现金红利

class KlineItem(object):
    def __init__(self, index, str_date, str_time):
        self.index = index # 分钟索引
        self.date = str_date # 日期 "2018-01-01"
        self.time = str_time # 时间 "11:30:00"
        self.open = 0.0 # 开盘价
        self.high = 0.0 # 最高价
        self.low = DEF_INIT_KLINE_ITEM_LOW # 最低价
        self.close = 0.0 # 收盘价
        self.volume = 0 # 成交量，股
        self.turnover = 0 # 成交额，元

class Singleton(object): # 与 common.py 中的相同
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

class BasicX(Singleton):
    def __init__(self):
        self.log_text = ""
        self.log_cate = "BasicX"
        self.logger = None
        self.ignore_user_tips = False
        self.ignore_local_file_loss = False
        self.ignore_exrights_data_loss = False
        self.ignore_local_data_imperfect = False
        try: self.logger = logger.Logger()
        except: pass

    def InitBasicData(self, **kwargs):
        self.host = kwargs.get("host", "0.0.0.0")
        self.port = kwargs.get("port", 0)
        self.user = kwargs.get("user", "user")
        self.passwd = kwargs.get("passwd", "123456")
        self.folder = kwargs.get("folder", "") # 数据文件缓存
        self.db_financial = "financial"
        self.db_quotedata = "quotedata"
        self.charset = "utf8"
        self.tb_trading_day = "trading_day"
        self.tb_industry_data = "industry_data"
        self.tb_security_info = "security_info"
        self.tb_capital_data = "capital_data"
        self.tb_ex_rights_data = "ex_rights_data"
        self.tb_ting_pai_stock = "tod_ting_pai"
        
        self.flag_use_database = True
        if self.host == "0.0.0.0": # 不使用数据库
            self.flag_use_database = False
        
        self.tables_financial = {} # 索引：表名
        self.tables_stock_daily = {} # 索引：sh_600000、sz_000001
        self.tables_stock_kline_1_m = {} # 索引：sh_600000、sz_000001
        
        self.df_tables_financial = pd.DataFrame(columns = ["table"]) # 空
        self.df_tables_stock_daily = pd.DataFrame(columns = ["table"]) # 空
        self.df_tables_stock_kline_1_m = pd.DataFrame(columns = ["table"]) # 空
        
        self.folder_financial = ""
        self.folder_quotedata = ""
        self.folder_quotedata_stock = ""
        self.folder_quotedata_stock_daily = ""
        self.folder_quotedata_stock_kline_1_m = ""
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
        
        self.dbm_financial = None
        self.dbm_quotedata = None
        if self.flag_use_database == True:
            self.dbm_financial = dbm_mysql.DBM_MySQL(host = self.host, port = self.port, user = self.user, passwd = self.passwd, db = self.db_financial, charset = self.charset) # db_financial
            self.dbm_quotedata = dbm_mysql.DBM_MySQL(host = self.host, port = self.port, user = self.user, passwd = self.passwd, db = self.db_quotedata, charset = self.charset) # db_quotedata
            if self.dbm_financial.Connect() == True:
                #self.InitTables_Financial() # 慢一点
                self.InitTables_Financial_DB() # 快一点
            if self.dbm_quotedata.Connect() == True:
                #self.InitTables_QuoteData() # 慢一点
                self.InitTables_QuoteData_DB() # 快一点
        
        self.security_dict = None # 首次计算除权时缓存一份证券信息
        self.exrights_dict = None # 首次计算除权时缓存一份除权数据

    def InitCacheData(self, **kwargs): # 目前先独立配置
        self.mongo_host = kwargs.get("host", "0.0.0.0")
        self.mongo_port = kwargs.get("port", 0)
        self.quote_flag = kwargs.get("quote", "")
        self.mongo_db_quote_stock_tdf = "quote_stock_tdf" # tdf
        self.mongo_db_quote_stock_ltb = "quote_stock_ltb" # ltb
        self.mongo_db_quote_stock_ltp = "quote_stock_ltp" # ltp
        self.mongo_db_quote_future_ctp = "quote_future_ctp" # ctp
        self.mongo_cc_stock_snapshot_s = "snapshot_s" # stock
        self.mongo_cc_stock_snapshot_i = "snapshot_i" # index
        self.mongo_cc_future_snapshot = "snapshot" # future
        
        self.dbm_mongo_quotedata_stock_s_tdf = None
        self.dbm_mongo_quotedata_stock_i_tdf = None
        self.dbm_mongo_quotedata_stock_s_ltb = None
        self.dbm_mongo_quotedata_stock_i_ltb = None
        self.dbm_mongo_quotedata_stock_s_ltp = None
        self.dbm_mongo_quotedata_stock_i_ltp = None
        self.dbm_mongo_quotedata_future_ctp = None
        if "TDF" in self.quote_flag:
            self.dbm_mongo_quotedata_stock_s_tdf = dbm_mongo.DBM_Mongo(host = self.mongo_host, port = self.mongo_port, database = self.mongo_db_quote_stock_tdf, collection = self.mongo_cc_stock_snapshot_s)
            self.dbm_mongo_quotedata_stock_i_tdf = dbm_mongo.DBM_Mongo(host = self.mongo_host, port = self.mongo_port, database = self.mongo_db_quote_stock_tdf, collection = self.mongo_cc_stock_snapshot_i)
            self.dbm_mongo_quotedata_stock_s_tdf.Connect()
            self.dbm_mongo_quotedata_stock_i_tdf.Connect()
        if "LTB" in self.quote_flag:
            self.dbm_mongo_quotedata_stock_s_ltb = dbm_mongo.DBM_Mongo(host = self.mongo_host, port = self.mongo_port, database = self.mongo_db_quote_stock_ltb, collection = self.mongo_cc_stock_snapshot_s)
            self.dbm_mongo_quotedata_stock_i_ltb = dbm_mongo.DBM_Mongo(host = self.mongo_host, port = self.mongo_port, database = self.mongo_db_quote_stock_ltb, collection = self.mongo_cc_stock_snapshot_i)
            self.dbm_mongo_quotedata_stock_s_ltb.Connect()
            self.dbm_mongo_quotedata_stock_i_ltb.Connect()
        if "LTP" in self.quote_flag:
            self.dbm_mongo_quotedata_stock_s_ltp = dbm_mongo.DBM_Mongo(host = self.mongo_host, port = self.mongo_port, database = self.mongo_db_quote_stock_ltp, collection = self.mongo_cc_stock_snapshot_s)
            self.dbm_mongo_quotedata_stock_i_ltp = dbm_mongo.DBM_Mongo(host = self.mongo_host, port = self.mongo_port, database = self.mongo_db_quote_stock_ltp, collection = self.mongo_cc_stock_snapshot_i)
            self.dbm_mongo_quotedata_stock_s_ltp.Connect()
            self.dbm_mongo_quotedata_stock_i_ltp.Connect()
        if "CTP" in self.quote_flag:
            self.dbm_mongo_quotedata_future_ctp = dbm_mongo.DBM_Mongo(host = self.mongo_host, port = self.mongo_port, database = self.mongo_db_quote_future_ctp, collection = self.mongo_cc_future_snapshot)
            self.dbm_mongo_quotedata_future_ctp.Connect()

    def __del__(self):
        if self.dbm_financial != None:
            self.dbm_financial.Disconnect()
        if self.dbm_quotedata != None:
            self.dbm_quotedata.Disconnect()

    def SendMessage(self, log_kind, log_class, log_cate, log_info, log_show = ""):
        if self.logger != None:
            self.logger.SendMessage(log_kind, log_class, log_cate, log_info, log_show)
        else:
            print("%s：%s：%s" % (log_kind, log_cate, log_info))

    def IgnoreUserTips(self, ignore):
        self.ignore_user_tips = ignore

    def IgnoreLocalFileLoss(self, ignore):
        self.ignore_local_file_loss = ignore

    def IgnoreExRightsDataLoss(self, ignore):
        self.ignore_exrights_data_loss = ignore

    def IgnoreLocalDataImperfect(self, ignore):
        self.ignore_local_data_imperfect = ignore

    def Version(self):
        return Version().version_df

    def TransDateIntToStr(self, int_date):
        year = int(int_date / 10000)
        month = int((int_date % 10000) / 100)
        day = int_date % 100
        return "%d-%d-%d" % (year, month, day)

    def TransDateIntToDate(self, int_date):
        year = int(int_date / 10000)
        month = int((int_date % 10000) / 100)
        day = int_date % 100
        return date(year, month, day)

    def TransTimeIntToStr(self, int_time):
        hour = int(int_time / 10000)
        minute = int((int_time % 10000) / 100)
        second = int_time % 100
        return "%d:%d:%d" % (hour, minute, second)

    def GetTableModifyTime(self, dbm, db_name, tb_name):
        modify_time = None
        sql = "SELECT CREATE_TIME, UPDATE_TIME " + \
              "FROM information_schema.TABLES " + \
              "WHERE TABLE_SCHEMA = '%s' AND information_schema.TABLES.TABLE_NAME = '%s'" % (db_name, tb_name)
        rows = dbm.QueryAllSql(sql)
        if len(rows) == 1: # 数据表存在
            create_time_db = rows[0][0]
            modify_time_db = rows[0][1]
            if create_time_db != None:
                modify_time = create_time_db # 先赋创建时间
            if modify_time_db != None:
                modify_time = modify_time_db # 再赋更新时间
        return modify_time

    def InitTables_Financial(self): # 慢一点
        dbm = self.dbm_financial
        sql = "SHOW TABLES"
        data_tables = [dbm.QueryAllSql(sql)]
        #print(data_tables)
        have_tables = re.findall("(\'.*?\')", str(data_tables))
        have_tables = [re.sub("'", "", table) for table in have_tables]
        #print(have_tables)
        for table in have_tables:
            self.tables_financial[table] = table
        self.df_tables_financial = pd.DataFrame(data = sorted(self.tables_financial.values()), columns = ["table"])

    def InitTables_Financial_DB(self): # 快一点
        dbm = self.dbm_financial
        sql = "SELECT TABLE_NAME " + \
              "FROM information_schema.TABLES " + \
              "WHERE TABLE_SCHEMA = '%s'" % self.db_financial
        rows = dbm.QueryAllSql(sql)
        for (table_name,) in rows:
            #print(table_name)
            self.tables_financial[table_name] = table_name
        self.df_tables_financial = pd.DataFrame(data = sorted(self.tables_financial.values()), columns = ["table"])

    def GetTables_Financial(self):
        return self.df_tables_financial

    def GetTradingDay(self):
        save_path = ""
        dbm = self.dbm_financial
        columns = ["natural_date", "market", "trading_day", "week_end", "month_end", "quarter_end", "year_end"]
        result = pd.DataFrame(columns = columns) # 空
        if dbm == None: # 直接读取本地文件
            if self.folder_financial == "": # 缓存路径为空
                self.log_text = "直接缓存获取 交易日期 时，本地数据缓存路径为空！"
                self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
            else:
                save_path = "%s/%s" % (self.folder_financial, self.tb_trading_day)
                if not os.path.exists(save_path): # 缓存文件不存在
                    self.log_text = "直接缓存获取 交易日期 时，本地数据缓存文件不存在！"
                    self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
                else: # 读取缓存文件
                    result = pd.read_pickle(save_path)
        else: # 可以查询数据库
            need_query = False
            if self.folder_financial == "": # 缓存路径为空
                need_query = True
            else:
                save_path = "%s/%s" % (self.folder_financial, self.tb_trading_day)
                if not os.path.exists(save_path): # 缓存文件不存在
                    need_query = True
                else:
                    modify_time_lf = datetime.fromtimestamp(os.path.getmtime(save_path))
                    modify_time_db = self.GetTableModifyTime(dbm, self.db_financial, self.tb_trading_day)
                    if modify_time_db != None and modify_time_lf < modify_time_db: # 数据库时间更新 # 如果 modify_time_db 为 None 估计数据库表不存在也就不用查询了
                        need_query = True
                    else: # 读取缓存文件
                        result = pd.read_pickle(save_path)
            if need_query == True: # 查询数据表
                sql = "SELECT natural_date, market, trading_day, week_end, month_end, quarter_end, year_end " + \
                      "FROM %s " % self.tb_trading_day + \
                      "WHERE market = 83 AND natural_date >= '2010-01-01' AND natural_date < '2020-01-01'" + \
                      "ORDER BY natural_date ASC, market ASC"
                rows = dbm.QueryAllSql(sql)
                if len(rows) > 0:
                    result = pd.DataFrame(data = list(rows), columns = columns)
                    if save_path != "": # 保存到文件
                        result.to_pickle(save_path)
        if result.empty:
            self.log_text = "获取的 交易日期 为空！"
            self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        return result

    def GetIndustryData(self):
        save_path = ""
        dbm = self.dbm_financial
        columns = ["standard", "industry", "industry_code_1", "industry_name_1", "industry_code_2", "industry_name_2", 
                   "industry_code_3", "industry_name_3", "industry_code_4", "industry_name_4", "inners", "market", "code", "name", "info_date"]
        result = pd.DataFrame(columns = columns) # 空
        if dbm == None: # 直接读取本地文件
            if self.folder_financial == "": # 缓存路径为空
                self.log_text = "直接缓存获取 行业划分 时，本地数据缓存路径为空！"
                self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
            else:
                save_path = "%s/%s" % (self.folder_financial, self.tb_industry_data)
                if not os.path.exists(save_path): # 缓存文件不存在
                    self.log_text = "直接缓存获取 行业划分 时，本地数据缓存文件不存在！"
                    self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
                else: # 读取缓存文件
                    result = pd.read_pickle(save_path)
        else: # 可以查询数据库
            need_query = False
            if self.folder_financial == "": # 缓存路径为空
                need_query = True
            else:
                save_path = "%s/%s" % (self.folder_financial, self.tb_industry_data)
                if not os.path.exists(save_path): # 缓存文件不存在
                    need_query = True
                else:
                    modify_time_lf = datetime.fromtimestamp(os.path.getmtime(save_path))
                    modify_time_db = self.GetTableModifyTime(dbm, self.db_financial, self.tb_industry_data)
                    if modify_time_db != None and modify_time_lf < modify_time_db: # 数据库时间更新 # 如果 modify_time_db 为 None 估计数据库表不存在也就不用查询了
                        need_query = True
                    else: # 读取缓存文件
                        result = pd.read_pickle(save_path)
            if need_query == True: # 查询数据表
                sql = "SELECT standard, industry, industry_code_1, industry_name_1, industry_code_2, industry_name_2, " + \
                      "industry_code_3, industry_name_3, industry_code_4, industry_name_4, inners, market, code, name, info_date " + \
                      "FROM %s " % self.tb_industry_data + \
                      "ORDER BY standard ASC, industry_code_1 ASC, industry_code_2 ASC, industry_code_3 ASC, industry_code_4 ASC, market ASC, code ASC"
                rows = dbm.QueryAllSql(sql)
                if len(rows) > 0:
                    result = pd.DataFrame(data = list(rows), columns = columns)
                    if save_path != "": # 保存到文件
                        result.to_pickle(save_path)
        if result.empty:
            self.log_text = "获取的 行业划分 为空！"
            self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        return result

    def GetSecurityInfo(self):
        save_path = ""
        dbm = self.dbm_financial
        columns = ["inners", "company", "market", "code", "name", "category", "sector", "is_st", "list_state", "list_date"]
        result = pd.DataFrame(columns = columns) # 空
        if dbm == None: # 直接读取本地文件
            if self.folder_financial == "": # 缓存路径为空
                self.log_text = "直接缓存获取 证券信息 时，本地数据缓存路径为空！"
                self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
            else:
                save_path = "%s/%s" % (self.folder_financial, self.tb_security_info)
                if not os.path.exists(save_path): # 缓存文件不存在
                    self.log_text = "直接缓存获取 证券信息 时，本地数据缓存文件不存在！"
                    self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
                else: # 读取缓存文件
                    result = pd.read_pickle(save_path)
        else: # 可以查询数据库
            need_query = False
            if self.folder_financial == "": # 缓存路径为空
                need_query = True
            else:
                save_path = "%s/%s" % (self.folder_financial, self.tb_security_info)
                if not os.path.exists(save_path): # 缓存文件不存在
                    need_query = True
                else:
                    modify_time_lf = datetime.fromtimestamp(os.path.getmtime(save_path))
                    modify_time_db = self.GetTableModifyTime(dbm, self.db_financial, self.tb_security_info)
                    if modify_time_db != None and modify_time_lf < modify_time_db: # 数据库时间更新 # 如果 modify_time_db 为 None 估计数据库表不存在也就不用查询了
                        need_query = True
                    else: # 读取缓存文件
                        result = pd.read_pickle(save_path)
            if need_query == True: # 查询数据表
                sql = "SELECT inners, company, market, code, name, category, sector, is_st, list_state, list_date " + \
                      "FROM %s " % self.tb_security_info + \
                      "ORDER BY market ASC, code ASC"
                rows = dbm.QueryAllSql(sql)
                if len(rows) > 0:
                    result = pd.DataFrame(data = list(rows), columns = columns)
                    if save_path != "": # 保存到文件
                        result.to_pickle(save_path)
        if result.empty:
            self.log_text = "获取的 证券信息 为空！"
            self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        # 首次调用时保存到 security_dict 中
        if self.security_dict == None and not result.empty:
            self.security_dict = {}
            data = result.values.tolist()
            for [inners, company, market, code, name, category, sector, is_st, list_state, list_date] in data:
                key = "%s_%s" % (market.lower(), code)
                self.security_dict[key] = Security(inners = inners, company = company, market = market, code = code, name = name, category = category, sector = sector, is_st = is_st, list_state = list_state, list_date = list_date)
            #for security_item in self.security_dict.values():
            #    print(security_item.inners, security_item.company, security_item.market, security_item.code, security_item.name, \
            #          security_item.category, security_item.sector, security_item.is_st, security_item.list_state, security_item.list_date)
        return result

    def GetCapitalData(self):
        save_path = ""
        dbm = self.dbm_financial
        columns = ["inners", "market", "code", "name", "end_date", "total_shares", "circu_shares"]
        result = pd.DataFrame(columns = columns) # 空
        if dbm == None: # 直接读取本地文件
            if self.folder_financial == "": # 缓存路径为空
                self.log_text = "直接缓存获取 股本结构 时，本地数据缓存路径为空！"
                self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
            else:
                save_path = "%s/%s" % (self.folder_financial, self.tb_capital_data)
                if not os.path.exists(save_path): # 缓存文件不存在
                    self.log_text = "直接缓存获取 股本结构 时，本地数据缓存文件不存在！"
                    self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
                else: # 读取缓存文件
                    result = pd.read_pickle(save_path)
        else: # 可以查询数据库
            need_query = False
            if self.folder_financial == "": # 缓存路径为空
                need_query = True
            else:
                save_path = "%s/%s" % (self.folder_financial, self.tb_capital_data)
                if not os.path.exists(save_path): # 缓存文件不存在
                    need_query = True
                else:
                    modify_time_lf = datetime.fromtimestamp(os.path.getmtime(save_path))
                    modify_time_db = self.GetTableModifyTime(dbm, self.db_financial, self.tb_capital_data)
                    if modify_time_db != None and modify_time_lf < modify_time_db: # 数据库时间更新 # 如果 modify_time_db 为 None 估计数据库表不存在也就不用查询了
                        need_query = True
                    else: # 读取缓存文件
                        result = pd.read_pickle(save_path)
            if need_query == True: # 查询数据表
                sql = "SELECT inners, market, code, name, end_date, total_shares, circu_shares " + \
                      "FROM %s " % self.tb_capital_data + \
                      "ORDER BY market ASC, code ASC"
                rows = dbm.QueryAllSql(sql)
                if len(rows) > 0:
                    result = pd.DataFrame(data = list(rows), columns = columns)
                    if save_path != "": # 保存到文件
                        result.to_pickle(save_path)
        if result.empty:
            self.log_text = "获取的 股本结构 为空！"
            self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        return result

    def GetExRightsData(self):
        save_path = ""
        dbm = self.dbm_financial
        columns = ["inners", "market", "code", "date", "muler", "adder", "sg", "pg", "price", "bonus"]
        result = pd.DataFrame(columns = columns) # 空
        if dbm == None: # 直接读取本地文件
            if self.folder_financial == "": # 缓存路径为空
                self.log_text = "直接缓存获取 除权数据 时，本地数据缓存路径为空！"
                self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
            else:
                save_path = "%s/%s" % (self.folder_financial, self.tb_ex_rights_data)
                if not os.path.exists(save_path): # 缓存文件不存在
                    self.log_text = "直接缓存获取 除权数据 时，本地数据缓存文件不存在！"
                    self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
                else: # 读取缓存文件
                    result = pd.read_pickle(save_path)
        else: # 可以查询数据库
            need_query = False
            if self.folder_financial == "": # 缓存路径为空
                need_query = True
            else:
                save_path = "%s/%s" % (self.folder_financial, self.tb_ex_rights_data)
                if not os.path.exists(save_path): # 缓存文件不存在
                    need_query = True
                else:
                    modify_time_lf = datetime.fromtimestamp(os.path.getmtime(save_path))
                    modify_time_db = self.GetTableModifyTime(dbm, self.db_financial, self.tb_ex_rights_data)
                    if modify_time_db != None and modify_time_lf < modify_time_db: # 数据库时间更新 # 如果 modify_time_db 为 None 估计数据库表不存在也就不用查询了
                        need_query = True
                    else: # 读取缓存文件
                        result = pd.read_pickle(save_path)
            if need_query == True: # 查询数据表
                sql = "SELECT inners, market, code, date, muler, adder, sg, pg, price, bonus " + \
                      "FROM %s " % self.tb_ex_rights_data + \
                      "ORDER BY market ASC, code ASC, date ASC"
                rows = dbm.QueryAllSql(sql)
                if len(rows) > 0:
                    result = pd.DataFrame(data = list(rows), columns = columns)
                    if save_path != "": # 保存到文件
                        result.to_pickle(save_path)
        if result.empty:
            self.log_text = "获取的 除权数据 为空！"
            self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        # 首次调用时保存到 exrights_dict 中
        if self.exrights_dict == None and not result.empty:
            self.exrights_dict = {}
            data = result.values.tolist()
            for [inners, market, code, date, muler, adder, sg, pg, price, bonus] in data:
                key = "%s_%s" % (market.lower(), code)
                exrights_item = ExRights(inners = inners, market = market, code = code, date = date, muler = muler, adder = adder, sg = sg, pg = pg, price = price, bonus = bonus)
                if not key in self.exrights_dict.keys():
                    self.exrights_dict[key] = []
                self.exrights_dict[key].append(exrights_item)
            #for exrights_list in self.exrights_dict.values():
            #    for exrights_item in exrights_list:
            #        print(exrights_item.inners, exrights_item.market, exrights_item.code, exrights_item.date, \
            #              exrights_item.muler, exrights_item.adder, exrights_item.sg, exrights_item.pg, exrights_item.price, exrights_item.bonus)
        return result

    def GetTingPaiStock(self):
        save_path = ""
        dbm = self.dbm_financial
        columns = ["inners", "market", "code", "name", "category", "tp_date", "tp_time", "tp_reason", "tp_statement", "tp_term", "fp_date", "fp_time", "fp_statement", "update_time"]
        result = pd.DataFrame(columns = columns) # 空
        if dbm == None: # 直接读取本地文件
            if self.folder_financial == "": # 缓存路径为空
                self.log_text = "直接缓存获取 当日停牌证券 时，本地数据缓存路径为空！"
                self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
            else:
                save_path = "%s/%s" % (self.folder_financial, self.tb_ting_pai_stock)
                if not os.path.exists(save_path): # 缓存文件不存在
                    self.log_text = "直接缓存获取 当日停牌证券 时，本地数据缓存文件不存在！"
                    self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
                else: # 读取缓存文件
                    result = pd.read_pickle(save_path)
        else: # 可以查询数据库
            need_query = False
            if self.folder_financial == "": # 缓存路径为空
                need_query = True
            else:
                save_path = "%s/%s" % (self.folder_financial, self.tb_ting_pai_stock)
                if not os.path.exists(save_path): # 缓存文件不存在
                    need_query = True
                else:
                    modify_time_lf = datetime.fromtimestamp(os.path.getmtime(save_path))
                    modify_time_db = self.GetTableModifyTime(dbm, self.db_financial, self.tb_ting_pai_stock)
                    if modify_time_db != None and modify_time_lf < modify_time_db: # 数据库时间更新 # 如果 modify_time_db 为 None 估计数据库表不存在也就不用查询了
                        need_query = True
                    else: # 读取缓存文件
                        result = pd.read_pickle(save_path)
            if need_query == True: # 查询数据表
                sql = "SELECT inners, market, code, name, category, " + \
                      "tp_date, tp_time, tp_reason, tp_statement, tp_term, fp_date, fp_time, fp_statement, update_time " + \
                      "FROM %s " % self.tb_ting_pai_stock + \
                      "ORDER BY market ASC, code ASC"
                rows = dbm.QueryAllSql(sql)
                if len(rows) > 0:
                    result = pd.DataFrame(data = list(rows), columns = columns)
                    if save_path != "": # 保存到文件
                        result.to_pickle(save_path)
        if result.empty:
            self.log_text = "获取的 当日停牌证券 为空！"
            self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        return result

    def InitTables_QuoteData(self): # 慢一点
        dbm = self.dbm_quotedata
        sql = "SHOW TABLES"
        data_tables = [dbm.QueryAllSql(sql)]
        #print(data_tables)
        have_tables = re.findall("(\'.*?\')", str(data_tables))
        have_tables = [re.sub("'", "", table) for table in have_tables]
        #print(have_tables)
        for table in have_tables:
            key = table[-9:] # sh_600000、sz_000001
            if table[0:11] == "stock_daily":
                self.tables_stock_daily[key] = table
            elif table[0:15] == "stock_kline_1_m":
                self.tables_stock_kline_1_m[key] = table
        self.df_tables_stock_daily = pd.DataFrame(data = sorted(self.tables_stock_daily.values()), columns = ["table"])
        self.df_tables_stock_kline_1_m = pd.DataFrame(data = sorted(self.tables_stock_kline_1_m.values()), columns = ["table"])

    def InitTables_QuoteData_DB(self): # 快一点
        dbm = self.dbm_quotedata
        sql = "SELECT TABLE_NAME " + \
              "FROM information_schema.TABLES " + \
              "WHERE TABLE_SCHEMA = '%s'" % self.db_quotedata
        rows = dbm.QueryAllSql(sql)
        for (table_name,) in rows:
            #print(table_name)
            key = table_name[-9:] # sh_600000、sz_000001
            if table_name[0:11] == "stock_daily":
                self.tables_stock_daily[key] = table_name
            elif table_name[0:15] == "stock_kline_1_m":
                self.tables_stock_kline_1_m[key] = table_name
        self.df_tables_stock_daily = pd.DataFrame(data = sorted(self.tables_stock_daily.values()), columns = ["table"])
        self.df_tables_stock_kline_1_m = pd.DataFrame(data = sorted(self.tables_stock_kline_1_m.values()), columns = ["table"])

    def GetTables_Stock_Daily(self):
        return self.df_tables_stock_daily

    def GetTables_Stock_Kline_1_M(self):
        return self.df_tables_stock_kline_1_m

    def GetStockDaily(self, market, code, date_s, date_e):
        save_path = ""
        dbm = self.dbm_quotedata
        columns = ["date", "open", "high", "low", "close", "volume", "turnover"]
        result = pd.DataFrame(columns = columns) # 空
        if date_s > date_e:
            self.log_text = "获取 %s %s 的 Daily 数据时，日期入参异常！S：%d > E：%d" % (market, code, date_s, date_e)
            self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
            return result
        str_file_date_s = "" # 缓存 起始 日期
        str_file_date_e = "" # 缓存 终止 日期
        str_user_date_s = self.TransDateIntToStr(date_s) # 用户 起始 日期
        str_user_date_e = self.TransDateIntToStr(date_e) # 用户 终止 日期
        date_user_date_s = self.TransDateIntToDate(date_s) # 用户 起始 日期
        date_user_date_e = self.TransDateIntToDate(date_e) # 用户 终止 日期
        if dbm == None: # 直接读取本地文件
            if self.folder_quotedata_stock_daily == "": # 缓存路径为空
                self.log_text = "直接缓存获取 %s %s 的 Daily 数据时，本地数据缓存路径为空！" % (market, code)
                self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
            else:
                save_path = "%s/stock_daily_%s_%s" % (self.folder_quotedata_stock_daily, market.lower(), code)
                if not os.path.exists(save_path): # 缓存文件不存在
                    if False == self.ignore_local_file_loss:
                        self.log_text = "直接缓存获取 %s %s 的 Daily 数据时，本地数据缓存文件不存在！" % (market, code)
                        self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
                else: # 读取缓存文件
                    locals = pd.read_pickle(save_path)
                    date_file_date_s = locals["date"].min()
                    date_file_date_e = locals["date"].max()
                    # 注意，如果缓存文件存在但是没有实际数据，这里取到的 date 就会变成值为 nan 的 float，目前以不生成空数据缓存文件来避免
                    int_file_date_s = date_file_date_s.year * 10000 + date_file_date_s.month * 100 + date_file_date_s.day
                    int_file_date_e = date_file_date_e.year * 10000 + date_file_date_e.month * 100 + date_file_date_e.day
                    result = locals.ix[(locals.date >= date_user_date_s) & (locals.date <= date_user_date_e), :]
                    #print("不使用数据库，直接从缓存数据读取")
                    if False == self.ignore_local_data_imperfect:
                        if date_file_date_s > date_user_date_s:
                            self.log_text = "直接缓存获取 %s %s 的 Daily 数据时，本地起始 %d，用户要求 %d，数据可能不全！" % (market, code, int_file_date_s, date_s)
                            self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
                        if date_file_date_e < date_user_date_e:
                            self.log_text = "直接缓存获取 %s %s 的 Daily 数据时，本地终止 %d，用户要求 %d，数据可能不全！" % (market, code, int_file_date_e, date_e)
                            self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        else: # 可以查询数据库
            need_query_all = False
            key = "%s_%s" % (market.lower(), code)
            if key in self.tables_stock_daily.keys():
                table_name = self.tables_stock_daily[key]
                if self.folder_quotedata_stock_daily == "": # 缓存路径为空
                    need_query_all = True
                else:
                    save_path = "%s/%s" % (self.folder_quotedata_stock_daily, table_name)
                    if not os.path.exists(save_path): # 缓存文件不存在
                        need_query_all = True
                    else: # 读取缓存文件
                        locals = pd.read_pickle(save_path)
                        date_file_date_s = locals["date"].min()
                        date_file_date_e = locals["date"].max()
                        # 注意，如果缓存文件存在但是没有实际数据，这里取到的 date 就会变成值为 nan 的 float，目前以不生成空数据缓存文件来避免
                        int_file_date_s = date_file_date_s.year * 10000 + date_file_date_s.month * 100 + date_file_date_s.day
                        int_file_date_e = date_file_date_e.year * 10000 + date_file_date_e.month * 100 + date_file_date_e.day
                        str_file_date_s = self.TransDateIntToStr(int_file_date_s)
                        str_file_date_e = self.TransDateIntToStr(int_file_date_e)
                        if date_file_date_s <= date_user_date_s and date_file_date_e >= date_user_date_e: # 用户请求都在缓存数据中
                            result = locals.ix[(locals.date >= date_user_date_s) & (locals.date <= date_user_date_e), :]
                            #print("都在缓存数据中")
                        else:
                            sql_from_where = ""
                            if date_file_date_s > date_user_date_s and date_file_date_e >= date_user_date_e: # 需要补充 早一点 的数据
                                #if date_file_date_s <= date_user_date_e: # 缓存数据和请求数据，有交集
                                #    usable = locals.ix[locals.date <= date_user_date_e, :]
                                #    sql_from_where = "FROM %s WHERE (date >= '%s' AND date < '%s') " % (table_name, str_user_date_s, str_file_date_s)
                                #    print("补充 早一点 的数据，有交集")
                                #if date_file_date_s > date_user_date_e: # 缓存数据和请求数据，有空隙
                                #    usable = pd.DataFrame(columns = columns) # 空
                                #    sql_from_where = "FROM %s WHERE (date >= '%s' AND date < '%s') " % (table_name, str_user_date_s, str_file_date_s)
                                #    print("补充 早一点 的数据，有空隙")
                                usable = locals.ix[locals.date <= date_user_date_e, :]
                                sql_from_where = "FROM %s WHERE (date >= '%s' AND date < '%s') " % (table_name, str_user_date_s, str_file_date_s)
                                #print("补充 早一点 的数据")
                            if date_file_date_s <= date_user_date_s and date_file_date_e < date_user_date_e: # 需要补充 晚一点 的数据
                                #if date_user_date_s <= date_file_date_e: # 缓存数据和请求数据，有交集
                                #    usable = locals.ix[locals.date >= date_user_date_s, :]
                                #    print("补充 晚一点 的数据，有交集")
                                #if date_user_date_s > date_file_date_e: # 缓存数据和请求数据，有空隙
                                #    usable = pd.DataFrame(columns = columns) # 空
                                #    print("补充 晚一点 的数据，有空隙")
                                usable = locals.ix[locals.date >= date_user_date_s, :]
                                sql_from_where = "FROM %s WHERE (date > '%s' AND date <= '%s') " % (table_name, str_file_date_e, str_user_date_e)
                                #print("补充 晚一点 的数据")
                            if date_file_date_s > date_user_date_s and date_file_date_e < date_user_date_e: # 需要补充 早一点 和 晚一点 的数据
                                usable = locals.ix[:, :]
                                sql_from_where = "FROM %s WHERE (date >= '%s' AND date < '%s') OR (date > '%s' AND date <= '%s')" % (table_name, str_user_date_s, str_file_date_s, str_file_date_e, str_user_date_e)
                                #print("补充 早一点 和 晚一点 的数据")
                            if sql_from_where != "":
                                sql = "SELECT date, open, high, low, close, volume, turnover " + sql_from_where + "ORDER BY date ASC"
                                rows = dbm.QueryAllSql(sql)
                                supply = pd.DataFrame(data = list(rows), columns = columns)
                                # 返回的结果
                                result = usable.append(supply, ignore_index = True)
                                if date_file_date_s > date_user_date_e: # 去掉空隙部分
                                    result = result.ix[result.date <= date_user_date_e, :]
                                if date_user_date_s > date_file_date_e: # 去掉空隙部分
                                    result = result.ix[result.date >= date_user_date_s, :]
                                result = result.sort_values(by = ["date"], ascending = True).reset_index(drop = True)
                                # 提示一下以期减少查询提高效率
                                date_result_date_s = result["date"].min()
                                date_result_date_e = result["date"].max()
                                if date_user_date_s < date_result_date_s or date_user_date_e > date_result_date_e:
                                    if False == self.ignore_user_tips:
                                        self.log_text = "建议将 %s %s 的 Daily 请求日期设为 %s 到 %s 以提高效率。" % \
                                              (market, code, date_result_date_s.strftime("%Y%m%d"), date_result_date_e.strftime("%Y%m%d"))
                                        self.SendMessage("H", 2, self.log_cate, self.log_text, "A")
                                # 更新的缓存
                                locals = locals.append(supply, ignore_index = True)
                                locals = locals.sort_values(by = ["date"], ascending = True).reset_index(drop = True)
                                if save_path != "": # 保存到文件
                                    locals.to_pickle(save_path)
                if need_query_all == True: # 所有都要查询
                    #print("数据需要全部查询")
                    sql = "SELECT date, open, high, low, close, volume, turnover " + \
                          "FROM %s " % table_name + \
                          "WHERE (date >= '%s' AND date <= '%s') " % (str_user_date_s, str_user_date_e) + \
                          "ORDER BY date ASC"
                    rows = dbm.QueryAllSql(sql)
                    if len(rows) > 0:
                        result = pd.DataFrame(data = list(rows), columns = columns)
                        if save_path != "": # 保存到文件
                            result.to_pickle(save_path)
                    if result.empty:
                        self.log_text = "获取 %s %s 的 %s ~ %s 的 Daily 数据为空！" % (market, code, str_user_date_s, str_user_date_e)
                        self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
            else:
                self.log_text = "数据库中不存在 %s %s 的 Daily 数据表！" % (market, code)
                self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        return result

    def GetStockKline_1_M(self, market, code, date_s, date_e):
        save_path = ""
        dbm = self.dbm_quotedata
        columns = ["date", "time", "open", "high", "low", "close", "volume", "turnover"]
        result = pd.DataFrame(columns = columns) # 空
        if date_s > date_e:
            self.log_text = "获取 %s %s 的 Kline_1_M 数据时，日期入参异常！S：%d > E：%d" % (market, code, date_s, date_e)
            self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
            return result
        str_file_date_s = "" # 缓存 起始 日期
        str_file_date_e = "" # 缓存 终止 日期
        str_user_date_s = self.TransDateIntToStr(date_s) # 用户 起始 日期
        str_user_date_e = self.TransDateIntToStr(date_e) # 用户 终止 日期
        date_user_date_s = self.TransDateIntToDate(date_s) # 用户 起始 日期
        date_user_date_e = self.TransDateIntToDate(date_e) # 用户 终止 日期
        if dbm == None: # 直接读取本地文件
            if self.folder_quotedata_stock_kline_1_m == "": # 缓存路径为空
                self.log_text = "直接缓存获取 %s %s 的 Kline_1_M 数据时，本地数据缓存路径为空！" % (market, code)
                self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
            else:
                save_path = "%s/stock_kline_1_m_%s_%s" % (self.folder_quotedata_stock_kline_1_m, market.lower(), code)
                if not os.path.exists(save_path): # 缓存文件不存在
                    if False == self.ignore_local_file_loss:
                        self.log_text = "直接缓存获取 %s %s 的 Kline_1_M 数据时，本地数据缓存文件不存在！" % (market, code)
                        self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
                else: # 读取缓存文件
                    locals = pd.read_pickle(save_path)
                    date_file_date_s = locals["date"].min()
                    date_file_date_e = locals["date"].max()
                    # 注意，如果缓存文件存在但是没有实际数据，这里取到的 date 就会变成值为 nan 的 float，目前以不生成空数据缓存文件来避免
                    int_file_date_s = date_file_date_s.year * 10000 + date_file_date_s.month * 100 + date_file_date_s.day
                    int_file_date_e = date_file_date_e.year * 10000 + date_file_date_e.month * 100 + date_file_date_e.day
                    result = locals.ix[(locals.date >= date_user_date_s) & (locals.date <= date_user_date_e), :]
                    #print("不使用数据库，直接从缓存数据读取")
                    if False == self.ignore_local_data_imperfect:
                        if date_file_date_s > date_user_date_s:
                            self.log_text = "直接缓存获取 %s %s 的 Kline_1_M 数据时，本地起始 %d，用户要求 %d，数据可能不全！" % (market, code, int_file_date_s, date_s)
                            self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
                        if date_file_date_e < date_user_date_e:
                            self.log_text = "直接缓存获取 %s %s 的 Kline_1_M 数据时，本地终止 %d，用户要求 %d，数据可能不全！" % (market, code, int_file_date_e, date_e)
                            self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        else: # 可以查询数据库
            need_query_all = False
            key = "%s_%s" % (market.lower(), code)
            if key in self.tables_stock_kline_1_m.keys():
                table_name = self.tables_stock_kline_1_m[key]
                if self.folder_quotedata_stock_kline_1_m == "": # 缓存路径为空
                    need_query_all = True
                else:
                    save_path = "%s/%s" % (self.folder_quotedata_stock_kline_1_m, table_name)
                    if not os.path.exists(save_path): # 缓存文件不存在
                        need_query_all = True
                    else: # 读取缓存文件
                        locals = pd.read_pickle(save_path)
                        date_file_date_s = locals["date"].min()
                        date_file_date_e = locals["date"].max()
                        # 注意，如果缓存文件存在但是没有实际数据，这里取到的 date 就会变成值为 nan 的 float，目前以不生成空数据缓存文件来避免
                        int_file_date_s = date_file_date_s.year * 10000 + date_file_date_s.month * 100 + date_file_date_s.day
                        int_file_date_e = date_file_date_e.year * 10000 + date_file_date_e.month * 100 + date_file_date_e.day
                        str_file_date_s = self.TransDateIntToStr(int_file_date_s)
                        str_file_date_e = self.TransDateIntToStr(int_file_date_e)
                        if date_file_date_s <= date_user_date_s and date_file_date_e >= date_user_date_e: # 用户请求都在缓存数据中
                            result = locals.ix[(locals.date >= date_user_date_s) & (locals.date <= date_user_date_e), :]
                            #print("都在缓存数据中")
                        else:
                            sql_from_where = ""
                            if date_file_date_s > date_user_date_s and date_file_date_e >= date_user_date_e: # 需要补充 早一点 的数据
                                #if date_file_date_s <= date_user_date_e: # 缓存数据和请求数据，有交集
                                #    usable = locals.ix[locals.date <= date_user_date_e, :]
                                #    sql_from_where = "FROM %s WHERE (date >= '%s' AND date < '%s') " % (table_name, str_user_date_s, str_file_date_s)
                                #    print("补充 早一点 的数据，有交集")
                                #if date_file_date_s > date_user_date_e: # 缓存数据和请求数据，有空隙
                                #    usable = pd.DataFrame(columns = columns) # 空
                                #    sql_from_where = "FROM %s WHERE (date >= '%s' AND date < '%s') " % (table_name, str_user_date_s, str_file_date_s)
                                #    print("补充 早一点 的数据，有空隙")
                                usable = locals.ix[locals.date <= date_user_date_e, :]
                                sql_from_where = "FROM %s WHERE (date >= '%s' AND date < '%s') " % (table_name, str_user_date_s, str_file_date_s)
                                #print("补充 早一点 的数据")
                            if date_file_date_s <= date_user_date_s and date_file_date_e < date_user_date_e: # 需要补充 晚一点 的数据
                                #if date_user_date_s <= date_file_date_e: # 缓存数据和请求数据，有交集
                                #    usable = locals.ix[locals.date >= date_user_date_s, :]
                                #    print("补充 晚一点 的数据，有交集")
                                #if date_user_date_s > date_file_date_e: # 缓存数据和请求数据，有空隙
                                #    usable = pd.DataFrame(columns = columns) # 空
                                #    print("补充 晚一点 的数据，有空隙")
                                usable = locals.ix[locals.date >= date_user_date_s, :]
                                sql_from_where = "FROM %s WHERE (date > '%s' AND date <= '%s') " % (table_name, str_file_date_e, str_user_date_e)
                                #print("补充 晚一点 的数据")
                            if date_file_date_s > date_user_date_s and date_file_date_e < date_user_date_e: # 需要补充 早一点 和 晚一点 的数据
                                usable = locals.ix[:, :]
                                sql_from_where = "FROM %s WHERE (date >= '%s' AND date < '%s') OR (date > '%s' AND date <= '%s')" % (table_name, str_user_date_s, str_file_date_s, str_file_date_e, str_user_date_e)
                                #print("补充 早一点 和 晚一点 的数据")
                            if sql_from_where != "":
                                sql = "SELECT date, time, open, high, low, close, volume, turnover " + sql_from_where + "ORDER BY date ASC, time ASC"
                                rows = dbm.QueryAllSql(sql)
                                supply = pd.DataFrame(data = list(rows), columns = columns)
                                # 返回的结果
                                result = usable.append(supply, ignore_index = True)
                                if date_file_date_s > date_user_date_e: # 去掉空隙部分
                                    result = result.ix[result.date <= date_user_date_e, :]
                                if date_user_date_s > date_file_date_e: # 去掉空隙部分
                                    result = result.ix[result.date >= date_user_date_s, :]
                                result = result.sort_values(by = ["date", "time"], ascending = True).reset_index(drop = True)
                                # 提示一下以期减少查询提高效率
                                date_result_date_s = result["date"].min()
                                date_result_date_e = result["date"].max()
                                if date_user_date_s < date_result_date_s or date_user_date_e > date_result_date_e:
                                    if False == self.ignore_user_tips:
                                        self.log_text = "建议将 %s %s 的 Kline_1_M 请求日期设为 %s 到 %s 以提高效率。" % \
                                              (market, code, date_result_date_s.strftime("%Y%m%d"), date_result_date_e.strftime("%Y%m%d"))
                                        self.SendMessage("H", 2, self.log_cate, self.log_text, "A")
                                # 更新的缓存
                                locals = locals.append(supply, ignore_index = True)
                                locals = locals.sort_values(by = ["date", "time"], ascending = True).reset_index(drop = True)
                                if save_path != "": # 保存到文件
                                    locals.to_pickle(save_path)
                if need_query_all == True: # 所有都要查询
                    #print("数据需要全部查询")
                    sql = "SELECT date, time, open, high, low, close, volume, turnover " + \
                          "FROM %s " % table_name + \
                          "WHERE (date >= '%s' AND date <= '%s') " % (str_user_date_s, str_user_date_e) + \
                          "ORDER BY date ASC, time ASC"
                    rows = dbm.QueryAllSql(sql)
                    if len(rows) > 0:
                        result = pd.DataFrame(data = list(rows), columns = columns)
                        if save_path != "": # 保存到文件
                            result.to_pickle(save_path)
                    if result.empty:
                        self.log_text = "获取 %s %s 的 %s ~ %s 的 Kline_1_M 数据为空！" % (market, code, str_user_date_s, str_user_date_e)
                        self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
            else:
                self.log_text = "数据库中不存在 %s %s 的 Kline_1_M 数据表！" % (market, code)
                self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        return result

    # 要求 data 为 DataFrame 结构，且包含 date, open, high, low, close 字段
    def MakeExRightsCalc(self, market, code, data, ex_rights): # 1 向前除权；2 向后除权
        if self.security_dict == None:
            self.GetSecurityInfo()
        if self.exrights_dict == None:
            self.GetExRightsData()
        caches = data
        result = pd.DataFrame(columns = data.columns) # 空
        if ex_rights == 1 or ex_rights == 2:
            key = "%s_%s" % (market.lower(), code)
            hold_point = 4 # 默认保留到小数点后四位
            if key in self.security_dict.keys():
                category = self.security_dict[key].category # 证券类别
                if category == 1: # A股
                    hold_point = 2
                elif category == 2 or category == 3 or category == 4: # ETF基金、分级基金、普通开放式基金
                    hold_point = 3
            else:
                self.log_text = "%s %s 没有相关证券信息！" % (market, code)
                self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
            if key in self.exrights_dict.keys():
                exrights_list = self.exrights_dict[key]
                for exrights_item in exrights_list:
                    f_f = lambda x: (x + exrights_item.adder) / exrights_item.muler # 前复权
                    f_b = lambda x: (x * exrights_item.muler) - exrights_item.pg * exrights_item.price + exrights_item.bonus # 后复权
                    if ex_rights == 1: # 前复权
                        caches.ix[caches.date < exrights_item.date, ["open", "high", "low", "close"]] = caches.ix[caches.date < exrights_item.date, ["open", "high", "low", "close"]].apply(f_f) # f_f、<
                    elif ex_rights == 2: # 后复权
                        caches.ix[caches.date >= exrights_item.date, ["open", "high", "low", "close"]] = caches.ix[caches.date >= exrights_item.date, ["open", "high", "low", "close"]].apply(f_b) # f_b、>=
                result = caches.round({"open" : hold_point, "high" : hold_point, "low" : hold_point, "close" : hold_point})
            else:
                if False == self.ignore_exrights_data_loss:
                    self.log_text = "%s %s 没有相关除权数据！" % (market, code)
                    self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        else:
            self.log_text = "%s %s 除权类型 %d 未知！" % (market, code, ex_rights)
            self.SendMessage("E", 4, self.log_cate, self.log_text, "A")
        return result

    # flag："TDF"、"LTB"、"LTP"、"CTP"
    # type："stock"、"index"、"future"
    # symbol："SZ000001"、"SH999999"、"IF1706"
    def GetTodayTicks(self, flag, type, symbol, time_s, time_e):
        dbm = None
        columns = []
        if flag == "TDF" and type == "stock":
            dbm = self.dbm_mongo_quotedata_stock_s_tdf
            columns = ["Code", "Name", "Type", "Market", "Status", "Last", "Open", "High", "Low", "Close", "PreClose", "Volume", "Turnover", \
                       "AskPrice1", "AskPrice2", "AskPrice3", "AskPrice4", "AskPrice5", "AskVolume1", "AskVolume2", "AskVolume3", "AskVolume4", "AskVolume5", \
                       "BidPrice1", "BidPrice2", "BidPrice3", "BidPrice4", "BidPrice5", "BidVolume1", "BidVolume2", "BidVolume3", "BidVolume4", "BidVolume5", \
                       "HighLimit", "LowLimit", "TotalBidVol", "TotalAskVol", "WeightedAvgBidPrice", "WeightedAvgAskPrice", \
                       "TradeCount", "IOPV", "YieldRate", "PeRate_1", "PeRate_2", "Units", "QuoteTime", "LocalTime", "LocalIndex"]
        elif flag == "TDF" and type == "index":
            dbm = self.dbm_mongo_quotedata_stock_i_tdf
            columns = ["Code", "Name", "Type", "Market", "Status", "Last", "Open", "High", "Low", "Close", "PreClose", "Volume", "Turnover", "QuoteTime", "LocalTime", "LocalIndex"]
        elif flag == "LTB" and type == "stock":
            dbm = self.dbm_mongo_quotedata_stock_s_ltb
            columns = ["Code", "Name", "Type", "Market", "Status", "Last", "Open", "High", "Low", "Close", "PreClose", "Volume", "Turnover", \
                       "AskPrice1", "AskPrice2", "AskPrice3", "AskPrice4", "AskPrice5", "AskVolume1", "AskVolume2", "AskVolume3", "AskVolume4", "AskVolume5", \
                       "BidPrice1", "BidPrice2", "BidPrice3", "BidPrice4", "BidPrice5", "BidVolume1", "BidVolume2", "BidVolume3", "BidVolume4", "BidVolume5", \
                       "HighLimit", "LowLimit", "OpenInterest", "IOPV", "TradeCount", "YieldToMaturity", "AuctionPrice", "BidPriceLevel", "OfferPriceLevel", "TotalBidVolume", "TotalOfferVolume", \
                       "WeightedAvgBidPrice", "WeightedAvgOfferPrice", "AltWeightedAvgBidPrice", "AltWeightedAvgOfferPrice", "TradingPhase", "OpenRestriction", "QuoteTime", "LocalTime", "LocalIndex"]
        elif flag == "LTB" and type == "index":
            dbm = self.dbm_mongo_quotedata_stock_i_ltb
            columns = ["Code", "Name", "Type", "Market", "Status", "Last", "Open", "High", "Low", "Close", "PreClose", "Volume", "Turnover", "QuoteTime", "LocalTime", "LocalIndex"]
        if flag == "LTP" and type == "stock":
            dbm = self.dbm_mongo_quotedata_stock_s_ltp
            columns = ["Code", "Name", "Type", "Market", "Status", "Last", "Open", "High", "Low", "Close", "PreClose", "Volume", "Turnover", \
                       "AskPrice1", "AskPrice2", "AskPrice3", "AskPrice4", "AskPrice5", "AskVolume1", "AskVolume2", "AskVolume3", "AskVolume4", "AskVolume5", \
                       "BidPrice1", "BidPrice2", "BidPrice3", "BidPrice4", "BidPrice5", "BidVolume1", "BidVolume2", "BidVolume3", "BidVolume4", "BidVolume5", \
                       "HighLimit", "LowLimit", "TotalBidVol", "TotalAskVol", "WeightedAvgBidPrice", "WeightedAvgAskPrice", \
                       "TradeCount", "IOPV", "YieldRate", "PeRate_1", "PeRate_2", "Units", "QuoteTime", "LocalTime", "LocalIndex"]
        elif flag == "LTP" and type == "index":
            dbm = self.dbm_mongo_quotedata_stock_i_ltp
            columns = ["Code", "Name", "Type", "Market", "Status", "Last", "Open", "High", "Low", "Close", "PreClose", "Volume", "Turnover", "QuoteTime", "LocalTime", "LocalIndex"]
        elif flag == "CTP" and type == "future":
            dbm = self.dbm_mongo_quotedata_future_ctp
            columns = ["Code", "Name", "Type", "Market", "Status", "Last", "Open", "High", "Low", "Close", "PreClose", "Volume", "Turnover", \
                       "AskPrice1", "AskPrice2", "AskPrice3", "AskPrice4", "AskPrice5", "AskVolume1", "AskVolume2", "AskVolume3", "AskVolume4", "AskVolume5", \
                       "BidPrice1", "BidPrice2", "BidPrice3", "BidPrice4", "BidPrice5", "BidVolume1", "BidVolume2", "BidVolume3", "BidVolume4", "BidVolume5", \
                       "HighLimit", "LowLimit", "Settle", "PreSettle", "Position", "PrePosition", "Average", "UpDown", "UpDownRate", \
                       "Swing", "Delta", "PreDelta", "QuoteDate", "QuoteTime", "LocalDate", "LocalTime", "LocalIndex"]
        else:
            self.log_text = "当日快照行情类 %s %s 不存在！" % (flag, type)
            self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        result = pd.DataFrame(columns = columns) # 空
        if dbm != None:
            exp = {"Code" : symbol.upper(), "QuoteTime" : {"$gte" : time_s, "$lte" : time_e}}
            sort = None # [["LocalIndex", 1]]
            projection = {"_id" : False} # ["Code", "Last", "QuoteTime", "LocalIndex"]
            rows = dbm.Query(exp, sort, projection)
            result = pd.DataFrame(data = list(rows), columns = columns)
        else:
            self.log_text = "当日快照行情类 %s %s 缓存数据库尚未连接！" % (flag, type)
            self.SendMessage("W", 3, self.log_cate, self.log_text, "A")
        return result

    def CreateKline_1_M_List_241(self): # 共 241 根，去头取尾，其中 930 收入开盘前集合竞价情况，上午 120 根，下午 120 根
        kline_list = []
        str_date = datetime.now().strftime("%Y%m%d")
        for i in range(930, 960, 1): # 930 ~ 959
            kline_list.append(KlineItem(i, str_date, self.TransTimeIntToStr(i * 100)))
        for i in range(1000, 1060, 1): # 1000 ~ 1059
            kline_list.append(KlineItem(i, str_date, self.TransTimeIntToStr(i * 100)))
        for i in range(1100, 1131, 1): # 1100 ~ 1130
            kline_list.append(KlineItem(i, str_date, self.TransTimeIntToStr(i * 100)))
        for i in range(1301, 1360, 1): # 1301 ~ 1359
            kline_list.append(KlineItem(i, str_date, self.TransTimeIntToStr(i * 100)))
        for i in range(1400, 1460, 1): # 1400 ~ 1459
            kline_list.append(KlineItem(i, str_date, self.TransTimeIntToStr(i * 100)))
        kline_list.append(KlineItem(1500, str_date, self.TransTimeIntToStr(1500 * 100)))
        return kline_list

    # vt_type：成交量和成交额，1 为累计，2 为单笔
    def HandleKline_1_M_List_241(self, list_time, list_price, list_volume, list_turnover, vt_type):
        pre_kline_list_index = -1 # 标记上一个分时数据下标
        pre_kline_list_price = 0.0 # 标记上一个分时数据价格
        pre_kline_list_volume = 0 # 标记上一个分时数据累计成交量
        pre_kline_list_turnover = 0.0 # 标记上一个分时数据累计成交额
        open_kline_list_volume = 0 # 标记当前分钟线起始累计成交量
        open_kline_list_turnover = 0.0 # 标记当前分钟线起始累计成交额
        kline_list = self.CreateKline_1_M_List_241()
        for i in range(list_time.shape[0]):
            ticks_time = list_time[i]
            kline_list_time = int(math.ceil(ticks_time / 100000.0))
            kline_list_index = -1
            if (ticks_time >= 92500000 and ticks_time < 93000000): # 第一根分钟线，集合竞价数据
                kline_list_index = 0
            elif ticks_time == 93000000: # 可能会有 == 93000000 的数据，如果有则 kline_list_index = 1
                kline_list_index = kline_list_time - 929
            elif (ticks_time > 93000000 and ticks_time < 100000000):
                kline_list_index = kline_list_time - 930
            elif (ticks_time >= 100000000 and ticks_time < 110000000):
                kline_list_index = kline_list_time - 930 - 40
            elif (ticks_time >= 110000000 and ticks_time <= 113000000): # 可能会有 == 113000000 的数据，如果有则 kline_list_index = 120
                kline_list_index = kline_list_time - 930 - 80
            elif (ticks_time > 113000000 and ticks_time < 113100000): # 可能会有 113002000 这样的数据，如果有则 kline_list_index = 120
                kline_list_index = kline_list_time - 931 - 80
            elif ticks_time == 130000000: # 可能会有 == 130000000 的数据，如果有则 kline_list_index = 121
                kline_list_index = kline_list_time - 1299 + 120
            elif (ticks_time > 130000000 and ticks_time < 140000000):
                kline_list_index = kline_list_time - 1300 + 120
            elif (ticks_time >= 140000000 and ticks_time < 150000000):
                kline_list_index = kline_list_time - 1300 + 120 - 40
            elif ticks_time == 150000000: # 可能会有 == 150000000 的数据，如果有则 kline_list_index = 240
                kline_list_index = kline_list_time - 1300 + 120 - 80
            elif (ticks_time > 150000000 and ticks_time < 150100000): # 可能会有 150002000 这样的数据，如果有则 kline_list_index = 240
                kline_list_index = kline_list_time - 1301 + 120 - 80
            #print(ticks_time / 1000, kline_list_time, kline_list_index, list_price[i], list_volume[i], list_turnover[i])
            if kline_list_index >= 0 and kline_list_index <= 240: # 要严格注意代码缩进
                kline_item = kline_list[kline_list_index]
                if pre_kline_list_index != kline_list_index: # 说明是该分钟线的第一个分时数据
                    if pre_kline_list_index >= 0 and pre_kline_list_index <= 240: # pre_kline_list_index
                        kline_list[pre_kline_list_index].close = pre_kline_list_price # pre_kline_list_index
                        if vt_type == 1: # 累计的
                            kline_list[pre_kline_list_index].volume = pre_kline_list_volume - open_kline_list_volume
                            kline_list[pre_kline_list_index].turnover = pre_kline_list_turnover - open_kline_list_turnover
                        #print("close: ", kline_list[pre_kline_list_index].close, pre_kline_list_volume, pre_kline_list_turnover)
                    kline_item.open = list_price[i]
                    if vt_type == 1: # 累计的
                        open_kline_list_volume = list_volume[i]
                        open_kline_list_turnover = list_turnover[i]
                    #print("open: ", kline_item.open, open_kline_list_volume, open_kline_list_turnover)
                    pre_kline_list_index = kline_list_index # 供下一个分时数据使用
                pre_kline_list_price = list_price[i] # 供下一个分时数据使用
                if vt_type == 1: # 累计的
                    pre_kline_list_volume = list_volume[i] # 供下一个分时数据使用
                    pre_kline_list_turnover = list_turnover[i] # 供下一个分时数据使用
                #print(ticks_time / 1000, kline_list_time, kline_list_index, list_price[i])
                if kline_item.high < list_price[i]:
                    kline_item.high = list_price[i]
                if kline_item.low > list_price[i]:
                    kline_item.low = list_price[i]
                if vt_type == 0: # 单笔的
                    kline_item.volume += list_volume[i]
                    kline_item.turnover += list_turnover[i]
                #if kline_item.high < kline_item.low or kline_item.low == DEF_INIT_KLINE_ITEM_LOW:
                #    print(kline_item.high, kline_item.low)
            if i == (list_time.shape[0] - 1): # 最后一个
                if pre_kline_list_index >= 0 and pre_kline_list_index <= 240: # pre_kline_list_index
                    kline_list[pre_kline_list_index].close = pre_kline_list_price # pre_kline_list_index
                    if vt_type == 1: # 累计的
                        kline_list[pre_kline_list_index].volume = pre_kline_list_volume - open_kline_list_volume
                        kline_list[pre_kline_list_index].turnover = pre_kline_list_turnover - open_kline_list_turnover
                    #print("close: ", kline_list[pre_kline_list_index].close, pre_kline_list_volume, pre_kline_list_turnover)
        return kline_list

    # flag："TDF"、"LTB"、"LTP"、"CTP"
    # type："stock"、"index"、"future"
    # symbol："SZ000001"、"SH999999"、"SZE000001"、"SSE000001"、"IF1706"
    # 这里 TDF、LTB、LTP 与宏汇盘后下载数据不同，快照的成交量和成交额是累计的，CTP快照的成交量和成交额也是累计的
    def TicksToKline_1_M(self, flag, type, symbol, data):
        kline_list = None
        columns = ["date", "time", "open", "high", "low", "close", "volume", "turnover"]
        result = pd.DataFrame(columns = columns) # 空
        if (flag == "TDF" or flag == "LTB" or flag == "LTP") and (type == "stock" or type == "index"): # 股票类
            kline_list = self.HandleKline_1_M_List_241(data["QuoteTime"], data["Last"], data["Volume"], data["Turnover"], 1) # 成交量和成交额为累计
        if flag == "CTP" and type == "future": # 期货类 # 目前未考虑商品类期货合约
            kline_list = self.HandleKline_1_M_List_241(data["QuoteTime"], data["Last"], data["Volume"], data["Turnover"], 1) # 成交量和成交额为累计
        if kline_list != None:
            result_list = []
            for kline_item in kline_list:
                if kline_item.low == DEF_INIT_KLINE_ITEM_LOW: # 修正初始赋值
                    kline_item.low = 0.0
                result_list.append({"date" : kline_item.date, "time" : kline_item.time, "open" : kline_item.open, "high" : kline_item.high, \
                                    "low" : kline_item.low, "close" : kline_item.close, "volume" : kline_item.volume, "turnover" : kline_item.turnover})
            if len(result_list) > 0:
                result = pd.DataFrame(data = list(result_list), columns = columns)
        return result

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    folder = "../data" # 缓存文件夹
    basicx = BasicX()
    #basicx.InitBasicData(folder = folder) # 不使用数据库
    #basicx.InitBasicData(host = "10.0.7.53", port = 3306, user = "user", passwd = "user", folder = folder) # 测试
    #basicx.InitBasicData(host = "10.0.7.80", port = 3306, user = "user", passwd = "user", folder = folder) # 生产
    #basicx.InitCacheData(host = "10.0.7.53", port = 27017, quote = ["CTP"]) # 测试 # ["TDF", "LTB", "LTP", "CTP"]
    basicx.InitCacheData(host = "10.0.7.80", port = 27017, quote = ["CTP"]) # 生产 # ["TDF", "LTB", "LTP", "CTP"]
    #result = basicx.Version()
    result = basicx.GetTodayTicks("CTP", "future", "IF1806", 92900000, 150100000)
    if not result.empty:
        print(result)
        result = basicx.TicksToKline_1_M("CTP", "future", "IF1806", result)
        if not result.empty:
            print(result)
    
    sys.exit(app.exec_())
