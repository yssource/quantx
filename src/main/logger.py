
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

import sys
import time
import json
import socket
import logging
import sqlite3
import datetime
import threading

from PyQt5.QtCore import QEvent, QTimer
from PyQt5.QtWidgets import QApplication
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
        
        self.timer = QTimer()
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
            QApplication.postEvent(self.log_info_panel_s, QEvent(define.DEF_EVENT_LOG_INFO_PRINT))
        elif log_show == define.DEF_LOG_SHOW_TYPE_T and self.log_info_panel_t != None:
            self.log_info_panel_t.AddLogInfo(log_item)
            QApplication.postEvent(self.log_info_panel_t, QEvent(define.DEF_EVENT_LOG_INFO_PRINT))
        elif log_show == define.DEF_LOG_SHOW_TYPE_M and self.log_info_panel_m != None:
            self.log_info_panel_m.AddLogInfo(log_item)
            QApplication.postEvent(self.log_info_panel_m, QEvent(define.DEF_EVENT_LOG_INFO_PRINT))
        elif log_show == define.DEF_LOG_SHOW_TYPE_A and self.log_info_panel_a != None:
            self.log_info_panel_a.AddLogInfo(log_item)
            QApplication.postEvent(self.log_info_panel_a, QEvent(define.DEF_EVENT_LOG_INFO_PRINT))
        elif log_show == define.DEF_LOG_SHOW_TYPE_SPBSA and self.log_info_panel_spbsa != None:
            self.log_info_panel_spbsa.AddLogInfo(log_item)
            QApplication.postEvent(self.log_info_panel_spbsa, QEvent(define.DEF_EVENT_LOG_INFO_PRINT))

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

    def StartServer(self, port, type):
        self.log_type = type
        if self.started == False:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            except socket.error as e:
                self.log_text = "日志服务 创建 socket 失败！端口：%d，%s" % (port, e)
                self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
                return False
            try:
                self.sock.bind(("0.0.0.0", port))
            except socket.error as e:
                self.log_text = "日志服务 绑定 socket 失败！端口：%d，%s" % (port, e)
                self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
                return False
            try:
                self.sock.listen(100) # 貌似不会受到连接数量限制
            except socket.error as e:
                self.log_text = "日志服务 监听 socket 失败！端口：%d，%s" % (port, e)
                self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
                return False
            self.started = True
            self.thread_handle_accept = threading.Thread(target = self.HandleAccept)
            self.thread_handle_accept.start()
            self.thread_heart_checker = threading.Thread(target = self.HeartChecker)
            self.thread_heart_checker.start()
        return True

    def StopServer(self):
        if self.started == True:
            self.started = False
            self.connect_lock.acquire()
            for describe, connect in self.connect_dict.items():
                if connect.available == True:
                    connect.socket.close()
                    connect.available = False
            self.connect_dict.clear()
            self.connect_lock.release()
            self.sock.close() # 对于 accept 无效，只能从 IDE 结束进程了

    def HandleAccept(self):
        while self.started == True:
            try:
                client, address = self.sock.accept()
                describe = "%s:%d" % (address[0], address[1])
                connect = Connect(client, describe, True, address[0], address[1])
                self.connect_lock.acquire()
                self.connect_dict[describe] = connect
                self.connect_lock.release()
                self.log_text = "日志服务新增连接：%s" % describe
                self.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            except socket.error as e:
                self.log_text = "日志服务接受连接发生异常！%s" % e
                self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            except Exception as e:
                self.log_text = "日志服务接受连接发生异常！%s" % e
                self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        
        self.log_text = "日志服务连接处理线程退出！"
        self.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def HeartChecker(self):
        while self.started == True:
            self.SendNoneAll()
            time.sleep(10)
        
        self.log_text = "日志服务心跳检测线程退出！"
        self.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def SendNone(self, sock, describe):
        try:
            msg_type = "0" # NW_MSG_TYPE_HEART_CHECK
            msg_code = "0" # NW_MSG_CODE_NONE
            msg_size = "%6x" % 0
            msg_send = msg_type + msg_code + msg_size
            sock.send(msg_send)
            return True
        except socket.error as e:
            self.log_text = "日志服务发送 心跳 发生异常！%s %s" % (describe, e)
            self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return False
        except Exception as e:
            self.log_text = "日志服务发送 心跳 发生异常！%s %s" % (describe, e)
            self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return False

    def SendData(self, sock, describe, msg_data):
        try:
            msg_type = "8" # NW_MSG_TYPE_USER_DATA
            msg_code = "2" # NW_MSG_CODE_JSON
            msg_json = json.dumps(msg_data)
            msg_size = "%6x" % len(msg_json)
            msg_send = msg_type + msg_code + msg_size + msg_json
            sock.send(msg_send)
            return True
        except socket.error as e:
            self.log_text = "日志服务发送 数据 发生异常！%s %s" % (describe, e)
            self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return False
        except Exception as e:
            self.log_text = "日志服务发送 数据 发生异常！%s %s" % (describe, e)
            self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return False

    def SendNoneAll(self):
        self.connect_lock.acquire()
        try:
            for describe, connect in self.connect_dict.items():
                if connect.available == True:
                    if self.SendNone(connect.socket, describe) == False:
                        connect.available = False
                        connect.socket.close()
                        self.log_text = "日志服务 心跳 主动断开连接！%s" % describe
                        self.SendMessage("W", 3, self.log_cate, self.log_text, "S")
        except Exception as e:
            self.log_text = "日志服务批量发送 心跳 发生异常！%s" % e
            self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        self.connect_lock.release()

    def SendDataAll(self, msg_data):
        self.connect_lock.acquire()
        try:
            for describe, connect in self.connect_dict.items():
                if connect.available == True:
                    if self.SendData(connect.socket, describe, msg_data) == False:
                        connect.available = False
                        connect.socket.close()
                        self.log_text = "日志服务 数据 主动断开连接！%s" % describe
                        self.SendMessage("W", 3, self.log_cate, self.log_text, "S")
        except Exception as e:
            self.log_text = "日志服务批量发送 数据 发生异常！%s" % e
            self.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        self.connect_lock.release()

####################################################################################################

def TestFunc_01(logger, locker, flag):
    for i in range(10000):
        #locker.acquire()
        log_text = "%d 金属类行情 距上次数据更新时间已超过 %s 秒！" % (flag, datetime.datetime.now().strftime("%H:%M:%S.%f"))
        logger.SendMessage("D", 0, "test", log_text, "")
        #locker.release()

def TestFunc_02(locker, flag):
    for i in range(10000):
        #locker.acquire()
        print("%d 金属类行情 距上次数据更新时间已超过 %s 秒！" % (flag, datetime.datetime.now().strftime("%H:%M:%S.%f")))
        #locker.release()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 测试显示，在开启系统时间优化为 0.5 毫秒以后，Logger 输出时间精度在 1 到 2 毫秒，一毫秒平均输出日志 15 条，即每秒约 1.5 万条
    #logger = Logger()
    #for i in range(10000):
    #    log_text = "金属类行情 距上次数据更新时间已超过 %s 秒！" % datetime.datetime.now().strftime("%H:%M:%S.%f")
    #    logger.SendMessage("D", 0, "test", log_text, "")

    # 测试显示，平均每毫秒可打印 35 条左右，从打印内容所含时间看似乎可以 1 毫秒打印 90 到 110 条
    #time1 = datetime.datetime.now()
    #for i in range(10000):
    #    print("金属类行情 距上次数据更新时间已超过 %s 秒！" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
    #time2 = datetime.datetime.now()
    #print(time2 - time1)

    # 测试显示，两个线程下，无锁时一毫秒平均输出日志 12.545 条，有锁时一毫秒平均输出日志 14.326 条，五线程无锁一毫秒平均输出日志 11.797 条，有锁时一毫秒平均输出日志 15.035 条
    logger = Logger()
    locker = threading.Lock()
    thread_1 = threading.Thread(target = TestFunc_01, args = (logger, locker, 1))
    thread_2 = threading.Thread(target = TestFunc_01, args = (logger, locker, 2))
    thread_3 = threading.Thread(target = TestFunc_01, args = (logger, locker, 3))
    thread_4 = threading.Thread(target = TestFunc_01, args = (logger, locker, 4))
    thread_5 = threading.Thread(target = TestFunc_01, args = (logger, locker, 5))

    # 测试显示，五线程下，无锁时一毫秒平均打印 44 条左右，有锁时一毫秒平均打印 50 条左右
    #locker = threading.Lock()
    #thread_1 = threading.Thread(target = TestFunc_02, args = (locker, 1))
    #thread_2 = threading.Thread(target = TestFunc_02, args = (locker, 2))
    #thread_3 = threading.Thread(target = TestFunc_02, args = (locker, 3))
    #thread_4 = threading.Thread(target = TestFunc_02, args = (locker, 4))
    #thread_5 = threading.Thread(target = TestFunc_02, args = (locker, 5))
    
    time1 = datetime.datetime.now()
    thread_1.start()
    thread_2.start()
    thread_3.start()
    thread_4.start()
    thread_5.start()
    thread_1.join()
    thread_2.join()
    thread_3.join()
    thread_4.join()
    thread_5.join()
    time2 = datetime.datetime.now()
    print(time2 - time1)
    
    sys.exit(app.exec_())
