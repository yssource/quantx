
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

import dbm_mysql
import LoadQuoteStockDaily

class DataMaker_StockDaily():
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

    def GetStockDailyFileList(self, folder): # 只读取一层
        file_list = []
        path_list = os.listdir(folder)
        for path_item in path_list:
            file_list.append(os.path.join("%s\%s" % (folder, path_item)))
            #print(os.path.join("%s\%s" % (folder, path_item)))
        return file_list

    def SaveData_StockDaily(self, file_list, market, code_list, model): # market：sh、sz
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
                for file_item in file_list:
                    file_head = 0
                    file_path = file_item
                    list_info = []
                    dict_data = {}
                    stock_code = file_item[-9:-3]
                    table_name = "stock_daily_" + market + "_" + stock_code
                    if code_list == None or stock_code in code_list:
                        total_file_number += 1
                        result = LoadQuoteStockDaily.LoadQuote(file_path, file_head, list_info, dict_data)
                        print(stock_code, result, len(list_info))
                        if result >= 0:
                            #for i in range(result):
                            #    print(dict_data["Date"][i], dict_data["Time"][i], dict_data["Open"][i], dict_data["High"][i], dict_data["Low"][i], dict_data["Close"][i], \
                            #          dict_data["Volume"][i], dict_data["Turnover"][i], dict_data["MatchItems"][i], dict_data["Interest"][i])
                            save_index_from = 0 #
                            read_file_success += 1
                            if table_name in have_tables:
                                if model == "create": # 需要清空表
                                    truncate_table += 1
                                    sql = "TRUNCATE TABLE %s" % table_name
                                    self.dbm_quotedata.ExecuteSql(sql)
                                if model == "update": # 需要过滤值
                                    sql = "SELECT MAX(date) FROM %s" % table_name
                                    query_result = self.dbm_quotedata.QueryAllSql(sql)
                                    if query_result != None:
                                        data_list = list(query_result)
                                        if len(data_list) > 0:
                                            data = data_list[0]
                                            #print(data) # (datetime.date(2016, 12, 30),)、(None,)
                                            if data[0] != None:
                                                save_index_from = result # 先置为最大下标
                                                max_date = data[0].year * 10000 + data[0].month * 100 + data[0].day
                                                for i in range(result):
                                                    if dict_data["Date"][i] > max_date:
                                                        save_index_from = i # 从这个下标开始保存入库
                                                        break
                            else:
                                create_table += 1
                                sql = "CREATE TABLE `%s` (" % table_name + \
                                      "`id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号'," + \
                                      "`date` date NOT NULL COMMENT '日期'," + \
                                      "`open` float(10,3) DEFAULT '0.000' COMMENT '开盘价'," + \
                                      "`high` float(10,3) DEFAULT '0.000' COMMENT '最高价'," + \
                                      "`low` float(10,3) DEFAULT '0.000' COMMENT '最低价'," + \
                                      "`close` float(10,3) DEFAULT '0.000' COMMENT '收盘价'," + \
                                      "`volume` bigint(64) DEFAULT '0' COMMENT '成交量，股'," + \
                                      "`turnover` bigint(64) DEFAULT '0' COMMENT '成交额，元'," + \
                                      "PRIMARY KEY (`id`)," + \
                                      "UNIQUE KEY `idx_date` (`date`)" + \
                                      ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
                                self.dbm_quotedata.ExecuteSql(sql)
                            values = []
                            no_error_flag = True
                            total_record_number += result
                            sql = "INSERT INTO %s" % table_name + "(date, open, high, low, close, volume, turnover) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                            for i in range(save_index_from, result):
                                str_date = self.TransDateIntToStr(dict_data["Date"][i])
                                values.append((str_date, dict_data["Open"][i], dict_data["High"][i], dict_data["Low"][i], dict_data["Close"][i], dict_data["Volume"][i], dict_data["Turnover"][i]))
                                if (i - save_index_from + 1) % 3000 == 0: # 自定义每批次保存条数
                                    if len(values) > 0: # 有记录需要保存
                                        if self.dbm_quotedata.ExecuteManySql(sql, values) == False:
                                            no_error_flag = False
                                            save_record_failed += len(values)
                                        else:
                                            save_record_success += len(values)
                                        #print(stock_code, " 保存：", len(values))
                                        values = [] #
                            if len(values) > 0: # 有记录需要保存
                                if self.dbm_quotedata.ExecuteManySql(sql, values) == False:
                                    no_error_flag = False
                                    save_record_failed += len(values)
                                else:
                                    save_record_success += len(values)
                                #print(stock_code, " 保存：", len(values))
                            if no_error_flag == False:
                                save_data_failed += 1
                            else:
                                save_data_success += 1
                            #for i in range(len(list_info)):
                            #    print("读取股票日线数据成功：", list_info[i])
                        else:
                            read_file_failed += 1
                            #for i in range(len(list_info)):
                            #    print("读取股票日线数据失败：", list_info[i])
                self.SendMessage("%s：总计 %d，读失败 %d，读成功 %d，建表 %d，清表 %d，存失败 %d，存成功 %d，总记录 %d，失败记录 %d，成功记录 %d。" % \
                    (market, total_file_number, read_file_failed, read_file_success, create_table, truncate_table, save_data_failed, save_data_success, total_record_number, save_record_failed, save_record_success))
            else:
                self.SendMessage("查询数据库表列表失败！")

if __name__ == "__main__":
    folder_stock_daily_sh = "X:\Daily_20170804\sh"
    folder_stock_daily_sz = "X:\Daily_20170804\sz"
    data_maker_stock_daily = DataMaker_StockDaily()
    data_maker_stock_daily.SetMySQL(host = "10.0.7.53", port = 3306, user = "root", passwd = "root", db = "quotedata", charset = "utf8") # 测试
    #data_maker_stock_daily.SetMySQL(host = "10.0.7.80", port = 3306, user = "root", passwd = "root", db = "quotedata", charset = "utf8") # 生产
    if data_maker_stock_daily.ConnectDB() == True:
        stock_daily_file_list_sh = data_maker_stock_daily.GetStockDailyFileList(folder_stock_daily_sh)
        stock_daily_file_list_sz = data_maker_stock_daily.GetStockDailyFileList(folder_stock_daily_sz)
        #data_maker_stock_daily.SaveData_StockDaily(stock_daily_file_list_sh, "sh", None, "update") # create、update
        #data_maker_stock_daily.SaveData_StockDaily(stock_daily_file_list_sz, "sz", None, "update") # create、update
        data_maker_stock_daily.SaveData_StockDaily(stock_daily_file_list_sh, "sh", ["600000", "600004"], "update") # create、update
        data_maker_stock_daily.SaveData_StockDaily(stock_daily_file_list_sz, "sz", ["000001", "000002"], "create") # create、update
        data_maker_stock_daily.DisconnectDB()
