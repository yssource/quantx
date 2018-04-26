
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
import threading
import traceback

from PyQt5 import QtGui, QtCore

import define
import logger
import analys

class AnalysisBase(threading.Thread):
    def __init__(self, analysis, analysis_name, analysis_introduction):
        self.log_text = ""
        self.log_cate = "AnalysisBase"
        self.logger = logger.Logger()
        self.analys = analys.Analys()
        self.analysis = analysis
        self.analysis_name = analysis_name
        self.analysis_introduction = analysis_introduction
        self.started = False
        self.analysis_panel = None
        self.analysis_info = self.analys.AnalysisInfo # 已经存在

    def CheckUserCtrl(self):
        self.analysis_info.state_locker.acquire()
        analysis_state = self.analysis_info.state
        self.analysis_info.state_locker.release()
        if analysis_state == define.USER_CTRL_EXEC:
            return 1
        elif analysis_state == define.USER_CTRL_STOP:
            self.log_text = "用户 停止 回测 %s %s 执行！" % (self.analysis, self.analysis_name)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return -1
        elif analysis_state == define.USER_CTRL_WAIT:
            self.log_text = "用户 暂停 回测 %s %s 执行！" % (self.analysis, self.analysis_name)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            while analysis_state == define.USER_CTRL_WAIT:
                time.sleep(1.0)
                self.analysis_info.state_locker.acquire()
                analysis_state = self.analysis_info.state
                self.analysis_info.state_locker.release()
            if analysis_state == define.USER_CTRL_EXEC:
                self.log_text = "用户 继续 回测 %s %s 执行！" % (self.analysis, self.analysis_name)
                self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
                return 1
            elif analysis_state == define.USER_CTRL_STOP:
                self.log_text = "用户 停止 回测 %s %s 执行！" % (self.analysis, self.analysis_name)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
                return -1

    def run(self):
        self.started = True
        while self.started:
            time.sleep(3)
            if self.CheckUserCtrl() != 1:
                break
        self.started = False
        self.log_text = "回测 %s %s 定期执行线程退出！" % (self.analysis, self.analysis_name)
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def Reload(self):
        self.log_text = "回测 %s %s 执行一些初始化工作。" % (self.analysis, self.analysis_name)
        self.logger.SendMessage("D", 0, self.log_cate, self.log_text, "S")

    def Working(self):
        self.analysis_info.state_locker.acquire()
        self.analysis_info.state = define.USER_CTRL_EXEC
        self.analysis_info.state_locker.release()

        threading.Thread.__init__(self)
        self.start()
        self.log_text = "用户 运行 回测：%s, %s, %s" % (self.analysis, self.analysis_name, self.analysis_introduction)
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def BackTest(self):
        self.thread_back_test = threading.Thread(target = self.ThreadBackTest)
        self.thread_back_test.start()

    def Suspend(self):
        self.analysis_info.state_locker.acquire()
        self.analysis_info.state = define.USER_CTRL_WAIT
        self.analysis_info.state_locker.release()
        self.log_text = "用户 暂停 回测：%s, %s, %s" % (self.analysis, self.analysis_name, self.analysis_introduction)
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def Continue(self):
        self.analysis_info.state_locker.acquire()
        self.analysis_info.state = define.USER_CTRL_EXEC
        self.analysis_info.state_locker.release()
        self.log_text = "用户 继续 回测：%s, %s, %s" % (self.analysis, self.analysis_name, self.analysis_introduction)
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def Terminal(self):
        self.analysis_info.state_locker.acquire()
        self.analysis_info.state = define.USER_CTRL_STOP
        self.analysis_info.state_locker.release()
        self.log_text = "用户 停止 回测：%s, %s, %s" % (self.analysis, self.analysis_name, self.analysis_introduction)
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def Unload(self):
        self.log_text = "回测 %s %s 执行一些销毁前工作。" % (self.analysis, self.analysis_name)
        self.logger.SendMessage("D", 0, self.log_cate, self.log_text, "S")

    def OnWorking(self): # 供具体回测继承调用，在 运行 前执行一些操作
        pass

    def OnSuspend(self): # 供具体回测继承调用，在 暂停 前执行一些操作
        pass

    def OnContinue(self): # 供具体回测继承调用，在 继续 前执行一些操作
        pass

    def OnTerminal(self): # 供具体回测继承调用，在 停止 前执行一些操作
        pass

    def ThreadBackTest(self):
        try:
            self.OnBackTest(self.analys.symbol_list, self.analys.trading_day_list)
        except Exception as e:
            traceback.print_exc() #
            QtGui.QApplication.postEvent(self.analysis_panel, QtCore.QEvent(define.DEF_EVENT_SET_ANALYSIS_PROGRESS_ERROR))
            self.log_text = "回测 %s %s 计算发生异常！%s" % (self.analysis, self.analysis_name, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def OnBackTest(self, symbol_list, trading_day_list): # 供具体回测继承调用，实现回测计算处理
        pass

    def IsModelError(self): # 供具体回测继承调用，判断模型是否异常 # 如果继承后仍然 pass 则函数返回会被视为 None，既非 True 也非 False
        pass

    def SetAnalysisProgress(self, total, finish):
        if self.analysis_panel != None and total != 0:
            progress = round(float(finish) / float(total) * 100.0)
            if self.analysis_panel.analysis_progress != progress: # 减少进度刷新
                self.analysis_panel.analysis_progress = progress
                QtGui.QApplication.postEvent(self.analysis_panel, QtCore.QEvent(define.DEF_EVENT_SET_ANALYSIS_PROGRESS))
