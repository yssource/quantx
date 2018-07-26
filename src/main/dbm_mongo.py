
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

import pymongo

try: import logger
except: pass

class DBM_Mongo():
    def __init__(self, **kwargs):
        self.log_text = ""
        self.log_cate = "DBM_Mongo"
        self.logger = None
        try: self.logger = logger.Logger()
        except: pass
        self.host = kwargs.get("host", "0.0.0.0")
        self.port = kwargs.get("port", 0)
        self.database = kwargs.get("database", "test")
        self.collection = kwargs.get("collection", "test")
        self.client = None
        self.db = None
        self.cc = None

    def __del__(self):
        self.connect = None
        self.db = None
        self.cc = None

    def SendMessage(self, log_kind, log_class, log_cate, log_info, log_show = ""):
        if self.logger != None:
            self.logger.SendMessage(log_kind, log_class, log_cate, log_info, log_show)
        else:
            print("%s：%s：%s" % (log_kind, log_cate, log_info))

    def Connect(self):
        try:
            self.client = pymongo.MongoClient(host = self.host, port = self.port)
            self.db = self.client.get_database(self.database)
            self.cc = self.db.get_collection(self.collection)
            return True
        except Exception as e:
            self.connect = None
            self.db = None
            self.cc = None
            self.log_text = "连接异常：%s，%s" % (Exception, e)
            self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        return False

    def Query(self, exp, sort = None, projection = None):
         if self.cc != None:
             return self.cc.find(exp, sort = sort, projection = projection)
         return None
