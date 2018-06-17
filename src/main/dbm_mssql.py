
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

import pymssql

try: import logger
except: pass

class DBM_MsSQL():
    def __init__(self, **kwargs):
        self.log_text = ""
        self.log_cate = "DBM_MsSQL"
        self.logger = None
        try: self.logger = logger.Logger()
        except: pass
        self.host = kwargs.get("host", "0.0.0.0")
        self.port = kwargs.get("port", "0")
        self.user = kwargs.get("user", "user")
        self.password = kwargs.get("password", "123456")
        self.database = kwargs.get("database", "test")
        self.charset = kwargs.get("charset", "utf8")
        self.connect = None
        self.cursor = None

    def __del__(self):
        self.Stop()

    def SendMessage(self, log_kind, log_class, log_cate, log_info, log_show = ""):
        if self.logger != None:
            self.logger.SendMessage(log_kind, log_class, log_cate, log_info, log_show)
        else:
            print("%s：%s：%s" % (log_kind, log_cate, log_info))

    def Start(self):
        if not self.database:
            self.SendMessage("E", 4, self.log_cate, "数据库设置为空！", "S")
            return False
        self.connect = pymssql.connect(host = self.host, port = self.port, user = self.user, password = self.password, database = self.database, charset = self.charset)
        if not self.connect:
            self.SendMessage("E", 4, self.log_cate, "数据库连接失败！", "S")
            return False
        self.cursor = self.connect.cursor()
        if not self.cursor:
            self.SendMessage("E", 4, self.log_cate, "数据库获取失败！", "S")
            return False
        return True

    def Stop(self):
        if self.cursor:
            self.cursor.close()
        if self.connect:
            self.connect.close()

    def ExecQuery(self, sql): #ִ 执行查询语句，返回一个 list 其元素是记录行，每个元素 tuple 是每行记录字段
        if self.cursor:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        else:
            self.log_text = "数据库查询失败！%s" % sql
            self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return None

    def ExecNonQuery(self, sql): # 执行非查询语句 # msSQL.ExecNonQuery("INSERT INTO WeiBoUser VALUES('2', '3')")
        if self.cursor:
            self.cursor.execute(sql)
            self.connect.commit()
            return True
        else:
            self.log_text = "数据库执行失败！%s" % sql
            self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return False
