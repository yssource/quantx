
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

    def __init__(self, parent, trade_name, tradeFlag, tradeSave, address, port, username, password, holderSH, holderSZ, asset_account, loginTimeOut):
        self.log_text = ""
        self.log_cate = "TradeX_Stk_Sy"
        self.config = config.Config()
        self.logger = logger.Logger()
        self.parent = parent
        self.trade_name = trade_name
        self.tradeFlag = tradeFlag
        self.tradeSave = tradeSave
        self.address = address
        self.port = port
        self.username = username
        self.password = password
        self.holderSH = holderSH
        self.holderSZ = holderSZ
        self.asset_account = asset_account
        self.loginTimeOut = loginTimeOut
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
        
        self.taskDict = {}
        self.taskIdLock = threading.Lock()
        self.straDict = center.Center().data.strategies
        
        self.showDebugInfo = self.config.cfg_main.stra_debug_info # 为 1 或 0

    def __del__(self):
        self.started = False

    def NewTaskItem(self, strategy, function):
        self.taskIdLock.acquire()
        self.task_id += 1
        task_id = copy.deepcopy(self.task_id) # copy
        self.taskIdLock.release()
        taskItem = self.TaskItem()
        taskItem.task_id = task_id # 任务标识
        taskItem.strategy = strategy # 策略标识
        taskItem.function = function # 功能编号
        taskItem.status = define.TASK_STATUS_EXEC # 任务状态
        taskItem.messages.append("开始执行任务....") # 任务信息
        #taskItem.order = None # 单个合约
        #taskItem.orderReplies = [] # 单个合约委托回报
        #taskItem.transReplies = [] # 单个合约成交回报
        #taskItem.queryResults = [] # 查询结果数据
        #self.batch = None # 批量合约，BatchInfo，股票类特有
        return taskItem

    def RegReplyMsgHandleFunc(self):
        self.replyMsgHandleFunc_Sys = {}
        self.replyMsgHandleFunc_Sys[define.trade_userlogin_s_func] = self.OnUserLogIn
        self.replyMsgHandleFunc_Sys[define.trade_userlogout_s_func] = self.OnUserLogOut
        self.replyMsgHandleFunc_Sys[define.trade_subscibe_s_func] = self.OnSubscibe
        self.replyMsgHandleFunc_Sys[define.trade_unsubscibe_s_func] = self.OnUnsubscibe
        self.replyMsgHandleFunc_Usr = {}
        self.replyMsgHandleFunc_Usr[define.trade_placeorder_s_func] = self.OnPlaceOrder
        self.replyMsgHandleFunc_Usr[define.trade_cancelorder_s_func] = self.OnCancelOrder
        self.replyMsgHandleFunc_Usr[define.trade_placeorderbatch_s_func] = self.OnPlaceOrderBatch
        self.replyMsgHandleFunc_Usr[define.trade_cancelorderbatch_s_func] = self.OnCancelOrderBatch
        self.replyMsgHandleFunc_Usr[define.trade_querycapital_s_func] = self.OnQueryCapital
        self.replyMsgHandleFunc_Usr[define.trade_queryposition_s_func] = self.OnQueryPosition
        self.replyMsgHandleFunc_Usr[define.trade_queryorder_s_func] = self.OnQueryOrder
        self.replyMsgHandleFunc_Usr[define.trade_querytrans_s_func] = self.OnQueryTrade
        self.replyMsgHandleFunc_Usr[define.trade_queryetfbase_s_func] = self.OnQueryEtfBase
        self.replyMsgHandleFunc_Usr[define.trade_queryetfdetail_s_func] = self.OnQueryEtfDetail
        self.replyMsgHandleFunc_Usr[define.trade_orderreply_s_func] = self.OnOrderReply
        self.replyMsgHandleFunc_Usr[define.trade_transreply_s_func] = self.OnTransReply
        self.replyMsgHandleFunc_Usr[define.trade_cancelreply_s_func] = self.OnCancelReply

    def Start(self):
        self.log_text = "%s：用户 启动 交易服务..." % self.trade_name
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        if self.started == False:
            if self.DoConnect(self.address, self.port):
                self.started = True
                self.userstop = False #
                self.threadRecv = threading.Thread(target = self.Thread_Recv)
                self.threadRecv.start()
                time.sleep(1)
                self.threadTime = threading.Thread(target = self.Thread_Time)
                self.threadTime.start()
            else:
                self.log_text = "%s：启动时连接交易服务器失败！" % self.trade_name
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

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
                waitCount = 0
                while self.userlogin == False and waitCount < self.loginTimeOut:
                    time.sleep(1)
                    waitCount += 1
                if self.userlogin == False:
                    self.log_text = "%s：重连时登录交易柜台超时！" % self.trade_name
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            if self.connected == True and self.userlogin == True and self.subscibed == False and self.userstop == False:
                self.Subscibe(self.session, self.password)
                waitCount = 0
                while self.subscibed == False and waitCount < self.loginTimeOut:
                    time.sleep(1)
                    waitCount += 1
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
        if self.sock:
            self.sock.close()

    def OnReplyMsg(self, retFunc, msgAns):
        try:
            if retFunc in self.replyMsgHandleFunc_Sys.keys():
                self.OnReplyMsg_Sys(retFunc, msgAns)
            else:
                self.OnReplyMsg_Usr(retFunc, msgAns)
        except Exception as e:
            self.log_text = "%s：处理应答消息发生异常！%s" % (self.trade_name, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def OnReplyMsg_Sys(self, retFunc, msgAns):
        try:
            retInfo = msgAns["ret_info"]
            retCode = int(msgAns["ret_code"])
            if retFunc in self.replyMsgHandleFunc_Sys.keys():
                self.replyMsgHandleFunc_Sys[retFunc](retCode, retInfo, msgAns)
            else:
                self.log_text = "%s：处理 系统 应答消息类型未知！%d" % (self.trade_name, retFunc)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            if self.parent != None: # 发给上层更新用户界面信息
                self.parent.OnTradeReplyMsg(self.trade_name, retFunc, retCode, retInfo)
        except Exception as e:
            self.log_text = "%s：处理 系统 应答消息发生异常！%s" % (self.trade_name, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def OnReplyMsg_Usr(self, retFunc, msgAns):
        try:
            if retFunc in self.replyMsgHandleFunc_Usr.keys():
                self.replyMsgHandleFunc_Usr[retFunc](retFunc, msgAns)
            else:
                self.log_text = "%s：处理 用户 应答消息类型未知！%d" % (self.trade_name, retFunc)
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

    def SendTraderEvent(self, retFunc, taskItem):
        #print(retFunc, taskItem.ToString())
        try:
            # 证券回报类
            if retFunc == define.trade_orderreply_s_func: # 股票报单回报，接口 APE 报单回报只有一个
                if taskItem.order != None:
                    orderReply = taskItem.order_replies[-1] # 取最新一个
                    if taskItem.order.order_id == "":
                        taskItem.order.order_id = orderReply.order_id # 委托编号
                    # 接口 APE 只在委托报入时有一个报单回报，之后是一系列成交回报，或者因为撤单才会有另外的撤单回报，故采用成交回报累加
                    taskItem.order.status = orderReply.status # 委托状态
                    # 0：未申报，1：正在申报，2：已申报未成交，3：非法委托，4：申请资金授权中，
                    # 5：部分成交，6：全部成交，7：部成部撤，8：全部撤单，9：撤单未成，10：等待人工申报
                    # 委托交易结束：非法委托、全部成交、部成部撤、全部撤单
                    if orderReply.status == 3 or orderReply.status == 6 or orderReply.status == 7 or orderReply.status == 8: # 因为撤单回报独立，估计不会有 7：部成部撤，甚至可能不会有 8：全部撤单
                        taskItem.event_task_finish.set()
                elif taskItem.batch != None:
                    pass
            if retFunc == define.trade_cancelreply_s_func: # 股票撤单回报，接口 APE 撤单回报只有一个
                if taskItem.order != None:
                    orderReply = taskItem.order_replies[-1] # 取最新一个
                    if taskItem.order.order_id == "":
                        taskItem.order.order_id = orderReply.order_id # 委托编号
                    taskItem.order.status = orderReply.status # 委托状态
                    taskItem.order.fill_qty = orderReply.fill_qty # 总成交数量
                    # 委托交易结束：非法委托、全部成交、部成部撤、全部撤单
                    if orderReply.status == 3 or orderReply.status == 6 or orderReply.status == 7 or orderReply.status == 8: # 撤单回报估计不会有 3：非法委托
                        taskItem.event_task_finish.set()
                elif taskItem.batch != None:
                    pass
            if retFunc == define.trade_transreply_s_func: # 股票成交回报，接口 APE 成交回报会有多个
                if taskItem.order != None:
                    transReply = taskItem.trans_replies[-1] # 取最新一个
                    if taskItem.order.order_id == "":
                        taskItem.order.order_id = transReply.order_id # 委托编号
                    taskItem.order.fill_qty += transReply.fill_qty # 本次成交数量
                    if taskItem.order.fill_qty >= taskItem.order.amount: # 全部成交
                        taskItem.order.status = 6 # 全部成交
                        taskItem.event_task_finish.set()
                elif taskItem.batch != None:
                    pass
            
            # 证券委托类
            if retFunc == define.trade_placeorder_s_func: # 股票单个证券委托下单
                if taskItem.status == define.TASK_STATUS_FAIL: # 这里只关注失败的，成功的根据成交回报处理
                    taskItem.event_task_finish.set() # 标记 下单 事务结束
            if retFunc == define.trade_cancelorder_s_func: # 股票单个证券委托撤单
                taskItem.event_task_finish.set() # 标记 撤单 事务结束
            if retFunc == define.trade_placeorderbatch_s_func: # 股票批量证券委托下单
                pass
            if retFunc == define.trade_cancelorderbatch_s_func: # 股票批量证券委托撤单
                pass
            
            # 证券查询类
            if retFunc == define.trade_querycapital_s_func: # 股票查询客户资金
                taskItem.event_task_finish.set()
            if retFunc == define.trade_queryposition_s_func: # 股票查询客户持仓
                taskItem.event_task_finish.set()
            if retFunc == define.trade_queryorder_s_func: # 股票查询客户当日委托
                taskItem.event_task_finish.set()
            if retFunc == define.trade_querytrans_s_func: # 股票查询客户当日成交
                taskItem.event_task_finish.set()
            if retFunc == define.trade_queryetfbase_s_func: # 股票查询ETF基本信息
                taskItem.event_task_finish.set()
            if retFunc == define.trade_queryetfdetail_s_func: # 股票查询ETF成分股信息
                taskItem.event_task_finish.set()
        except Exception as e:
            self.log_text = "%s：处理事件消息 %d 发生异常！%s" % (self.trade_name, retFunc, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        
        if taskItem.strategy in self.straDict.keys():
            self.straDict[taskItem.strategy].instance.OnTraderEvent(self.trade_name, retFunc, taskItem)

####################################################################################################

    def UserLogIn(self, username, password):
        msgReq = {"function":define.trade_userlogin_s_func, "task_id":0, "username":username, "password":password}
        if self.SendData(msgReq) == False:
            self.UnConnect()

    def OnUserLogIn(self, retCode, retInfo, msgAns):
        if retCode == 0:
            self.session = int(msgAns["ret_data"][0]["session"])
            self.log_text = "%s：交易登录成功。%d %s" % (self.trade_name, self.session, retInfo)
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            self.userlogin = True
        else:
            self.log_text = "%s：交易登录失败！%d %s" % (self.trade_name, retCode, retInfo)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def UserLogOut(self, session):
        msgReq = {"function":define.trade_userlogout_s_func, "session":session, "task_id":0}
        if self.SendData(msgReq) == False:
            self.UnConnect()

    def OnUserLogOut(self, retCode, retInfo, msgAns):
        if retCode == 0:
            self.log_text = "%s：交易登出成功。%d %s" % (self.trade_name, self.session, retInfo)
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            self.userlogin = False
        else:
            self.log_text = "%s：交易登出失败！%d %s" % (self.trade_name, retCode, retInfo)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def Subscibe(self, session, password):
        msgReq = {"function":define.trade_subscibe_s_func, "session":session, "task_id":0, "password":password}
        if self.SendData(msgReq) == False:
            self.UnConnect()

    def OnSubscibe(self, retCode, retInfo, msgAns):
        if retCode == 0:
            self.log_text = "%s：消息订阅成功。%d %s" % (self.trade_name, self.session, retInfo)
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            self.subscibed = True
        else:
            self.log_text = "%s：消息订阅失败！%d %s" % (self.trade_name, retCode, retInfo)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def Unsubscibe(self, session):
        msgReq = {"function":define.trade_unsubscibe_s_func, "session":session, "task_id":0}
        if self.SendData(msgReq) == False:
            self.UnConnect()

    def OnUnsubscibe(self, retCode, retInfo, msgAns):
        if retCode == 0:
            self.log_text = "%s：消息退订成功。%d %s" % (self.trade_name, self.session, retInfo)
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            self.subscibed = False
        else:
            self.log_text = "%s：消息退订失败！%d %s" % (self.trade_name, retCode, retInfo)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

####################################################################################################

    def PlaceOrder(self, order, strategy):
        holder = self.holderSH
        if order.exchange == "SZ":
            holder = self.holderSZ
        taskItem = self.NewTaskItem(strategy, define.trade_placeorder_s_func)
        taskItem.order = order # 在这里放入原始委托
        self.taskDict[taskItem.task_id] = taskItem # 目前这里未加锁
        msgReq = {"function":define.trade_placeorder_s_func, "session":self.session, "task_id":taskItem.task_id, "asset_account":self.asset_account, 
                  "holder":holder, "symbol":order.symbol, "exchange":order.exchange, "price":order.price, "amount":order.amount, 
                  "entr_type":order.entr_type, "exch_side":order.exch_side}
        if self.SendData(msgReq) == False:
            self.UnConnect()
            return None
        return taskItem

    def OnPlaceOrder(self, retFunc, msgAns): # 每次一条
        #print(msgAns["ret_func"], msgAns["ret_code"], msgAns["ret_info"], msgAns["ret_task"], msgAns["ret_last"], msgAns["ret_numb"])
        retFunc = int(msgAns["ret_func"])
        task_id = int(msgAns["ret_task"])
        if task_id in self.taskDict.keys():
            taskItem = self.taskDict[task_id]
            retCode = int(msgAns["ret_code"])
            if retCode == 0:
                #print(msgAns["ret_data"][0]["otc_code"], msgAns["ret_data"][0]["otc_info"])
                taskItem.order.order_id = msgAns["ret_data"][0]["order_id"] # 委托编号
                #taskItem.order.status = define.order_status_s_wait_trans # 委托状态
                #print("下单应答：" + taskItem.order.ToString())
                taskItem.status = define.TASK_STATUS_OVER # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
            else: # 执行失败
                taskItem.order.status = define.order_status_s_error_place # 委托状态
                taskItem.status = define.TASK_STATUS_FAIL # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
        else:
            self.log_text = "%s：下单应答：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def CancelOrder(self, order, strategy):
        taskItem = self.NewTaskItem(strategy, define.trade_cancelorder_s_func)
        self.taskDict[taskItem.task_id] = taskItem # 目前这里未加锁
        msgReq = {"function":define.trade_cancelorder_s_func, "session":self.session, "task_id":taskItem.task_id, "asset_account":self.asset_account, "order_id":order.order_id}
        if self.SendData(msgReq) == False:
            self.UnConnect()
            return None
        return taskItem

    def OnCancelOrder(self, retFunc, msgAns): # 每次一条
        #print(msgAns["ret_func"], msgAns["ret_code"], msgAns["ret_info"], msgAns["ret_task"], msgAns["ret_last"], msgAns["ret_numb"])
        retFunc = int(msgAns["ret_func"])
        task_id = int(msgAns["ret_task"])
        if task_id in self.taskDict.keys():
            taskItem = self.taskDict[task_id]
            retCode = int(msgAns["ret_code"])
            if retCode == 0:
                #print(msgAns["ret_data"][0]["otc_code"], msgAns["ret_data"][0]["otc_info"])
                #order_id = msgAns["ret_data"][0]["order_id"] # 撤单委托号
                #print("撤单应答：", order_id)
                taskItem.status = define.TASK_STATUS_OVER # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
            else: # 执行失败
                taskItem.status = define.TASK_STATUS_FAIL # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
        else:
            self.log_text = "%s：撤单应答：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def NumberToZeroStr(self, number, strLen, decimal = 0):
        tempString = ""
        if decimal > 0:
            tempString = str(round(number, decimal))
        else:
            tempString = str(number)
        needZero = strLen - len(tempString)
        for i in range(needZero):
            tempString = "0" + tempString
        return tempString

    def PlaceOrderBatch(self, orders, strategy): # 这里限制最大 100 个委托，需在外部调用前处理好拆单事宜
        if len(orders) > 100:
            self.log_text = "%s：批量下单：单批委托数量 %d > 100 个！" % (self.trade_name, len(orders))
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return None
        order_list = "" # 长度限制 30*500 现在windows下也有15000长度了 # 貌似windows下还是限制为 30*100 的
        order_numb = len(orders)
        batchInfo = self.BatchInfo()
        for order in orders:
            # "SZ000001100010.000000000100000" -> "SZ 000001 1 00010.000 000000100 000"
            # 交易所SZ 证券代码000001 委托类别1 委托价格00010.000 委托数量000000100 订单类型000
            order_list += order.exchange + order.symbol + str(order.exch_side) + self.numberToZeroStr(order.price, 9, 3) + self.numberToZeroStr(order.amount, 9) + self.numberToZeroStr(order.entr_type, 3)
            batchItem = self.BatchItem()
            batchItem.order = order # 单个合约
            batchInfo.batch_orders_list.append(batchItem) # 在这里放入原始委托
        taskItem = self.NewTaskItem(strategy, define.trade_placeorderbatch_s_func)
        taskItem.batch = batchInfo # 批量合约，BatchInfo，股票类特有
        self.taskDict[taskItem.task_id] = taskItem # 目前这里未加锁
        msgReq = {"function":define.trade_placeorderbatch_s_func, "session":self.session, "task_id":taskItem.task_id, "asset_account":self.asset_account, "order_numb":order_numb, "order_list":order_list}
        if self.SendData(msgReq) == False:
            self.UnConnect()
            return None
        return taskItem

    def OnPlaceOrderBatch(self, retFunc, msgAns): # 每次一条
        #print(msgAns["ret_func"], msgAns["ret_code"], msgAns["ret_info"], msgAns["ret_task"], msgAns["ret_last"], msgAns["ret_numb"])
        retFunc = int(msgAns["ret_func"])
        task_id = int(msgAns["ret_task"])
        if task_id in self.taskDict.keys():
            taskItem = self.taskDict[task_id]
            retCode = int(msgAns["ret_code"])
            if retCode == 0:
                #print(msgAns["ret_data"][0]["otc_code"], msgAns["ret_data"][0]["otc_info"])
                taskItem.batch.batch_id = msgAns["ret_data"][0]["batch_id"] # 批量委托编号
                taskItem.batch.batch_ht = msgAns["ret_data"][0]["batch_ht"] # 委托合同号列表
                wththList = taskItem.batch.batch_ht.split(",") # 分割为列表
                if len(wththList) > 0:
                    wththList.pop() # 去掉最后一个空的
                if len(wththList) != len(taskItem.batch.batch_orders_list):
                    self.log_text = "%s：批量下单应答：委托个数与合同号个数不一致！%d != %d" % (self.trade_name, len(taskItem.batch.batch_orders_list), len(wththList))
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
                else:
                    for i in range(len(taskItem.batch.batch_orders_list)): # wththList 与 batch_orders_list 长度和顺序都一致
                        order_id = int(wththList[i]) # 注意：如果某个股票委托出现异常，则该股票的委托合同号为-620002XXX，可以用 委托数量 <= 0 或 委托价格 <= 0.0 测试
                        taskItem.batch.batch_orders_list[i].order.order_id = order_id # 委托编号
                        taskItem.batch.batch_orders_list[i].order.batch_id = taskItem.batch.batch_id # 批量委托编号
                        if order_id < 0:
                            taskItem.batch.batch_orders_list[i].order.status = define.order_status_s_error_place # 委托状态
                        else: #放入 batch_orders_map 之中
                            #taskItem.batch.batch_orders_list[i].order.status = define.order_status_s_wait_trans # 委托状态
                            taskItem.batch.batch_orders_map[order_id] = taskItem.batch.batch_orders_list[i] # BatchItem
                #print("批量下单应答：" + taskItem.batch.batch_id + "：" + taskItem.batch.batch_ht)
                taskItem.status = define.TASK_STATUS_OVER # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
            else: # 执行失败
                for i in range(len(taskItem.batch.batch_orders_list)):
                    taskItem.batch.batch_orders_list[i].order.status = define.order_status_s_error_place # 委托状态
                taskItem.status = define.TASK_STATUS_FAIL # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
        else:
            self.log_text = "%s：批量下单应答：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def CancelOrderBatch(self, batch_id, batch_ht, strategy):
        taskItem = self.NewTaskItem(strategy, define.trade_cancelorderbatch_s_func)
        self.taskDict[taskItem.task_id] = taskItem # 目前这里未加锁
        msgReq = {"function":define.trade_cancelorderbatch_s_func, "session":self.session, "task_id":taskItem.task_id, "asset_account":self.asset_account, "batch_id":batch_id, "batch_ht":batch_ht}
        if self.SendData(msgReq) == False:
            self.UnConnect()
            return None
        return taskItem

    def OnCancelOrderBatch(self, retFunc, msgAns): # 每次一条
        #print(msgAns["ret_func"], msgAns["ret_code"], msgAns["ret_info"], msgAns["ret_task"], msgAns["ret_last"], msgAns["ret_numb"])
        retFunc = int(msgAns["ret_func"])
        task_id = int(msgAns["ret_task"])
        if task_id in self.taskDict.keys():
            taskItem = self.taskDict[task_id]
            retCode = int(msgAns["ret_code"])
            if retCode == 0:
                #print(msgAns["ret_data"][0]["otc_code"], msgAns["ret_data"][0]["otc_info"])
                #print("批量撤单应答：")
                taskItem.status = define.TASK_STATUS_OVER # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
            else: # 执行失败
                taskItem.status = define.TASK_STATUS_FAIL # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
        else:
            self.log_text = "%s：批量撤单应答：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryCapital(self, strategy):
        taskItem = self.NewTaskItem(strategy, define.trade_querycapital_s_func)
        self.taskDict[taskItem.task_id] = taskItem # 目前这里未加锁
        msgReq = {"function":define.trade_querycapital_s_func, "session":self.session, "task_id":taskItem.task_id}
        if self.SendData(msgReq) == False:
            self.UnConnect()
            return None
        return taskItem

    def OnQueryCapital(self, retFunc, msgAns): # 每次可能多条 # 原接口是同步的，字段 ret_last 均为 True 的
        #print(msgAns["ret_func"], msgAns["ret_code"], msgAns["ret_info"], msgAns["ret_task"], msgAns["ret_last"], msgAns["ret_numb"])
        retFunc = int(msgAns["ret_func"])
        task_id = int(msgAns["ret_task"])
        if task_id in self.taskDict.keys():
            taskItem = self.taskDict[task_id]
            retCode = int(msgAns["ret_code"])
            if retCode == 0:
                for i in range(int(msgAns["ret_numb"])):
                    #print(msgAns["ret_data"][i]["otc_code"], msgAns["ret_data"][i]["otc_info"])
                    capital = self.Capital()
                    capital.account = msgAns["ret_data"][i]["account"] # 资金账号
                    capital.currency = msgAns["ret_data"][i]["currency"] # 币种，RMB：人民币，USD：美元，HKD：港币
                    capital.available = float(msgAns["ret_data"][i]["available"]) # 可用资金
                    capital.balance = float(msgAns["ret_data"][i]["balance"]) # 账户余额
                    capital.frozen = float(msgAns["ret_data"][i]["frozen"]) # 冻结金额
                    #print("客户资金：" + capital.ToString())
                    taskItem.query_results.append(capital) # 查询结果数据
                taskItem.status = define.TASK_STATUS_OVER # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
            else: # 查询失败
                taskItem.status = define.TASK_STATUS_FAIL # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
        else:
            self.log_text = "%s：客户资金：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryPosition(self, strategy):
        taskItem = self.NewTaskItem(strategy, define.trade_queryposition_s_func)
        self.taskDict[taskItem.task_id] = taskItem # 目前这里未加锁
        msgReq = {"function":define.trade_queryposition_s_func, "session":self.session, "task_id":taskItem.task_id}
        if self.SendData(msgReq) == False:
            self.UnConnect()
            return None
        return taskItem

    def OnQueryPosition(self, retFunc, msgAns): # 每次可能多条 # 原接口是同步的，字段 ret_last 均为 True 的
        #print(msgAns["ret_func"], msgAns["ret_code"], msgAns["ret_info"], msgAns["ret_task"], msgAns["ret_last"], msgAns["ret_numb"])
        retFunc = int(msgAns["ret_func"])
        task_id = int(msgAns["ret_task"])
        if task_id in self.taskDict.keys():
            taskItem = self.taskDict[task_id]
            retCode = int(msgAns["ret_code"])
            if retCode == 0:
                for i in range(int(msgAns["ret_numb"])):
                    #print(msgAns["ret_data"][i]["otc_code"], msgAns["ret_data"][i]["otc_info"])
                    position = self.Position()
                    position.holder = msgAns["ret_data"][i]["holder"] # 股东号
                    position.exchange = msgAns["ret_data"][i]["exchange"] # 交易所
                    position.currency = msgAns["ret_data"][i]["currency"] # 币种
                    position.symbol = msgAns["ret_data"][i]["symbol"] # 证券代码
                    position.security_type = msgAns["ret_data"][i]["security_type"] # 证券类别
                    position.security_name = msgAns["ret_data"][i]["security_name"] # 证券名称
                    position.security_qty = int(msgAns["ret_data"][i]["security_qty"]) # 持仓数量
                    position.can_sell = int(msgAns["ret_data"][i]["can_sell"]) # 可卖出数量
                    position.can_sub = int(msgAns["ret_data"][i]["can_sub"]) # 可申购数量
                    position.can_red = int(msgAns["ret_data"][i]["can_red"]) # 可赎回数量
                    position.non_tradable = int(msgAns["ret_data"][i]["non_tradable"]) # 非流通数量
                    position.frozen_qty = int(msgAns["ret_data"][i]["frozen_qty"]) # 冻结数量
                    position.sell_qty = int(msgAns["ret_data"][i]["sell_qty"]) # 当日卖出成交数量
                    position.sell_money = float(msgAns["ret_data"][i]["sell_money"]) # 当日卖出成交金额
                    position.buy_qty = int(msgAns["ret_data"][i]["buy_qty"]) # 当日买入成交数量
                    position.buy_money = float(msgAns["ret_data"][i]["buy_money"]) # 当日买入成交金额
                    position.sub_qty = int(msgAns["ret_data"][i]["sub_qty"]) # 当日申购成交数量
                    position.red_qty = int(msgAns["ret_data"][i]["red_qty"]) # 当日赎回成交数量
                    #print("客户库存：" + position.ToString())
                    taskItem.query_results.append(position) # 查询结果数据
                taskItem.status = define.TASK_STATUS_OVER # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
            else: # 查询失败
                taskItem.status = define.TASK_STATUS_FAIL # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
        else:
            self.log_text = "%s：客户库存：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryOrder(self, order_id, brow_index, strategy):
        taskItem = self.NewTaskItem(strategy, define.trade_queryorder_s_func)
        self.taskDict[taskItem.task_id] = taskItem # 目前这里未加锁
        msgReq = {"function":define.trade_queryorder_s_func, "session":self.session, "task_id":taskItem.task_id, "order_id":order_id, "brow_index":brow_index}
        if self.SendData(msgReq) == False:
            self.UnConnect()
            return None
        return taskItem

    def OnQueryOrder(self, retFunc, msgAns): # 每次可能多条 # 原接口是同步的，字段 ret_last 均为 True 的
        #print(msgAns["ret_func"], msgAns["ret_code"], msgAns["ret_info"], msgAns["ret_task"], msgAns["ret_last"], msgAns["ret_numb"])
        retFunc = int(msgAns["ret_func"])
        task_id = int(msgAns["ret_task"])
        if task_id in self.taskDict.keys():
            taskItem = self.taskDict[task_id]
            retCode = int(msgAns["ret_code"])
            if retCode == 0:
                for i in range(int(msgAns["ret_numb"])):
                    #print(msgAns["ret_data"][i]["otc_code"], msgAns["ret_data"][i]["otc_info"])
                    order = self.Order()
                    order.exchange = msgAns["ret_data"][i]["exchange"] # 交易所
                    order.symbol = msgAns["ret_data"][i]["symbol"] # 证券代码
                    order.security_type = msgAns["ret_data"][i]["security_type"] # 证券类别
                    order.order_id = int(msgAns["ret_data"][i]["order_id"]) # 委托号
                    order.entr_type = int(msgAns["ret_data"][i]["entr_type"]) # 委托方式
                    order.exch_side = int(msgAns["ret_data"][i]["exch_side"]) # 交易类型
                    order.price = float(msgAns["ret_data"][i]["price"]) # 委托价格
                    order.amount = int(msgAns["ret_data"][i]["amount"]) # 委托数量
                    order.fill_qty = int(msgAns["ret_data"][i]["fill_amount"]) # 成交数量
                    order.cxl_qty = int(msgAns["ret_data"][i]["cxl_qty"]) # 撤单数量
                    order.status = int(msgAns["ret_data"][i]["report_ret"]) # 申报结果
                    order.status_msg = msgAns["ret_data"][i]["message"] # 结果说明
                    order.brow_index = msgAns["ret_data"][i]["brow_index"] # 增量查询索引值
                    #order.batch_id = 0 # 批量委托编号 # 委托查询不返回此项
                    #msgAns["ret_data"][i]["holder"] # 股东号
                    #msgAns["ret_data"][i]["currency"] # 币种
                    #msgAns["ret_data"][i]["security_name"] # 证券名称
                    #float(msgAns["ret_data"][i]["fill_price"]) # 成交价格
                    #float(msgAns["ret_data"][i]["fill_money"]) # 成交金额
                    #msgAns["ret_data"][i]["cxl_flag"] # 撤销标志
                    #float(msgAns["ret_data"][i]["frozen"]) # 冻结资金
                    #float(msgAns["ret_data"][i]["settlement"]) # 清算资金
                    #msgAns["ret_data"][i]["report_time"] # 申报时间
                    #msgAns["ret_data"][i]["order_time"] # 委托时间
                    #msgAns["ret_data"][i]["fill_time"] # 成交时间
                    #msgAns["ret_data"][i]["account"] # 资金账号
                    #print("当日委托：" + order.ToString())
                    taskItem.query_results.append(order) # 查询结果数据
                taskItem.status = define.TASK_STATUS_OVER # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
            else: # 查询失败
                taskItem.status = define.TASK_STATUS_FAIL # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
        else:
            self.log_text = "%s：当日委托：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryTrade(self, order_id, brow_index, strategy):
        taskItem = self.NewTaskItem(strategy, define.trade_querytrans_s_func)
        self.taskDict[taskItem.task_id] = taskItem # 目前这里未加锁
        msgReq = {"function":define.trade_querytrans_s_func, "session":self.session, "task_id":taskItem.task_id, "order_id":order_id, "brow_index":brow_index}
        if self.SendData(msgReq) == False:
            self.UnConnect()
            return None
        return taskItem

    def OnQueryTrade(self, retFunc, msgAns): # 每次可能多条 # 原接口是同步的，字段 ret_last 均为 True 的
        #print(msgAns["ret_func"], msgAns["ret_code"], msgAns["ret_info"], msgAns["ret_task"], msgAns["ret_last"], msgAns["ret_numb"])
        retFunc = int(msgAns["ret_func"])
        task_id = int(msgAns["ret_task"])
        if task_id in self.taskDict.keys():
            taskItem = self.taskDict[task_id]
            retCode = int(msgAns["ret_code"])
            if retCode == 0:
                for i in range(int(msgAns["ret_numb"])):
                    #print(msgAns["ret_data"][i]["otc_code"], msgAns["ret_data"][i]["otc_info"])
                    trans = self.Trans()
                    trans.exchange = msgAns["ret_data"][i]["exchange"] # 交易所
                    trans.symbol = msgAns["ret_data"][i]["symbol"] # 证券代码
                    trans.security_type = msgAns["ret_data"][i]["security_type"] # 证券类别
                    trans.order_id = int(msgAns["ret_data"][i]["order_id"]) # 委托号
                    trans.trans_id = msgAns["ret_data"][i]["trans_id"] # 成交编号
                    trans.exch_side = int(msgAns["ret_data"][i]["exch_side"]) # 交易类型
                    trans.fill_price = float(msgAns["ret_data"][i]["fill_price"]) # 成交价格
                    trans.fill_qty = int(msgAns["ret_data"][i]["fill_amount"]) # 成交数量
                    trans.brow_index = msgAns["ret_data"][i]["brow_index"] # 增量查询索引值
                    #trans.fill_time = "" # 成交时间 # 成交查询不返回此项
                    #trans.cxl_qty = 0 # 撤单数量 # 成交查询不返回此项
                    #msgAns["ret_data"][i]["holder"] # 股东号
                    #msgAns["ret_data"][i]["currency"] # 币种
                    #msgAns["ret_data"][i]["security_name"] # 证券名称
                    #float(msgAns["ret_data"][i]["fill_money"]) # 成交金额
                    #msgAns["ret_data"][i]["cxl_flag"] # 撤销标志
                    #float(msgAns["ret_data"][i]["settlement"]) # 清算资金
                    #float(msgAns["ret_data"][i]["commission"]) # 佣金
                    #msgAns["ret_data"][i]["account"] # 资金账号
                    #print("当日成交：" + trans.ToString())
                    taskItem.query_results.append(trans) # 查询结果数据
                taskItem.status = define.TASK_STATUS_OVER # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
            else: # 查询失败
                taskItem.status = define.TASK_STATUS_FAIL # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
        else:
            self.log_text = "%s：当日成交：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryEtfBase(self, fund_id_2, strategy):
        taskItem = self.NewTaskItem(strategy, define.trade_queryetfbase_s_func)
        self.taskDict[taskItem.task_id] = taskItem # 目前这里未加锁
        msgReq = {"function":define.trade_queryetfbase_s_func, "session":self.session, "task_id":taskItem.task_id, "fund_id_2":fund_id_2}
        if self.SendData(msgReq) == False:
            self.UnConnect()
            return None
        return taskItem

    def OnQueryEtfBase(self, retFunc, msgAns): # 每次一条 # 原接口是同步的，字段 ret_last 均为 True 的
        #print(msgAns["ret_func"], msgAns["ret_code"], msgAns["ret_info"], msgAns["ret_task"], msgAns["ret_last"], msgAns["ret_numb"])
        retFunc = int(msgAns["ret_func"])
        task_id = int(msgAns["ret_task"])
        if task_id in self.taskDict.keys():
            taskItem = self.taskDict[task_id]
            retCode = int(msgAns["ret_code"])
            if retCode == 0:
                for i in range(int(msgAns["ret_numb"])):
                    #print(msgAns["ret_data"][i]["otc_code"], msgAns["ret_data"][i]["otc_info"])
                    etfBaseInfo = self.EtfBaseInfo()
                    etfBaseInfo.fund_name = msgAns["ret_data"][i]["fund_name"] # 基金名称
                    etfBaseInfo.fund_id_1 = msgAns["ret_data"][i]["fund_id_1"] # 申赎代码
                    etfBaseInfo.fund_id_2 = msgAns["ret_data"][i]["fund_id_2"] # 基金代码
                    etfBaseInfo.exchange = msgAns["ret_data"][i]["exchange"] # 交易所
                    etfBaseInfo.count = int(msgAns["ret_data"][i]["count"]) # 股票记录数
                    etfBaseInfo.status = int(msgAns["ret_data"][i]["status"]) # 申赎允许状态，-1：无资格，0：禁止申赎，1：允许申赎，2：允许申购，3：允许赎回
                    etfBaseInfo.pub_iopv = int(msgAns["ret_data"][i]["pub_iopv"]) # 是否发布IOPV
                    etfBaseInfo.unit = int(msgAns["ret_data"][i]["unit"]) # 最小申赎单位
                    etfBaseInfo.cash_ratio = float(msgAns["ret_data"][i]["cash_ratio"]) # 最大现金替代比例
                    etfBaseInfo.cash_diff = float(msgAns["ret_data"][i]["cash_diff"]) # T日现金差额
                    etfBaseInfo.iopv = float(msgAns["ret_data"][i]["iopv"]) # T-1日单位净值
                    etfBaseInfo.trade_iopv = float(msgAns["ret_data"][i]["trade_iopv"]) # T-1日申赎单位净值
                    #etfBaseInfo.stocks = [] # 成分股清单
                    #print("ETF基本信息：" + etfBaseInfo.ToString())
                    taskItem.query_results.append(etfBaseInfo) # 查询结果数据
                taskItem.status = define.TASK_STATUS_OVER # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
            else: # 查询失败
                taskItem.status = define.TASK_STATUS_FAIL # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
        else:
            self.log_text = "%s：ETF基本信息：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def QueryEtfDetail(self, fund_id_2, strategy):
        taskItem = self.NewTaskItem(strategy, define.trade_queryetfdetail_s_func)
        self.taskDict[taskItem.task_id] = taskItem # 目前这里未加锁
        msgReq = {"function":define.trade_queryetfdetail_s_func, "session":self.session, "task_id":taskItem.task_id, "fund_id_2":fund_id_2}
        if self.SendData(msgReq) == False:
            self.UnConnect()
            return None
        return taskItem

    def OnQueryEtfDetail(self, retFunc, msgAns): # 每次可能多条 # 原接口是同步的，字段 ret_last 均为 True 的
        #print(msgAns["ret_func"], msgAns["ret_code"], msgAns["ret_info"], msgAns["ret_task"], msgAns["ret_last"], msgAns["ret_numb"])
        retFunc = int(msgAns["ret_func"])
        task_id = int(msgAns["ret_task"])
        if task_id in self.taskDict.keys():
            taskItem = self.taskDict[task_id]
            retCode = int(msgAns["ret_code"])
            if retCode == 0:
                for i in range(int(msgAns["ret_numb"])):
                    #print(msgAns["ret_data"][i]["otc_code"], msgAns["ret_data"][i]["otc_info"])
                    etfDetailInfo = self.EtfDetailInfo()
                    etfDetailInfo.fund_name = msgAns["ret_data"][i]["fund_name"] # 基金名称
                    etfDetailInfo.stock_code = msgAns["ret_data"][i]["stock_code"] # 成分股代码
                    etfDetailInfo.stock_name = msgAns["ret_data"][i]["stock_name"] # 成分股名称
                    etfDetailInfo.stock_qty = int(msgAns["ret_data"][i]["stock_qty"]) # 成分股数量
                    etfDetailInfo.exchange = msgAns["ret_data"][i]["exchange"]# 交易所
                    etfDetailInfo.replace_flag = int(msgAns["ret_data"][i]["replace_flag"]) # 现金替代标志，1：允许，2：必须，3：禁止
                    etfDetailInfo.replace_money = float(msgAns["ret_data"][i]["replace_money"]) # 现金替代金额
                    etfDetailInfo.up_px_ratio = float(msgAns["ret_data"][i]["up_px_ratio"]) # 溢价比例
                    #print("ETF成分信息：" + etfDetailInfo.ToString())
                    taskItem.query_results.append(etfDetailInfo) # 查询结果数据
                taskItem.status = define.TASK_STATUS_OVER # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
            else: # 查询失败
                taskItem.status = define.TASK_STATUS_FAIL # 任务状态
                taskItem.messages.append("%d %s" % (retCode, msgAns["ret_info"])) # 任务信息
                self.SendTraderEvent(retFunc, taskItem)
        else:
            self.log_text = "%s：ETF成分信息：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def OnOrderReply(self, retFunc, msgAns):
        retFunc = int(msgAns["ret_func"])
        task_id = int(msgAns["task_id"])
        if task_id in self.taskDict.keys():
            taskItem = self.taskDict[task_id]
            order = self.Order()
            order.order_id = int(msgAns["order_id"]) # 委托号
            order.exch_side = int(msgAns["exch_side"]) # 交易类型
            order.symbol = msgAns["symbol"] # 证券代码
            order.security_type = msgAns["security_type"] # 证券类别
            order.exchange = msgAns["exchange"] # 交易所
            order.cxl_qty = int(msgAns["cxl_qty"]) # 撤单数量
            order.fill_qty = 0 # 总成交数量
            order.status = int(msgAns["commit_ret"]) # 申报结果
            order.status_msg = msgAns["commit_msg"] # 申报说明
            print("申报回报：" + order.ToString())
            if taskItem.order != None:
                taskItem.order_replies.append(order) # 单个合约委托回报
            elif taskItem.batch != None:
                if order.order_id in taskItem.batch.batch_orders_map.keys():
                    batchItem = taskItem.batch.batch_orders_map[order.order_id]
                    batchItem.order_replies.append(order) # 单个合约委托回报
                else:
                    self.log_text = "%s：(批量)申报回报：未知委托编号！%d" % (self.trade_name, order.order_id)
                    self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            self.SendTraderEvent(retFunc, taskItem)
        else:
            self.log_text = "%s：申报回报：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def OnTransReply(self, retFunc, msgAns):
        retFunc = int(msgAns["ret_func"])
        task_id = int(msgAns["task_id"])
        if task_id in self.taskDict.keys():
            taskItem = self.taskDict[task_id]
            trans = self.Trans()
            trans.order_id = int(msgAns["order_id"]) # 委托号
            trans.exch_side = int(msgAns["exch_side"]) # 交易类型
            trans.trans_id = msgAns["trans_id"] # 成交编号
            trans.symbol = msgAns["symbol"] # 证券代码
            trans.security_type = msgAns["security_type"] # 证券类别
            trans.exchange = msgAns["exchange"] # 交易所
            trans.fill_qty = int(msgAns["fill_qty"]) # 本次成交数量
            trans.fill_price = float(msgAns["fill_price"]) # 本次成交价格
            trans.fill_time = msgAns["fill_time"] # 成交时间
            trans.cxl_qty = int(msgAns["cxl_qty"]) # 撤单数量
            print("成交回报：" + trans.ToString())
            if taskItem.order != None:
                taskItem.trans_replies.append(trans) # 单个合约成交回报
            elif taskItem.batch != None:
                if trans.order_id in taskItem.batch.batch_orders_map.keys():
                    batchItem = taskItem.batch.batch_orders_map[trans.order_id]
                    batchItem.trans_replies.append(trans) # 单个合约成交回报
                else:
                    self.log_text = "%s：(批量)成交回报：未知委托编号！%d" % (self.trade_name, trans.order_id)
                    self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            self.SendTraderEvent(retFunc, taskItem)
        else:
            self.log_text = "%s：成交回报：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def OnCancelReply(self, retFunc, msgAns):
        retFunc = int(msgAns["ret_func"])
        task_id = int(msgAns["task_id"])
        if task_id in self.taskDict.keys():
            taskItem = self.taskDict[task_id]
            order = self.Order()
            order.order_id = int(msgAns["order_id"]) # 委托号
            order.exch_side = int(msgAns["exch_side"]) # 交易类型
            order.symbol = msgAns["symbol"] # 证券代码
            order.security_type = msgAns["security_type"] # 证券类别
            order.exchange = msgAns["exchange"] # 交易所
            order.cxl_qty = int(msgAns["cxl_qty"]) # 撤单数量
            order.fill_qty = int(msgAns["total_fill_qty"]) # 总成交数量
            if order.cxl_qty == 0:
                order.status = define.order_status_s_entire_trans # 申报结果 # 全部成交
            elif order.fill_qty == 0:
                order.status = define.order_status_s_entire_cancel # 申报结果 # 全部撤单
            else:
                order.status = define.order_status_s_part_cancel # 申报结果 # 部成部撤
            order.status_msg = "撤单成功。" # 申报说明
            print("撤单回报：" + order.ToString())
            if taskItem.order != None:
                taskItem.order_replies.append(order) # 单个合约委托回报
            elif taskItem.batch != None:
                if order.order_id in taskItem.batch.batch_orders_map.keys():
                    batchItem = taskItem.batch.batch_orders_map[order.order_id]
                    batchItem.order_replies.append(order) # 单个合约委托回报
                else:
                    self.log_text = "%s：(批量)撤单回报：未知委托编号！%d" % (self.trade_name, order.order_id)
                    self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            self.SendTraderEvent(retFunc, taskItem)
        else:
            self.log_text = "%s：撤单回报：未知任务编号！%d" % (self.trade_name, task_id)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

####################################################################################################

    def QueryCapital_Syn(self, strategy, queryWait = 5):
        taskItem = self.QueryCapital(strategy)
        ret_wait = taskItem.event_task_finish.wait(timeout = queryWait) # 等待结果
        if ret_wait == True:
            if taskItem.status == define.TASK_STATUS_OVER:
                for capital in taskItem.query_results: #应该只有一条的
                    #self.log_text = "%s：证券资金：%s" % (strategy, capital.ToString())
                    #self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                    return [True, capital]
                return [True, None]
            else:
                self.log_text = "%s：证券 资金 查询失败！原因：%s" % (strategy, taskItem.messages[-1])
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, None]
        else:
            self.log_text = "%s：证券 资金 查询超时！状态：%d" % (strategy, taskItem.status)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, None]

    def QueryPosition_Syn(self, symbol, strategy, queryWait = 5):
        taskItem = self.QueryPosition(strategy)
        ret_wait = taskItem.event_task_finish.wait(timeout = queryWait) # 等待结果
        if ret_wait == True:
            if taskItem.status == define.TASK_STATUS_OVER:
                for position in taskItem.query_results: #注意是：PositionDefer
                    if position.symbol == symbol:
                        return [True, position]
                    #self.log_text = "%s：证券持仓：%s" % (strategy, position.ToString())
                    #self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                return [True, None]
            else:
                self.log_text = "%s：证券 持仓 查询失败！原因：%s" % (strategy, taskItem.messages[-1])
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, None]
        else:
            self.log_text = "%s：证券 持仓 查询超时！状态：%d" % (strategy, taskItem.status)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, None]

    def QueryPosition_All_Syn(self, strategy, queryWait = 5):
        taskItem = self.QueryPosition(strategy)
        ret_wait = taskItem.event_task_finish.wait(timeout = queryWait) # 等待结果
        if ret_wait == True:
            if taskItem.status == define.TASK_STATUS_OVER:
                if len(taskItem.query_results) > 0:
                    #for position in taskItem.query_results: #注意是：PositionDefer
                    #    self.log_text = "%s：证券持仓：%s" % (strategy, position.ToString())
                    #    self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                    return [True, taskItem.query_results]
                return [True, None]
            else:
                self.log_text = "%s：证券 持仓 查询失败！原因：%s" % (strategy, taskItem.messages[-1])
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, None]
        else:
            self.log_text = "%s：证券 持仓 查询超时！状态：%d" % (strategy, taskItem.status)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, None]

    def QueryOrder_Syn(self, order_id, brow_index, strategy, queryWait = 5):
        taskItem = self.QueryOrder(order_id, brow_index, strategy)
        ret_wait = taskItem.event_task_finish.wait(timeout = queryWait) # 等待结果
        if ret_wait == True:
            if taskItem.status == define.TASK_STATUS_OVER:
                for order in taskItem.query_results:
                    if order.order_id == order_id:
                        return [True, order]
                    #self.log_text = "%s：证券委托：%s" % (strategy, order.ToString())
                    #self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                return [True, None]
            else:
                self.log_text = "%s：证券 委托 查询失败！原因：%s" % (strategy, taskItem.messages[-1])
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, None]
        else:
            self.log_text = "%s：证券 委托 查询超时！状态：%d" % (strategy, taskItem.status)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, None]

    def QueryTrade_Syn(self, order_id, brow_index, strategy, queryWait = 5): # 返回列表
        transList = []
        taskItem = self.QueryTrade(order_id, brow_index, strategy)
        ret_wait = taskItem.event_task_finish.wait(timeout = queryWait) # 等待结果
        if ret_wait == True:
            if taskItem.status == define.TASK_STATUS_OVER:
                for trans in taskItem.query_results:
                    if trans.order_id == order_id:
                        transList.append(trans) #
                    #self.log_text = "%s：证券成交：%s" % (strategy, trans.ToString())
                    #self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                return [True, transList]
            else:
                self.log_text = "%s：证券 成交 查询失败！原因：%s" % (strategy, taskItem.messages[-1])
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, None]
        else:
            self.log_text = "%s：证券 成交 查询超时！状态：%d" % (strategy, taskItem.status)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, None]

    def QueryEtfBase_Syn(self, fund_id_2, strategy, queryWait = 5):
        taskItem = self.QueryEtfBase(fund_id_2, strategy)
        ret_wait = taskItem.event_task_finish.wait(timeout = queryWait) # 等待结果
        if ret_wait == True:
            if taskItem.status == define.TASK_STATUS_OVER:
                for etfBaseInfo in taskItem.query_results: # 应该只有一条的
                    #self.log_text = "%s：证券资金：%s" % (strategy, etfBaseInfo.ToString())
                    #self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                    return [True, etfBaseInfo]
                return [True, None]
            else:
                self.log_text = "%s：证券 ETF基本 查询失败！原因：%s" % (strategy, taskItem.messages[-1])
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, None]
        else:
            self.log_text = "%s：证券 ETF基本 查询超时！状态：%d" % (strategy, taskItem.status)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, None]

    def QueryEtfDetail_Syn(self, fund_id_2, strategy, queryWait = 5): # 返回列表
        stockList = []
        taskItem = self.QueryEtfDetail(fund_id_2, strategy)
        ret_wait = taskItem.event_task_finish.wait(timeout = queryWait) # 等待结果
        if ret_wait == True:
            if taskItem.status == define.TASK_STATUS_OVER:
                for stock in taskItem.query_results:
                    stockList.append(stock) #
                    #self.log_text = "%s：证券ETF成分股：%s" % (strategy, stock.ToString())
                    #self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                return [True, stockList]
            else:
                self.log_text = "%s：证券 ETF成分股 查询失败！原因：%s" % (strategy, taskItem.messages[-1])
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, None]
        else:
            self.log_text = "%s：证券 ETF成分股 查询超时！状态：%d" % (strategy, taskItem.status)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
            return [False, None]

    def PlaceOrder_FOC_Syn(self, label, order, strategy, tradeWait = 1, cancelWait = 5):
        self.log_text = "%s: 准备  %s: %s" % (strategy, label, order.ToString())
        self.logger.SendMessage("D", 0, self.log_cate, self.log_text, "T")
        
#        time.sleep(2)
#        order.fill_qty = order.amount
#        return [True, order] # 测试！！
        
        taskItem_Place = self.PlaceOrder(order, strategy)
        ret_wait = taskItem_Place.event_task_finish.wait(tradeWait) # 等待结果
        # 在 wait 结束时，要么报单异常，要么交易结束，要么等待超时
        if ret_wait == True: # 报单异常、交易结束
            if taskItem_Place.status == define.TASK_STATUS_FAIL: # 报单异常
                self.log_text = "%s: 委托 %s %s 下单异常！任务： %d， 原因: %s" % (strategy, label, order.symbol, taskItem_Place.task_id, taskItem_Place.messages[-1])
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, taskItem_Place.order]
            else: # 交易结束
                self.log_text = "%s: 委托 %s %s 交易完成。任务： %d， 状态: %d, 成交: %d" % (strategy, label, order.symbol, taskItem_Place.task_id, taskItem_Place.status, taskItem_Place.order.fill_qty)
                self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                return [True, taskItem_Place.order]
        else: # 等待超时
            if taskItem_Place.order.order_id != "":
                self.log_text = "%s: 委托 %s %s 准备撤单。 委托： %s， 超时： %d" % (strategy, label, order.symbol, taskItem_Place.order.order_id, tradeWait)
                self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                taskItem_Cancel = self.CancelOrder(taskItem_Place.order, strategy)
                ret_wait = taskItem_Place.event_task_finish.wait(cancelWait) # 等待结果 #使用 taskItem_Place
                # 在 wait 结束时，要么交易结束，要么等待超时
                if ret_wait == True: # 交易结束
                    self.log_text = "%s：委托 %s %s 撤单完成。任务：%d，状态：%d，成交：%d" % (strategy, label, order.symbol, taskItem_Place.task_id, taskItem_Place.order.status, taskItem_Place.order.fill_qty)
                    self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
                    return [True, taskItem_Place.order]
                else: # 等待超时
                    if taskItem_Cancel.status == define.TASK_STATUS_FAIL: # 撤单异常
                        self.log_text = "%s：委托 %s %s 撤单异常！任务：%d，原因：%s" % (strategy, label, order.symbol, taskItem_Cancel.task_id, taskItem_Cancel.messages[-1])
                        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                        return [False, taskItem_Place.order]
                    else:
                        self.log_text = "%s：委托 %s %s 撤单超时！任务：%d，超时：%d" % (strategy, label, order.symbol, taskItem_Cancel.task_id, cancelWait)
                        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                        return [False, taskItem_Place.order]
            else:
                self.log_text = "%s：委托 %s %s 撤单时缺少委托编号！任务：%d" % (strategy, label, order.symbol, taskItem_Place.task_id)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
                return [False, taskItem_Place.order]

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
