
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

from datetime import datetime

import basicx # 要求已安装 numpy、pandas、pymysql、pymongo

if __name__ == "__main__":
    folder = "../data" # 缓存文件夹
    basicx_demo = basicx.BasicX()
    #basicx_demo.InitBasicData(folder = folder) # 不使用数据库
    #basicx_demo.InitBasicData(host = "10.0.7.53", port = 3306, user = "user", passwd = "user", folder = folder) # 测试
    #basicx_demo.InitBasicData(host = "10.0.7.80", port = 3306, user = "user", passwd = "user", folder = folder) # 生产
    #basicx_demo.IgnoreUserTips(False) # 提高效率等信息提示
    #basicx_demo.IgnoreLocalFileLoss(False) # 本地缓存文件缺失
    #basicx_demo.IgnoreExRightsDataLoss(False) # 除权数据缺失
    #basicx_demo.IgnoreLocalDataImperfect(False) # 本地缓存数据不完整
    #result = basicx_demo.Version()
    #result = basicx_demo.GetTables_Financial()
    #result = basicx_demo.GetTables_Stock_Daily()
    #result = basicx_demo.GetTables_Stock_Kline_1_M()
    #result = basicx_demo.GetTradingDay()
    #result = basicx_demo.GetIndustryData()
    #result = basicx_demo.GetSecurityInfo()
    #result = basicx_demo.GetCapitalData()
    #result = basicx_demo.GetExRightsData()
    #result = basicx_demo.GetTodTingPai()
    #result = basicx_demo.GetStockDaily("sz", "000001", 20160101, 20161231)
    #result = basicx_demo.GetStockKline_1_M("sh", "600000", 20160101, 20161231)
    #if not result.empty:
        #print(result)
        #f_f = lambda x: datetime(x.year, x.month, x.day)
        #print(result["date"].ix[:].apply(f_f) + result["time"])
        #result = basicx_demo.MakeExRightsCalc("sz", "000001", result, 1) # 1 向前除权；2 向后除权
        #result = basicx_demo.MakeExRightsCalc("sh", "600000", result, 1) # 1 向前除权；2 向后除权
        #if not result.empty:
            #print(result)
    basicx_demo.InitCacheData(host = "10.0.7.53", port = 27017, quote = ["CTP"]) # 测试 # ["TDF", "LTB", "LTP", "CTP"]
    #basicx_demo.InitCacheData(host = "10.0.7.80", port = 27017, quote = ["CTP"]) # 生产 # ["TDF", "LTB", "LTP", "CTP"]
    result = basicx_demo.GetTodayTicks("TDF", "stock", "SZ000001", 92900000, 150100000)
    #result = basicx_demo.GetTodayTicks("TDF", "index", "SH999999", 92900000, 150100000)
    #result = basicx_demo.GetTodayTicks("LTB", "stock", "SZE000001", 92900000, 150100000)
    #result = basicx_demo.GetTodayTicks("LTB", "index", "SSE000001", 92900000, 150100000)
    #result = basicx_demo.GetTodayTicks("LTP", "stock", "SZE000001", 92900000, 150100000)
    #result = basicx_demo.GetTodayTicks("LTP", "index", "SSE000001", 92900000, 150100000)
    #result = basicx_demo.GetTodayTicks("CTP", "future", "IF1806", 92900000, 150100000)
    if not result.empty:
        print(result)
        result = basicx_demo.TicksToKline_1_M("TDF", "stock", "SZ000001", result)
        #result = basicx_demo.TicksToKline_1_M("TDF", "index", "SH999999", result)
        #result = basicx_demo.TicksToKline_1_M("LTB", "stock", "SZE000001", result)
        #result = basicx_demo.TicksToKline_1_M("LTB", "index", "SSE000001", result)
        #result = basicx_demo.TicksToKline_1_M("LTP", "stock", "SZE000001", result)
        #result = basicx_demo.TicksToKline_1_M("LTP", "index", "SSE000001", result)
        #result = basicx_demo.TicksToKline_1_M("CTP", "future", "IF1806", result)
        if not result.empty:
            print(result)
