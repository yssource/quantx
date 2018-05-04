
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
import sys
import time
import threading
import traceback

from pubsub import pub
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import config
import define
import common
import logger
import center

class Strate(common.Singleton, threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.log_text = ""
        self.log_cate = "Strate"
        self.started = False
        self.config = config.Config()
        self.logger = logger.Logger()
        self.center = center.Center()

    def __del__(self):
        self.started = False

    def GetInstance(self):
        return self

    def LoadStrategy(self):
        stra_folder = self.config.cfg_main.stra_folder
        sys.path.insert(0, stra_folder) # 添加策略模块查找路径

        if self.config.cfg_main.stra_auto_load == 1: # 是否启动时自动加载
            self.log_text = "系统启动时 自动加载 策略..."
            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
            for file_name in os.listdir(stra_folder):
                if file_name[-3:] == ".py":
                    if file_name != "__init__.py" and file_name != "strategy_base.py":
                        if not (file_name[:-3] in sys.modules.keys()):
                            file_path = stra_folder + "/" + file_name
                            stra_info = center.StrategyInfo()
                            stra_info.strategy = file_name[:-3]
                            try:
                                __import__(stra_info.strategy)
                                stra_info.module = sys.modules[stra_info.strategy]
                                stra_info.classer = getattr(stra_info.module, stra_info.strategy)
                                stra_info.file_path = file_path
                                stra_info.state = define.USER_CTRL_LOAD
                                self.center.data.strategies[stra_info.strategy] = stra_info # 先放进去，策略类初始化时要用
                                stra_info.instance = stra_info.classer() # 策略类初始化
                                stra_info.name = stra_info.instance.strategy_name
                                stra_info.introduction = stra_info.instance.strategy_introduction
                                stra_info.instance.Reload() # 可以执行一些初始化工作
                                self.log_text = "加载策略：%s, %s, %s, %d, %s" % (stra_info.strategy, stra_info.name, stra_info.introduction, stra_info.state, stra_info.file_path)
                                self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
                            except Exception as e:
                                self.log_text = "策略 %s.py 加载发生错误！%s %s" % (stra_info.strategy, Exception, e)
                                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
                                self.OnUnloadStrategy(stra_info) #
                elif file_name[-4:] == ".pyd":
                    if file_name != "strategy_base.pyd":
                        if not (file_name[:-4] in sys.modules.keys()):
                            file_path = stra_folder + "/" + file_name
                            stra_info = center.StrategyInfo()
                            stra_info.strategy = file_name[:-4]
                            try:
                                __import__(stra_info.strategy)
                                stra_info.module = sys.modules[stra_info.strategy]
                                stra_info.classer = getattr(stra_info.module, stra_info.strategy)
                                stra_info.file_path = file_path
                                stra_info.state = define.USER_CTRL_LOAD
                                self.center.data.strategies[stra_info.strategy] = stra_info # 先放进去，策略类初始化时要用
                                stra_info.instance = stra_info.classer() # 策略类初始化
                                stra_info.name = stra_info.instance.strategy_name
                                stra_info.introduction = stra_info.instance.strategy_introduction
                                stra_info.instance.Reload() # 可以执行一些初始化工作
                                self.log_text = "加载策略：%s, %s, %s, %d, %s" % (stra_info.strategy, stra_info.name, stra_info.introduction, stra_info.state, stra_info.file_path)
                                self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
                            except Exception as e:
                                self.log_text = "策略 %s.pyd 加载发生错误！%s %s" % (stra_info.strategy, Exception, e)
                                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
                                self.OnUnloadStrategy(stra_info) #
        else:
            self.log_text = "系统启动时 不自动加载 策略..."
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def OnChangeStrategyState(self, strategy_info, str_type):
        if str_type == "运行":
            if strategy_info.instance.IsTradeError() == True: # 用 == 判断，可能返回 None 的
                self.log_text = "策略 %s %s 的交易已经发生异常，重新加载运行！" % (strategy_info.strategy, strategy_info.name)
                self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            elif strategy_info.instance.started == True:
                self.log_text = "策略 %s %s 的执行线程还未结束，无法重新运行！" % (strategy_info.strategy, strategy_info.name)
                self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            else:
                try:
                    strategy_info.instance.OnWorking()
                    strategy_info.instance.Working()
                except Exception as e:
                    traceback.print_exc() #
                    self.log_text = "策略 %s %s 运行 时发生异常！%s" % (strategy_info.strategy, strategy_info.name, e)
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        elif str_type == "暂停":
            try:
                strategy_info.instance.OnSuspend()
                strategy_info.instance.Suspend()
            except Exception as e:
                traceback.print_exc() #
                self.log_text = "策略 %s %s 暂停 时发生异常！%s" % (strategy_info.strategy, strategy_info.name, e)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        elif str_type == "继续":
            try:
                strategy_info.instance.OnContinue()
                strategy_info.instance.Continue()
            except Exception as e:
                traceback.print_exc() #
                self.log_text = "策略 %s %s 继续 时发生异常！%s" % (strategy_info.strategy, strategy_info.name, e)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        elif str_type == "停止":
            try:
                strategy_info.instance.OnTerminal()
                strategy_info.instance.Terminal()
            except Exception as e:
                traceback.print_exc() #
                self.log_text = "策略 %s %s 停止 时发生异常！%s" % (strategy_info.strategy, strategy_info.name, e)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def OnReloadStrategy(self):
        stra_folder = self.config.cfg_main.stra_folder
        sys.path.insert(0, stra_folder) # 添加策略模块查找路径

        dlg_file = QFileDialog.getOpenFileName(None, caption = "选择策略文件...", directory = stra_folder, filter = "Python Files(*.py*)")
        if dlg_file != "":
            file_path = dlg_file[0].__str__()
            file_name = os.path.basename(file_path)
            if file_name != "":
                if file_name[-3:] == ".py":
                    if file_name != "__init__.py" and file_name != "strategy_base.py":
                        if not (file_name[:-3] in sys.modules.keys()):
                            file_path = stra_folder + "/" + file_name
                            stra_info = center.StrategyInfo()
                            stra_info.strategy = file_name[:-3]
                            try:
                                __import__(stra_info.strategy)
                                stra_info.module = sys.modules[stra_info.strategy]
                                stra_info.classer = getattr(stra_info.module, stra_info.strategy)
                                stra_info.file_path = file_path
                                stra_info.state = define.USER_CTRL_LOAD
                                self.center.data.strategies[stra_info.strategy] = stra_info # 先放进去，策略类初始化时要用
                                stra_info.instance = stra_info.classer() # 策略类初始化
                                stra_info.name = stra_info.instance.strategy_name
                                stra_info.introduction = stra_info.instance.strategy_introduction
                                stra_info.instance.Reload() # 可以执行一些初始化工作
                                self.log_text = "用户 加载 策略：%s, %s, %s, %d, %s" % (stra_info.strategy, stra_info.name, stra_info.introduction, stra_info.state, stra_info.file_path)
                                self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
                            except Exception as e:
                                self.log_text = "策略 %s.py 加载发生错误！%s %s" % (stra_info.strategy, Exception, e)
                                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
                                self.OnUnloadStrategy(stra_info) #
                        else:
                            QMessageBox.information(None, "提示", "选择的策略模块 %s 系统已经加载！" % file_name[:-3], QMessageBox.Ok)
                    else:
                        QMessageBox.information(None, "提示", "选择的策略文件 %s 不是用户定义！" % file_name, QMessageBox.Ok)
                elif file_name[-4:] == ".pyd":
                    if file_name != "strategy_base.pyd":
                        if not (file_name[:-4] in sys.modules.keys()):
                            file_path = stra_folder + "/" + file_name
                            stra_info = center.StrategyInfo()
                            stra_info.strategy = file_name[:-4]
                            try:
                                __import__(stra_info.strategy)
                                stra_info.module = sys.modules[stra_info.strategy]
                                stra_info.classer = getattr(stra_info.module, stra_info.strategy)
                                stra_info.file_path = file_path
                                stra_info.state = define.USER_CTRL_LOAD
                                self.center.data.strategies[stra_info.strategy] = stra_info # 先放进去，策略类初始化时要用
                                stra_info.instance = stra_info.classer() # 策略类初始化
                                stra_info.name = stra_info.instance.strategy_name
                                stra_info.introduction = stra_info.instance.strategy_introduction
                                stra_info.instance.Reload() # 可以执行一些初始化工作
                                self.log_text = "用户 加载 策略：%s, %s, %s, %d, %s" % (stra_info.strategy, stra_info.name, stra_info.introduction, stra_info.state, stra_info.file_path)
                                self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
                            except Exception as e:
                                self.log_text = "策略 %s.pyd 加载发生错误！%s %s" % (stra_info.strategy, Exception, e)
                                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
                                self.OnUnloadStrategy(stra_info) #
                        else:
                            QMessageBox.information(None, "提示", "选择的策略模块 %s 系统已经加载！" % file_name[:-4], QMessageBox.Ok)
                    else:
                        QMessageBox.information(None, "提示", "选择的策略文件 %s 不是用户定义！" % file_name, QMessageBox.Ok)
                else:
                    QMessageBox.information(None, "提示", "选择的策略文件 %s 后缀名称异常！" % file_name, QMessageBox.Ok)

    def OnUnloadStrategy(self, strategy_info):
        if strategy_info.instance != None:
            strategy_info.instance.Unload() # 可以执行一些销毁前工作
        self.center.data.strategies_locker.acquire()
        strategy = strategy_info.strategy
        if strategy in self.center.data.strategies.keys():
            del self.center.data.strategies[strategy]
        self.center.data.strategies_locker.release()
        if strategy in sys.modules.keys():
            del sys.modules[strategy]
        self.log_text = "用户 卸载 策略：%s, %s, %s" % (strategy_info.strategy, strategy_info.name, strategy_info.introduction)
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def run(self):
        self.started = True
        while self.started:
            self.center.data.strategies_locker.acquire()
            for stra_info in self.center.data.strategies.values():
                if stra_info.state == define.USER_CTRL_EXEC and stra_info.instance.IsTradeError() == True: # 这里 IsTradeError 用 == 判断，因为可能返回 None 的
                    stra_info.state = define.USER_CTRL_FAIL
                    pub.sendMessage("strategy.info.status", msg = stra_info)
            self.center.data.strategies_locker.release()
            time.sleep(3)
        self.log_text = "策略监控线程退出！"
        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def stop(self):
        self.started = False
