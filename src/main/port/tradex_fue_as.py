
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
import copy
import socket
import sqlite3
import threading
from datetime import datetime, timedelta

from PyQt5.QtCore import QTimer

import config
import define
import logger
import center

class TradeX_Fue_As():
    class Order(object):
        def __init__(self, **kwargs):
            self.order_id = "" # 委托编号
            self.order_sys_id = "" # 报单编号
            self.instrument = kwargs.get("instrument", "") # 合约代码
            self.exchange = kwargs.get("exchange", "") # 交易所
            self.price = kwargs.get("price", 0.0) # 委托价格
            self.amount = kwargs.get("amount", 0) # 委托数量
            self.entr_type = kwargs.get("entr_type", 0) # 单个委托方式，1：限价，2：市价 #组合委托方式，郑商所：8 跨期套利，9 跨品种套利，大商所：2 套利订单，7 互换订单
            self.exch_side = kwargs.get("exch_side", 0) # 交易类型，1：买入，2：卖出，3：金属延期交割收货，4：金属延期交割交货，5：金属延期中立收货，6：金属延期中立交货
            self.offset = kwargs.get("offset", 0) # 开平方向，1：开仓，2：平仓，3：强平，4：平今，5：平昨，6：强减，7：本地强平
            self.hedge = kwargs.get("hedge", 0) # 投机套保，1：投机，2：套保，3：套利
            self.fill_qty = 0 # 成交数量
            # 0：尚未申报，1：正在申报，2：非法委托，3：已报未成，4：部分成交，5：全部成交，6：等待撤单，
            # 7：部成部撤，8：全部撤单，9：撤单未成，10：等待修改，11：尚未触发，12：已经触发，13：自动挂起，14：未知状态
            self.status = 0 # 委托状态
            self.status_msg = "" # 状态信息
            self.combin_flag = 0 # 在 PlaceCombinOrder() 中置为 1

        def ToString(self):
            return "order_id：%s, " % self.order_id + \
                   "order_sys_id：%s, " % self.order_sys_id + \
                   "instrument：%s, " % self.instrument + \
                   "exchange：%s, " % self.exchange + \
                   "price：%f, " % self.price + \
                   "amount：%d, " % self.amount + \
                   "entr_type：%d, " % self.entr_type + \
                   "exch_side：%d, " % self.exch_side + \
                   "offset：%d, " % self.offset + \
                   "hedge：%d, " % self.hedge + \
                   "fill_qty：%d, " % self.fill_qty + \
                   "status：%d, " % self.status + \
                   "status_msg：%s, " % self.status_msg + \
                   "combin_flag：%d" % self.combin_flag

    class Trans(object):
        def __init__(self):
            self.order_id = "" # 委托编号
            self.trans_id = "" # 成交编号
            self.instrument = "" # 合约代码
            self.exchange = "" # 交易所
            self.exch_side = 0 # 交易类型，1：买入，2：卖出
            self.fill_qty = 0 # 成交数量
            self.fill_price = 0.0 # 成交价格
            self.fill_time = "" # 成交时间

        def ToString(self):
            return "order_id：%s, " % self.order_id + \
                   "trans_id：%s, " % self.trans_id + \
                   "instrument：%s, " % self.instrument + \
                   "exchange：%s, " % self.exchange + \
                   "exch_side：%d, " % self.exch_side + \
                   "fill_qty：%d, " % self.fill_qty + \
                   "fill_price：%f, " % self.fill_price + \
                   "fill_time：%s" % self.fill_time

    class Capital(object):
        def __init__(self):
            self.account = "" # 资金账号
            self.currency = "" # 币种
            self.available = 0.0 # 可用资金
            self.profit = 0.0 # 平仓盈亏
            self.float_profit = 0.0 # 持仓盈亏
            self.margin = 0.0 # 保证金总额
            self.frozen_margin = 0.0 # 冻结保证金
            self.fee = 0.0 # 手续费
            self.frozen_fee = 0.0 # 冻结手续费

        def ToString(self):
            return "account：%s, " % self.account + \
                   "currency：%s, " % self.currency + \
                   "available：%f, " % self.available + \
                   "profit：%f, " % self.profit + \
                   "float_profit：%f, " % self.float_profit + \
                   "margin：%f, " % self.margin + \
                   "frozen_margin：%f, " % self.frozen_margin + \
                   "fee：%f, " % self.fee + \
                   "frozen_fee：%f" % self.frozen_fee

    class Position(object):
        def __init__(self):
            self.instrument = "" # 合约代码
            self.exch_side = 0 # 交易类型
            self.position = 0 # 总持仓
            self.tod_position = 0 # 今日持仓
            self.pre_position = 0 # 上日持仓
            self.open_volume = 0 # 开仓量
            self.close_volume = 0 # 平仓量

        def ToString(self):
            return "instrument：%s, " % self.instrument + \
                   "exch_side：%d, " % self.exch_side + \
                   "position：%d, " % self.position + \
                   "tod_position：%d, " % self.tod_position + \
                   "pre_position：%d, " % self.pre_position + \
                   "open_volume：%d, " % self.open_volume + \
                   "close_volume：%d" % self.close_volume

    class PositionDetail(object):
        def __init__(self):
            self.instrument = "" # 合约代码
            self.exch_side = 0 # 交易类型
            self.volume = 0 # 数量
            self.open_price = 0.0 # 开仓价格 # 接口 PGT 为 持仓均价
            self.exchange = "" # 交易所
            self.margin = 0.0 # 投资者保证金
            self.exch_margin = 0.0 # 交易所保证金 # 接口 PGT 为 昨持仓量

        def ToString(self):
            return "instrument：%s, " % self.instrument + \
                   "exch_side：%d, " % self.exch_side + \
                   "volume：%d, " % self.volume + \
                   "open_price：%f, " % self.open_price + \
                   "exchange：%s, " % self.exchange + \
                   "margin：%f, " % self.margin + \
                   "exch_margin：%f" % self.exch_margin

    class Instrument(object):
        def __init__(self):
            self.instrument = "" # 合约代码
            self.exchange = "" # 交易所
            self.delivery_y = 0 # 交割年份
            self.delivery_m = 0 # 交割月份
            self.long_margin = 0.0 # 多头保证金率
            self.short_margin = 0.0 # 空头保证金率

        def ToString(self):
            return "instrument：%s, " % self.instrument + \
                   "exchange：%s, " % self.exchange + \
                   "delivery_y：%d, " % self.delivery_y + \
                   "delivery_m：%d, " % self.delivery_m + \
                   "long_margin：%f, " % self.long_margin + \
                   "short_margin：%f" % self.short_margin

    class RiskInfo(object):
        def __init__(self):
            self.seq_no = 0 # 序列号
            self.seq_series = 0 # 序列系列号
            self.content = "" # 消息正文

        def ToString(self):
            return "seq_no：%d, " % self.seq_no + \
                   "seq_series：%d, " % self.seq_series + \
                   "content：%s" % self.content

    class TaskItem(object):
        def __init__(self):
            self.task_id = 0 # 任务标识
            self.strategy = "" # 策略标识
            self.function = 0 # 功能编号
            self.status = 0 # 任务状态
            self.messages = [] # 任务信息
            self.order = None # 单个合约
            self.order_replies = [] # 单个合约委托回报
            self.trans_replies = [] # 单个合约成交回报
            self.query_results = [] # 查询结果数据
            self.event_task_finish = threading.Event()
            self.event_recv_answer = threading.Event() # 用于标记已收到报单应答或报单回报或成交回报，保证获得 order_id 用于撤单
            # 接口 CTP 和 JQG 等一般延迟都很低，但是遇到过CTP下郑商所报单回报近三秒的，导致撤单时CTP报找不到交易所委托号

        def ToString(self):
            return "task_id：%d, " % self.task_id + \
                   "strategy：%s, " % self.strategy + \
                   "function：%d, " % self.function + \
                   "status：%d, " % self.status + \
                   "messages：%s" % self.messages[-1] # 只打印最后一条

####################################################################################################

    class TradeInfo(object):
        def __init__(self, db_name):
            self.log_text = ""
            self.log_cate = "TradeInfo"
            self.logger = logger.Logger()
            self.id = db_name # 数据库名称
            self.db = None # 数据库对象
            self.cu = None # 数据库游标
            self.tb_name_place = "tb_place"
            self.tb_name_order = "tb_order"
            self.tb_name_trans = "tb_trans"
            self.tb_data_place = []
            self.tb_data_order = []
            self.tb_data_trans = []
            self.tb_lock_place = threading.Lock()
            self.tb_lock_order = threading.Lock()
            self.tb_lock_trans = threading.Lock()
            self.db_init_time = 600
            self.db_init_flag = False # 目前 23:00 还原
            
            self.InitDataBase()
            
            self.timer = QTimer()
            self.timer.timeout.connect(self.TrySaveData)
            self.timer.start(5000)

        def __del__(self):
            self.timer.Stop()
            del self.timer
            self.TrySaveData() # 最后再调用一次吧
            if self.cu != None:
                self.cu.close()
                self.cu = None
            if self.db != None:
                self.db.close()
                self.db = None

        def InitDataBase(self):
            if self.cu != None:
                self.cu.close()
                self.cu = None
            if self.db != None:
                self.db.close()
                self.db = None
            
            self.db = sqlite3.connect("../data/%s_%s.db" % (self.id, datetime.now().strftime("%Y%m%d")))
            self.db.text_factory = str # 支持中文字符
            self.cu = self.db.cursor()
            
            sql_check_table_place = "select count(*) from sqlite_master where type = 'table' and name = '%s'" % self.tb_name_place
            sql_check_table_order = "select count(*) from sqlite_master where type = 'table' and name = '%s'" % self.tb_name_order
            sql_check_table_trans = "select count(*) from sqlite_master where type = 'table' and name = '%s'" % self.tb_name_trans
            
            sql_create_table_place = "create table %s ( id integer primary key not null, \
                                                        date integer, \
                                                        time integer, \
                                                        task_id integer, \
                                                        strategy varchar(64), \
                                                        order_id varchar(64), \
                                                        order_sys_id varchar(64), \
                                                        instrument varchar(64), \
                                                        price double, \
                                                        amount integer, \
                                                        entr_type integer, \
                                                        exch_side integer, \
                                                        offset integer, \
                                                        hedge integer, \
                                                        combin_flag integer )" % self.tb_name_place # 表存续期间自增：INTEGER PRIMARY KEY AUTOINCREMENT
            sql_create_table_order = "create table %s ( id integer primary key not null, \
                                                        date integer, \
                                                        time integer, \
                                                        task_id integer, \
                                                        strategy varchar(64), \
                                                        order_id varchar(64), \
                                                        order_sys_id varchar(64), \
                                                        instrument varchar(64), \
                                                        exchange varchar(64), \
                                                        exch_side integer, \
                                                        fill_qty integer, \
                                                        status integer, \
                                                        status_msg text )" % self.tb_name_order # 表存续期间自增：INTEGER PRIMARY KEY AUTOINCREMENT
            sql_create_table_trans = "create table %s ( id integer primary key not null, \
                                                        date integer, \
                                                        time integer, \
                                                        task_id integer, \
                                                        strategy varchar(64), \
                                                        order_id varchar(64), \
                                                        trans_id varchar(64), \
                                                        instrument varchar(64), \
                                                        exchange varchar(64), \
                                                        exch_side integer, \
                                                        fill_qty integer, \
                                                        fill_price double, \
                                                        fill_time varchar(64) )" % self.tb_name_trans # 表存续期间自增：INTEGER PRIMARY KEY AUTOINCREMENT
            
            try:
                self.cu.execute(sql_check_table_place)
                if self.cu.fetchone()[0] == 0:
                    self.cu.execute(sql_create_table_place)
                self.db.commit()
            except sqlite3.Error as e:
                self.log_text = "创建 %s 数据表 %s 异常！%s" % (self.id, self.tb_name_place, e.args[0])
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            
            try:
                self.cu.execute(sql_check_table_order)
                if self.cu.fetchone()[0] == 0:
                    self.cu.execute(sql_create_table_order)
                self.db.commit()
            except sqlite3.Error as e:
                self.log_text = "创建 %s 数据表 %s 异常！%s" % (self.id, self.tb_name_order, e.args[0])
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            
            try:
                self.cu.execute(sql_check_table_trans)
                if self.cu.fetchone()[0] == 0:
                    self.cu.execute(sql_create_table_trans)
                self.db.commit()
            except sqlite3.Error as e:
                self.log_text = "创建 %s 数据表 %s 异常！%s" % (self.id, self.tb_name_trans, e.args[0])
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

        def AddTbData_Place(self, task_id, strategy, order): # 委托下单
            data = [
                    int(datetime.now().strftime("%Y%m%d")), # 当前日期
                    int(datetime.now().strftime("%H%M%S%f")), # 当前时间
                    task_id, # 任务编号
                    strategy, # 策略名称
                    order.order_id, # 委托编号 # 可以区分是下单还是撤单
                    order.order_sys_id, # 报单编号 # 可以区分是下单还是撤单
                    order.instrument, # 合约代码
                    order.price, # 委托价格
                    order.amount, # 委托数量
                    order.entr_type, # 单个委托方式
                    order.exch_side, # 交易类型
                    order.offset, # 开平方向
                    order.hedge, # 投机套保
                    order.combin_flag # 组合标识
                   ]
            self.tb_lock_place.acquire()
            self.tb_data_place.append(data)
            self.tb_lock_place.release()

        def AddTbData_Order(self, task_id, strategy, order): # 报单回报
            data = [
                    int(datetime.now().strftime("%Y%m%d")), # 当前日期
                    int(datetime.now().strftime("%H%M%S%f")), # 当前时间
                    task_id, # 任务编号
                    strategy, # 策略名称
                    order.order_id, # 委托编号
                    order.order_sys_id, # 报单编号
                    order.instrument, # 合约代码
                    order.exchange, # 交易所
                    order.exch_side, # 交易类型
                    order.fill_qty, # 成交数量
                    order.status, # 报单状态
                    order.status_msg # 状态信息
                   ]
            self.tb_lock_order.acquire()
            self.tb_data_order.append(data)
            self.tb_lock_order.release()

        def AddTbData_Trans(self, task_id, strategy, trans): # 成交回报
            data = [
                    int(datetime.now().strftime("%Y%m%d")), # 当前日期
                    int(datetime.now().strftime("%H%M%S%f")), # 当前时间
                    task_id, # 任务编号
                    strategy, # 策略名称
                    trans.order_id, # 委托编号
                    trans.trans_id, # 成交编号
                    trans.instrument, # 合约代码
                    trans.exchange, # 交易所
                    trans.exch_side, # 交易类型
                    trans.fill_qty, # 成交数量
                    trans.fill_price, # 成交价格
                    trans.fill_time # 成交时间
                   ]
            self.tb_lock_trans.acquire()
            self.tb_data_trans.append(data)
            self.tb_lock_trans.release()

        def TrySaveData(self): # 定时保存
            now_time = int(datetime.now().strftime("%H%M"))
            if now_time == self.db_init_time and self.db_init_flag == False:
                self.db_init_flag = True
                self.InitDataBase()
            if now_time == 2300:
                self.db_init_flag = False
            
            if self.db != None and self.cu != None:
                self.PutTbData_Place()
                self.PutTbData_Order()
                self.PutTbData_Trans()

        def PutTbData_Place(self): # 委托下单
            if len(self.tb_data_place) > 0:
                self.tb_lock_place.acquire()
                tb_data = self.tb_data_place
                self.tb_data_place = []
                self.tb_lock_place.release()
                self.cu.executemany("insert into %s values (null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" % self.tb_name_place, tb_data)
                self.db.commit()

        def PutTbData_Order(self): # 报单回报
            if len(self.tb_data_order) > 0:
                self.tb_lock_order.acquire()
                tb_data = self.tb_data_order
                self.tb_data_order = []
                self.tb_lock_order.release()
                self.cu.executemany("insert into %s values (null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" % self.tb_name_order, tb_data)
                self.db.commit()

        def PutTbData_Trans(self): # 成交回报
            if len(self.tb_data_trans) > 0:
                self.tb_lock_trans.acquire()
                tb_data = self.tb_data_trans
                self.tb_data_trans = []
                self.tb_lock_trans.release()
                self.cu.executemany("insert into %s values (null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" % self.tb_name_trans, tb_data)
                self.db.commit()

####################################################################################################

    def __init__(self, parent, trade_name, trade_flag, trade_save, address, port, username, password, asset_account, login_time_out):
        self.log_text = ""
        self.log_cate = "TradeX_Fue_As"
        self.config = config.Config()
        self.logger = logger.Logger()
        self.parent = parent
        self.trade_name = trade_name
        self.trade_flag = trade_flag
        self.trade_save = trade_save
        self.address = address
        self.port = port
        self.username = username
        self.password = password
        self.asset_account = asset_account
        self.login_time_out = login_time_out
        self.sock = None
        self.session = 0
        self.task_id = 0
        self.started = False
        self.userstop = False # 防止用户退出时交易服务重连线程执行操作
        self.connected = False
        self.userlogin = False
        self.subscibed = False
        self.heart_check_time = datetime.now()
        self.heart_check_span = timedelta(seconds = 10 * 3)
        self.RegReplyMsgHandleFunc()
        
        self.task_dict = {}
        self.task_id_lock = threading.Lock()
        self.strategy_dict = center.Center().data.strategies
        
        self.show_debug_info = self.config.cfg_main.stra_debug_info # 为 1 或 0
        
        self.trade_info = None
        if self.trade_save == 1: # 需要将交易记录到本地数据库
            self.trade_info = self.TradeInfo("%s_%s" % (self.log_cate, self.trade_flag))

    def __del__(self):
        self.started = False

    def NewTaskItem(self, strategy, function):
        self.task_id_lock.acquire()
        self.task_id += 1
        task_id = copy.deepcopy(self.task_id) # copy
        self.task_id_lock.release()
        task_item = self.TaskItem()
        task_item.task_id = task_id # 任务标识
        task_item.strategy = strategy # 策略标识
        task_item.function = function # 功能编号
        task_item.status = define.TASK_STATUS_EXEC # 任务状态
        task_item.messages.append("开始执行任务 ...") # 任务信息
        #task_item.order = None # 单个合约
        #task_item.order_replies = [] # 单个合约委托回报
        #task_item.trans_replies = [] # 单个合约成交回报
        #task_item.query_results = [] # 查询结果数据
        return task_item

    def RegReplyMsgHandleFunc(self):
        self.reply_msg_handle_func_sys = {}
        self.reply_msg_handle_func_sys[define.trade_userlogin_f_func] = self.OnUserLogIn
        self.reply_msg_handle_func_sys[define.trade_userlogout_f_func] = self.OnUserLogOut
        self.reply_msg_handle_func_sys[define.trade_subscibe_f_func] = self.OnSubscibe
        self.reply_msg_handle_func_sys[define.trade_unsubscibe_f_func] = self.OnUnsubscibe
        self.reply_msg_handle_func_usr = {}
        self.reply_msg_handle_func_usr[define.trade_placeorder_f_func] = self.OnPlaceOrder
        self.reply_msg_handle_func_usr[define.trade_cancelorder_f_func] = self.OnCancelOrder
        self.reply_msg_handle_func_usr[define.trade_placecombinorder_f_func] = self.OnPlaceCombinOrder
        self.reply_msg_handle_func_usr[define.trade_querycapital_f_func] = self.OnQueryCapital
        self.reply_msg_handle_func_usr[define.trade_queryposition_f_func] = self.OnQueryPosition
        self.reply_msg_handle_func_usr[define.trade_queryorder_f_func] = self.OnQueryOrder
        self.reply_msg_handle_func_usr[define.trade_querytrans_f_func] = self.OnQueryTrans
        self.reply_msg_handle_func_usr[define.trade_queryinstrument_f_func] = self.OnQueryInstrument
        self.reply_msg_handle_func_usr[define.trade_querypositiondetail_f_func] = self.OnQueryPositionDetail
        self.reply_msg_handle_func_usr[define.trade_orderreply_f_func] = self.OnOrderReply
        self.reply_msg_handle_func_usr[define.trade_transreply_f_func] = self.OnTransReply
        self.reply_msg_handle_func_usr[define.trade_riskinform_f_func] = self.OnRiskInform

    def Start(self):
        self.log_text = "%s：用户 启动 交易服务..." % self.trade_name
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        if self.started == False:
            if self.DoConnect(self.address, self.port):
                self.started = True
                self.userstop = False #
                self.thread_recv = threading.Thread(target = self.Thread_Recv)
                self.thread_recv.start()
                time.sleep(1)
                self.thread_time = threading.Thread(target = self.Thread_Time)
                self.thread_time.start()
            else:
                self.log_text = "%s：启动时连接交易服务器失败！" % self.trade_name
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def IsTraderReady(self):
        return self.started == True and self.connected == True and self.userlogin == True and self.subscibed == True

    def Thread_Recv(self):
        self.log_text = "%s：启动交易数据接收线程..." % self.trade_name
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        while self.started:
            if self.connected == True:
                if self.RecvData() == False:
                    self.UnConnect()
            else:
                time.sleep(1) # 等待重连完成
        if self.connected == True:
            self.UnConnect()
        self.log_text = "%s：交易数据接收线程退出！" % self.trade_name
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def Thread_Time(self):
        self.log_text = "%s：启动交易服务重连线程..." % self.trade_name
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        while self.started:
            if self.connected == False and self.userstop == False:
                if self.DoConnect(self.address, self.port):
                    time.sleep(1)
                else:
                    self.log_text = "%s：重连时连接交易服务器失败！" % self.trade_name
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            if self.connected == True and datetime.now() > self.heart_check_time + self.heart_check_span:
                try:
                    self.sock.shutdown(socket.SHUT_RDWR) # 网络物理连接断开时直接 close 的话 recv 不会退出阻塞的
                except socket.error as e:
                    self.log_text = "%s：主动关闭 socket 异常！%s" % (self.trade_name, e)
                    self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
                self.UnConnect()
                self.log_text = "%s：心跳检测超时连接已经断开！" % self.trade_name
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            if self.connected == True and self.userlogin == False and self.userstop == False:
                self.UserLogIn(self.username, self.password)
                wait_count = 0
                while self.userlogin == False and wait_count < self.login_time_out:
                    time.sleep(1)
                    wait_count += 1
                if self.userlogin == False:
                    self.log_text = "%s：重连时登录交易柜台超时！" % self.trade_name
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            if self.connected == True and self.userlogin == True and self.subscibed == False and self.userstop == False:
                self.Subscibe(self.session, self.password)
                wait_count = 0
                while self.subscibed == False and wait_count < self.login_time_out:
                    time.sleep(1)
                    wait_count += 1
                if self.subscibed == False:
                    self.log_text = "%s：重连时订阅交易柜台超时！" % self.trade_name
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            time.sleep(5)
        self.log_text = "%s：交易服务重连线程退出！" % self.trade_name
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def Stop(self):
        self.log_text = "%s：用户 停止 交易服务..." % self.trade_name
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        self.userstop = True #
        if self.started == True:
            self.Unsubscibe(self.session)
            time.sleep(1)
            self.UserLogOut(self.session)
            time.sleep(1)
            self.started = False # 通过心跳机制来中断 RecvData 阻塞进而退出交易数据接收线程

    def DoConnect(self, address, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            self.log_text = "%s：创建 socket 失败！%s %d %s" % (self.trade_name, address, port, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            time.sleep(1)
            return False
        try:
            self.sock.settimeout(3) # 设置连接超时
            self.sock.connect((address, port))
            self.sock.settimeout(None) # 需要这样设置，回到阻塞模式，不然数据读写会变非阻塞
        except socket.error as e:
            self.log_text = "%s：建立 connect 失败！%s %d %s" % (self.trade_name, address, port, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            time.sleep(1)
            return False
        self.connected = True
        self.heart_check_time = datetime.now()
        return True

    def UnConnect(self):
        self.subscibed = False
        self.userlogin = False
        self.connected = False
        if self.sock != None:
            self.sock.close()

    def OnReplyMsg(self, ret_func, msg_ans):
        try:
            if ret_func in self.reply_msg_handle_func_sys.keys():
                self.OnReplyMsg_Sys(ret_func, msg_ans)
            else:
                self.OnReplyMsg_Usr(ret_func, msg_ans)
        except Exception as e:
            self.log_text = "%s：处理应答消息发生异常！%s" % (self.trade_name, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def OnReplyMsg_Sys(self, ret_func, msg_ans):
        try:
            ret_info = msg_ans["ret_info"]
            ret_code = int(msg_ans["ret_code"])
            if ret_func in self.reply_msg_handle_func_sys.keys():
                self.reply_msg_handle_func_sys[ret_func](ret_code, ret_info, msg_ans)
            else:
                self.log_text = "%s：处理 系统 应答消息类型未知！%d" % (self.trade_name, ret_func)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            if self.parent != None: # 发给上层更新用户界面信息
                self.parent.OnTradeReplyMsg(self.trade_name, ret_func, ret_code, ret_info)
        except Exception as e:
            self.log_text = "%s：处理 系统 应答消息发生异常！%s" % (self.trade_name, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def OnReplyMsg_Usr(self, ret_func, msg_ans):
        try:
            if ret_func in self.reply_msg_handle_func_usr.keys():
                self.reply_msg_handle_func_usr[ret_func](ret_func, msg_ans)
            else:
                self.log_text = "%s：处理 用户 应答消息类型未知！%d" % (self.trade_name, ret_func)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        except Exception as e:
            self.log_text = "%s：处理 用户 应答消息发生异常！%s" % (self.trade_name, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def SendData(self, msg_data):
        try:
            msg_type = "8" # NW_MSG_TYPE_USER_DATA
            msg_code = "2" # NW_MSG_CODE_JSON
            msg_json = json.dumps(msg_data)
            msg_size = "%6x" % len(msg_json)
            msg_send = msg_type + msg_code + msg_size + msg_json
            self.sock.sendall(bytes(msg_send, encoding = "gbk"))
            return True
        except socket.error as e:
            self.log_text = "%s：发送数据发生异常！%s %d %s" % (self.trade_name, self.address, self.port, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return False
        except Exception as e:
            self.log_text = "%s：发送数据发生异常！%s %d %s" % (self.trade_name, self.address, self.port, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return False

    def RecvData(self):
        try:
            msg_type = "0"
            msg_code = "0"
            tmp_size = 0
            msg_head = bytearray(self.sock.recv(8))
            while len(msg_head) < 8:
                msg_head.extend(self.sock.recv(8 - len(msg_head)))
            msg_head = msg_head.decode()
            if msg_head[0] == "8": # NW_MSG_TYPE_USER_DATA # 用户数据处理消息
                msg_type = msg_head[0]
                msg_code = msg_head[1]
                tmp_size = msg_head[2:]
                msg_size = int(tmp_size, 16)
                msg_recv = bytearray(self.sock.recv(msg_size))
                while len(msg_recv) < msg_size:
                    msg_recv.extend(self.sock.recv(msg_size - len(msg_recv)))
                if msg_code == "2": # NW_MSG_CODE_JSON # 应答消息
                    msg_data = json.loads(msg_recv.decode("gbk")) # 含中文
                    self.OnReplyMsg(int(msg_data["ret_func"]), msg_data)
            elif msg_head[0] == "0": # NW_MSG_TYPE_HEART_CHECK # 连接心跳检测消息
                self.heart_check_time = datetime.now()
            return True
        except socket.error as e:
            self.log_text = "%s：接收数据发生异常！%s %d %s" % (self.trade_name, self.address, self.port, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return False
        except Exception as e:
            self.log_text = "%s：接收数据发生异常！%s %d %s" % (self.trade_name, self.address, self.port, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return False

    def SendTraderEvent(self, ret_func, task_item):
        #print(ret_func, task_item.ToString())
        try:
            # 期货回报类
            if ret_func == define.trade_orderreply_f_func: # 期货报单回报，接口 CTP、JQG 报单回报会有多个
                order_reply = task_item.order_replies[-1] # 取最新一个
                if task_item.order.order_id == "":
                    task_item.order.order_id = order_reply.order_id # 委托编号
                if task_item.order.order_sys_id == "":
                    task_item.order.order_sys_id = order_reply.order_sys_id # 报单编号
                if task_item.order.combin_flag == 0: # 单个合约委托
                    if task_item.order.fill_qty < order_reply.fill_qty:
                        task_item.order.fill_qty = order_reply.fill_qty # 成交数量
                if task_item.order.combin_flag == 1: # 组合合约委托
                    if task_item.order.fill_qty < order_reply.fill_qty * 2:
                        task_item.order.fill_qty = order_reply.fill_qty * 2 # 成交数量
                task_item.order.status = order_reply.status # 委托状态
                # 0：尚未申报，1：正在申报，2：非法委托，3：已报未成，4：部分成交，
                # 5：全部成交，6：等待撤单，7：部成部撤，8：全部撤单，9：撤单未成，
                # 10：等待修改，11：尚未触发，12：已经触发，13：自动挂起，14：未知状态
                # 委托交易结束：非法委托、全部成交、部成部撤、全部撤单
                if order_reply.status == 2 or order_reply.status == 5 or order_reply.status == 7 or order_reply.status == 8:
                    if order_reply.status == 8 and task_item.order.order_sys_id == "": # 单子没入交易队列就已被撤单说明报单异常，包括交易所限制开空单等
                        task_item.status = define.TASK_STATUS_FAIL
                    task_item.event_task_finish.set()
                if task_item.order.order_sys_id != "":
                    task_item.event_recv_answer.set() # 需要用 order_sys_id 才能说明可以从交易所撤单
            if ret_func == define.trade_transreply_f_func: # 期货成交回报，接口 CTP、JQG 成交回报会有多个
                trans_reply = task_item.trans_replies[-1] # 取最新一个
                if task_item.order.order_id == "":
                    task_item.order.order_id = trans_reply.order_id # 委托编号
                if task_item.order.order_sys_id != "":
                    task_item.event_recv_answer.set() # 需要用 order_sys_id 才能说明可以从交易所撤单
                # 接口 CTP、JQG 报单回报和成交回报均有多个，且成交一定数量时成交回报一般会在报单回报之后，故以下方式不适用，采用报单回报赋值
                #task_item.order.fill_qty += trans_reply.fill_qty # 本次成交数量
                #if task_item.order.combin_flag == 0: # 单个合约委托
                #    if task_item.order.fill_qty >= task_item.order.amount: # 全部成交
                #        task_item.order.status = 5 # 全部成交
                #        task_item.event_task_finish.set()
                #if task_item.order.combin_flag == 1: # 组合合约委托
                #    if task_item.order.fill_qty >= task_item.order.amount * 2: # 全部成交
                #        task_item.order.status = 5 # 全部成交
                #        task_item.event_task_finish.set()
            
            # 期货委托类
            if ret_func == define.trade_placeorder_f_func: # 期货单个/组合合约委托下单 # 下单成功或失败都会收到
                if task_item.status == define.TASK_STATUS_FAIL: # 这里只关注失败的，成功的根据委托回报处理
                    task_item.event_task_finish.set()
                    task_item.event_recv_answer.set() # 因为需要 order_sys_id 所以这里只在下单失败时才设置，下单成功的需要继续等待交易所报单回报获得 order_sys_id 后才设置
            if ret_func == define.trade_cancelorder_f_func: # 期货单个/组合合约委托撤单 #撤单成功或失败都会收到
                if task_item.status == define.TASK_STATUS_FAIL: # 这里只关注失败的，成功的根据委托回报处理
                    task_item.event_task_finish.set()
            
            # 期货查询类
            if ret_func == define.trade_querycapital_f_func: # 期货查询客户资金
                task_item.event_task_finish.set()
            if ret_func == define.trade_queryposition_f_func: # 期货查询客户持仓
                task_item.event_task_finish.set()
            if ret_func == define.trade_queryorder_f_func: # 期货查询客户当日委托
                task_item.event_task_finish.set()
            if ret_func == define.trade_querytrans_f_func: # 期货查询客户当日成交
                task_item.event_task_finish.set()
        except Exception as e:
            self.log_text = "%s：处理事件消息 %d 发生异常！%s" % (self.trade_name, ret_func, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        
        if task_item.strategy in self.strategy_dict.keys():
            self.strategy_dict[task_item.strategy].instance.OnTraderEvent(self.trade_name, ret_func, task_item)

####################################################################################################

    def UserLogIn(self, username, password):
        msg_req = {"function":define.trade_userlogin_f_func, "task_id":0, "username":username, "password":password}
        if self.SendData(msg_req) == False:
            self.UnConnect()

    def OnUserLogIn(self, ret_code, ret_info, msg_ans):
        if ret_code == 0:
            self.session = int(msg_ans["ret_data"][0]["session"])
            self.log_text = "%s：交易登录成功。%d %s" % (self.trade_name, self.session, ret_info)
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            self.userlogin = True
        else:
            self.log_text = "%s：交易登录失败！%d %s" % (self.trade_name, ret_code, ret_info)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def UserLogOut(self, session):
        msg_req = {"function":define.trade_userlogout_f_func, "session":session, "task_id":0}
        if self.SendData(msg_req) == False:
            self.UnConnect()

    def OnUserLogOut(self, ret_code, ret_info, msg_ans):
        if ret_code == 0:
            self.log_text = "%s：交易登出成功。%d %s" % (self.trade_name, self.session, ret_info)
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            self.userlogin = False
        else:
            self.log_text = "%s：交易登出失败！%d %s" % (self.trade_name, ret_code, ret_info)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def Subscibe(self, session, password):
        msg_req = {"function":define.trade_subscibe_f_func, "session":session, "task_id":0, "password":password}
        if self.SendData(msg_req) == False:
            self.UnConnect()

    def OnSubscibe(self, ret_code, ret_info, msg_ans):
        if ret_code == 0:
            self.log_text = "%s：消息订阅成功。%d %s" % (self.trade_name, self.session, ret_info)
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            self.subscibed = True
        else:
            self.log_text = "%s：消息订阅失败！%d %s" % (self.trade_name, ret_code, ret_info)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def Unsubscibe(self, session):
        msg_req = {"function":define.trade_unsubscibe_f_func, "session":session, "task_id":0}
        if self.SendData(msg_req) == False:
            self.UnConnect()

    def OnUnsubscibe(self, ret_code, ret_info, msg_ans):
        if ret_code == 0:
            self.log_text = "%s：消息退订成功。%d %s" % (self.trade_name, self.session, ret_info)
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            self.subscibed = False
        else:
            self.log_text = "%s：消息退订失败！%d %s" % (self.trade_name, ret_code, ret_info)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

####################################################################################################

    def PlaceOrder(self, order, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_placeorder_f_func)
        task_item.order = order # 在这里放入原始委托
        if self.trade_info != None:
            self.trade_info.AddTbData_Place(task_item.task_id, strategy, order) #
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_placeorder_f_func, "session":self.session, "task_id":task_item.task_id, "asset_account":self.asset_account, 
                  "instrument":order.instrument, "price":order.price, "amount":order.amount, 
                  "entr_type":order.entr_type, "exch_side":order.exch_side, "offset":order.offset, "hedge":order.hedge}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnPlaceOrder(self, ret_func, msg_ans): # 每次一条
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0: # CTP下不会有委托成功的应答，UTP下也可以不理会
                #print(msg_ans["ret_data"][0]["otc_code"], msg_ans["ret_data"][0]["otc_info"])
                task_item.order.order_id = msg_ans["ret_data"][0]["order_id"] # 委托编号
                #task_item.order.status = define.order_status_f_wait_trans # 委托状态
                #print("下单应答：" + task_item.order.ToString())
                task_item.status = define.TASK_STATUS_OVER # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
            else: # 执行失败
                task_item.order.status = define.order_status_f_error_place # 委托状态
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
                #print("下单失败：" + task_item.messages[-1])
        else:
            self.log_text = "%s：单个下单应答：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def CancelOrder(self, order, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_cancelorder_f_func)
        if self.trade_info != None:
            self.trade_info.AddTbData_Place(task_item.task_id, strategy, order) #
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_cancelorder_f_func, "session":self.session, "task_id":task_item.task_id, "asset_account":self.asset_account, "order_id":order.order_id}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnCancelOrder(self, ret_func, msg_ans): # 每次一条
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0: # CTP下不会有撤单成功的应答，UTP下也可以不理会
                #print(msg_ans["ret_data"][0]["otc_code"], msg_ans["ret_data"][0]["otc_info"])
                #order_id = msg_ans["ret_data"][0]["order_id"] # 委托编号
                #print("撤单应答：" + order_id)
                task_item.status = define.TASK_STATUS_OVER # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
            else: # 执行失败
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
                #print("撤单失败：" + task_item.messages[-1])
        else:
            self.log_text = "%s：撤单应答：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def PlaceCombinOrder(self, order, strategy):
        order.combin_flag = 1 # 标记为组合委托
        task_item = self.NewTaskItem(strategy, define.trade_placecombinorder_f_func)
        task_item.order = order # 在这里放入原始委托
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_placecombinorder_f_func, "session":self.session, "task_id":task_item.task_id, "asset_account":self.asset_account, 
                  "instrument":order.instrument, "exchange":order.exchange, "price":order.price, "amount":order.amount, 
                  "entr_type":order.entr_type, "exch_side":order.exch_side, "offset":order.offset, "hedge":order.hedge}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnPlaceCombinOrder(self, ret_func, msg_ans): # 每次一条
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0: # CTP下不会有委托成功的应答，UTP下也可以不理会
                #print(msg_ans["ret_data"][0]["otc_code"], msg_ans["ret_data"][0]["otc_info"])
                task_item.order.order_id = msg_ans["ret_data"][0]["order_id"] # 委托编号
                #task_item.order.status = define.order_status_f_wait_trans # 委托状态
                #print("下单应答：" + task_item.order.ToString())
                task_item.status = define.TASK_STATUS_OVER # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
            else: # 执行失败
                task_item.order.status = define.order_status_f_error_place # 委托状态
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：组合下单应答：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryCapital(self, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_querycapital_f_func)
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_querycapital_f_func, "session":self.session, "task_id":task_item.task_id}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnQueryCapital(self, ret_func, msg_ans): # 每次一条
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0:
                if msg_ans["ret_last"] == False:
                    #print(msg_ans["ret_data"][0]["otc_code"], msg_ans["ret_data"][0]["otc_info"])
                    capital = self.Capital()
                    capital.account = msg_ans["ret_data"][0]["account"] # 资金账号
                    capital.currency = msg_ans["ret_data"][0]["currency"] # 币种
                    capital.available = float(msg_ans["ret_data"][0]["available"]) # 可用资金
                    capital.profit = float(msg_ans["ret_data"][0]["profit"]) # 平仓盈亏
                    capital.float_profit = float(msg_ans["ret_data"][0]["float_profit"]) # 持仓盈亏
                    capital.margin = float(msg_ans["ret_data"][0]["margin"]) # 保证金总额
                    capital.frozen_margin = float(msg_ans["ret_data"][0]["frozen_margin"]) # 冻结保证金
                    capital.fee = float(msg_ans["ret_data"][0]["fee"]) # 手续费
                    capital.frozen_fee = float(msg_ans["ret_data"][0]["frozen_fee"]) # 冻结手续费
                    #print("客户资金：" + capital.ToString())
                    task_item.query_results.append(capital) # 查询结果数据
                else: # 结束通知
                    task_item.status = define.TASK_STATUS_OVER # 任务状态
                    task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                    self.SendTraderEvent(ret_func, task_item)
            else: # 查询失败
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：客户资金：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryPosition(self, instrument, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_queryposition_f_func)
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_queryposition_f_func, "session":self.session, "task_id":task_item.task_id, "instrument":instrument}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnQueryPosition(self, ret_func, msg_ans): # 每次一条
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0:
                if msg_ans["ret_last"] == False:
                    #print(msg_ans["ret_data"][0]["otc_code"], msg_ans["ret_data"][0]["otc_info"])
                    position = self.Position()
                    position.instrument = msg_ans["ret_data"][0]["instrument"] # 合约代码
                    position.exch_side = int(msg_ans["ret_data"][0]["exch_side"]) # 交易类型
                    position.position = int(msg_ans["ret_data"][0]["position"]) # 总持仓
                    position.tod_position = int(msg_ans["ret_data"][0]["tod_position"]) # 今日持仓
                    position.pre_position = int(msg_ans["ret_data"][0]["pre_position"]) # 上日持仓
                    position.open_volume = int(msg_ans["ret_data"][0]["open_volume"]) # 开仓量
                    position.close_volume = int(msg_ans["ret_data"][0]["close_volume"]) # 平仓量
                    #print("客户持仓：" + position.ToString())
                    task_item.query_results.append(position) # 查询结果数据
                else: # 结束通知
                    task_item.status = define.TASK_STATUS_OVER # 任务状态
                    task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                    self.SendTraderEvent(ret_func, task_item)
            else: # 查询失败
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：客户持仓：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryOrder(self, order_id, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_queryorder_f_func)
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_queryorder_f_func, "session":self.session, "task_id":task_item.task_id, "order_id":order_id}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnQueryOrder(self, ret_func, msg_ans): # 每次一条
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0:
                if msg_ans["ret_last"] == False:
                    #print(msg_ans["ret_data"][0]["otc_code"], msg_ans["ret_data"][0]["otc_info"])
                    order = self.Order()
                    order.order_id = msg_ans["ret_data"][0]["order_id"] # 委托号
                    order.order_sys_id = msg_ans["ret_data"][0]["order_sys_id"] # 报单号
                    order.instrument = msg_ans["ret_data"][0]["instrument"] # 合约代码
                    order.exchange = msg_ans["ret_data"][0]["exchange"] # 交易所
                    order.exch_side = int(msg_ans["ret_data"][0]["exch_side"]) # 交易类型
                    order.fill_qty = int(msg_ans["ret_data"][0]["fill_qty"]) # 成交数量
                    order.status = int(msg_ans["ret_data"][0]["status"]) # 报单状态
                    order.status_msg = msg_ans["ret_data"][0]["status_msg"] # 状态信息
                    #print("当日委托：" + order.ToString())
                    task_item.query_results.append(order) # 查询结果数据
                else: # 结束通知
                    task_item.status = define.TASK_STATUS_OVER # 任务状态
                    task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                    self.SendTraderEvent(ret_func, task_item)
            else: # 查询失败
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：当日委托：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryTrans(self, order_id, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_querytrans_f_func)
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_querytrans_f_func, "session":self.session, "task_id":task_item.task_id, "order_id":order_id}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnQueryTrans(self, ret_func, msg_ans): # 每次一条
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0:
                if msg_ans["ret_last"] == False:
                    #print(msg_ans["ret_data"][0]["otc_code"], msg_ans["ret_data"][0]["otc_info"])
                    trans = self.Trans()
                    trans.order_id = msg_ans["ret_data"][0]["order_id"] # 委托编号
                    trans.trans_id = msg_ans["ret_data"][0]["trans_id"] # 成交编号
                    trans.instrument = msg_ans["ret_data"][0]["instrument"] # 合约代码
                    trans.exchange = msg_ans["ret_data"][0]["exchange"] # 交易所
                    trans.exch_side = int(msg_ans["ret_data"][0]["exch_side"]) # 交易类型，1：买入，2：卖出
                    trans.fill_qty = int(msg_ans["ret_data"][0]["fill_qty"]) # 成交数量
                    trans.fill_price = float(msg_ans["ret_data"][0]["fill_price"]) # 成交价格
                    trans.fill_time = msg_ans["ret_data"][0]["fill_time"] # 成交时间
                    #print("当日成交：" + trans.ToString())
                    task_item.query_results.append(trans) # 查询结果数据
                else: # 结束通知
                    task_item.status = define.TASK_STATUS_OVER # 任务状态
                    task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                    self.SendTraderEvent(ret_func, task_item)
            else: # 查询失败
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：当日成交：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryInstrument(self, category, instrument, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_queryinstrument_f_func)
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_queryinstrument_f_func, "session":self.session, "task_id":task_item.task_id, 
                  "category":category, "instrument":instrument}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnQueryInstrument(self, ret_func, msg_ans): # 每次一条
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0:
                if msg_ans["ret_last"] == False:
                    #print(msg_ans["ret_data"][0]["otc_code"], msg_ans["ret_data"][0]["otc_info"])
                    instrument = self.Instrument()
                    instrument.instrument = msg_ans["ret_data"][0]["instrument"] # 合约代码
                    instrument.exchange = msg_ans["ret_data"][0]["exchange"] # 交易所
                    instrument.delivery_y = int(msg_ans["ret_data"][0]["delivery_y"]) # 交割年份
                    instrument.delivery_m = int(msg_ans["ret_data"][0]["delivery_m"]) # 交割月份
                    instrument.long_margin = float(msg_ans["ret_data"][0]["long_margin"]) # 多头保证金率
                    instrument.short_margin = float(msg_ans["ret_data"][0]["short_margin"]) # 空头保证金率
                    #print("期货合约：" + instrument.ToString())
                    task_item.query_results.append(instrument) # 查询结果数据
                else: # 结束通知
                    task_item.status = define.TASK_STATUS_OVER # 任务状态
                    task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                    self.SendTraderEvent(ret_func, task_item)
            else: # 查询失败
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：期货合约：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryPositionDetail(self, instrument, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_querypositiondetail_f_func)
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_querypositiondetail_f_func, "session":self.session, "task_id":task_item.task_id, "instrument":instrument}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnQueryPositionDetail(self, ret_func, msg_ans): # 每次一条
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0:
                if msg_ans["ret_last"] == False:
                    #print(msg_ans["ret_data"][0]["otc_code"], msg_ans["ret_data"][0]["otc_info"])
                    detail = self.PositionDetail()
                    detail.instrument = msg_ans["ret_data"][0]["instrument"] # 合约代码
                    detail.exch_side = int(msg_ans["ret_data"][0]["exch_side"]) # 交易类型
                    detail.volume = int(msg_ans["ret_data"][0]["volume"]) # 数量
                    detail.open_price = float(msg_ans["ret_data"][0]["open_price"]) # 开仓价格 # 接口 PGT 为 持仓均价
                    detail.exchange = msg_ans["ret_data"][0]["exchange"] # 交易所
                    detail.margin = float(msg_ans["ret_data"][0]["margin"]) # 投资者保证金
                    detail.exch_margin = float(msg_ans["ret_data"][0]["exch_margin"]) # 交易所保证金 # 接口 PGT 为 昨持仓量
                    #print("客户持仓明细：" + detail.ToString())
                    task_item.query_results.append(detail) # 查询结果数据
                else: # 结束通知
                    task_item.status = define.TASK_STATUS_OVER # 任务状态
                    task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                    self.SendTraderEvent(ret_func, task_item)
            else: # 查询失败
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：客户持仓明细：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def OnOrderReply(self, ret_func, msg_ans):
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["task_id"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            order = self.Order()
            order.order_id = msg_ans["order_id"] # 委托号
            order.order_sys_id = msg_ans["order_sys_id"] # 报单号
            order.instrument = msg_ans["instrument"] # 合约代码
            order.exchange = msg_ans["exchange"] # 交易所
            order.exch_side = int(msg_ans["exch_side"]) # 交易类型
            order.fill_qty = int(msg_ans["fill_qty"]) # 成交数量
            order.status = int(msg_ans["status"]) # 报单状态
            order.status_msg = msg_ans["status_msg"] # 状态信息
            #print("委托回报：" + order.ToString())
            task_item.order_replies.append(order) # 单个合约委托回报
            if self.trade_info != None:
                self.trade_info.AddTbData_Order(task_id, task_item.strategy, order) #
            self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：委托回报：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def OnTransReply(self, ret_func, msg_ans):
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["task_id"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            trans = self.Trans()
            trans.order_id = msg_ans["order_id"] # 委托编号
            trans.trans_id = msg_ans["trans_id"] # 成交编号
            trans.instrument = msg_ans["instrument"] # 合约代码
            trans.exchange = msg_ans["exchange"] # 交易所
            trans.exch_side = int(msg_ans["exch_side"]) # 交易类型，1：买入，2：卖出
            trans.fill_qty = int(msg_ans["fill_qty"]) # 成交数量
            trans.fill_price = float(msg_ans["fill_price"]) # 成交价格
            trans.fill_time = msg_ans["fill_time"] # 成交时间
            #print("成交回报：" + trans.ToString())
            task_item.trans_replies.append(trans) # 单个合约成交回报
            if self.trade_info != None:
                self.trade_info.AddTbData_Trans(task_id, task_item.strategy, trans) #
            self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：成交回报：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def OnRiskInform(self, ret_func, msg_ans):
        risk_info = self.RiskInfo()
        risk_info.seq_no = int(msg_ans["seq_no"]) # 序列号
        risk_info.seq_series = int(msg_ans["seq_series"]) # 序列系列号
        risk_info.content = msg_ans["content"] # 消息正文
        #print("风控通知：" + risk_info.ToString())
        # 因为无法得到任务号，目前不处理风控通知

####################################################################################################

# 这里 南华UTP 和 易盛ESP 的资金数据是按 币种 返回多条的

    def QueryCapital_Syn(self, strategy, query_wait = 5):
        capital_list = []
        task_item = self.QueryCapital(strategy)
        if task_item != None:
            ret_wait = task_item.event_task_finish.wait(timeout = query_wait) # 等待结果
            if ret_wait == True:
                if task_item.status == define.TASK_STATUS_OVER:
                    for item in task_item.query_results:
                        capital_list.append(item)
                        #self.log_text = "%s：期货资金：%s" % (strategy, item.ToString())
                        #self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                    return [True, capital_list]
                else:
                    self.log_text = "%s：期货 资金 查询失败！原因：%s" % (strategy, task_item.messages[-1])
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                    return [False, capital_list]
            else:
                self.log_text = "%s：期货 资金 查询超时！状态：%d" % (strategy, task_item.status)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, capital_list]
        else:
            self.log_text = "%s：期货 资金 查询异常！返回任务对象为空！" % strategy
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, capital_list]

# 东证期货CTP持仓查询有点混乱的，目前以总仓和今仓为准计算昨仓，已开和已平也用累加：

# 总仓：756，多头今仓：756，多头昨仓：0，空头今仓：0，空头昨仓：0
#    客户持仓：instrument：ag1412, exch_side：1, position：0, tod_position：0, pre_position：626, open_volume：0, close_volume：626
#    客户持仓：instrument：ag1412, exch_side：1, position：756, tod_position：756, pre_position：0, open_volume：2858, close_volume：2102

# 总仓：276，多头今仓：0，多头昨仓：276，空头今仓：0，空头昨仓：0
#    客户持仓：instrument：ag1412, exch_side：1, position：276, tod_position：0, pre_position：276, open_volume：0, close_volume：0
# 平掉四手以后：
#    客户持仓：instrument：ag1412, exch_side：1, position：272, tod_position：0, pre_position：276, open_volume：0, close_volume：4
# 全部平完以后：
#    客户持仓：instrument：ag1412, exch_side：1, position：0, tod_position：0, pre_position：276, open_volume：0, close_volume：276
# 全部平完以后：(早盘前)
#    客户持仓：instrument：ag1412, exch_side：1, position：0, tod_position：0, pre_position：276, open_volume：0, close_volume：276
#    客户持仓：instrument：ag1412, exch_side：2, position：0, tod_position：0, pre_position：0, open_volume：2114, close_volume：2114

# 总仓：59，多头今仓：35，多头昨仓：24，空头今仓：0，空头昨仓：0
#    客户持仓：instrument：au1412, exch_side：1, position：24, tod_position：0, pre_position：100, open_volume：0, close_volume：76
#    客户持仓：instrument：au1412, exch_side：1, position：35, tod_position：35, pre_position：0, open_volume：130, close_volume：95

# 另外 南华UTP 和 易盛ESP 返回的持仓可能同一个合约同一个方向有多条，需要累加起来，并且 tod_position、pre_position、open_volume、close_volume 均为零

    def QueryPosition_Syn(self, instrument, strategy, query_wait = 5): # 需要指定合约，合约为空的话会全部被过滤掉
        position_l = self.Position() #多
        position_l.instrument = instrument
        position_l.exch_side = define.DEF_EXCHSIDE_BUY
        position_s = self.Position() #空
        position_s.instrument = instrument
        position_s.exch_side = define.DEF_EXCHSIDE_SELL
        task_item = self.QueryPosition(instrument, strategy)
        if task_item != None:
            ret_wait = task_item.event_task_finish.wait(timeout = query_wait) # 等待结果
            if ret_wait == True:
                if task_item.status == define.TASK_STATUS_OVER:
                    for item in task_item.query_results:
                        if item.instrument == instrument:
                            if item.exch_side == define.DEF_EXCHSIDE_BUY: # 多 # 目前发现 CTP 今仓和昨仓也是分开记录的，已开和已平暂时也用 += 吧
                                position_l.position += item.position
                                position_l.tod_position += item.tod_position
                                position_l.pre_position = position_l.position - position_l.tod_position
                                position_l.open_volume += item.open_volume
                                position_l.close_volume += item.close_volume
                            if item.exch_side == define.DEF_EXCHSIDE_SELL: # 空 # 目前发现 CTP 今仓和昨仓也是分开记录的，已开和已平暂时也用 += 吧
                                position_s.position += item.position
                                position_s.tod_position += item.tod_position
                                position_s.pre_position = position_s.position - position_s.tod_position
                                position_s.open_volume += item.open_volume
                                position_s.close_volume += item.close_volume
                        #self.log_text = "%s：期货持仓：%s" % (strategy, item.ToString())
                        #self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                    return [True, position_l, position_s]
                else:
                    self.log_text = "%s：期货 持仓 查询失败！原因：%s" % (strategy, task_item.messages[-1])
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                    return [False, position_l, position_s]
            else:
                self.log_text = "%s：期货 持仓 查询超时！状态：%d" % (strategy, task_item.status)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, position_l, position_s]
        else:
            self.log_text = "%s：期货 持仓 查询异常！返回任务对象为空！" % strategy
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, position_l, position_s]

    def PlaceOrder_FOC_Syn(self, label, order, strategy, trade_wait = 1, cancel_wait = 5):
        self.log_text = "%s：准备 %s：%s" % (strategy, label, order.ToString())
        self.logger.SendMessage("D", 0, self.log_cate, self.log_text, "T")
        
#        time.sleep(2)
#        order.fill_qty = order.amount
#        return [True, order] # 测试！！
        
        task_item_place = self.PlaceOrder(order, strategy)
        if task_item_place == None:
            self.log_text = "%s：委托 %s %s 下单异常！返回任务对象为空！" % (strategy, label, order.instrument)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, order]
        ret_wait = task_item_place.event_task_finish.wait(trade_wait) # 等待结果
        # 在 wait 结束时，要么报单异常，要么交易结束，要么等待超时
        if ret_wait == True: # 报单异常、交易结束
            if task_item_place.status == define.TASK_STATUS_FAIL: # 报单异常
                self.log_text = "%s：委托 %s %s 下单异常！任务：%d，原因：%s" % (strategy, label, order.instrument, task_item_place.task_id, task_item_place.messages[-1])
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, task_item_place.order]
            else: # 交易结束
                self.log_text = "%s：委托 %s %s 交易完成。任务：%d，状态：%d，成交：%d" % (strategy, label, order.instrument, task_item_place.task_id, task_item_place.order.status, task_item_place.order.fill_qty)
                self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                return [True, task_item_place.order]
        else: # 等待超时
            task_item_place.event_recv_answer.wait(120) # 等待交易所报单回报，保证获得 order_sys_id 用于撤单
            if task_item_place.order.order_id != "": # 已保证 order_sys_id != ""
                self.log_text = "%s：委托 %s %s 准备撤单。委托：%s，超时：%d" % (strategy, label, order.instrument, task_item_place.order.order_id, trade_wait)
                self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                task_item_cancel = self.CancelOrder(task_item_place.order, strategy)
                if task_item_cancel == None:
                    self.log_text = "%s：委托 %s %s 撤单异常！返回任务对象为空！" % (strategy, label, order.instrument)
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                    return [False, task_item_place.order]
                ret_wait = task_item_place.event_task_finish.wait(cancel_wait) # 等待结果 # 使用 task_item_place
                # 在 wait 结束时，要么交易结束，要么等待超时
                if ret_wait == True: # 交易结束
                    self.log_text = "%s：委托 %s %s 撤单完成。任务：%d，状态：%d，成交：%d" % (strategy, label, order.instrument, task_item_place.task_id, task_item_place.order.status, task_item_place.order.fill_qty)
                    self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                    return [True, task_item_place.order]
                else: # 等待超时
                    if task_item_cancel.status == define.TASK_STATUS_FAIL: # 撤单异常
                        self.log_text = "%s：委托 %s %s 撤单异常！任务：%d，原因：%s" % (strategy, label, order.instrument, task_item_cancel.task_id, task_item_cancel.messages[-1])
                        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                        return [False, task_item_place.order]
                    else:
                        self.log_text = "%s：委托 %s %s 撤单超时！任务：%d，超时：%d" % (strategy, label, order.instrument, task_item_cancel.task_id, cancel_wait)
                        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                        return [False, task_item_place.order]
            else:
                self.log_text = "%s：委托 %s %s 撤单时缺少委托编号！任务：%d" % (strategy, label, order.instrument, task_item_place.task_id)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, task_item_place.order]

    def PlaceCombinOrder_FOC_Syn(self, label, order, strategy, trade_wait = 1, cancel_wait = 5):
        self.log_text = "%s：准备 %s：%s" % (strategy, label, order.ToString())
        self.logger.SendMessage("D", 0, self.log_cate, self.log_text, "T")
        
#        time.sleep(2)
#        order.fill_qty = order.amount * 2 # * 2
#        return [True, order] # 测试！！
        
        task_item_place = self.PlaceCombinOrder(order, strategy)
        if task_item_place == None:
            self.log_text = "%s：委托 %s %s 下单异常！返回任务对象为空！" % (strategy, label, order.instrument)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, order]
        ret_wait = task_item_place.event_task_finish.wait(trade_wait) # 等待结果
        # 在 wait 结束时，要么报单异常，要么交易结束，要么等待超时
        if ret_wait == True: # 报单异常、交易结束
            if task_item_place.status == define.TASK_STATUS_FAIL: # 报单异常
                self.log_text = "%s：委托 %s %s 下单异常！任务：%d，原因：%s" % (strategy, label, order.instrument, task_item_place.task_id, task_item_place.messages[-1])
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, task_item_place.order]
            else: # 交易结束
                self.log_text = "%s：委托 %s %s 交易完成。任务：%d，状态：%d，成交：%d" % (strategy, label, order.instrument, task_item_place.task_id, task_item_place.order.status, task_item_place.order.fill_qty)
                self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                return [True, task_item_place.order]
        else: # 等待超时
            task_item_place.event_recv_answer.wait(120) # 等待交易所报单回报，保证获得 order_sys_id 用于撤单
            if task_item_place.order.order_id != "": # 已保证 order_sys_id != ""
                self.log_text = "%s：委托 %s %s 准备撤单。委托：%s，超时：%d" % (strategy, label, order.instrument, task_item_place.order.order_id, trade_wait)
                self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                task_item_cancel = self.CancelOrder(task_item_place.order, strategy)
                if task_item_cancel == None:
                    self.log_text = "%s：委托 %s %s 撤单异常！返回任务对象为空！" % (strategy, label, order.instrument)
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                    return [False, task_item_place.order]
                ret_wait = task_item_place.event_task_finish.wait(cancel_wait) # 等待结果 # 使用 task_item_place
                # 在 wait 结束时，要么交易结束，要么等待超时
                if ret_wait == True: # 交易结束
                    self.log_text = "%s：委托 %s %s 撤单完成。任务：%d，状态：%d，成交：%d" % (strategy, label, order.instrument, task_item_place.task_id, task_item_place.order.status, task_item_place.order.fill_qty)
                    self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                    return [True, task_item_place.order]
                else: # 等待超时
                    if task_item_cancel.status == define.TASK_STATUS_FAIL: # 撤单异常
                        self.log_text = "%s：委托 %s %s 撤单异常！任务：%d，原因：%s" % (strategy, label, order.instrument, task_item_cancel.task_id, task_item_cancel.messages[-1])
                        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                        return [False, task_item_place.order]
                    else:
                        self.log_text = "%s：委托 %s %s 撤单超时！任务：%d，超时：%d" % (strategy, label, order.instrument, task_item_cancel.task_id, cancel_wait)
                        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                        return [False, task_item_place.order]
            else:
                self.log_text = "%s：委托 %s %s 撤单时缺少委托编号！任务：%d" % (strategy, label, order.instrument, task_item_place.task_id)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, task_item_place.order]

    def PlaceOrder_Basket_Syn(self, label, orders, strategy, trade_wait = 1, cancel_wait = 5): # 同一合约的多个委托不能在一个 orders 中
        trade_error = False
        task_item_dict_place = {} # 委托 下单 了的
        for order in orders: # 下单
            task_item_place = self.PlaceOrder(order, strategy)
            if task_item_place == None:
                trade_error = True
                self.log_text = "%s：下单 %s %s 返回任务对象为空！" % (strategy, label, order.instrument)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            else:
                task_item_dict_place[order.instrument] = task_item_place
        if trade_error == True:
            return [False, orders]
        task_item_dict_cancel = {} # 委托 撤单 了的
        for task_item_place in task_item_dict_place.values(): # 撤单
            order = task_item_place.order # instrument
            ret_wait = task_item_place.event_task_finish.wait(trade_wait) # 等待结果
            # 在 wait 结束时，要么报单异常，要么交易结束，要么等待超时
            if ret_wait == True: # 报单异常、交易结束
                if task_item_place.status == define.TASK_STATUS_FAIL: # 报单异常
                    trade_error = True
                    self.log_text = "%s：委托 %s %s 下单异常！任务：%d，原因：%s" % (strategy, label, order.instrument, task_item_place.task_id, task_item_place.messages[-1])
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                else:
                    self.log_text = "%s：委托 %s %s 交易完成。任务：%d，状态：%d，成交：%d" % (strategy, label, order.instrument, task_item_place.task_id, task_item_place.order.status, task_item_place.order.fill_qty)
                    self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
            else: # 等待超时
                task_item_place.event_recv_answer.wait(120) # 等待交易所报单回报，保证获得 order_sys_id 用于撤单
                if task_item_place.order.order_id != "": # 已保证 order_sys_id != ""
                    self.log_text = "%s：委托 %s %s 准备撤单。委托：%s，超时：%d" % (strategy, label, order.instrument, task_item_place.order.order_id, trade_wait)
                    self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                    task_item_cancel = self.CancelOrder(task_item_place.order, strategy)
                    if task_item_cancel == None:
                        trade_error = True
                        self.log_text = "%s：撤单 %s %s 返回任务对象为空！" % (strategy, label, order.instrument)
                        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                    else:
                        task_item_dict_cancel[order.instrument] = task_item_cancel
                else:
                    trade_error = True
                    self.log_text = "%s：委托 %s %s 撤单时缺少委托编号！任务：%d" % (strategy, label, order.instrument, task_item_place.task_id)
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
        if trade_error == True:
            return [False, orders]
        for task_item_place in task_item_dict_place.values(): # 完成
            order = task_item_place.order # instrument
            if order.instrument in task_item_dict_cancel.keys():
                task_item_cancel = task_item_dict_cancel[order.instrument]
                ret_wait = task_item_place.event_task_finish.wait(cancel_wait) # 等待结果 # 使用 task_item_place
                # 在 wait 结束时，要么交易结束，要么等待超时
                if ret_wait == True: # 交易结束
                    self.log_text = "%s：委托 %s %s 撤单完成。任务：%d，状态：%d，成交：%d" % (strategy, label, order.instrument, task_item_place.task_id, task_item_place.order.status, task_item_place.order.fill_qty)
                    self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                else: # 等待超时
                    if task_item_cancel.status == define.TASK_STATUS_FAIL: # 撤单异常
                        trade_error = True
                        self.log_text = "%s：委托 %s %s 撤单异常！任务：%d，原因：%s" % (strategy, label, order.instrument, task_item_cancel.task_id, task_item_cancel.messages[-1])
                        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                    else:
                        trade_error = True
                        self.log_text = "%s：委托 %s %s 撤单超时！任务：%d，超时：%d" % (strategy, label, order.instrument, task_item_cancel.task_id, cancel_wait)
                        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
        if trade_error == True:
            return [False, orders]
        return [True, orders]

####################################################################################################

def TestData(trader):
    count = 0
    for i in range(0, 10):
        for j in range(0, 100):
            count += 1
            
            place = trader.Order(instrument = "Ag(T+D)", exchange = "SGE", price = 3830.0, amount = 1, entr_type = 1, exch_side = 1, offset = 1, hedge = 1)
            trader.trade_info.AddTbData_Place(count, "strategy_test", place) # 下单
            
            place.order_id = "1234567890"
            place.order_sys_id = "123321"
            trader.trade_info.AddTbData_Place(count, "strategy_test", place) # 撤单
            
            order = trader.Order(instrument = "Ag(T+D)", exchange = "SGE", exch_side = 1, )
            order.order_id = "1234567890"
            order.order_sys_id = "123321"
            order.fill_qty = 1
            order.status = 5
            order.status_msg = "test_status_msg_中文！"
            trader.trade_info.AddTbData_Order(count, "strategy_test", order) # 报单
            
            trans = trader.Trans()
            trans.order_id = "1234567890"
            trans.trans_id = "789987"
            trans.instrument = "Ag(T+D)"
            trans.exchange = "SGE"
            trans.exch_side = 1
            trans.fill_qty = 1
            trans.fill_price = 3830.0
            trans.fill_time = "102305"
            trader.trade_info.AddTbData_Trans(count, "strategy_test", trans) # 成交
            
            time.sleep(0.001)
    print("Total：%d" % count)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    future_trader = TradeX_Fue_As(None, "期货类内盘交易", "test", 1, "10.0.7.80", 3001, "16313", "143417", "LHTZ_20170428001_000", 30)
    
    #thread = threading.Thread(target = TestData, args = (future_trader,))
    #thread.start()
    
    future_trader.Start()
    
    time.sleep(5)
    
    #time.sleep(2)
    #order = future_trader.Order(instrument = "IF1701", exchange = "CFFE", price = 3330.0, amount = 1, entr_type = 1, exch_side = 1, offset = 1, hedge = 1) # 限，买，开，投机
    #order = future_trader.Order(instrument = "IF1701", exchange = "CFFE", price = 3330.0, amount = 1, entr_type = 1, exch_side = 2, offset = 1, hedge = 1) # 限，卖，平，投机
    #task_place = future_trader.PlaceOrder(order, "strategy_test")
    #time.sleep(5)
    #task_cancel = future_trader.CancelOrder(task_place.order, "strategy_test")
    #time.sleep(5)
    
    #time.sleep(2)
    #order = future_trader.Order(instrument = "Ag(T+D)", exchange = "SGE", price = 3225.0, amount = 5, entr_type = 1, exch_side = 4, offset = 1, hedge = 1) # 限，递延交割交货，开平随意，投机
    #task_place = future_trader.PlaceOrder(order, "strategy_test")
    #time.sleep(5)
    
    #time.sleep(2)
    #order = future_trader.Order(instrument = "Ag99.99", exchange = "SGE", price = 3200.0, amount = 1, entr_type = 1, exch_side = 1, offset = 1, hedge = 1) # 限，买，开，投机
    #order = future_trader.Order(instrument = "Ag99.99", exchange = "SGE", price = 3200.0, amount = 1, entr_type = 1, exch_side = 2, offset = 1, hedge = 1) # 限，卖，平，投机
    #task_place = future_trader.PlaceOrder(order, "strategy_test")
    #time.sleep(5)
    #task_cancel = future_trader.CancelOrder(task_place.order, "strategy_test")
    #time.sleep(5)
    
    #time.sleep(2)
    #future_trader.QueryCapital("strategy_test") # UTP、ESP：不同币种各一条
    #time.sleep(2)
    #future_trader.QueryPosition("HKEX HSI 1509", "strategy_test")
    #time.sleep(2)
    #future_trader.QueryPosition("", "strategy_test")
    #time.sleep(2)
    #future_trader.QueryOrder("306180", "strategy_test")
    #time.sleep(2)
    #future_trader.QueryOrder("", "strategy_test")
    #time.sleep(2)
    #future_trader.QueryTrans("306227", "strategy_test")
    #time.sleep(2)
    #future_trader.QueryTrans("", "strategy_test")
    #time.sleep(5)
    
    future_trader.Stop()
    
    sys.exit(app.exec_())
