
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

import re
import time
import math

import pymysql

from warnings import filterwarnings
filterwarnings("error", category = pymysql.Warning)

try: import logger
except: pass

class DBM_MySQL():
    def __init__(self, **kwargs):
        self.log_text = ""
        self.log_cate = "DBM_MySQL"
        self.logger = None
        try: self.logger = logger.Logger()
        except: pass
        self.host = kwargs.get("host", "0.0.0.0")
        self.port = kwargs.get("port", 0)
        self.user = kwargs.get("user", "user")
        self.passwd = kwargs.get("passwd", "123456")
        self.db = kwargs.get("db", "test")
        self.charset = kwargs.get("charset", "utf8")
        self.connect = None
        self.cursor = None
        self.batch_number = 3000

    def __del__(self):
        self.Disconnect()

    def SendMessage(self, log_kind, log_class, log_cate, log_info, log_show = ""):
        if self.logger != None:
            self.logger.SendMessage(log_kind, log_class, log_cate, log_info, log_show)
        else:
            print("%s：%s：%s" % (log_kind, log_cate, log_info))

    def Connect(self):
        self.Disconnect()
        try:
            self.connect = pymysql.connect(host = self.host, port = self.port, user = self.user, passwd = self.passwd, db = self.db, charset = self.charset)
            return True
        except pymysql.Warning as w:
            self.connect = None
            self.log_text = "连接警告：%s" % str(w)
            self.SendMessage("W", 3, self.log_cate, self.log_text, "S")
        except pymysql.Error as e:
            self.connect = None
            self.log_text = "连接错误：%s" % str(e)
            self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        return False

    def Disconnect(self):
        if self.connect != None:
            self.connect.close()
            self.connect = None

    def CheckConnect(self):
        try_times = 0
        not_connect = True
        while not_connect == True and try_times < 1000:
            try:
                self.connect.ping()
                not_connect = False # 说明连接正常
            except Exception as e:
                self.log_text = "检测到数据库连接已断开！%s" % e
                self.SendMessage("W", 3, self.log_cate, self.log_text, "S")
                if self.Connect() == True: # 重连成功
                    not_connect = False # 连接已经正常
                    self.log_text = "数据库重连成功。"
                    self.SendMessage("I", 1, self.log_cate, self.log_text, "S")
                    break
                else:
                    try_times += 1
                    self.log_text = "数据库重连失败！%d" % try_times
                    self.SendMessage("W", 3, self.log_cate, self.log_text, "S")
                    time.sleep(5) # 等待重试

    def ExecuteSql(self, sql):
        if self.connect == None:
            self.log_text = "执行(单)错误：数据库尚未连接！"
            self.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            return False
        else:
            try:
                self.CheckConnect()
                self.cursor = self.connect.cursor()
                self.cursor.execute(sql)
                self.connect.commit() #
                self.cursor.close()
                return True
            except pymysql.Warning as w:
                self.log_text = "执行(单)警告：%s" % str(w)
                self.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            except pymysql.Error as e:
                self.log_text = "执行(单)错误：%s" % str(e)
                self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return False

    def ExecuteManySql(self, sql, values):
        if self.connect == None:
            self.log_text = "执行(多)错误：数据库尚未连接！"
            self.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            return False
        else:
            try:
                self.CheckConnect()
                self.cursor = self.connect.cursor()
                self.cursor.executemany(sql, values)
                self.connect.commit() #
                self.cursor.close()
                return True
            except pymysql.Warning as w:
                self.log_text = "执行(多)警告：%s" % str(w)
                self.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            except pymysql.Error as e:
                self.log_text = "执行(多)错误：%s" % str(e)
                self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return False

    def QueryAllSql(self, sql):
        if self.connect == None:
            self.log_text = "查询(全)错误：数据库尚未连接！"
            self.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            return None
        else:
            try:
                self.CheckConnect()
                self.cursor = self.connect.cursor()
                self.cursor.execute(sql)
                result = self.cursor.fetchall()
                self.cursor.close()
                return result
            except pymysql.Warning as w:
                self.log_text = "查询(全)警告：%s" % str(w)
                self.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            except pymysql.Error as e:
                self.log_text = "查询(全)错误：%s" % str(e)
                self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return None

    def TruncateOrCreateTable(self, table_name, sql_create):
        sql = "SHOW TABLES"
        result = self.QueryAllSql(sql)
        if result != None:
            data_tables = list(result)
            #print(data_tables)
            have_tables = re.findall("(\'.*?\')", str(data_tables))
            have_tables = [re.sub("'", "", table) for table in have_tables]
            #print(have_tables)
            if table_name in have_tables:
                sql = "TRUNCATE TABLE %s" % table_name
                return self.ExecuteSql(sql)
            else:
                return self.ExecuteSql(sql_create)
        else:
            self.SendMessage("E", 4, self.log_cate, "查询数据库表列表失败！", "S")
        return False

    def BatchInsert(self, values_list, sql_insert):
        save_record_failed = 0
        save_record_success = 0
        total_record_num = len(values_list)
        divide_count = math.floor(total_record_num / self.batch_number)
        if divide_count >= 1:
            for i in range(divide_count):
                if self.ExecuteManySql(sql_insert, values_list[(i * self.batch_number) : ((i + 1) * self.batch_number)]) == True:
                    save_record_success += self.batch_number
                else:
                    save_record_failed += self.batch_number
                #print("保存：", self.batch_number)
        left_number = total_record_num - divide_count * self.batch_number
        if left_number > 0:
            if self.ExecuteManySql(sql_insert, values_list[(divide_count * self.batch_number) : (total_record_num)]) == True:
                save_record_success += left_number
            else:
                save_record_failed += left_number
            #print("保存：", left_number)
        return total_record_num, save_record_success, save_record_failed
