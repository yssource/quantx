
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
import threading
from datetime import datetime, timedelta

import config
import define
import logger
import center

class TradeX_Stk_Sy():
    class Order(object):
        def __init__(self, **kwargs):
            self.order_id = 0 # 委托编号
            self.batch_id = 0 # 批量委托编号
            self.symbol = kwargs.get("symbol", "") # 证券代码
            self.exchange = kwargs.get("exchange", "") # 交易所，SH：上交所，SZ：深交所
            self.entr_type = kwargs.get("entr_type", 0) # 委托方式，1：限价，2：市价
            self.exch_side = kwargs.get("exch_side", 0) # 交易类型，1：买入，2：卖出，29：申购，30：赎回，37：质押入库，38：质押出库
            # A0：A股，E0：ETF基金，E1：ETF资金，E3：ETF发行，E4：ETF申赎，EZ：国债ETF，F8：质押券，
            # H0：国债回购，H1：企债回购，H2：买断回购，H3：账户回购，Z0：现券国债，Z1：记帐国债，Z4：企业债券
            self.security_type = "" # 证券类别
            self.price = kwargs.get("price", 0.0) # 委托价格
            self.amount = kwargs.get("amount", 0) # 委托数量
            self.fill_qty = 0 # 总成交数量
            self.cxl_qty = 0 # 撤单数量
            # 0：未申报，1：正在申报，2：已申报未成交，3：非法委托，4：申请资金授权中，
            # 5：部分成交，6：全部成交，7：部成部撤，8：全部撤单，9：撤单未成，10：等待人工申报
            self.status = 0 # 申报结果
            self.status_msg = "" # 申报说明
            self.brow_index = "" # 增量查询索引值

        def ToString(self):
            return "order_id：%d, " % self.order_id + \
                   "batch_id：%d, " % self.batch_id + \
                   "symbol：%s, " % self.symbol + \
                   "exchange：%s, " % self.exchange + \
                   "entr_type：%d, " % self.entr_type + \
                   "exch_side：%d, " % self.exch_side + \
                   "security_type：%s, " % self.security_type + \
                   "price：%f, " % self.price + \
                   "amount：%d, " % self.amount + \
                   "fill_qty：%d, " % self.fill_qty + \
                   "cxl_qty：%d, " % self.cxl_qty + \
                   "status：%d, " % self.status + \
                   "status_msg：%s, " % self.status_msg + \
                   "brow_index：%s" % self.brow_index

    class Trans(object):
        def __init__(self):
            self.order_id = 0 # 委托编号
            self.trans_id = "" # 成交编号
            self.symbol = "" # 证券代码
            self.exchange = "" # 交易所，SH：上交所，SZ：深交所
            self.exch_side = 0 # 交易类型，1：买入，2：卖出，29：申购，30：赎回，37：质押入库，38：质押出库
            # A0：A股，E0：ETF基金，E1：ETF资金，E3：ETF发行，E4：ETF申赎，EZ：国债ETF，F8：质押券，
            # H0：国债回购，H1：企债回购，H2：买断回购，H3：账户回购，Z0：现券国债，Z1：记帐国债，Z4：企业债券
            self.security_type = "" # 证券类别
            self.fill_qty = 0 # 本次成交数量
            self.fill_price = 0.0 # 本次成交价格
            self.fill_time = "" # 成交时间
            self.cxl_qty = 0 # 撤单数量
            self.brow_index = "" # 增量查询索引值

        def ToString(self):
            return "order_id：%d, " % self.order_id + \
                   "trans_id：%s, " % self.trans_id + \
                   "symbol：%s, " % self.symbol + \
                   "exchange：%s, " % self.exchange + \
                   "exch_side：%d, " % self.exch_side + \
                   "security_type：%s, " % self.security_type + \
                   "fill_qty：%d, " % self.fill_qty + \
                   "fill_price：%f, " % self.fill_price + \
                   "fill_time：%s, " % self.fill_time + \
                   "cxl_qty：%d, " % self.cxl_qty + \
                   "brow_index：%s" % self.brow_index

    class Capital(object):
        def __init__(self):
            self.account = "" # 资金账号
            self.currency = "" # 币种，RMB：人民币，USD：美元，HKD：港币
            self.available = 0.0 # 可用资金
            self.balance = 0.0 # 账户余额
            self.frozen = 0.0 # 冻结金额

        def ToString(self):
            return "account：%s, " % self.account + \
                   "currency：%s, " % self.currency + \
                   "available：%f, " % self.available + \
                   "balance：%f, " % self.balance + \
                   "frozen：%f" % self.frozen

    class Position(object):
        def __init__(self):
            self.holder = "" # 股东号
            self.exchange = "" # 交易所
            self.currency = "" # 币种
            self.symbol = "" # 证券代码
            self.security_type = "" # 证券类别
            self.security_name = "" # 证券名称
            self.security_qty = 0 # 持仓数量
            self.can_sell = 0 # 可卖出数量
            self.can_sub = 0 # 可申购数量
            self.can_red = 0 # 可赎回数量
            self.non_tradable = 0 # 非流通数量
            self.frozen_qty = 0 # 冻结数量
            self.sell_qty = 0 # 当日卖出成交数量
            self.sell_money = 0.0 # 当日卖出成交金额
            self.buy_qty = 0 # 当日买入成交数量
            self.buy_money = 0.0 # 当日买入成交金额
            self.sub_qty = 0 # 当日申购成交数量
            self.red_qty = 0 # 当日赎回成交数量

        def ToString(self):
            return "holder：%s, " % self.holder + \
                   "exchange：%s, " % self.exchange + \
                   "currency：%s, " % self.currency + \
                   "symbol：%s, " % self.symbol + \
                   "security_type：%s, " % self.security_type + \
                   "security_name：%s, " % self.security_name + \
                   "security_qty：%d, " % self.security_qty + \
                   "can_sell：%d, " % self.can_sell + \
                   "can_sub：%d, " % self.can_sub + \
                   "can_red：%d, " % self.can_red + \
                   "non_tradable：%d, " % self.non_tradable + \
                   "frozen_qty：%d, " % self.frozen_qty + \
                   "sell_qty：%d, " % self.sell_qty + \
                   "sell_money：%f, " % self.sell_money + \
                   "buy_qty：%d, " % self.buy_qty + \
                   "buy_money：%f, " % self.buy_money + \
                   "sub_qty：%d, " % self.sub_qty + \
                   "red_qty：%d" % self.red_qty

    class EtfBaseInfo(object):
        def __init__(self):
            self.fund_name = "" # 基金名称
            self.fund_id_1 = "" # 申赎代码
            self.fund_id_2 = "" # 基金代码
            self.exchange = "" # 交易所
            self.count = 0 # 股票记录数
            self.status = 0 # 申赎允许状态，-1：无资格，0：禁止申赎，1：允许申赎，2：允许申购，3：允许赎回
            self.pub_iopv = 0 # 是否发布IOPV
            self.unit = 0 # 最小申赎单位
            self.cash_ratio = 0.0 # 最大现金替代比例
            self.cash_diff = 0.0 # T日现金差额
            self.iopv = 0.0 # T-1日单位净值
            self.trade_iopv = 0.0 # T-1日申赎单位净值
            self.stocks = [] # 成分股清单

        def ToString(self):
            return "fund_name：%s, " % self.fund_name + \
                   "fund_id_1：%s, " % self.fund_id_1 + \
                   "fund_id_2：%s, " % self.fund_id_2 + \
                   "exchange：%s, " % self.exchange + \
                   "count：%d, " % self.count + \
                   "status：%d, " % self.status + \
                   "pub_iopv：%d, " % self.pub_iopv + \
                   "unit：%d, " % self.unit + \
                   "cash_ratio：%f, " % self.cash_ratio + \
                   "cash_diff：%f, " % self.cash_diff + \
                   "iopv：%f, " % self.iopv + \
                   "trade_iopv：%f" % self.trade_iopv

    class EtfDetailInfo(object):
        def __init__(self):
            self.fund_name = "" # 基金名称
            self.stock_code = "" # 成分股代码
            self.stock_name = "" # 成分股名称
            self.stock_qty = 0 # 成分股数量
            self.exchange = "" # 交易所
            self.replace_flag = 0 # 现金替代标志，1：允许，2：必须，3：禁止
            self.replace_money = 0.0 # 现金替代金额
            self.up_px_ratio = 0.0 # 溢价比例

        def ToString(self):
            return "fund_name：%s, " % self.fund_name + \
                   "stock_code：%s, " % self.stock_code + \
                   "stock_name：%s, " % self.stock_name + \
                   "stock_qty：%d, " % self.stock_qty + \
                   "exchange：%s, " % self.exchange + \
                   "replace_flag：%d, " % self.replace_flag + \
                   "replace_money：%f, " % self.replace_money + \
                   "up_px_ratio：%f" % self.up_px_ratio

    class BatchItem(object):
        def __init__(self):
            self.order = None # 单个合约
            self.order_replies = [] # 单个合约委托回报
            self.trans_replies = [] # 单个合约成交回报

    class BatchInfo(object):
        def __init__(self):
            self.batch_id = "" # 批量委托编号
            self.batch_ht = "" # 委托编号列表
            self.batch_orders_list = [] # 批量委托信息，用于下单之前 # BatchItem
            self.batch_orders_map = {} # 批量委托信息，用于下单以后，成功的委托 # BatchItem

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
            self.batch = None # 批量合约，BatchInfo，股票类特有
            self.event_task_finish = threading.Event()

        def ToString(self):
            return "task_id：%d, " % self.task_id + \
                   "strategy：%s, " % self.strategy + \
                   "function：%d, " % self.function + \
                   "status：%d, " % self.status + \
                   "messages：%s" % self.messages[-1] # 只打印最后一条

####################################################################################################

    def __init__(self, parent, trade_name, trade_flag, trade_save, address, port, username, password, holder_sh, holder_sz, asset_account, login_time_out):
        self.log_text = ""
        self.log_cate = "TradeX_Stk_Sy"
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
        self.holder_sh = holder_sh
        self.holder_sz = holder_sz
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
        task_item.messages.append("开始执行任务....") # 任务信息
        #task_item.order = None # 单个合约
        #task_item.order_replies = [] # 单个合约委托回报
        #task_item.trans_replies = [] # 单个合约成交回报
        #task_item.query_results = [] # 查询结果数据
        #self.batch = None # 批量合约，BatchInfo，股票类特有
        return task_item

    def RegReplyMsgHandleFunc(self):
        self.reply_msg_handle_func_sys = {}
        self.reply_msg_handle_func_sys[define.trade_userlogin_s_func] = self.OnUserLogIn
        self.reply_msg_handle_func_sys[define.trade_userlogout_s_func] = self.OnUserLogOut
        self.reply_msg_handle_func_sys[define.trade_subscibe_s_func] = self.OnSubscibe
        self.reply_msg_handle_func_sys[define.trade_unsubscibe_s_func] = self.OnUnsubscibe
        self.reply_msg_handle_func_usr = {}
        self.reply_msg_handle_func_usr[define.trade_placeorder_s_func] = self.OnPlaceOrder
        self.reply_msg_handle_func_usr[define.trade_cancelorder_s_func] = self.OnCancelOrder
        self.reply_msg_handle_func_usr[define.trade_placeorderbatch_s_func] = self.OnPlaceOrderBatch
        self.reply_msg_handle_func_usr[define.trade_cancelorderbatch_s_func] = self.OnCancelOrderBatch
        self.reply_msg_handle_func_usr[define.trade_querycapital_s_func] = self.OnQueryCapital
        self.reply_msg_handle_func_usr[define.trade_queryposition_s_func] = self.OnQueryPosition
        self.reply_msg_handle_func_usr[define.trade_queryorder_s_func] = self.OnQueryOrder
        self.reply_msg_handle_func_usr[define.trade_querytrans_s_func] = self.OnQueryTrade
        self.reply_msg_handle_func_usr[define.trade_queryetfbase_s_func] = self.OnQueryEtfBase
        self.reply_msg_handle_func_usr[define.trade_queryetfdetail_s_func] = self.OnQueryEtfDetail
        self.reply_msg_handle_func_usr[define.trade_orderreply_s_func] = self.OnOrderReply
        self.reply_msg_handle_func_usr[define.trade_transreply_s_func] = self.OnTransReply
        self.reply_msg_handle_func_usr[define.trade_cancelreply_s_func] = self.OnCancelReply

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
            msg_head = self.sock.recv(8)
            while len(msg_head) < 8:
                msg_head.extend(self.sock.recv(8 - len(msg_head)))
            msg_head = msg_head.decode()
            if msg_head[0] == "8": # NW_MSG_TYPE_USER_DATA # 用户数据处理消息
                msg_type = msg_head[0]
                msg_code = msg_head[1]
                tmp_size = msg_head[2:]
                msg_size = int(tmp_size, 16)
                msg_recv = self.sock.recv(msg_size)
                while len(msg_recv) < msg_size:
                    msg_recv = "".join([msg_recv, self.sock.recv(msg_size - len(msg_recv))])
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
            # 证券回报类
            if ret_func == define.trade_orderreply_s_func: # 股票报单回报，接口 APE 报单回报只有一个
                if task_item.order != None:
                    order_reply = task_item.order_replies[-1] # 取最新一个
                    if task_item.order.order_id == "":
                        task_item.order.order_id = order_reply.order_id # 委托编号
                    # 接口 APE 只在委托报入时有一个报单回报，之后是一系列成交回报，或者因为撤单才会有另外的撤单回报，故采用成交回报累加
                    task_item.order.status = order_reply.status # 委托状态
                    # 0：未申报，1：正在申报，2：已申报未成交，3：非法委托，4：申请资金授权中，
                    # 5：部分成交，6：全部成交，7：部成部撤，8：全部撤单，9：撤单未成，10：等待人工申报
                    # 委托交易结束：非法委托、全部成交、部成部撤、全部撤单
                    if order_reply.status == 3 or order_reply.status == 6 or order_reply.status == 7 or order_reply.status == 8: # 因为撤单回报独立，估计不会有 7：部成部撤，甚至可能不会有 8：全部撤单
                        task_item.event_task_finish.set()
                elif task_item.batch != None:
                    pass
            if ret_func == define.trade_cancelreply_s_func: # 股票撤单回报，接口 APE 撤单回报只有一个
                if task_item.order != None:
                    order_reply = task_item.order_replies[-1] # 取最新一个
                    if task_item.order.order_id == "":
                        task_item.order.order_id = order_reply.order_id # 委托编号
                    task_item.order.status = order_reply.status # 委托状态
                    task_item.order.fill_qty = order_reply.fill_qty # 总成交数量
                    # 委托交易结束：非法委托、全部成交、部成部撤、全部撤单
                    if order_reply.status == 3 or order_reply.status == 6 or order_reply.status == 7 or order_reply.status == 8: # 撤单回报估计不会有 3：非法委托
                        task_item.event_task_finish.set()
                elif task_item.batch != None:
                    pass
            if ret_func == define.trade_transreply_s_func: # 股票成交回报，接口 APE 成交回报会有多个
                if task_item.order != None:
                    trans_reply = task_item.trans_replies[-1] # 取最新一个
                    if task_item.order.order_id == "":
                        task_item.order.order_id = trans_reply.order_id # 委托编号
                    task_item.order.fill_qty += trans_reply.fill_qty # 本次成交数量
                    if task_item.order.fill_qty >= task_item.order.amount: # 全部成交
                        task_item.order.status = 6 # 全部成交
                        task_item.event_task_finish.set()
                elif task_item.batch != None:
                    pass
            
            # 证券委托类
            if ret_func == define.trade_placeorder_s_func: # 股票单个证券委托下单
                if task_item.status == define.TASK_STATUS_FAIL: # 这里只关注失败的，成功的根据成交回报处理
                    task_item.event_task_finish.set() # 标记 下单 事务结束
            if ret_func == define.trade_cancelorder_s_func: # 股票单个证券委托撤单
                task_item.event_task_finish.set() # 标记 撤单 事务结束
            if ret_func == define.trade_placeorderbatch_s_func: # 股票批量证券委托下单
                pass
            if ret_func == define.trade_cancelorderbatch_s_func: # 股票批量证券委托撤单
                pass
            
            # 证券查询类
            if ret_func == define.trade_querycapital_s_func: # 股票查询客户资金
                task_item.event_task_finish.set()
            if ret_func == define.trade_queryposition_s_func: # 股票查询客户持仓
                task_item.event_task_finish.set()
            if ret_func == define.trade_queryorder_s_func: # 股票查询客户当日委托
                task_item.event_task_finish.set()
            if ret_func == define.trade_querytrans_s_func: # 股票查询客户当日成交
                task_item.event_task_finish.set()
            if ret_func == define.trade_queryetfbase_s_func: # 股票查询ETF基本信息
                task_item.event_task_finish.set()
            if ret_func == define.trade_queryetfdetail_s_func: # 股票查询ETF成分股信息
                task_item.event_task_finish.set()
        except Exception as e:
            self.log_text = "%s：处理事件消息 %d 发生异常！%s" % (self.trade_name, ret_func, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        
        if task_item.strategy in self.strategy_dict.keys():
            self.strategy_dict[task_item.strategy].instance.OnTraderEvent(self.trade_name, ret_func, task_item)

####################################################################################################

    def UserLogIn(self, username, password):
        msg_req = {"function":define.trade_userlogin_s_func, "task_id":0, "username":username, "password":password}
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
        msg_req = {"function":define.trade_userlogout_s_func, "session":session, "task_id":0}
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
        msg_req = {"function":define.trade_subscibe_s_func, "session":session, "task_id":0, "password":password}
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
        msg_req = {"function":define.trade_unsubscibe_s_func, "session":session, "task_id":0}
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
        holder = self.holder_sh
        if order.exchange == "SZ":
            holder = self.holder_sz
        task_item = self.NewTaskItem(strategy, define.trade_placeorder_s_func)
        task_item.order = order # 在这里放入原始委托
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_placeorder_s_func, "session":self.session, "task_id":task_item.task_id, "asset_account":self.asset_account, 
                  "holder":holder, "symbol":order.symbol, "exchange":order.exchange, "price":order.price, "amount":order.amount, 
                  "entr_type":order.entr_type, "exch_side":order.exch_side}
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
            if ret_code == 0:
                #print(msg_ans["ret_data"][0]["otc_code"], msg_ans["ret_data"][0]["otc_info"])
                task_item.order.order_id = msg_ans["ret_data"][0]["order_id"] # 委托编号
                #task_item.order.status = define.order_status_s_wait_trans # 委托状态
                #print("下单应答：" + task_item.order.ToString())
                task_item.status = define.TASK_STATUS_OVER # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
            else: # 执行失败
                task_item.order.status = define.order_status_s_error_place # 委托状态
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：下单应答：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def CancelOrder(self, order, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_cancelorder_s_func)
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_cancelorder_s_func, "session":self.session, "task_id":task_item.task_id, "asset_account":self.asset_account, "order_id":order.order_id}
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
            if ret_code == 0:
                #print(msg_ans["ret_data"][0]["otc_code"], msg_ans["ret_data"][0]["otc_info"])
                #order_id = msg_ans["ret_data"][0]["order_id"] # 撤单委托号
                #print("撤单应答：", order_id)
                task_item.status = define.TASK_STATUS_OVER # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
            else: # 执行失败
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：撤单应答：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def NumberToZeroStr(self, number, str_len, decimal = 0):
        temp_string = ""
        if decimal > 0:
            temp_string = str(round(number, decimal))
        else:
            temp_string = str(number)
        need_zero = str_len - len(temp_string)
        for i in range(need_zero):
            temp_string = "0" + temp_string
        return temp_string

    def PlaceOrderBatch(self, orders, strategy): # 这里限制最大 100 个委托，需在外部调用前处理好拆单事宜
        if len(orders) > 100:
            self.log_text = "%s：批量下单：单批委托数量 %d > 100 个！" % (self.trade_name, len(orders))
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return None
        order_list = "" # 长度限制 30*500 现在windows下也有15000长度了 # 貌似windows下还是限制为 30*100 的
        order_numb = len(orders)
        batch_info = self.BatchInfo()
        for order in orders:
            # "SZ000001100010.000000000100000" -> "SZ 000001 1 00010.000 000000100 000"
            # 交易所SZ 证券代码000001 委托类别1 委托价格00010.000 委托数量000000100 订单类型000
            order_list += order.exchange + order.symbol + str(order.exch_side) + self.NumberToZeroStr(order.price, 9, 3) + self.NumberToZeroStr(order.amount, 9) + self.NumberToZeroStr(order.entr_type, 3)
            batch_item = self.BatchItem()
            batch_item.order = order # 单个合约
            batch_info.batch_orders_list.append(batch_item) # 在这里放入原始委托
        task_item = self.NewTaskItem(strategy, define.trade_placeorderbatch_s_func)
        task_item.batch = batch_info # 批量合约，BatchInfo，股票类特有
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_placeorderbatch_s_func, "session":self.session, "task_id":task_item.task_id, "asset_account":self.asset_account, "order_numb":order_numb, "order_list":order_list}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnPlaceOrderBatch(self, ret_func, msg_ans): # 每次一条
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0:
                #print(msg_ans["ret_data"][0]["otc_code"], msg_ans["ret_data"][0]["otc_info"])
                task_item.batch.batch_id = msg_ans["ret_data"][0]["batch_id"] # 批量委托编号
                task_item.batch.batch_ht = msg_ans["ret_data"][0]["batch_ht"] # 委托合同号列表
                wthth_list = task_item.batch.batch_ht.split(",") # 分割为列表
                if len(wthth_list) > 0:
                    wthth_list.pop() # 去掉最后一个空的
                if len(wthth_list) != len(task_item.batch.batch_orders_list):
                    self.log_text = "%s：批量下单应答：委托个数与合同号个数不一致！%d != %d" % (self.trade_name, len(task_item.batch.batch_orders_list), len(wthth_list))
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
                else:
                    for i in range(len(task_item.batch.batch_orders_list)): # wthth_list 与 batch_orders_list 长度和顺序都一致
                        order_id = int(wthth_list[i]) # 注意：如果某个股票委托出现异常，则该股票的委托合同号为-620002XXX，可以用 委托数量 <= 0 或 委托价格 <= 0.0 测试
                        task_item.batch.batch_orders_list[i].order.order_id = order_id # 委托编号
                        task_item.batch.batch_orders_list[i].order.batch_id = task_item.batch.batch_id # 批量委托编号
                        if order_id < 0:
                            task_item.batch.batch_orders_list[i].order.status = define.order_status_s_error_place # 委托状态
                        else: #放入 batch_orders_map 之中
                            #task_item.batch.batch_orders_list[i].order.status = define.order_status_s_wait_trans # 委托状态
                            task_item.batch.batch_orders_map[order_id] = task_item.batch.batch_orders_list[i] # BatchItem
                #print("批量下单应答：" + task_item.batch.batch_id + "：" + task_item.batch.batch_ht)
                task_item.status = define.TASK_STATUS_OVER # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
            else: # 执行失败
                for i in range(len(task_item.batch.batch_orders_list)):
                    task_item.batch.batch_orders_list[i].order.status = define.order_status_s_error_place # 委托状态
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：批量下单应答：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def CancelOrderBatch(self, batch_id, batch_ht, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_cancelorderbatch_s_func)
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_cancelorderbatch_s_func, "session":self.session, "task_id":task_item.task_id, "asset_account":self.asset_account, "batch_id":batch_id, "batch_ht":batch_ht}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnCancelOrderBatch(self, ret_func, msg_ans): # 每次一条
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0:
                #print(msg_ans["ret_data"][0]["otc_code"], msg_ans["ret_data"][0]["otc_info"])
                #print("批量撤单应答：")
                task_item.status = define.TASK_STATUS_OVER # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
            else: # 执行失败
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：批量撤单应答：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryCapital(self, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_querycapital_s_func)
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_querycapital_s_func, "session":self.session, "task_id":task_item.task_id}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnQueryCapital(self, ret_func, msg_ans): # 每次可能多条 # 原接口是同步的，字段 ret_last 均为 True 的
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0:
                for i in range(int(msg_ans["ret_numb"])):
                    #print(msg_ans["ret_data"][i]["otc_code"], msg_ans["ret_data"][i]["otc_info"])
                    capital = self.Capital()
                    capital.account = msg_ans["ret_data"][i]["account"] # 资金账号
                    capital.currency = msg_ans["ret_data"][i]["currency"] # 币种，RMB：人民币，USD：美元，HKD：港币
                    capital.available = float(msg_ans["ret_data"][i]["available"]) # 可用资金
                    capital.balance = float(msg_ans["ret_data"][i]["balance"]) # 账户余额
                    capital.frozen = float(msg_ans["ret_data"][i]["frozen"]) # 冻结金额
                    #print("客户资金：" + capital.ToString())
                    task_item.query_results.append(capital) # 查询结果数据
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

    def QueryPosition(self, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_queryposition_s_func)
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_queryposition_s_func, "session":self.session, "task_id":task_item.task_id}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnQueryPosition(self, ret_func, msg_ans): # 每次可能多条 # 原接口是同步的，字段 ret_last 均为 True 的
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0:
                for i in range(int(msg_ans["ret_numb"])):
                    #print(msg_ans["ret_data"][i]["otc_code"], msg_ans["ret_data"][i]["otc_info"])
                    position = self.Position()
                    position.holder = msg_ans["ret_data"][i]["holder"] # 股东号
                    position.exchange = msg_ans["ret_data"][i]["exchange"] # 交易所
                    position.currency = msg_ans["ret_data"][i]["currency"] # 币种
                    position.symbol = msg_ans["ret_data"][i]["symbol"] # 证券代码
                    position.security_type = msg_ans["ret_data"][i]["security_type"] # 证券类别
                    position.security_name = msg_ans["ret_data"][i]["security_name"] # 证券名称
                    position.security_qty = int(msg_ans["ret_data"][i]["security_qty"]) # 持仓数量
                    position.can_sell = int(msg_ans["ret_data"][i]["can_sell"]) # 可卖出数量
                    position.can_sub = int(msg_ans["ret_data"][i]["can_sub"]) # 可申购数量
                    position.can_red = int(msg_ans["ret_data"][i]["can_red"]) # 可赎回数量
                    position.non_tradable = int(msg_ans["ret_data"][i]["non_tradable"]) # 非流通数量
                    position.frozen_qty = int(msg_ans["ret_data"][i]["frozen_qty"]) # 冻结数量
                    position.sell_qty = int(msg_ans["ret_data"][i]["sell_qty"]) # 当日卖出成交数量
                    position.sell_money = float(msg_ans["ret_data"][i]["sell_money"]) # 当日卖出成交金额
                    position.buy_qty = int(msg_ans["ret_data"][i]["buy_qty"]) # 当日买入成交数量
                    position.buy_money = float(msg_ans["ret_data"][i]["buy_money"]) # 当日买入成交金额
                    position.sub_qty = int(msg_ans["ret_data"][i]["sub_qty"]) # 当日申购成交数量
                    position.red_qty = int(msg_ans["ret_data"][i]["red_qty"]) # 当日赎回成交数量
                    #print("客户库存：" + position.ToString())
                    task_item.query_results.append(position) # 查询结果数据
                task_item.status = define.TASK_STATUS_OVER # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
            else: # 查询失败
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：客户库存：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryOrder(self, order_id, brow_index, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_queryorder_s_func)
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_queryorder_s_func, "session":self.session, "task_id":task_item.task_id, "order_id":order_id, "brow_index":brow_index}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnQueryOrder(self, ret_func, msg_ans): # 每次可能多条 # 原接口是同步的，字段 ret_last 均为 True 的
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0:
                for i in range(int(msg_ans["ret_numb"])):
                    #print(msg_ans["ret_data"][i]["otc_code"], msg_ans["ret_data"][i]["otc_info"])
                    order = self.Order()
                    order.exchange = msg_ans["ret_data"][i]["exchange"] # 交易所
                    order.symbol = msg_ans["ret_data"][i]["symbol"] # 证券代码
                    order.security_type = msg_ans["ret_data"][i]["security_type"] # 证券类别
                    order.order_id = int(msg_ans["ret_data"][i]["order_id"]) # 委托号
                    order.entr_type = int(msg_ans["ret_data"][i]["entr_type"]) # 委托方式
                    order.exch_side = int(msg_ans["ret_data"][i]["exch_side"]) # 交易类型
                    order.price = float(msg_ans["ret_data"][i]["price"]) # 委托价格
                    order.amount = int(msg_ans["ret_data"][i]["amount"]) # 委托数量
                    order.fill_qty = int(msg_ans["ret_data"][i]["fill_amount"]) # 成交数量
                    order.cxl_qty = int(msg_ans["ret_data"][i]["cxl_qty"]) # 撤单数量
                    order.status = int(msg_ans["ret_data"][i]["report_ret"]) # 申报结果
                    order.status_msg = msg_ans["ret_data"][i]["message"] # 结果说明
                    order.brow_index = msg_ans["ret_data"][i]["brow_index"] # 增量查询索引值
                    #order.batch_id = 0 # 批量委托编号 # 委托查询不返回此项
                    #msg_ans["ret_data"][i]["holder"] # 股东号
                    #msg_ans["ret_data"][i]["currency"] # 币种
                    #msg_ans["ret_data"][i]["security_name"] # 证券名称
                    #float(msg_ans["ret_data"][i]["fill_price"]) # 成交价格
                    #float(msg_ans["ret_data"][i]["fill_money"]) # 成交金额
                    #msg_ans["ret_data"][i]["cxl_flag"] # 撤销标志
                    #float(msg_ans["ret_data"][i]["frozen"]) # 冻结资金
                    #float(msg_ans["ret_data"][i]["settlement"]) # 清算资金
                    #msg_ans["ret_data"][i]["report_time"] # 申报时间
                    #msg_ans["ret_data"][i]["order_time"] # 委托时间
                    #msg_ans["ret_data"][i]["fill_time"] # 成交时间
                    #msg_ans["ret_data"][i]["account"] # 资金账号
                    #print("当日委托：" + order.ToString())
                    task_item.query_results.append(order) # 查询结果数据
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

    def QueryTrade(self, order_id, brow_index, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_querytrans_s_func)
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_querytrans_s_func, "session":self.session, "task_id":task_item.task_id, "order_id":order_id, "brow_index":brow_index}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnQueryTrade(self, ret_func, msg_ans): # 每次可能多条 # 原接口是同步的，字段 ret_last 均为 True 的
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0:
                for i in range(int(msg_ans["ret_numb"])):
                    #print(msg_ans["ret_data"][i]["otc_code"], msg_ans["ret_data"][i]["otc_info"])
                    trans = self.Trans()
                    trans.exchange = msg_ans["ret_data"][i]["exchange"] # 交易所
                    trans.symbol = msg_ans["ret_data"][i]["symbol"] # 证券代码
                    trans.security_type = msg_ans["ret_data"][i]["security_type"] # 证券类别
                    trans.order_id = int(msg_ans["ret_data"][i]["order_id"]) # 委托号
                    trans.trans_id = msg_ans["ret_data"][i]["trans_id"] # 成交编号
                    trans.exch_side = int(msg_ans["ret_data"][i]["exch_side"]) # 交易类型
                    trans.fill_price = float(msg_ans["ret_data"][i]["fill_price"]) # 成交价格
                    trans.fill_qty = int(msg_ans["ret_data"][i]["fill_amount"]) # 成交数量
                    trans.brow_index = msg_ans["ret_data"][i]["brow_index"] # 增量查询索引值
                    #trans.fill_time = "" # 成交时间 # 成交查询不返回此项
                    #trans.cxl_qty = 0 # 撤单数量 # 成交查询不返回此项
                    #msg_ans["ret_data"][i]["holder"] # 股东号
                    #msg_ans["ret_data"][i]["currency"] # 币种
                    #msg_ans["ret_data"][i]["security_name"] # 证券名称
                    #float(msg_ans["ret_data"][i]["fill_money"]) # 成交金额
                    #msg_ans["ret_data"][i]["cxl_flag"] # 撤销标志
                    #float(msg_ans["ret_data"][i]["settlement"]) # 清算资金
                    #float(msg_ans["ret_data"][i]["commission"]) # 佣金
                    #msg_ans["ret_data"][i]["account"] # 资金账号
                    #print("当日成交：" + trans.ToString())
                    task_item.query_results.append(trans) # 查询结果数据
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

    def QueryEtfBase(self, fund_id_2, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_queryetfbase_s_func)
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_queryetfbase_s_func, "session":self.session, "task_id":task_item.task_id, "fund_id_2":fund_id_2}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnQueryEtfBase(self, ret_func, msg_ans): # 每次一条 # 原接口是同步的，字段 ret_last 均为 True 的
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0:
                for i in range(int(msg_ans["ret_numb"])):
                    #print(msg_ans["ret_data"][i]["otc_code"], msg_ans["ret_data"][i]["otc_info"])
                    etf_base_info = self.EtfBaseInfo()
                    etf_base_info.fund_name = msg_ans["ret_data"][i]["fund_name"] # 基金名称
                    etf_base_info.fund_id_1 = msg_ans["ret_data"][i]["fund_id_1"] # 申赎代码
                    etf_base_info.fund_id_2 = msg_ans["ret_data"][i]["fund_id_2"] # 基金代码
                    etf_base_info.exchange = msg_ans["ret_data"][i]["exchange"] # 交易所
                    etf_base_info.count = int(msg_ans["ret_data"][i]["count"]) # 股票记录数
                    etf_base_info.status = int(msg_ans["ret_data"][i]["status"]) # 申赎允许状态，-1：无资格，0：禁止申赎，1：允许申赎，2：允许申购，3：允许赎回
                    etf_base_info.pub_iopv = int(msg_ans["ret_data"][i]["pub_iopv"]) # 是否发布IOPV
                    etf_base_info.unit = int(msg_ans["ret_data"][i]["unit"]) # 最小申赎单位
                    etf_base_info.cash_ratio = float(msg_ans["ret_data"][i]["cash_ratio"]) # 最大现金替代比例
                    etf_base_info.cash_diff = float(msg_ans["ret_data"][i]["cash_diff"]) # T日现金差额
                    etf_base_info.iopv = float(msg_ans["ret_data"][i]["iopv"]) # T-1日单位净值
                    etf_base_info.trade_iopv = float(msg_ans["ret_data"][i]["trade_iopv"]) # T-1日申赎单位净值
                    #etf_base_info.stocks = [] # 成分股清单
                    #print("ETF基本信息：" + etf_base_info.ToString())
                    task_item.query_results.append(etf_base_info) # 查询结果数据
                task_item.status = define.TASK_STATUS_OVER # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
            else: # 查询失败
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：ETF基本信息：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryEtfDetail(self, fund_id_2, strategy):
        task_item = self.NewTaskItem(strategy, define.trade_queryetfdetail_s_func)
        self.task_dict[task_item.task_id] = task_item # 目前这里未加锁
        msg_req = {"function":define.trade_queryetfdetail_s_func, "session":self.session, "task_id":task_item.task_id, "fund_id_2":fund_id_2}
        if self.SendData(msg_req) == False:
            self.UnConnect()
            return None
        return task_item

    def OnQueryEtfDetail(self, ret_func, msg_ans): # 每次可能多条 # 原接口是同步的，字段 ret_last 均为 True 的
        #print(msg_ans["ret_func"], msg_ans["ret_code"], msg_ans["ret_info"], msg_ans["ret_task"], msg_ans["ret_last"], msg_ans["ret_numb"])
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["ret_task"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            ret_code = int(msg_ans["ret_code"])
            if ret_code == 0:
                for i in range(int(msg_ans["ret_numb"])):
                    #print(msg_ans["ret_data"][i]["otc_code"], msg_ans["ret_data"][i]["otc_info"])
                    etf_detail_info = self.EtfDetailInfo()
                    etf_detail_info.fund_name = msg_ans["ret_data"][i]["fund_name"] # 基金名称
                    etf_detail_info.stock_code = msg_ans["ret_data"][i]["stock_code"] # 成分股代码
                    etf_detail_info.stock_name = msg_ans["ret_data"][i]["stock_name"] # 成分股名称
                    etf_detail_info.stock_qty = int(msg_ans["ret_data"][i]["stock_qty"]) # 成分股数量
                    etf_detail_info.exchange = msg_ans["ret_data"][i]["exchange"]# 交易所
                    etf_detail_info.replace_flag = int(msg_ans["ret_data"][i]["replace_flag"]) # 现金替代标志，1：允许，2：必须，3：禁止
                    etf_detail_info.replace_money = float(msg_ans["ret_data"][i]["replace_money"]) # 现金替代金额
                    etf_detail_info.up_px_ratio = float(msg_ans["ret_data"][i]["up_px_ratio"]) # 溢价比例
                    #print("ETF成分信息：" + etf_detail_info.ToString())
                    task_item.query_results.append(etf_detail_info) # 查询结果数据
                task_item.status = define.TASK_STATUS_OVER # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
            else: # 查询失败
                task_item.status = define.TASK_STATUS_FAIL # 任务状态
                task_item.messages.append("%d %s" % (ret_code, msg_ans["ret_info"])) # 任务信息
                self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：ETF成分信息：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def OnOrderReply(self, ret_func, msg_ans):
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["task_id"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            order = self.Order()
            order.order_id = int(msg_ans["order_id"]) # 委托号
            order.exch_side = int(msg_ans["exch_side"]) # 交易类型
            order.symbol = msg_ans["symbol"] # 证券代码
            order.security_type = msg_ans["security_type"] # 证券类别
            order.exchange = msg_ans["exchange"] # 交易所
            order.cxl_qty = int(msg_ans["cxl_qty"]) # 撤单数量
            order.fill_qty = 0 # 总成交数量
            order.status = int(msg_ans["commit_ret"]) # 申报结果
            order.status_msg = msg_ans["commit_msg"] # 申报说明
            print("申报回报：" + order.ToString())
            if task_item.order != None:
                task_item.order_replies.append(order) # 单个合约委托回报
            elif task_item.batch != None:
                if order.order_id in task_item.batch.batch_orders_map.keys():
                    batch_item = task_item.batch.batch_orders_map[order.order_id]
                    batch_item.order_replies.append(order) # 单个合约委托回报
                else:
                    self.log_text = "%s：(批量)申报回报：未知委托编号！%d" % (self.trade_name, order.order_id)
                    self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：申报回报：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def OnTransReply(self, ret_func, msg_ans):
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["task_id"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            trans = self.Trans()
            trans.order_id = int(msg_ans["order_id"]) # 委托号
            trans.exch_side = int(msg_ans["exch_side"]) # 交易类型
            trans.trans_id = msg_ans["trans_id"] # 成交编号
            trans.symbol = msg_ans["symbol"] # 证券代码
            trans.security_type = msg_ans["security_type"] # 证券类别
            trans.exchange = msg_ans["exchange"] # 交易所
            trans.fill_qty = int(msg_ans["fill_qty"]) # 本次成交数量
            trans.fill_price = float(msg_ans["fill_price"]) # 本次成交价格
            trans.fill_time = msg_ans["fill_time"] # 成交时间
            trans.cxl_qty = int(msg_ans["cxl_qty"]) # 撤单数量
            print("成交回报：" + trans.ToString())
            if task_item.order != None:
                task_item.trans_replies.append(trans) # 单个合约成交回报
            elif task_item.batch != None:
                if trans.order_id in task_item.batch.batch_orders_map.keys():
                    batch_item = task_item.batch.batch_orders_map[trans.order_id]
                    batch_item.trans_replies.append(trans) # 单个合约成交回报
                else:
                    self.log_text = "%s：(批量)成交回报：未知委托编号！%d" % (self.trade_name, trans.order_id)
                    self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：成交回报：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def OnCancelReply(self, ret_func, msg_ans):
        ret_func = int(msg_ans["ret_func"])
        task_id = int(msg_ans["task_id"])
        if task_id in self.task_dict.keys():
            task_item = self.task_dict[task_id]
            order = self.Order()
            order.order_id = int(msg_ans["order_id"]) # 委托号
            order.exch_side = int(msg_ans["exch_side"]) # 交易类型
            order.symbol = msg_ans["symbol"] # 证券代码
            order.security_type = msg_ans["security_type"] # 证券类别
            order.exchange = msg_ans["exchange"] # 交易所
            order.cxl_qty = int(msg_ans["cxl_qty"]) # 撤单数量
            order.fill_qty = int(msg_ans["total_fill_qty"]) # 总成交数量
            if order.cxl_qty == 0:
                order.status = define.order_status_s_entire_trans # 申报结果 # 全部成交
            elif order.fill_qty == 0:
                order.status = define.order_status_s_entire_cancel # 申报结果 # 全部撤单
            else:
                order.status = define.order_status_s_part_cancel # 申报结果 # 部成部撤
            order.status_msg = "撤单成功。" # 申报说明
            print("撤单回报：" + order.ToString())
            if task_item.order != None:
                task_item.order_replies.append(order) # 单个合约委托回报
            elif task_item.batch != None:
                if order.order_id in task_item.batch.batch_orders_map.keys():
                    batch_item = task_item.batch.batch_orders_map[order.order_id]
                    batch_item.order_replies.append(order) # 单个合约委托回报
                else:
                    self.log_text = "%s：(批量)撤单回报：未知委托编号！%d" % (self.trade_name, order.order_id)
                    self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            self.SendTraderEvent(ret_func, task_item)
        else:
            self.log_text = "%s：撤单回报：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

####################################################################################################

    def QueryCapital_Syn(self, strategy, query_wait = 5):
        task_item = self.QueryCapital(strategy)
        if task_item != None:
            ret_wait = task_item.event_task_finish.wait(timeout = query_wait) # 等待结果
            if ret_wait == True:
                if task_item.status == define.TASK_STATUS_OVER:
                    for capital in task_item.query_results: #应该只有一条的
                        #self.log_text = "%s：证券资金：%s" % (strategy, capital.ToString())
                        #self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                        return [True, capital]
                    return [True, None]
                else:
                    self.log_text = "%s：证券 资金 查询失败！原因：%s" % (strategy, task_item.messages[-1])
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                    return [False, None]
            else:
                self.log_text = "%s：证券 资金 查询超时！状态：%d" % (strategy, task_item.status)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, None]
        else:
            self.log_text = "%s：证券 资金 查询异常！返回任务对象为空！" % strategy
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, None]

    def QueryPosition_Syn(self, symbol, strategy, query_wait = 5):
        task_item = self.QueryPosition(strategy)
        if task_item != None:
            ret_wait = task_item.event_task_finish.wait(timeout = query_wait) # 等待结果
            if ret_wait == True:
                if task_item.status == define.TASK_STATUS_OVER:
                    for position in task_item.query_results: #注意是：PositionDefer
                        if position.symbol == symbol:
                            return [True, position]
                        #self.log_text = "%s：证券持仓：%s" % (strategy, position.ToString())
                        #self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                    return [True, None]
                else:
                    self.log_text = "%s：证券 持仓 查询失败！原因：%s" % (strategy, task_item.messages[-1])
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                    return [False, None]
            else:
                self.log_text = "%s：证券 持仓 查询超时！状态：%d" % (strategy, task_item.status)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, None]
        else:
            self.log_text = "%s：证券 持仓 查询异常！返回任务对象为空！" % strategy
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, None]

    def QueryPosition_All_Syn(self, strategy, query_wait = 5):
        task_item = self.QueryPosition(strategy)
        if task_item != None:
            ret_wait = task_item.event_task_finish.wait(timeout = query_wait) # 等待结果
            if ret_wait == True:
                if task_item.status == define.TASK_STATUS_OVER:
                    if len(task_item.query_results) > 0:
                        #for position in task_item.query_results: #注意是：PositionDefer
                        #    self.log_text = "%s：证券持仓：%s" % (strategy, position.ToString())
                        #    self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                        return [True, task_item.query_results]
                    return [True, None]
                else:
                    self.log_text = "%s：证券 持仓 查询失败！原因：%s" % (strategy, task_item.messages[-1])
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                    return [False, None]
            else:
                self.log_text = "%s：证券 持仓 查询超时！状态：%d" % (strategy, task_item.status)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, None]
        else:
            self.log_text = "%s：证券 持仓 查询异常！返回任务对象为空！" % strategy
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, None]

    def QueryOrder_Syn(self, order_id, brow_index, strategy, query_wait = 5):
        task_item = self.QueryOrder(order_id, brow_index, strategy)
        if task_item != None:
            ret_wait = task_item.event_task_finish.wait(timeout = query_wait) # 等待结果
            if ret_wait == True:
                if task_item.status == define.TASK_STATUS_OVER:
                    for order in task_item.query_results:
                        if order.order_id == order_id:
                            return [True, order]
                        #self.log_text = "%s：证券委托：%s" % (strategy, order.ToString())
                        #self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                    return [True, None]
                else:
                    self.log_text = "%s：证券 委托 查询失败！原因：%s" % (strategy, task_item.messages[-1])
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                    return [False, None]
            else:
                self.log_text = "%s：证券 委托 查询超时！状态：%d" % (strategy, task_item.status)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, None]
        else:
            self.log_text = "%s：证券 委托 查询异常！返回任务对象为空！" % strategy
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, None]

    def QueryTrade_Syn(self, order_id, brow_index, strategy, query_wait = 5): # 返回列表
        trans_list = []
        task_item = self.QueryTrade(order_id, brow_index, strategy)
        if task_item != None:
            ret_wait = task_item.event_task_finish.wait(timeout = query_wait) # 等待结果
            if ret_wait == True:
                if task_item.status == define.TASK_STATUS_OVER:
                    for trans in task_item.query_results:
                        if trans.order_id == order_id:
                            trans_list.append(trans) #
                        #self.log_text = "%s：证券成交：%s" % (strategy, trans.ToString())
                        #self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                    return [True, trans_list]
                else:
                    self.log_text = "%s：证券 成交 查询失败！原因：%s" % (strategy, task_item.messages[-1])
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                    return [False, None]
            else:
                self.log_text = "%s：证券 成交 查询超时！状态：%d" % (strategy, task_item.status)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, None]
        else:
            self.log_text = "%s：证券 成交 查询异常！返回任务对象为空！" % strategy
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, None]

    def QueryEtfBase_Syn(self, fund_id_2, strategy, query_wait = 5):
        task_item = self.QueryEtfBase(fund_id_2, strategy)
        if task_item != None:
            ret_wait = task_item.event_task_finish.wait(timeout = query_wait) # 等待结果
            if ret_wait == True:
                if task_item.status == define.TASK_STATUS_OVER:
                    for etf_base_info in task_item.query_results: # 应该只有一条的
                        #self.log_text = "%s：证券资金：%s" % (strategy, etf_base_info.ToString())
                        #self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                        return [True, etf_base_info]
                    return [True, None]
                else:
                    self.log_text = "%s：证券 ETF基本 查询失败！原因：%s" % (strategy, task_item.messages[-1])
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                    return [False, None]
            else:
                self.log_text = "%s：证券 ETF基本 查询超时！状态：%d" % (strategy, task_item.status)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, None]
        else:
            self.log_text = "%s：证券 ETF基本 查询异常！返回任务对象为空！" % strategy
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, None]

    def QueryEtfDetail_Syn(self, fund_id_2, strategy, query_wait = 5): # 返回列表
        stock_list = []
        task_item = self.QueryEtfDetail(fund_id_2, strategy)
        if task_item != None:
            ret_wait = task_item.event_task_finish.wait(timeout = query_wait) # 等待结果
            if ret_wait == True:
                if task_item.status == define.TASK_STATUS_OVER:
                    for stock in task_item.query_results:
                        stock_list.append(stock) #
                        #self.log_text = "%s：证券ETF成分股：%s" % (strategy, stock.ToString())
                        #self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                    return [True, stock_list]
                else:
                    self.log_text = "%s：证券 ETF成分股 查询失败！原因：%s" % (strategy, task_item.messages[-1])
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                    return [False, None]
            else:
                self.log_text = "%s：证券 ETF成分股 查询超时！状态：%d" % (strategy, task_item.status)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, None]
        else:
            self.log_text = "%s：证券 ETF成分股 查询异常！返回任务对象为空！" % strategy
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, None]

    def PlaceOrder_FOC_Syn(self, label, order, strategy, trade_wait = 1, cancel_wait = 5):
        self.log_text = "%s: 准备  %s: %s" % (strategy, label, order.ToString())
        self.logger.SendMessage("D", 0, self.log_cate, self.log_text, "T")
        
#        time.sleep(2)
#        order.fill_qty = order.amount
#        return [True, order] # 测试！！
        
        task_item_place = self.PlaceOrder(order, strategy)
        if task_item_place == None:
            self.log_text = "%s：委托 %s %s 下单异常！返回任务对象为空！" % (strategy, label, order.symbol)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, order]
        ret_wait = task_item_place.event_task_finish.wait(trade_wait) # 等待结果
        # 在 wait 结束时，要么报单异常，要么交易结束，要么等待超时
        if ret_wait == True: # 报单异常、交易结束
            if task_item_place.status == define.TASK_STATUS_FAIL: # 报单异常
                self.log_text = "%s: 委托 %s %s 下单异常！任务： %d， 原因: %s" % (strategy, label, order.symbol, task_item_place.task_id, task_item_place.messages[-1])
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, task_item_place.order]
            else: # 交易结束
                self.log_text = "%s: 委托 %s %s 交易完成。任务： %d， 状态: %d, 成交: %d" % (strategy, label, order.symbol, task_item_place.task_id, task_item_place.status, task_item_place.order.fill_qty)
                self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                return [True, task_item_place.order]
        else: # 等待超时
            if task_item_place.order.order_id != "":
                self.log_text = "%s: 委托 %s %s 准备撤单。 委托： %s， 超时： %d" % (strategy, label, order.symbol, task_item_place.order.order_id, trade_wait)
                self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                task_item_cancel = self.CancelOrder(task_item_place.order, strategy)
                if task_item_cancel == None:
                    self.log_text = "%s：委托 %s %s 撤单异常！返回任务对象为空！" % (strategy, label, order.symbol)
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                    return [False, task_item_place.order]
                ret_wait = task_item_place.event_task_finish.wait(cancel_wait) # 等待结果 #使用 task_item_place
                # 在 wait 结束时，要么交易结束，要么等待超时
                if ret_wait == True: # 交易结束
                    self.log_text = "%s：委托 %s %s 撤单完成。任务：%d，状态：%d，成交：%d" % (strategy, label, order.symbol, task_item_place.task_id, task_item_place.order.status, task_item_place.order.fill_qty)
                    self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                    return [True, task_item_place.order]
                else: # 等待超时
                    if task_item_cancel.status == define.TASK_STATUS_FAIL: # 撤单异常
                        self.log_text = "%s：委托 %s %s 撤单异常！任务：%d，原因：%s" % (strategy, label, order.symbol, task_item_cancel.task_id, task_item_cancel.messages[-1])
                        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                        return [False, task_item_place.order]
                    else:
                        self.log_text = "%s：委托 %s %s 撤单超时！任务：%d，超时：%d" % (strategy, label, order.symbol, task_item_cancel.task_id, cancel_wait)
                        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                        return [False, task_item_place.order]
            else:
                self.log_text = "%s：委托 %s %s 撤单时缺少委托编号！任务：%d" % (strategy, label, order.symbol, task_item_place.task_id)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, task_item_place.order]

####################################################################################################

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    stock_trader = TradeX_Stk_Sy(None, "股票类交易", "test", 0, "10.0.7.80", 2001, "020090030000", "123321", "A679624770", "0124819363", "LHTZ_20170428001_000", 30)
    stock_trader.Start()
    
    time.sleep(5)
    
    # entr_type # 委托方式，1：限价，2：市价
    # exch_side # 交易类型，1：买入，2：卖出，29：申购，30：赎回，37：质押入库，38：质押出库
    #                      A0：A股，E0：ETF基金，E1：ETF资金，E3：ETF发行，E4：ETF申赎，EZ：国债ETF，F8：质押券，
    #                      H0：国债回购，H1：企债回购，H2：买断回购，H3：账户回购，Z0：现券国债，Z1：记帐国债，Z4：企业债券
    
    #order = stock_trader.Order(symbol = "600001", exchange = "SH", price = 5.29, amount = 100, entr_type = 1, exch_side = 1)
    #order = stock_trader.Order(symbol = "601618", exchange = "SH", price = 3.28, amount = 1000, entr_type = 1, exch_side = 2)
    #order = stock_trader.Order(symbol = "159901", exchange = "SZ", price = 3.69, amount = 100, entr_type = 1, exch_side = 1)
    #order = stock_trader.Order(symbol = "159901", exchange = "SZ", price = 3.69, amount = 100, entr_type = 1, exch_side = 2)
    
    #task_place = stock_trader.PlaceOrder(order, "strategy")
    #print(task_place.task_id)
    #time.sleep(2)
    #stock_trader.PlaceOrder(order, "strategy")
    #time.sleep(2)
    #task_cancel = stock_trader.CancelOrder(task_place.order, "strategy") #order.order_id = "O50215091607360574"
    #time.sleep(2)
    #stock_trader.PlaceOrder_FOC_Syn("", order, "strategy")
    #time.sleep(2)
    
    #stock_trader.QueryCapital("strategy")
    #time.sleep(2)
    #stock_trader.QueryCapital_Syn("strategy")
    #time.sleep(2)
    
    #stock_trader.QueryPosition("strategy")
    #time.sleep(2)
    #stock_trader.QueryPosition_Syn(0, "strategy")
    #time.sleep(2)
    
    #stock_trader.QueryOrder(0, "", "strategy")
    #time.sleep(2)
    #stock_trader.QueryOrder_Syn(0, "", "strategy")
    #time.sleep(2)
    
    #stock_trader.QueryTrade(0, "", "strategy")
    #time.sleep(2)
    #stock_trader.QueryTrade_Syn(0, "", "strategy")
    #time.sleep(2)
    
    #stock_trader.QueryEtfBase("159901", "strategy")
    #time.sleep(2)
    #stock_trader.QueryEtfBase_Syn("159901", "strategy")
    #time.sleep(2)
    
    #stock_trader.QueryEtfDetail("159901", "strategy")
    #time.sleep(2)
    #stock_trader.QueryEtfDetail_Syn("159901", "strategy")
    #time.sleep(2)
    
    #time.sleep(5)
    
    stock_trader.Stop()
    
    sys.exit(app.exec_())
