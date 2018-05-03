
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
import traceback

from PyQt5.QtWidgets import QFileDialog, QMessageBox

import config
import define
import common
import logger
import center

class Analys(common.Singleton):
    def __init__(self):
        self.log_text = ""
        self.log_cate = "Analys"
        self.symbol_list = []
        self.trading_day_list = []
        self.analysis_info = None
        self.config = config.Config()
        self.logger = logger.Logger()

    def __del__(self):
        pass

    def GetInstance(self):
        return self

    def SetSymbolList(self, symbol_list):
        self.symbol_list = symbol_list

    def SetTradingDayList(self, trading_day_list):
        self.trading_day_list = trading_day_list

    def OnChangeAnalysisState(self, analysis_info, str_type):
        if str_type == "运行":
            if analysis_info.instance.IsModelError() == True: # 用 == 判断，可能返回 None 的
                self.log_text = "模型 %s %s 的回测已经发生异常，重新加载运行！" % (analysis_info.analysis, analysis_info.name)
                self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            elif analysis_info.instance.started == True:
                self.log_text = "模型 %s %s 的回测线程还未结束，无法重新运行！" % (analysis_info.analysis, analysis_info.name)
                self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            else:
                try:
                    analysis_info.instance.OnWorking()
                    analysis_info.instance.Working()
                    analysis_info.instance.BackTest() #
                except Exception as e:
                    traceback.print_exc() #
                    self.log_text = "模型 %s %s 运行 时发生异常！%s" % (analysis_info.analysis, analysis_info.name, e)
                    self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        elif str_type == "暂停":
            try:
                analysis_info.instance.OnSuspend()
                analysis_info.instance.Suspend()
            except Exception as e:
                traceback.print_exc() #
                self.log_text = "模型 %s %s 暂停 时发生异常！%s" % (analysis_info.analysis, analysis_info.name, e)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        elif str_type == "继续":
            try:
                analysis_info.instance.OnContinue()
                analysis_info.instance.Continue()
            except Exception as e:
                traceback.print_exc() #
                self.log_text = "模型 %s %s 继续 时发生异常！%s" % (analysis_info.analysis, analysis_info.name, e)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        elif str_type == "停止":
            try:
                analysis_info.instance.OnTerminal()
                analysis_info.instance.Terminal()
            except Exception as e:
                traceback.print_exc() #
                self.log_text = "模型 %s %s 停止 时发生异常！%s" % (analysis_info.analysis, analysis_info.name, e)
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def OnReloadAnalysis(self):
        anal_folder = self.config.cfg_main.anal_folder
        sys.path.insert(0, anal_folder) # 添加回测模块查找路径

        dlg_file = QFileDialog.getOpenFileName(None, caption = "选择回测文件...", directory = anal_folder, filter = "Python Files(*.py*)")
        if dlg_file != "":
            file_path = dlg_file[0].__str__()
            file_name = os.path.basename(file_path)
            if file_name[-3:] == ".py":
                if file_name != "__init__.py" and file_name != "analysis_base.py":
                    if not (file_name[:-3] in sys.modules.keys()):
                        file_path = anal_folder + "/" + file_name
                        analy_info = center.AnalysisInfo()
                        analy_info.analysis = file_name[:-3]
                        try:
                            __import__(analy_info.analysis)
                            analy_info.module = sys.modules[analy_info.analysis]
                            analy_info.classer = getattr(analy_info.module, analy_info.analysis)
                            analy_info.filePath = file_path
                            analy_info.state = define.USER_CTRL_LOAD
                            self.analysis_info = analy_info # 先赋值，策略类初始化时要用
                            analy_info.instance = analy_info.classer() # 策略类初始化
                            analy_info.name = analy_info.instance.analysis_name
                            analy_info.introduction = analy_info.instance.analy_intro
                            analy_info.instance.Reload() # 可以执行一些初始化工作
                            self.log_text = "用户 加载 回测：%s, %s, %s, %d, %s" % (analy_info.analysis, analy_info.name, analy_info.introduction, analy_info.state, analy_info.file_path)
                            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
                        except Exception as e:
                            self.log_text = "回测 %s.py 加载发生错误！%s %s" % (analy_info.analysis, Exception, e)
                            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
                            self.OnUnloadAnalysis(analy_info) #
                    else:
                        QMessageBox.information(None, "提示", "选择的回测模块 %s 系统已经加载！" % file_name[:-3], QMessageBox.Ok)
                else:
                    QMessageBox.information(None, "提示", "选择的回测文件 %s 不是用户定义！" % file_name, QMessageBox.Ok)
            elif file_name[-4:] == ".pyd":
                if file_name != "analysis_base.pyd":
                    if not (file_name[:-4] in sys.modules.keys()):
                        file_path = anal_folder + "/" + file_name
                        analy_info = center.AnalysisInfo()
                        analy_info.analysis = file_name[:-4]
                        try:
                            __import__(analy_info.analysis)
                            analy_info.module = sys.modules[analy_info.analysis]
                            analy_info.classer = getattr(analy_info.module, analy_info.analysis)
                            analy_info.filePath = file_path
                            analy_info.state = define.USER_CTRL_LOAD
                            self.analysis_info = analy_info # 先赋值，策略类初始化时要用
                            analy_info.instance = analy_info.classer() # 策略类初始化
                            analy_info.name = analy_info.instance.analysis_name
                            analy_info.introduction = analy_info.instance.analy_intro
                            analy_info.instance.Reload() # 可以执行一些初始化工作
                            self.log_text = "用户 加载 回测：%s, %s, %s, %d, %s" % (analy_info.analysis, analy_info.name, analy_info.introduction, analy_info.state, analy_info.file_path)
                            self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
                        except Exception as e:
                            self.log_text = "回测 %s.pyd 加载发生错误！%s %s" % (analy_info.analysis, Exception, e)
                            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
                            self.OnUnloadAnalysis(analy_info) #
                    else:
                        QMessageBox.information(None, "提示", "选择的回测模块 %s 系统已经加载！" % file_name[:-4], QMessageBox.Ok)
                else:
                    QMessageBox.information(None, "提示", "选择的回测文件 %s 不是用户定义！" % file_name, QMessageBox.Ok)
            else:
                QMessageBox.information(None, "提示", "选择的回测文件 %s 后缀名称异常！" % file_name, QMessageBox.Ok)

    def OnUnloadAnalysis(self, analysis_info):
        if analysis_info.instance != None:
            analysis_info.instance.Unload() # 可以执行一些销毁前工作
        if analysis_info.analysis in sys.modules.keys():
            del sys.modules[analysis_info.analysis]
        self.analysis_info = None
        self.log_text = "用户 卸载 回测：%s, %s, %s" % (analysis_info.analysis, analysis_info.name, analysis_info.introduction)
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
