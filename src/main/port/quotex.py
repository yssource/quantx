
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

import io
import time
import json
import gzip
import numpy
import socket
import threading
from datetime import datetime, timedelta

import define
import logger
import center

class QuoteX():
    def __init__(self, parent, quote_name, address, port, quote_subs):
        self.log_text = ""
        self.log_cate = "QuoteX"
        self.parent = parent
        self.quote_name = quote_name
        self.address = address
        self.port = port
        self.quote_subs = quote_subs # Dict
        self.started = False
        self.userstop = False # 防止用户退出时行情服务重连线程执行操作
        self.connected = False
        self.heart_check_time = datetime.now()
        self.heart_check_span = timedelta(seconds = 10 * 3)
        self.logger = logger.Logger()
        self.center = center.Center()
        self.RegReplyMsgHandleFunc()

    def __del__(self):
        self.started = False

    def RegReplyMsgHandleFunc(self):
        self.reply_msg_handle_func = {}
        self.reply_msg_handle_func[define.quote_subscibe_func] = self.OnSubscibe
        self.reply_msg_handle_func[define.quote_unsubscibe_func] = self.OnUnsubscibe
        self.reply_msg_handle_func[define.quote_status_info_func] = self.OnStateInfo

    def Start(self):
        self.log_text = "%s：用户 启动 行情服务..." % self.quote_name
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        if self.started == False:
            if self.DoConnect(self.address, self.port):
                self.started = True
                self.thread_recv = threading.Thread(target = self.Thread_Recv)
                self.thread_recv.start()
                time.sleep(1)
                for sub_info in self.quote_subs.values():
                    self.Subscibe(sub_info[0], sub_info[2])
                time.sleep(1)
                self.thread_time = threading.Thread(target = self.Thread_Time)
                self.thread_time.start()
            else:
                self.log_text = "%s：启动时连接行情服务器失败！" % self.quote_name
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def Thread_Recv(self):
        self.log_text = "%s：启动行情数据接收线程..." % self.quote_name
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        while self.started:
            if self.connected == True:
                if self.RecvData() == False:
                    self.UnConnect()
            else:
                time.sleep(1) # 等待重连完成
        if self.connected == True:
            self.UnConnect()
        self.log_text = "%s：行情数据接收线程退出！" % self.quote_name
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def Thread_Time(self):
        self.log_text = "%s：启动行情服务重连线程..." % self.quote_name
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        while self.started:
            if self.connected == False and self.userstop == False:
                if self.DoConnect(self.address, self.port):
                    time.sleep(1)
                    for sub_info in self.quote_subs.values():
                        self.Subscibe(sub_info[0], sub_info[2])
                else:
                    self.log_text = "%s：重连时连接行情服务器失败！" % self.quote_name
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            if self.connected == True and datetime.now() > self.heart_check_time + self.heart_check_span:
                try:
                    self.sock.shutdown(socket.SHUT_RDWR) # 网络物理连接断开时直接 close 的话 recv 不会退出阻塞的
                except socket.error as e:
                    self.log_text = "%s：主动关闭 socket 异常！%s" % (self.quote_name, e)
                    self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
                self.UnConnect()
                self.log_text = "%s：心跳检测超时连接已经断开！" % self.quote_name
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            time.sleep(5)
        self.log_text = "%s：行情服务重连线程退出！" % self.quote_name
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def Stop(self):
        self.log_text = "%s：用户 停止 行情服务..." % self.quote_name
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        self.userstop = True
        if self.started == True:
            for sub_info in self.quote_subs.values():
                self.Unsubscibe(sub_info[0], sub_info[2])
            time.sleep(1)
            self.started = False # 通过心跳机制来中断 RecvData 阻塞进而退出行情数据接收线程

    def DoConnect(self, address, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            self.log_text = "%s：创建 socket 失败！%s %d %s" % (self.quote_name, address, port, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            time.sleep(1)
            return False
        try:
            self.sock.settimeout(3) # 设置连接超时
            self.sock.connect((address, port))
            self.sock.settimeout(None) # 需要这样设置，回到阻塞模式，不然数据读写会变非阻塞
        except socket.error as e:
            self.log_text = "%s：建立 connect 失败！%s %d %s" % (self.quote_name, address, port, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            time.sleep(1)
            return False
        self.connected = True
        self.heart_check_time = datetime.now()
        return True

    def UnConnect(self):
        self.connected = False
        self.sock.close()

    def OnReplyMsg(self, ret_func, msg_ans):
        try:
            ret_info = msg_ans["ret_info"]
            ret_code = int(msg_ans["ret_code"])
            if ret_func in self.reply_msg_handle_func.keys():
                self.reply_msg_handle_func[ret_func](ret_code, ret_info)
            else:
                self.log_text = "%s：处理应答消息类型未知！%d" % (self.quote_name, ret_func)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            if self.parent != None: # 发给上层更新用户界面信息
                self.parent.OnQuoteReplyMsg(self.quote_name, ret_func, ret_code, ret_info)
        except Exception as e:
            self.log_text = "%s：处理应答消息发生异常！%s" % (self.quote_name, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def OnQuoteMsg(self, quote_func, quote_flag, quote_data):
        try:
            if quote_func in self.quote_subs.keys():
                sub_info = self.quote_subs[quote_func]
                data = numpy.frombuffer(quote_data, dtype = sub_info[1])
                self.center.UpdateSnapshot(quote_func, data[0])
        except Exception as e:
            self.log_text = "%s：处理行情消息发生异常！%s" % (self.quote_name, e)
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
            self.log_text = "%s：发送数据发生异常！%s %d %s" % (self.quote_name, self.address, self.port, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return False
        except Exception as e:
            self.log_text = "%s：发送数据发生异常！%s %d %s" % (self.quote_name, self.address, self.port, e)
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
                elif msg_code == "5": # NW_MSG_CODE_ZLIB # 行情消息
                    quote_func = msg_recv[:6].decode() # 行情类型
                    quote_flag = msg_recv[6:8].decode() # 行情版本
                    zip_data = io.BytesIO(msg_recv[8:])
                    g_zipper = gzip.GzipFile(fileobj = zip_data)
                    msg_data = g_zipper.read()
                    self.OnQuoteMsg(int(quote_func), quote_flag, msg_data)
            elif msg_head[0] == "0": # NW_MSG_TYPE_HEART_CHECK # 连接心跳检测消息
                self.heart_check_time = datetime.now()
            return True
        except socket.error as e:
            self.log_text = "%s：接收数据发生异常！%s %d %s" % (self.quote_name, self.address, self.port, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return False
        except Exception as e:
            self.log_text = "%s：接收数据发生异常！%s %d %s" % (self.quote_name, self.address, self.port, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return False

####################################################################################################

    def Subscibe(self, quote_type, quote_list):
        msg_req = {"function":define.quote_subscibe_func, "quote_type":quote_type, "quote_list":quote_list}
        if self.SendData(msg_req) == False:
            self.UnConnect()

    def OnSubscibe(self, ret_code, ret_info):
        if ret_code == 0:
            self.log_text = "%s：行情订阅成功。%d %s" % (self.quote_name, ret_code, ret_info)
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        else:
            self.log_text = "%s：行情订阅失败！%d %s" % (self.quote_name, ret_code, ret_info)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def Unsubscibe(self, quote_type, quote_list):
        msg_req = {"function":define.quote_unsubscibe_func, "quote_type":quote_type, "quote_list":quote_list}
        if self.SendData(msg_req) == False:
            self.UnConnect()

    def OnUnsubscibe(self, ret_code, ret_info):
        if ret_code == 0:
            self.log_text = "%s：行情退订成功。%d %s" % (self.quote_name, ret_code, ret_info)
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        else:
            self.log_text = "%s：行情退订失败！%d %s" % (self.quote_name, ret_code, ret_info)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def OnStateInfo(self, ret_code, ret_info):
        self.log_text = "%s：行情状态信息：%d %s" % (self.quote_name, ret_code, ret_info)
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")

####################################################################################################

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    quote_subs_stock_ltb = {define.stock_ltb_market_s_func : (define.stock_ltb_market_s_func, define.stock_ltb_market_s_type, ""),
                         define.stock_ltb_market_i_func : (define.stock_ltb_market_i_func, define.stock_ltb_market_i_type, ""),
                         define.stock_ltb_market_t_func : (define.stock_ltb_market_t_func, define.stock_ltb_market_t_type, "")}
    quote_subs_stock_ltp = {define.stock_ltp_market_s_func : (define.stock_ltp_market_s_func, define.stock_ltp_market_s_type, ""),
                         define.stock_ltp_market_i_func : (define.stock_ltp_market_i_func, define.stock_ltp_market_i_type, ""),
                         define.stock_ltp_market_t_func : (define.stock_ltp_market_t_func, define.stock_ltp_market_t_type, "")}
    quote_subs_stock_tdf = {define.stock_tdf_market_s_func : (define.stock_tdf_market_s_func, define.stock_tdf_market_s_type, ""),
                         define.stock_tdf_market_i_func : (define.stock_tdf_market_i_func, define.stock_tdf_market_i_type, ""),
                         define.stock_tdf_market_t_func : (define.stock_tdf_market_t_func, define.stock_tdf_market_t_type, "")}
    quote_subs_future_np = {define.future_np_market_func : (define.future_np_market_func, define.future_np_market_type, "")}
    #quotex = QuoteX(None, "股票类LTB行情", "10.0.7.80", 8001, quote_subs_stock_ltb) # 股票类LTB快照
    #quotex = QuoteX(None, "股票类LTP行情", "10.0.7.80", 6001, quote_subs_stock_ltp) # 股票类LTP快照
    #quotex = QuoteX(None, "股票类TDF行情", "10.0.7.80", 9001, quote_subs_stock_tdf) # 股票类TDF快照
    quotex = QuoteX(None, "期货类内盘行情", "10.0.7.80", 7001, quote_subs_future_np) # 期货类内盘快照
    quotex.Start()
    time.sleep(30)
    quotex.Stop()
    sys.exit(app.exec_())
