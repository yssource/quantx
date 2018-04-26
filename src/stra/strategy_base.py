
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

import config
import define
import logger
import center

class StrategyBase(threading.Thread):
    def __init__(self, strategy, strategy_name, strategy_introduction):
        self.log_text = ""
        self.log_cate = "StrategyBase"
        self.beat_calc = None
        self.strategy_panel = None
        self.config = config.Config()
        self.logger = logger.Logger()
        self.center = center.Center()
        self.strategy = strategy
        self.strategy_name = strategy_name
        self.strategy_introduction = strategy_introduction
        
        self.center.data.strategies_locker.acquire()
        self.strategy_info = self.center.data.strategies[self.strategy] # 已经存在
        self.center.data.strategies_locker.release()
        
        self.show_debug_info = self.config.cfg_main.stra_debug_info # 为 1 或 0
        
        self.started = False

    def CheckUserCtrl(self):
        self.strategy_info.state_locker.acquire()
        stra_state = self.strategy_info.state
        self.strategy_info.state_locker.release()
        if stra_state == define.USER_CTRL_EXEC:
            return 1
        elif stra_state == define.USER_CTRL_STOP:
            self.log_text = "用户 停止 策略 %s %s 执行！" % (self.strategy, self.strategy_name)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
            return -1
        elif stra_state == define.USER_CTRL_WAIT:
            self.log_text = "用户 暂停 策略 %s %s 执行！" % (self.strategy, self.strategy_name)
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            while stra_state == define.USER_CTRL_WAIT:
                time.sleep(1.0)
                self.strategy_info.state_locker.acquire()
                stra_state = self.strategy_info.state
                self.strategy_info.state_locker.release()
            if stra_state == define.USER_CTRL_EXEC:
                self.log_text = "用户 继续 策略 %s %s 执行！" % (self.strategy, self.strategy_name)
                self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
                return 1
            elif stra_state == define.USER_CTRL_STOP:
                self.log_text = "用户 停止 策略 %s %s 执行！" % (self.strategy, self.strategy_name)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
                return -1

    def run(self):
        self.started = True
        while self.started:
            if self.CheckUserCtrl() != 1:
                break
            if self.beat_calc != None:
                time.sleep(self.beat_calc.calc_wait) # TODO: 先等待，避免动态加载策略模块后类 beat_calc 中 self.parent.SendMessage 冲突，目前原因未明
                self.beat_calc.MakeCalc()
                #time.sleep(self.beat_calc.calc_wait)
            else:
                time.sleep(3)
        self.started = False
        self.log_text = "策略 %s %s 定期执行线程退出！" % (self.strategy, self.strategy_name)
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def Reload(self):
        self.log_text = "策略 %s %s 执行一些初始化工作。" % (self.strategy, self.strategy_name)
        self.logger.SendMessage("D", 0, self.log_cate, self.log_text, "S")

    def Working(self):
        self.strategy_info.state_locker.acquire()
        self.strategy_info.state = define.USER_CTRL_EXEC
        self.strategy_info.state_locker.release()

        threading.Thread.__init__(self)
        self.start()
        self.log_text = "用户 运行 策略：%s, %s, %s" % (self.strategy, self.strategy_name, self.strategy_introduction)
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def Suspend(self):
        self.strategy_info.state_locker.acquire()
        self.strategy_info.state = define.USER_CTRL_WAIT
        self.strategy_info.state_locker.release()
        self.log_text = "用户 暂停 策略：%s, %s, %s" % (self.strategy, self.strategy_name, self.strategy_introduction)
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def Continue(self):
        self.strategy_info.state_locker.acquire()
        self.strategy_info.state = define.USER_CTRL_EXEC
        self.strategy_info.state_locker.release()
        self.log_text = "用户 继续 策略：%s, %s, %s" % (self.strategy, self.strategy_name, self.strategy_introduction)
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def Terminal(self):
        self.strategy_info.state_locker.acquire()
        self.strategy_info.state = define.USER_CTRL_STOP
        self.strategy_info.state_locker.release()
        self.log_text = "用户 停止 策略：%s, %s, %s" % (self.strategy, self.strategy_name, self.strategy_introduction)
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")

    def Unload(self):
        if self.strategy_panel != None:
            self.strategy_panel.close()
        self.log_text = "策略 %s %s 执行一些销毁前工作。" % (self.strategy, self.strategy_name)
        self.logger.SendMessage("D", 0, self.log_cate, self.log_text, "S")

    def OnWorking(self): # 供具体策略继承调用，在 运行 前执行一些操作
        pass

    def OnSuspend(self): # 供具体策略继承调用，在 暂停 前执行一些操作
        pass

    def OnContinue(self): # 供具体策略继承调用，在 继续 前执行一些操作
        pass

    def OnTerminal(self): # 供具体策略继承调用，在 停止 前执行一些操作
        pass

    def OnDoubleClick(self): # 供具体策略继承调用，在 双击 时执行一些操作
        pass

    def OnTraderEvent(self, trader, ret_func, task_item): # 交易模块事件通知，供具体策略继承调用
        pass

    def IsTradeError(self): # 供具体策略继承调用，判断交易是否异常 #如果继承后仍然 pass 则函数返回会被视为 None，既非 True 也非 False
        pass
