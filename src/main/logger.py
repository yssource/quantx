
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
import json
import socket
import logging
import sqlite3
import datetime
import StringIO
import threading
import exceptions

from PyQt5 import QtCore, QtWidgets
from logging.handlers import TimedRotatingFileHandler

import define
import common

logger = logging.getLogger("QuantX")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s %(levelname)-5s %(message)s")

debuger = TimedRotatingFileHandler("..\logs\QuantX_%s.log" % common.GetDateShort(), "D", 1)
debuger.setLevel(logging.DEBUG)
debuger.setFormatter(formatter)
logger.addHandler(debuger)

errorer = TimedRotatingFileHandler("..\logs\QuantX_%s_E.log" % common.GetDateShort(), "D", 1)
errorer.setLevel(logging.ERROR)
errorer.setFormatter(formatter)
logger.addHandler(errorer)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)

class LogInfo(object):
    def __init__(self, log_kind, log_class, log_cate, log_info, major_id = ""):
        self.time_stamp = datetime.datetime.now()
        self.log_kind = log_kind
        self.log_class = log_class
        self.log_cate = log_cate
        self.log_info = log_info
        self.major_id = major_id

class Connect():
    def __init__(self, socket, describe, available, address, port):
        self.socket = socket
        self.describe = describe
        self.available = available
        self.address = address
        self.port = port

class Logger(common.Singleton):
    def __init__(self):
        self.logger = logger
        self.log_text = ""
        self.log_cate = "Logger"
        self.id = "QuantX" # 数据库名称
        self.db = None # 数据库对象
        self.cu = None # 数据库游标
        self.tb_name_logger = "tb_logger"
        self.tb_data_logger = []
        self.tb_lock_logger = threading.Lock()
        self.db_init_time = 600
        self.db_init_flag = False # 目前 23:00 还原
        
        self.main_mindow = None
        self.log_info_panel_s = None
        self.log_info_panel_t = None
        self.log_info_panel_m = None
        self.log_info_panel_a = None
        self.log_info_panel_spbsa = None
        
        self.started = False
        self.msg_type = "logger"
        self.connect_dict = {}
        self.connect_lock = threading.Lock()
        
        self.InitDataBase()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.TrySaveSendData)
        self.timer.start(5000)

    def __del__(self):
        self.timer.stop()
        del self.timer
        self.TrySaveSendData() # 最后再调用一次吧，如果 Server 已调用过 StopServer 则 self.started == False 的，不会在 PutTbData_Logger 中再发送数据
        self.StopDataBase()
        self.StopServer()

    def SetMainWindow(self, window):
        self.main_mindow = window

    def SetLogInfoPanel_S(self, panel):
        self.log_info_panel_s = panel
        self.log_info_panel_s.main_mindow = self.main_mindow

    def SetLogInfoPanel_T(self, panel):
        self.log_info_panel_t = panel
        self.log_info_panel_t.main_mindow = self.main_mindow

    def SetLogInfoPanel_M(self, panel):
        self.log_info_panel_m = panel
        self.log_info_panel_m.main_mindow = self.main_mindow

    def SetLogInfoPanel_A(self, panel):
        self.log_info_panel_a = panel
        self.log_info_panel_a.main_mindow = self.main_mindow

    def SetLogInfoPanel_SPBSA(self, panel):
        self.log_info_panel_spbsa = panel
        self.log_info_panel_spbsa.main_mindow = self.main_mindow

    def ChangeInfoMsgColor(self):
        if self.log_info_panel_s != None:
            self.log_info_panel_s.ChangeInfoMsgColor()
        if self.log_info_panel_t != None:
            self.log_info_panel_t.ChangeInfoMsgColor()
        if self.log_info_panel_m != None:
            self.log_info_panel_m.ChangeInfoMsgColor()
        if self.log_info_panel_a != None:
            self.log_info_panel_a.ChangeInfoMsgColor()
        if self.log_info_panel_spbsa != None:
            self.log_info_panel_spbsa.ChangeInfoMsgColor()

    def SendMessage(self, log_kind, log_class, log_cate, log_info, log_show = ""): # 自身的日志就不保存到数据库了
        if log_kind == "D" or log_kind == "I" or log_kind == "H" or log_kind == "W":
            self.logger.debug("%s %d <%s> - %s" % (log_kind, log_class, log_cate, log_info))
        elif log_kind == "S" or log_kind == "E" or log_kind == "F":
            self.logger.error("%s %d <%s> - %s" % (log_kind, log_class, log_cate, log_info))
        log_item = LogInfo(log_kind, log_class, log_cate, log_info)
        self.AddTbData_Logger(log_item)
        if log_show == define.DEF_LOG_SHOW_TYPE_S and self.log_info_panel_s != None:
            self.log_info_panel_s.AddLogInfo(log_item)
            QtWidgets.QApplication.postEvent(self.log_info_panel_s, QtCore.QEvent(define.DEF_EVENT_LOG_INFO_PRINT))
        elif log_show == define.DEF_LOG_SHOW_TYPE_T and self.log_info_panel_t != None:
            self.log_info_panel_t.AddLogInfo(log_item)
            QtWidgets.QApplication.postEvent(self.log_info_panel_t, QtCore.QEvent(define.DEF_EVENT_LOG_INFO_PRINT))
        elif log_show == define.DEF_LOG_SHOW_TYPE_M and self.log_info_panel_m != None:
            self.log_info_panel_m.AddLogInfo(log_item)
            QtWidgets.QApplication.postEvent(self.log_info_panel_m, QtCore.QEvent(define.DEF_EVENT_LOG_INFO_PRINT))
        elif log_show == define.DEF_LOG_SHOW_TYPE_A and self.log_info_panel_a != None:
            self.log_info_panel_a.AddLogInfo(log_item)
            QtWidgets.QApplication.postEvent(self.log_info_panel_a, QtCore.QEvent(define.DEF_EVENT_LOG_INFO_PRINT))
        elif log_show == define.DEF_LOG_SHOW_TYPE_SPBSA and self.log_info_panel_spbsa != None:
            self.log_info_panel_spbsa.AddLogInfo(log_item)
            QtWidgets.QApplication.postEvent(self.log_info_panel_spbsa, QtCore.QEvent(define.DEF_EVENT_LOG_INFO_PRINT))

####################################################################################################

    def InitDataBase(self):
        self.StopDataBase()
        
        self.db = sqlite3.connect("../logs/%s_%s.db" % (self.id, common.GetDateShort()))
        self.db.text_factory = str # 支持中文字符
        self.cu = self.db.cursor()
        
        sql_check_table_logger = "select count(*) from sqlite_master where type = 'table' and name = '%s'" % self.tb_name_logger
        
        sql_create_table_logger = "create table %s ( id integer primary key not null, \
                                                     date integer, \
                                                     time integer, \
                                                     kind varchar(2), \
                                                     class integer, \
                                                     cate varchar(64), \
                                                     info text )" % self.tb_name_logger # 表存续期间自增：INTEGER PRIMARY KEY AUTOINCREMENT
        
        try:
            self.cu.execute(sql_check_table_logger)
            if self.cu.fetchone()[0] == 0:
                self.cu.execute(sql_create_table_logger)
            self.db.commit()
        except sqlite3.Error as e:
            self.log_text = "创建 数据表 %s 异常！%s" % (self.tb_name_logger, e.args[0])
            self.SendMessage("E", self.log_cate, self.log_text, "S")

    def StopDataBase(self):
        if self.cu != None:
            self.cu.close()
            self.cu = None
        if self.db != None:
            self.db.close()
            self.db = None

####################################################################################################

    def AddTbData_Logger(self, log_item):
        data = [
                int(log_item.time_stamp.strftime("%Y%m%d")), # 日期
                int(log_item.time_stamp.strftime("%H%M%S%f")), # 时间
                log_item.log_kind, # 分类
                log_item.log_class, # 级别
                log_item.log_cate, # 模块
                log_item.log_info # 信息
               ]
        self.tb_lock_logger.acquire()
        self.tb_data_logger.append(data)
        self.tb_lock_logger.release()

    def PutTbData_Logger(self):
        if len(self.tb_data_logger) > 0:
            self.tb_lock_logger.acquire()
            tb_data = self.tb_data_logger
            self.tb_data_logger = []
            self.tb_lock_logger.release()
            
            if self.db != None and self.cu != None:
                self.cu.executemany("insert into %s values (null, ?, ?, ?, ?, ?, ?)" % self.tb_name_logger, tb_data)
                self.db.commit()
            
            if self.started == True:
                for data in tb_data:
                    log_data = {"type":self.msg_type, "func":900001, "date":data[0], "time":data[1], "kind":data[2], "class":data[3], "cate":data[4], "info":data[5]}
                    self.SendDataAll(log_data)

    def TrySaveSendData(self): # 定时保存
        now_time = int(datetime.datetime.now().strftime("%H%M"))
        if now_time == self.db_init_time and self.db_init_flag == False:
            self.db_init_flag = True
            self.InitDataBase()
        if now_time == 2300:
            self.db_init_flag = False
        
        self.PutTbData_Logger()

####################################################################################################
