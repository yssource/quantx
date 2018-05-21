
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
from datetime import datetime, date

import numpy as np
import pandas as pd
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QTextEdit, QHBoxLayout, QVBoxLayout

import dbm_mssql
import dbm_mysql

pd.set_option("max_colwidth", 200)
pd.set_option("display.width", 500)

class Capital(object):
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
        str_sql = "SELECT SecuMain.InnerCode, SecuMain.SecuCode, SecuMain.SecuAbbr, SecuMain.SecuMarket, LC_ShareStru.EndDate, LC_ShareStru.TotalShares, LC_ShareStru.AFloatListed \
                  FROM SecuMain INNER JOIN LC_ShareStru \
                  ON SecuMain.CompanyCode = LC_ShareStru.CompanyCode \
                  WHERE (SecuMain.SecuMarket = 83 OR SecuMain.SecuMarket = 90) \
                    AND (SecuMain.SecuCategory = 1) \
                    AND (SecuMain.ListedSector = 1 or SecuMain.ListedSector = 2 or SecuMain.ListedSector = 6) \
                    AND CAST(LC_ShareStru.CompanyCode as nvarchar) + CAST(LC_ShareStru.EndDate as nvarchar) IN \
                      ( \
                        SELECT CAST(CompanyCode as nvarchar) + CAST(MAX(EndDate) as nvarchar) \
                        FROM LC_ShareStru \
                        GROUP BY CompanyCode \
                      ) \
                  ORDER BY SecuMain.SecuMarket ASC, SecuMain.SecuCode ASC"
        result_list = dbm.ExecQuery(str_sql)
        if result_list != None:
            for (InnerCode, SecuCode, SecuAbbr, SecuMarket, EndDate, TotalShares, AFloatListed) in result_list:
                if not SecuCode[0] == "X": # 排除未上市的新股
                    stock_market = ""
                    if SecuMarket == 83:
                        stock_market = "SH"
                    elif SecuMarket == 90:
                        stock_market = "SZ"
                    capital = Capital(inners = InnerCode, market = stock_market, code = SecuCode, name = SecuAbbr)
                    capital.SetEndDate(EndDate) # 截止日期
                    if TotalShares != None:
                        capital.total_shares = TotalShares
                    if AFloatListed != None:
                        capital.circu_shares = AFloatListed
                    self.capital_dict[InnerCode] = capital
                    #print InnerCode, SecuCode, SecuAbbr, SecuMarket, EndDate, TotalShares, AFloatListed
            self.SendMessage("获取 股本结构 成功。总计 %d 个。" % len(result_list))
            self.CheckStockGuBen()
        else:
            self.SendMessage("获取 股本结构 失败！")

    def PushData_Capital(self, dbm):
        if dbm == None:
            self.SendMessage("PushData_Capital 数据库 dbm 尚未连接！")
            return
        table_name = "capital_data"
        sql = "SHOW TABLES"
        result = dbm.QueryAllSql(sql)
        data_tables = list(result)
        #print(data_tables)
        have_tables = re.findall("(\'.*?\')", str(data_tables))
        have_tables = [re.sub("'", "", table) for table in have_tables]
        #print(have_tables)
        if table_name in have_tables:
            sql = "TRUNCATE TABLE %s" % table_name
            dbm.ExecuteSql(sql)
        else:
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
            dbm.ExecuteSql(sql)
        capital_keys = list(self.capital_dict.keys())
        capital_keys.sort()
        capital_dict_list = [self.capital_dict[key] for key in capital_keys]
        total_record_num = 0
        save_record_failed = 0
        save_record_success = 0
        values = []
        save_index_from = 0 #
        total_record_num = len(capital_dict_list)
        sql = "INSERT INTO %s" % table_name + "(inners, market, code, name, end_date, total_shares, circu_shares) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        for i in range(save_index_from, total_record_num):
            str_date = self.TransDateIntToStr(capital_dict_list[i].end_date)
            values.append((capital_dict_list[i].inners, capital_dict_list[i].market, capital_dict_list[i].code, capital_dict_list[i].name, str_date, capital_dict_list[i].total_shares, capital_dict_list[i].circu_shares))
            if (i - save_index_from + 1) % 3000 == 0: # 自定义每批次保存条数
                if len(values) > 0: # 有记录需要保存
                    if dbm.ExecuteManySql(sql, values) == False:
                        save_record_failed += len(values)
                    else:
                        save_record_success += len(values)
                    #print("保存：", len(values))
                    values = [] #
        if len(values) > 0: # 有记录需要保存
            if dbm.ExecuteManySql(sql, values) == False:
                save_record_failed += len(values)
            else:
                save_record_success += len(values)
            #print("保存：", len(values))
        self.SendMessage("入库：总记录 %d，成功记录 %d，失败记录 %d。" % (total_record_num, save_record_success, save_record_failed))

    def SaveData_Capital(self, save_path):
        values = []
        capital_keys = list(self.capital_dict.keys())
        capital_keys.sort()
        capital_dict_list = [self.capital_dict[key] for key in capital_keys]
        total_record_num = len(capital_dict_list)
        for i in range(total_record_num):
            date_date = self.TransDateIntToDate(capital_dict_list[i].end_date)
            values.append((capital_dict_list[i].inners, capital_dict_list[i].market, capital_dict_list[i].code, capital_dict_list[i].name, date_date, capital_dict_list[i].total_shares, capital_dict_list[i].circu_shares))
        columns = ["inners", "market", "code", "name", "end_date", "total_shares", "circu_shares"]
        result = pd.DataFrame(columns = columns) # 空
        if len(values) > 0:
            result = pd.DataFrame(data = values, columns = columns)
        #print(result)
        result.to_pickle(save_path)
        self.SendMessage("保存：总记录 %d，保存记录 %d，失败记录 %d。" % (total_record_num, result.shape[0], total_record_num - result.shape[0]))

class BasicDataMaker(QDialog):
    def __init__(self, save_folder):
        super(BasicDataMaker, self).__init__()
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
        
        self.save_folder = save_folder
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
        
        self.InitUserInterface()

    def __del__(self):
        pass

    def SendMessage(self, text_info):
        self.text_edit_text_info.append(text_info)

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

    def ConnectDB(self):
        self.dbm_jydb = dbm_mssql.DBM_MsSQL(host = self.mssql_host, port = self.mssql_port, user = self.mssql_user, password = self.mssql_password, database = self.mssql_database, charset = self.mssql_charset)
        self.dbm_financial = dbm_mysql.DBM_MySQL(host = self.mysql_host, port = self.mysql_port, user = self.mysql_user, passwd = self.mysql_passwd, db = self.mysql_db, charset = self.mysql_charset)
        self.dbm_jydb.Start()
        self.dbm_financial.Connect()
        self.SendMessage("数据库连接完成。")

    def InitUserInterface(self):
        self.setWindowTitle("基础数据面板")
        self.resize(400, 600)
        self.setFont(QFont("SimSun", 9))
        
        self.button_capital = QPushButton("股本结构")
        self.button_capital.setFont(QFont("SimSun", 9))
        self.button_capital.setStyleSheet("font:bold;color:blue")
        self.button_capital.setFixedWidth(70)
        
        self.text_edit_text_info = QTextEdit()
        
        self.h_box_layout_buttons = QHBoxLayout()
        self.h_box_layout_buttons.setContentsMargins(-1, -1, -1, -1)
        self.h_box_layout_buttons.addWidget(self.button_capital)
        
        self.h_box_layout_text_info = QHBoxLayout()
        self.h_box_layout_text_info.setContentsMargins(-1, -1, -1, -1)
        self.h_box_layout_text_info.addWidget(self.text_edit_text_info)
        
        self.v_box_layout = QVBoxLayout()
        self.v_box_layout.setContentsMargins(-1, -1, -1, -1)
        self.v_box_layout.addLayout(self.h_box_layout_buttons)
        self.v_box_layout.addLayout(self.h_box_layout_text_info)
        
        self.setLayout(self.v_box_layout)
        
        self.button_capital.clicked.connect(self.OnButtonCapital)

    def OnButtonCapital(self):
        self.SendMessage("# ---------- 开始：股本结构 ---------- #")
        data_maker_capital = DataMaker_Capital(self)
        data_maker_capital.PullData_Capital(self.dbm_jydb)
        data_maker_capital.PushData_Capital(self.dbm_financial)
        data_maker_capital.SaveData_Capital(self.save_folder + "/capital_data")
        self.SendMessage("# ---------- 完成：股本结构 ---------- #")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    basic_data_maker = BasicDataMaker("I:/Project/Project/QuantX/src/main/tool")
    basic_data_maker.show()
    basic_data_maker.SetMsSQL(host = "10.0.7.80", port = "1433", user = "research", password = "Research@123", database = "JYDB_NEW", charset = "GBK")
    basic_data_maker.SetMySQL(host = "10.0.7.80", port = 3306, user = "root", passwd = "Root123456lhtZ", db = "financial", charset = "utf8")
    basic_data_maker.ConnectDB()
    sys.exit(app.exec_())
