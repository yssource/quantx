
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
import math

import dbm_mysql
import LoadQuoteStockTicks

DEF_INIT_KLINE_ITEM_LOW = 99999.0

class KlineItem(object):
    def __init__(self, index, str_date, str_time):
        self.index = index # 分钟索引
        self.date = str_date # 日期 "2017-01-01"
        self.time = str_time # 时间 "11:30:00"
        self.open = 0.0 # 开盘价
        self.high = 0.0 # 最高价
        self.low = DEF_INIT_KLINE_ITEM_LOW # 最低价
        self.close = 0.0 # 收盘价
        self.volume = 0 # 成交量，股
        self.turnover = 0 # 成交额，元

class DataMaker_StockKline_1_M():
    def __init__(self):
        self.mysql_host = "0.0.0.0"
        self.mysql_port = 0
        self.mysql_user = "user"
        self.mysql_passwd = "123456"
        self.mysql_database = "test"
        self.mysql_charset = "utf8"
        self.dbm_quotedata = None
        self.flag_use_database = False

    def SendMessage(self, text_info):
        print(text_info)

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
            if self.flag_use_database == True:
                self.dbm_quotedata = dbm_mysql.DBM_MySQL(host = self.mysql_host, port = self.mysql_port, user = self.mysql_user, passwd = self.mysql_passwd, db = self.mysql_db, charset = self.mysql_charset)
                if self.dbm_quotedata.Connect() == True:
                    self.SendMessage("数据库 quotedata 连接完成。")
                    return True
                else:
                    self.dbm_quotedata = None
                    self.SendMessage("数据库 quotedata 连接失败！")
            else:
                self.SendMessage("不使用数据库 quotedata 保存行情数据。")
                return True
        except Exception as e:
            self.dbm_quotedata = None
            self.SendMessage("建立数据库连接发生异常！%s" % e)
        return False

    def DisconnectDB(self):
        try:
            if self.flag_use_database == True:
                if self.dbm_quotedata != None:
                    self.dbm_quotedata.Disconnect()
                    self.dbm_quotedata = None
                    self.SendMessage("数据库 quotedata 连接断开！")
        except Exception as e:
            self.SendMessage("断开数据库连接发生异常！%s" % e)

    def TransDateIntToStr(self, int_date):
        year = int(int_date / 10000)
        month = int((int_date % 10000) / 100)
        day = int_date % 100
        return "%d-%d-%d" % (year, month, day)

    def TransTimeIntToStr(self, int_time):
        hour = int(int_time / 10000)
        minute = int((int_time % 10000) / 100)
        second = int_time % 100
        return "%d:%d:%d" % (hour, minute, second)

    def CreateKline_1_M_List(self, int_date): # 共 241 根，去头取尾，其中 930 收入开盘前集合竞价情况，上午 120 根，下午 120 根
        kline_list = []
        str_date = self.TransDateIntToStr(int_date)
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

    def GetStockTicksFileList(self, path):
        ticks_list = [] # X:\Ticks_201701\sz\399998\20170126.fs
        folder_list = os.listdir(path)
        for folder_item in folder_list:
            folder_path = os.path.join("%s\%s" % (path, folder_item))
            file_list = os.listdir(folder_path)
            for file_item in file_list:
                file_path = os.path.join("%s\%s" % (folder_path, file_item))
                ticks_list.append(file_path)
                #print file_path
        return ticks_list

    def SaveData_StockTicks(self, ticks_list, market, code_list, model): # market：sh、sz
        total_file_number = 0
        read_file_failed = 0
        read_file_success = 0
        create_table = 0
        truncate_table = 0
        save_data_failed = 0
        save_data_success = 0
        total_record_number = 0
        save_record_failed = 0
        save_record_success = 0
        if self.dbm_quotedata != None:
            sql = "SHOW TABLES"
            query_result = self.dbm_quotedata.QueryAllSql(sql)
            if query_result != None:
                data_tables = list(query_result)
                #print(data_tables)
                have_tables = re.findall("(\'.*?\')", str(data_tables))
                have_tables = [re.sub("'", "", table) for table in have_tables]
                #print(have_tables)
                pre_ticks_code = ""
                for ticks_item in ticks_list:
                    file_head = 16
                    file_path = ticks_item
                    list_info = []
                    dict_data = {}
                    ticks_date = ticks_item[-11:-3]
                    ticks_code = ticks_item[-18:-12]
                    table_name = "stock_kline_1_m_" + market + "_" + ticks_code
                    #print(ticks_item, ticks_code, ticks_date, table_name)
                    if code_list == None or ticks_code in code_list:
                        total_file_number += 1
                        result = LoadQuoteStockTicks.LoadQuote(file_path, file_head, list_info, dict_data)
                        print(ticks_code, ticks_date, result, len(list_info))
                        if result >= 0:
                            #for i in range(result):
                            #    print(dict_data["Time"][i], dict_data["Index"][i], dict_data["Price"][i], dict_data["Volume"][i], dict_data["Turnover"][i], \
                            #          dict_data["MatchItems"][i], dict_data["Interest"][i], dict_data["TradeFlag"][i], dict_data["BSFlag"][i], dict_data["AccVolume"][i], dict_data["AccTurnover"][i])
                            #    for j in range(10):
                            #        print(dict_data["AskPrice"][j][i], dict_data["AskVolume"][j][i], dict_data["BidPrice"][j][i], dict_data["BidVolume"][j][i])
                            kline_list = self.CreateKline_1_M_List(int(ticks_date))
                            data_list_time = dict_data["Time"]
                            data_list_price = dict_data["Price"]
                            data_list_volume = dict_data["Volume"]
                            data_list_turnover = dict_data["Turnover"]
                            pre_kline_list_index = -1 # 标记上一个分时数据下标
                            pre_kline_list_price = 0.0 # 标记上一个分时数据价格
                            for i in range(result):
                                ticks_time = data_list_time[i]
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
                                #print(ticks_time / 1000, kline_list_time, kline_list_index, data_list_price[i], data_list_volume[i], data_list_turnover[i])
                                if kline_list_index >= 0 and kline_list_index <= 240: # 要严格注意代码缩进
                                    kline_item = kline_list[kline_list_index]
                                    if pre_kline_list_index != kline_list_index: # 说明是该分钟线的第一个分时数据
                                        if pre_kline_list_index >= 0 and pre_kline_list_index <= 240: # pre_kline_list_index
                                            kline_list[pre_kline_list_index].close = pre_kline_list_price # pre_kline_list_index
                                            #print("close: ", kline_list[pre_kline_list_index].close)
                                        kline_item.open = data_list_price[i]
                                        #print("open: ", kline_item.open)
                                        pre_kline_list_index = kline_list_index # 供下一个分时数据使用
                                    pre_kline_list_price = data_list_price[i] # 供下一个分时数据使用
                                    #print(ticks_time / 1000, kline_list_time, kline_list_index, data_list_price[i])
                                    if kline_item.high < data_list_price[i]:
                                        kline_item.high = data_list_price[i]
                                    if kline_item.low > data_list_price[i]:
                                        kline_item.low = data_list_price[i]
                                    kline_item.volume += data_list_volume[i]
                                    kline_item.turnover += data_list_turnover[i]
                                    #if kline_item.high < kline_item.low or kline_item.low == DEF_INIT_KLINE_ITEM_LOW:
                                    #    print(kline_item.high, kline_item.low)
                                if i == (result - 1): # 最后一个
                                    if pre_kline_list_index >= 0 and pre_kline_list_index <= 240: # pre_kline_list_index
                                        kline_list[pre_kline_list_index].close = pre_kline_list_price # pre_kline_list_index
                                        #print("close: ", kline_list[pre_kline_list_index].close)
                            save_index_from = 0 #
                            read_file_success += 1
                            if pre_ticks_code != ticks_code: # 需要初始化数据库表
                                pre_ticks_code = ticks_code
                                if table_name in have_tables:
                                    if model == "create": # 需要清空表
                                        truncate_table += 1
                                        sql = "TRUNCATE TABLE %s" % table_name
                                        self.dbm_quotedata.ExecuteSql(sql)
                                    if model == "update": # 需要过滤值
                                        pass
                                else:
                                    create_table += 1
                                    sql = "CREATE TABLE `%s` (" % table_name + \
                                          "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                                          "`date` date NOT NULL COMMENT '日期'," + \
                                          "`time` time NOT NULL COMMENT '时间'," + \
                                          "`open` float(10,3) DEFAULT '0.000' COMMENT '开盘价'," + \
                                          "`high` float(10,3) DEFAULT '0.000' COMMENT '最高价'," + \
                                          "`low` float(10,3) DEFAULT '0.000' COMMENT '最低价'," + \
                                          "`close` float(10,3) DEFAULT '0.000' COMMENT '收盘价'," + \
                                          "`volume` bigint(64) DEFAULT '0' COMMENT '成交量，股'," + \
                                          "`turnover` bigint(64) DEFAULT '0' COMMENT '成交额，元'," + \
                                          "PRIMARY KEY (`id`)," + \
                                          "UNIQUE KEY `idx_date_time` (`date`,`time`)" + \
                                          ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
                                    self.dbm_quotedata.ExecuteSql(sql)
                            values = []
                            no_error_flag = True
                            total_record_number += len(kline_list)
                            sql = "INSERT INTO %s" % table_name + "(date, time, open, high, low, close, volume, turnover) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                            for i in range(save_index_from, len(kline_list)):
                                if kline_list[i].low == DEF_INIT_KLINE_ITEM_LOW: # 修正初始赋值
                                    kline_list[i].low = 0.0
                                values.append((kline_list[i].date, kline_list[i].time, kline_list[i].open, kline_list[i].high, kline_list[i].low, kline_list[i].close, kline_list[i].volume, kline_list[i].turnover))
                                if (i - save_index_from + 1) % 3000 == 0: # 自定义每批次保存条数
                                    if len(values) > 0: # 有记录需要保存
                                        if self.dbm_quotedata.ExecuteManySql(sql, values) == False:
                                            no_error_flag = False
                                            save_record_failed += len(values)
                                        else:
                                            save_record_success += len(values)
                                        #print(ticks_code, " 保存：", len(values))
                                        values = [] #
                            if len(values) > 0: # 有记录需要保存
                                if self.dbm_quotedata.ExecuteManySql(sql, values) == False:
                                    no_error_flag = False
                                    save_record_failed += len(values)
                                else:
                                    save_record_success += len(values)
                                #print(ticks_code, " 保存：", len(values))
                            if no_error_flag == False:
                                save_data_failed += 1
                            else:
                                save_data_success += 1
                            #for i in range(len(list_info)):
                            #    print("读取股票分时数据成功：", list_info[i])
                        else:
                            read_file_failed += 1
                            #for i in range(len(list_info)):
                            #    print("读取股票分时数据失败：", list_info[i])
                self.SendMessage("%s：总计 %d，读失败 %d，读成功 %d，建表 %d，清表 %d，存失败 %d，存成功 %d，总记录 %d，失败记录 %d，成功记录 %d。" % \
                    (market, total_file_number, read_file_failed, read_file_success, create_table, truncate_table, save_data_failed, save_data_success, total_record_number, save_record_failed, save_record_success))
            else:
                self.SendMessage("查询数据库表列表失败！")

if __name__ == "__main__":
    folder_stock_ticks_sh = "X:\Ticks_201612\sh"
    folder_stock_ticks_sz = "X:\Ticks_201612\sz"
    data_maker_stock_kline_1_m = DataMaker_StockKline_1_M()
    data_maker_stock_kline_1_m.SetMySQL(host = "10.0.7.53", port = 3306, user = "root", passwd = "root", db = "quotedata", charset = "utf8") # 测试
    #data_maker_stock_kline_1_m.SetMySQL(host = "10.0.7.80", port = 3306, user = "root", passwd = "root", db = "quotedata", charset = "utf8") # 生产
    if data_maker_stock_kline_1_m.ConnectDB() == True:
        stock_ticks_file_list_sh = data_maker_stock_kline_1_m.GetStockTicksFileList(folder_stock_ticks_sh)
        stock_ticks_file_list_sz = data_maker_stock_kline_1_m.GetStockTicksFileList(folder_stock_ticks_sz)
        #data_maker_stock_kline_1_m.SaveData_StockTicks(stock_ticks_file_list_sh, "sh", None, "update") # create、update
        #data_maker_stock_kline_1_m.SaveData_StockTicks(stock_ticks_file_list_sz, "sz", None, "update") # create、update
        data_maker_stock_kline_1_m.SaveData_StockTicks(stock_ticks_file_list_sh, "sh", ["600000", "600004"], "update") # create、update
        data_maker_stock_kline_1_m.SaveData_StockTicks(stock_ticks_file_list_sz, "sz", ["000001", "000002"], "create") # create、update
        data_maker_stock_kline_1_m.DisconnectDB()
