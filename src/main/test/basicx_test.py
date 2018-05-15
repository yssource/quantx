
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

import time
import pstats
import cProfile

import basicx # 要求已安装 numpy、pandas、pymysql、pymongo

def Main(basicx_test):
    start_time = time.clock()
    #basicx_test.IgnoreUserTips(False) # 提高效率等信息提示
    #basicx_test.IgnoreLocalFileLoss(False) # 本地缓存文件缺失
    #basicx_test.IgnoreExRightsDataLoss(False) # 除权数据缺失
    #basicx_test.IgnoreLocalDataImperfect(False) # 本地缓存数据不完整
    #result = basicx_test.Version()
    #result = basicx_test.GetTables_Financial()
    #result = basicx_test.GetTables_Stock_Daily()
    #result = basicx_test.GetTables_Stock_Kline_1_M()
    #result = basicx_test.GetTradingDay()
    #result = basicx_test.GetIndustryData()
    #result = basicx_test.GetSecurityInfo()
    #result = basicx_test.GetCapitalData()
    #result = basicx_test.GetExRightsData()
    #result = basicx_test.GetTodTingPai()
    #result = basicx_test.GetStockDaily("sz", "000001", 20100104, 20170126)
    #result = basicx_test.GetStockDaily("sz", "000001", 20160613, 20160620) # 删除文件，数据需要全部查询
    #result = basicx_test.GetStockDaily("sz", "000001", 20160614, 20160617) # 都在缓存数据中
    #result = basicx_test.GetStockDaily("sz", "000001", 20160605, 20160620) # 补充 早一点 的数据，有交集
    #result = basicx_test.GetStockDaily("sz", "000001", 20160610, 20160625) # 补充 晚一点 的数据，有交集
    #result = basicx_test.GetStockDaily("sz", "000001", 20160601, 20160630) # 补充 早一点 和 晚一点 的数据
    #result = basicx_test.GetStockDaily("sz", "000001", 20160516, 20160520) # 补充 早一点 的数据，有空隙
    #result = basicx_test.GetStockDaily("sz", "000001", 20160705, 20160708) # 补充 晚一点 的数据，有空隙
    #result = basicx_test.GetStockDaily("sz", "000001", 20160516, 20160708) # 查验本地缓存已有空隙部分数据
    #result = basicx_test.GetStockKline_1_M("sh", "000300", 20100401, 20170126)
    #result = basicx_test.GetStockKline_1_M("sh", "000300", 20160615, 20160615) # 删除文件，数据需要全部查询
    #result = basicx_test.GetStockKline_1_M("sh", "000300", 20160614, 20160615) # 补充 早一点 的数据，有交集
    #result = basicx_test.GetStockKline_1_M("sh", "000300", 20160615, 20160616) # 补充 晚一点 的数据，有交集
    #result = basicx_test.GetStockKline_1_M("sh", "000300", 20160613, 20160617) # 补充 早一点 和 晚一点 的数据
    #result = basicx_test.GetStockKline_1_M("sh", "000300", 20160607, 20160607) # 补充 早一点 的数据，有空隙
    #result = basicx_test.GetStockKline_1_M("sh", "000300", 20160621, 20160621) # 补充 晚一点 的数据，有空隙
    #result = basicx_test.GetStockKline_1_M("sh", "000300", 20160608, 20160620) # 都在缓存数据中
    #print("cost %s seconds" % (time.clock() - start_time))
    #if not result.empty:
        #print(result)
        #result = basicx_test.MakeExRightsCalc("sz", "000001", result, 1) # 1 向前除权；2 向后除权
        #result = basicx_test.MakeExRightsCalc("sh", "000300", result, 1) # 1 向前除权；2 向后除权
        #if not result.empty:
            #print(result)
    # 根据行情时间取值是有可能混入几条开盘前推送的前一日收盘行情数据的
    #result = basicx_test.GetTodayTicks("TDF", "stock", "SZ000001", 92900000, 150100000)
    #result = basicx_test.GetTodayTicks("TDF", "index", "SH999999", 92900000, 150100000)
    #result = basicx_test.GetTodayTicks("LTB", "stock", "SZE000001", 92900000, 150100000)
    #result = basicx_test.GetTodayTicks("LTB", "index", "SSE000001", 92900000, 150100000)
    #result = basicx_test.GetTodayTicks("LTP", "stock", "SZE000001", 92900000, 150100000)
    #result = basicx_test.GetTodayTicks("LTP", "index", "SSE000001", 92900000, 150100000)
    result = basicx_test.GetTodayTicks("CTP", "future", "IF1806", 92900000, 150100000)
    if not result.empty:
        print(result)
        #result = basicx_test.TicksToKline_1_M("TDF", "stock", "SZ000001", result)
        #result = basicx_test.TicksToKline_1_M("TDF", "index", "SH999999", result)
        #result = basicx_test.TicksToKline_1_M("LTB", "stock", "SZE000001", result)
        #result = basicx_test.TicksToKline_1_M("LTB", "index", "SSE000001", result)
        #result = basicx_test.TicksToKline_1_M("LTP", "stock", "SZE000001", result)
        #result = basicx_test.TicksToKline_1_M("LTP", "index", "SSE000001", result)
        result = basicx_test.TicksToKline_1_M("CTP", "future", "IF1806", result)
        if not result.empty:
            print(result)

if __name__ == "__main__":
    folder = "../data" # 缓存文件夹
    basicx_test = basicx.BasicX()
    #basicx_test.InitBasicData(folder = folder) # 不使用数据库
    #basicx_test.InitBasicData(host = "10.0.7.53", port = 3306, user = "user", passwd = "user", folder = folder) # 测试
    #basicx_test.InitBasicData(host = "10.0.7.80", port = 3306, user = "user", passwd = "user", folder = folder) # 生产
    #basicx_test.InitCacheData(host = "10.0.7.53", port = 27017, quote = ["CTP"]) # 测试 # ["TDF", "LTB", "LTP", "CTP"]
    basicx_test.InitCacheData(host = "10.0.7.80", port = 27017, quote = ["CTP"]) # 生产 # ["TDF", "LTB", "LTP", "CTP"]
    
    cProfile.run("Main(basicx_test)", "profile.log")
    # ncalls:  函数被call的次数
    # tottime：函数总的耗时，但是不包括其子函数的耗时
    # percall：tottime平均到每次调用的耗时
    # cumtime：函数总的耗时，包括了其子函数的耗时（递归函数也不例外）
    # percall：cumtime平均到每次调用的耗时
    # filename:lineno(function) ：每个函数各自的信息

    # 创建Stats对象
    p = pstats.Stats("profile.log")
    # 这一行的效果和直接运行cProfile.run("foo()")的显示效果是一样的
#    p.strip_dirs().sort_stats(-1).print_stats()
    # strip_dirs():从所有模块名中去掉无关的路径信息
    # sort_stats():把打印信息按照标准的module/name/line字符串进行排序
    # print_stats():打印出所有分析信息

    # 按照函数名排序 
#    p.strip_dirs().sort_stats("name").print_stats()

    # 按照在一个函数中累积的运行时间进行排序
    # print_stats(3):只打印前3行函数的信息,参数还可为小数,表示前百分之几的函数信息
    p.strip_dirs().sort_stats("cumulative").print_stats(10)

    # 还有一种用法
#    p.sort_stats('time', 'cum').print_stats(.5, 'foo')
    # 先按time排序,再按cumulative时间排序,然后打倒出前50%中含有函数信息

    # 如果想知道有哪些函数调用了bar,可使用
#    p.print_callers(0.5, "bar")

    # 同理,查看foo()函数中调用了哪些函数
#    p.print_callees("foo")
