
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
from datetime import datetime

import numpy as np
import pandas as pd

pd.set_option("max_colwidth", 200)
pd.set_option("display.width", 500)

try: import logger
except: pass
import dbm_mongo
import dbm_mysql

DEF_INIT_KLINE_ITEM_LOW = 99999.0

class Version(object):
    def __init__(self):
        self.major     = "major"
        self.minor     = "minor"
        self.revision  = "revision"
        self.build     = "build"
        self.name      = "name         BasicX"
        self.version   = "version      V0.1.0-Beta Build 20180430"
        self.author    = "author       Xu Rendong"
        self.developer = "developer    Developed by the X-Lab."
        self.company   = "company      X-Lab (Shanghai) Co., Ltd."
        self.copyright = "copyright    Copyright 2018-2018 X-Lab All Rights Reserved."
        self.homeurl   = "homeurl      http://www.xlab.com"
        self.data = [0, 1, 0, 20180430, "", "", "", "", "", "", ""]
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

class Kline_Item(object):
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
        pass

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    folder = "../data" # 缓存文件夹
    basicX = BasicX()
    #basicX.InitBasicData(folder = folder) # 不使用数据库
    #basicX.InitBasicData(host = "10.0.7.53", port = 3306, user = "user", passwd = "user", folder = folder) # 测试
    #basicX.InitBasicData(host = "10.0.7.80", port = 3306, user = "user", passwd = "user", folder = folder) # 生产
    #basicX.InitCacheData(host = "10.0.7.53", port = 27017, quote = ["CTP"]) # 测试 # ["TDF", "LTB", "LTP", "CTP"]
    basicX.InitCacheData(host = "10.0.7.80", port = 27017, quote = ["CTP"]) # 生产 # ["TDF", "LTB", "LTP", "CTP"]
    #result = basicX.Version()
    result = basicX.GetTodayTicks("CTP", "future", "IF1706", 92900000, 150100000)
    if not result.empty:
        print(result)
        result = basicX.TicksToKline_1_M("CTP", "future", "IF1706", result)
        if not result.empty:
            print(result)
    
    sys.exit(app.exec_())
