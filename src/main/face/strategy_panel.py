
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
import csv

from pubsub import pub
from PyQt5.QtGui import QBrush, QColor, QCursor, QFont, QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QAction, QDialog, QFileDialog, QHeaderView, QMenu, QMessageBox, QPushButton, QTableView, QHBoxLayout, QVBoxLayout

import define
import common
import logger
import center
import strate

class StraLister(QTableView):
    def __init__(self, parent):
        super(StraLister, self).__init__(parent)
        self.parent = parent
        self.stra_info_map = {}
        self.center = center.Center()
        self.head_name_list = ["", "模块", "名称", "状态", "说明", "路径"]
        self.InitUserInterface()

    def InitUserInterface(self):
        self.icon_reload = QIcon(define.DEF_ICON_STRATEGY_LOAD)
        self.icon_working = QIcon(define.DEF_ICON_STRATEGY_EXEC)
        self.icon_suspend = QIcon(define.DEF_ICON_STRATEGY_WAIT)
        self.icon_terminal = QIcon(define.DEF_ICON_STRATEGY_STOP)
        self.icon_abnormal = QIcon(define.DEF_ICON_STRATEGY_FAIL)
        self.icon_unknow = QIcon(define.DEF_ICON_STRATEGY_NULL)
        
        self.setFont(QFont("SimSun", 9))
        self.setShowGrid(False)
        self.setSortingEnabled(True) # 设置表头排序
        self.setEditTriggers(QAbstractItemView.NoEditTriggers) # 禁止编辑
        self.setSelectionBehavior(QAbstractItemView.SelectRows) # 选中整行
        self.setSelectionMode(QAbstractItemView.SingleSelection) # 选择方式 # 只允许选单行
        #self.setAlternatingRowColors(True) # 隔行变色
        self.setContextMenuPolicy(Qt.CustomContextMenu) # 右键菜单
        self.customContextMenuRequested.connect(self.OnContextMenu) # 菜单触发
        self.vertical_header = self.verticalHeader() # 垂直表头
        self.vertical_header.setVisible(False)
        self.vertical_header.setDefaultSectionSize(17)
        self.vertical_header.setSectionResizeMode(QHeaderView.Fixed) # 固定行高
        self.horizontal_header = self.horizontalHeader() # 水平表头
        self.horizontal_header.setDefaultAlignment(Qt.AlignCenter) # 显示居中
        self.stra_list_model = QStandardItemModel()
        self.stra_list_model.setColumnCount(len(self.head_name_list))
        for i in range(len(self.head_name_list)):
            self.stra_list_model.setHeaderData(i, Qt.Horizontal, self.head_name_list[i])
        self.setModel(self.stra_list_model)
        
        pub.subscribe(self.OnStrategyInfoStatus, "strategy.info.status")

    def GetSelectedRowIndex(self):
        selected = self.selectionModel().selectedRows()
        if len(selected) > 0:
            return selected[0].row() # 因为只允许选单行
        return -1

    def GetSelectedStrategy(self):
        selected = self.selectionModel().selectedRows()
        if len(selected) > 0:
            return self.stra_list_model.item(selected[0].row(), 1).text().__str__() # 因为只允许选单行
        return ""

    def ClearListItems(self):
        self.stra_info_map = {}
        row_count = self.stra_list_model.rowCount()
        if row_count > 0:
            self.stra_list_model.removeRows(0, row_count)

    def OnContextMenu(self):
        self.action_refresh = QAction(QIcon(define.DEF_ICON_STRATEGY_MENU_REFRESH), "刷新列表", self)
        self.action_refresh.setStatusTip("刷新策略列表显示")
        self.action_refresh.triggered.connect(self.OnActionRefresh)
        
        self.action_export = QAction(QIcon(define.DEF_ICON_STRATEGY_MENU_REFRESH), "导出数据", self)
        self.action_export.setStatusTip("导出策略列表数据")
        self.action_export.triggered.connect(self.OnActionExport)
        
        self.menu = QMenu(self)
        self.menu.addAction(self.action_refresh)
        self.menu.addAction(self.action_export)
        self.menu.popup(QCursor.pos())

    def OnActionRefresh(self):
        self.ClearListItems()
        self.OnReloadStrategy()

    def OnActionExport(self):
        dlg_file = QFileDialog.getSaveFileName(None, caption = "文件保存为...", filter = "CSV(逗号分隔)(*.csv)")
        if dlg_file != "":
            file_path = dlg_file.__str__()
            if file_path.endswith(".csv") == False:
                file_path += ".csv"
            try:
                writer = csv.writer(open(file_path, "wb"))
                writer.writerow([data.encode("gbk") for data in self.head_name_list[1:]]) # 排除第一列
                for stra_info in self.stra_info_map.values():
                    writer.writerow([stra_info.strategy.encode("gbk"), stra_info.name.encode("gbk"), 
                                     common.TransStrategyState(stra_info.state).encode("gbk"), 
                                     stra_info.introduction.encode("gbk"), stra_info.file_path.encode("gbk")])
                QMessageBox.information(None, "提示", "策略列表数据导出成功。", QMessageBox.Ok)
            except:
                QMessageBox.information(None, "提示", "策略列表数据导出失败！", QMessageBox.Ok)

    def OnReloadStrategy(self):
        for stra_info in self.center.data.strategies.values():
            if not stra_info.strategy in self.stra_info_map.keys():
                self.stra_info_map[stra_info.strategy] = stra_info
                row_index = self.stra_list_model.rowCount()
                self.stra_list_model.setItem(row_index, 0, QStandardItem(self.GetIconByState(stra_info.state), ""))
                self.stra_list_model.setItem(row_index, 1, QStandardItem(stra_info.strategy))
                self.stra_list_model.setItem(row_index, 2, QStandardItem(stra_info.name))
                self.stra_list_model.setItem(row_index, 3, QStandardItem(common.TransStrategyState(stra_info.state)))
                self.stra_list_model.setItem(row_index, 4, QStandardItem(stra_info.introduction))
                self.stra_list_model.setItem(row_index, 5, QStandardItem(stra_info.file_path))
                color = self.GetColorByState(stra_info.state)
                for i in range(len(self.head_name_list)):
                    self.stra_list_model.item(row_index, i).setForeground(QBrush(color))
        self.resizeColumnsToContents()

    def OnUnloadStrategy(self, stra_info):
        row_count = self.stra_list_model.rowCount()
        for i in range(row_count):
            if self.stra_list_model.item(i, 1).text().__str__() == stra_info.strategy:
                self.stra_list_model.removeRow(i)
                del self.stra_info_map[stra_info.strategy]
                break

    def OnStrategyInfoStatus(self, msg):
        self.OnChangeStrategyState(msg.data) # msg.data 为 StrategyInfo

    def OnChangeStrategyState(self, stra_info):
        row_count = self.stra_list_model.rowCount()
        for i in range(row_count):
            if self.stra_list_model.item(i, 1).text().__str__() == stra_info.strategy:
                self.stra_list_model.setItem(i, 0, QStandardItem(self.GetIconByState(stra_info.state), ""))
                self.stra_list_model.setItem(i, 3, QStandardItem(common.TransStrategyState(stra_info.state)))
                color = self.GetColorByState(stra_info.state)
                for j in range(len(self.head_name_list)):
                    self.stra_list_model.item(i, j).setForeground(QBrush(color))
                self.stra_info_map[stra_info.strategy] = stra_info
                self.selectRow(i) # 不然会出现全部行被选中的现象
                break

    def mouseDoubleClickEvent(self, event):
        QTableView.mouseDoubleClickEvent(self, event)
        pos = event.pos()
        item = self.indexAt(pos)
        if item and item.row() >= 0:
            strategy = self.stra_list_model.item(item.row(), 1).text().__str__()
            self.center.data.strategies_locker.acquire()
            self.center.data.strategies[strategy].instance.OnDoubleClick()
            self.center.data.strategies_locker.release()

    def GetIconByState(self, state):
        if state == 0:
            return self.icon_reload
        elif state == 1:
            return self.icon_working
        elif state == 2:
            return self.icon_suspend
        elif state == 3:
            return self.icon_terminal
        elif state == 4:
            return self.icon_abnormal
        else:
            return self.icon_unknow

    def GetColorByState(self, state):
        if state == 0:
            return QColor(0, 0, 0)
        elif state == 1:
            return QColor(0, 128, 255)
        elif state == 2:
            return QColor(255, 128, 0)
        elif state == 3:
            return QColor(128, 128, 128)
        elif state == 4:
            return QColor(255, 0, 0)
        else:
            return QColor(128, 128, 128)

class StrategyPanel(QDialog):
    def __init__(self, parent):
        super(StrategyPanel, self).__init__(parent)
        self.parent = parent
        self.InitUserInterface()

    def __del__(self):
        pass

    def InitUserInterface(self):
        self.button_reload = QPushButton("加  载")
        self.button_reload.setFont(QFont("SimSun", 9))
        self.button_run = QPushButton("运  行")
        self.button_run.setFont(QFont("SimSun", 9))
        self.button_suspend = QPushButton("暂  停")
        self.button_suspend.setFont(QFont("SimSun", 9))
        self.button_continue = QPushButton("继  续")
        self.button_continue.setFont(QFont("SimSun", 9))
        self.button_stop = QPushButton("停  止")
        self.button_stop.setFont(QFont("SimSun", 9))
        self.button_unload = QPushButton("卸  载")
        self.button_unload.setFont(QFont("SimSun", 9))
        
        self.h_box_buttons = QHBoxLayout()
        self.h_box_buttons.addStretch(1)
        self.h_box_buttons.addWidget(self.button_reload)
        self.h_box_buttons.addStretch(1)
        self.h_box_buttons.addWidget(self.button_run)
        self.h_box_buttons.addStretch(1)
        self.h_box_buttons.addWidget(self.button_suspend)
        self.h_box_buttons.addStretch(1)
        self.h_box_buttons.addWidget(self.button_continue)
        self.h_box_buttons.addStretch(1)
        self.h_box_buttons.addWidget(self.button_stop)
        self.h_box_buttons.addStretch(1)
        self.h_box_buttons.addWidget(self.button_unload)
        self.h_box_buttons.addStretch(1)
        
        self.button_reload.clicked.connect(self.OnClickButtonStrategyReload)
        self.button_run.clicked.connect(self.OnClickButtonStrategyRun)
        self.button_suspend.clicked.connect(self.OnClickButtonStrategySuspend)
        self.button_continue.clicked.connect(self.OnClickButtonStrategyContinue)
        self.button_stop.clicked.connect(self.OnClickButtonStrategyStop)
        self.button_unload.clicked.connect(self.OnClickButtonStrategyUnload)
        
        self.stra_lister = StraLister(self)
        
        #self.button_Test = QPushButton("Button Test", self)
        #self.button_Test.clicked.connect(self.OnButtonClicked_Test)
        
        self.h_box = QHBoxLayout()
        self.h_box.addStretch(1)
        #self.h_box.addWidget(self.button_Test)
        #self.h_box.addStretch(1)
        
        self.v_box = QVBoxLayout()
        self.v_box.setContentsMargins(0, 0, 0, 0)
        self.v_box.addWidget(self.stra_lister, 1)
        self.v_box.addLayout(self.h_box_buttons)
        self.v_box.addLayout(self.h_box)
        
        self.setLayout(self.v_box)

    def OnClickButtonStrategyReload(self):
        self.HandleStrategyUserControl("加载")

    def OnClickButtonStrategyRun(self):
        self.HandleStrategyUserControl("运行")

    def OnClickButtonStrategySuspend(self):
        self.HandleStrategyUserControl("暂停")

    def OnClickButtonStrategyContinue(self):
        self.HandleStrategyUserControl("继续")

    def OnClickButtonStrategyStop(self):
        self.HandleStrategyUserControl("停止")

    def OnClickButtonStrategyUnload(self):
        self.HandleStrategyUserControl("卸载")

    def HandleStrategyUserControl(self, str_type):
        self.center = center.StraCenter()
        self.strate = strate.StraStrate()
        if str_type == "加载":
            self.strate.OnReloadStrategy() # 先添加内部数据
            self.stra_lister.OnReloadStrategy() # 再更新界面显示
        else:
            if self.stra_lister.GetSelectedRowIndex() < 0:
                QMessageBox.information(self, "提示", "请先选择要 %s 的策略。" % str_type, QMessageBox.Ok)
                return
            else:
                strategy = self.stra_lister.GetSelectedStrategy()
                self.center.data.strategies_locker.acquire()
                strategy_info = self.center.data.strategies[strategy]
                self.center.data.strategies_locker.release()
                dlg = None
                if str_type == "运行":
                    if strategy_info.state != define.USER_CTRL_LOAD and strategy_info.state != define.USER_CTRL_STOP:
                        dlg = QMessageBox.information(self, "提示", "%s：状态不是已加载或已停止，无需运行。" % strategy, QMessageBox.Ok)
                elif str_type == "暂停":
                    if strategy_info.state != define.USER_CTRL_EXEC:
                        dlg = QMessageBox.information(self, "提示", "%s：状态不是运行中，无需暂停。" % strategy, QMessageBox.Ok)
                elif str_type == "继续":
                    if strategy_info.state != define.USER_CTRL_WAIT:
                        dlg = QMessageBox.information(self, "提示", "%s：状态不是已暂停，无需继续。" % strategy, QMessageBox.Ok)
                elif str_type == "停止":
                    if strategy_info.state != define.USER_CTRL_EXEC and strategy_info.state != define.USER_CTRL_WAIT and strategy_info.state != define.USER_CTRL_FAIL:
                        dlg = QMessageBox.information(self, "提示", "%s：状态不是运行中或已暂停或已异常，无需停止。" % strategy, QMessageBox.Ok)
                elif str_type == "卸载":
                    if strategy_info.state != define.USER_CTRL_LOAD and strategy_info.state != define.USER_CTRL_STOP:
                        dlg = QMessageBox.information(self, "提示", "%s：请先停止策略运行，再进行卸载。" % strategy, QMessageBox.Ok)
                if dlg != None:
                    return
                reply = QMessageBox.question(self, "询问", u"确定 %s 策略 %s ？" % (str_type, strategy), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    if str_type == "卸载":
                       self.stra_lister.OnUnloadStrategy(strategy_info) # 先删除界面显示
                       self.strate.OnUnloadStrategy(strategy_info) # 再删除内部数据
                    else:
                        self.strate.OnChangeStrategyState(strategy_info, str_type) # 先改变数据状态
                        self.stra_lister.OnChangeStrategyState(strategy_info) # 再改变界面显示

    def OnReloadStrategy(self):
        self.stra_lister.OnReloadStrategy()

    def OnButtonClicked_Test(self):
        sender = self.sender()
        self.parent.status_bar.showMessage(sender.text() + " was pressed")
        
        self.log_cate = "StrategyPanel"
        self.log_text = "系统初始化完成。啦啦啦啦啦啦啦啦啦啦啦啦啦，fjafhghjadkjgalfilwe5738573^*#%^^%$^*哈舒服啥时间发货时间都是"
        self.logger = logger.Logger()
        self.logger.SendMessage("D", 0, self.log_cate, self.log_text, "S")
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "S")
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")
        self.logger.SendMessage("F", 5, self.log_cate, self.log_text, "S")
        self.logger.SendMessage("D", 0, self.log_cate, self.log_text, "T")
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "T")
        self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "T")
        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "T")
        self.logger.SendMessage("F", 5, self.log_cate, self.log_text, "T")
        self.logger.SendMessage("D", 0, self.log_cate, self.log_text, "M")
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "M")
        self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "M")
        self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "M")
        self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "M")
        self.logger.SendMessage("F", 5, self.log_cate, self.log_text, "M")
        
        pub.sendMessage("tip.info.message", self.log_text)
