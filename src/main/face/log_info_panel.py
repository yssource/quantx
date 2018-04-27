
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

import csv

from PyQt5 import QtGui, QtCore

import define

class LogInfoPanel(QtGui.QWidget):
    def __init__(self, parent):
        super(LogInfoPanel, self).__init__(parent)
        self.main_window = None
        self.log_info_list = []
        self.log_info_index = 0
        self.head_name_list = ["", "时间", "级别", "分类", "信息"]
        self.InitUserInterface()

    def __del__(self):
        #self.timer_log_info_print.stop()
        #del self.timer_log_info_print
        pass

    def InitUserInterface(self):
        self.setMinimumWidth(300)
        self.setMinimumHeight(150)
        
        self.table_view = QtGui.QTableView(self)
        self.table_view.setFont(QtGui.QFont("SimSun", 9))
        self.table_view.setShowGrid(False)
        #self.table_view.setSortingEnabled(True) # 设置表头排序
        self.table_view.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers) # 禁止编辑
        self.table_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows) # 选中整行
        self.table_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection) # 选择方式
        #self.table_view.setAlternatingRowColors(True) # 隔行变色
        self.table_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu) # 右键菜单
        self.table_view.customContextMenuRequested.connect(self.OnContextMenu) # 菜单触发
        self.vertical_header = self.table_view.verticalHeader() # 垂直表头
        self.vertical_header.setVisible(False)
        self.vertical_header.setDefaultSectionSize(17)
        self.vertical_header.setResizeMode(QtGui.QHeaderView.Fixed) # 固定行高
        self.horizontal_header = self.table_view.horizontal_header() # 水平表头
        self.horizontal_header.setDefaultAlignment(QtCore.Qt.AlignCenter) # 显示居中
        self.info_list_model = QtGui.QStandardItemModel()
        self.info_list_model.setColumnCount(len(self.head_name_list))
        for i in range(len(self.head_name_list)):
            self.info_list_model.setHeaderData(i, QtCore.Qt.Horizontal, self.head_name_list[i])
        self.table_view.setModel(self.info_list_model)
        
        self.v_box = QtGui.QVBoxLayout()
        self.v_box.setContentsMargins(5, 5, 5, 5)
        self.v_box.addWidget(self.table_view)
        
        self.setLayout(self.v_box)
        
        # 这样不需要来一条日志就刷新一下列表
        #self.timer_log_info_print = QtCore.QTimer()
        #self.timer_log_info_print.timeout.connect(self.OnLogInfoPrint)
        #self.timer_log_info_print.start(250)

    def event(self, event):
        if event.type() == define.DEF_EVENT_LOG_INFO_PRINT:
            self.OnLogInfoPrint()
        return QtGui.QWidget.event(self, event)

    def AddLogInfo(self, item):
        self.log_info_list.append(item)

    def GetLogColor(self, log_class):
        if log_class == 0: return QtGui.QColor(128, 128, 128)
        elif log_class == 1:
            if self.main_window != None:
                if self.main_window.action_show_skin__norm.isChecked():
                    return QtGui.QColor(0, 0, 0)
                elif self.main_window.action_show_skin_dark.isChecked():
                    return QtGui.QColor(255, 255, 255)
            else:
                return QtGui.QColor(0, 255, 0)
        elif log_class == 2: return QtGui.QColor(0, 128, 255)
        elif log_class == 3: return QtGui.QColor(255, 128, 0)
        elif log_class == 4: return QtGui.QColor(255, 0, 255)
        elif log_class == 5: return QtGui.QColor(255, 0, 0)
        else: return QtGui.QColor(0, 0, 0)

    def OnContextMenu(self):
        self.action_clear = QtGui.QAction(QtGui.QIcon(define.DEF_ICON_LOG_INFO_MENU_CLEAR), "清除日志", self)
        self.action_clear.setStatusTip("清除日志信息显示")
        self.action_clear.triggered.connect(self.OnActionClear)
        
        self.action_export = QtGui.QAction(QtGui.QIcon(define.DEF_ICON_LOG_INFO_MENU_EXPORT), "导出数据", self)
        self.action_export.setStatusTip("导出日志信息数据")
        self.action_export.triggered.connect(self.OnActionExport)
        
        self.menu = QtGui.QMenu(self)
        self.menu.addAction(self.action_clear)
        self.menu.addAction(self.action_export)
        self.menu.popup(QtGui.QCursor.pos())

    def OnActionClear(self):
        row_count = self.info_list_model.rowCount()
        if row_count > 0:
            self.info_list_model.removeRows(0, row_count)

    def OnActionExport(self):
        dlg_file = QtGui.QFileDialog.getSaveFileName(None, caption = "文件保存为...", filter = "CSV(逗号分隔)(*.csv)")
        if dlg_file != "":
            file_path = dlg_file.__str__()
            if file_path.endswith(".csv") == False:
                file_path += ".csv"
            try:
                writer = csv.writer(open(file_path, "wb"))
                writer.writerow([data.encode("gbk") for data in self.head_name_list[1:]]) # 排除第一列
                for i in range(self.log_info_index):
                    log_item = self.log_info_list[i]
                    writer.writerow([log_item.time_stamp.strftime("%H:%M:%S.%f"), log_item.log_kind.encode("gbk"), 
                                     log_item.log_cate.encode("gbk"), log_item.log_info.encode("gbk")])
                QtGui.QMessageBox.information(None, "提示", "日志信息数据导出成功。", QtGui.QMessageBox.Ok)
            except:
                QtGui.QMessageBox.information(None, "提示", "日志信息数据导出失败！", QtGui.QMessageBox.Ok)

    def OnLogInfoPrint(self):
        log_info_count = len(self.log_info_list)
        if log_info_count > self.log_info_index:
            for i in range(self.log_info_index, log_info_count):
                log_item = self.log_info_list[i]
                log_time = log_item.time_stamp.strftime("%H:%M:%S.%f")
                log_kind = log_item.log_kind
                log_cate = log_item.log_cate
                log_info = log_item.log_info
                log_class = log_item.log_class
                log_color = self.GetLogColor(log_class)
                
                row_index = self.info_list_model.rowCount()
                self.info_list_model.setItem(row_index, 0, QtGui.QStandardItem(QtGui.QIcon(define.DEF_ICON_LOG_INFO_ITEM), ""))
                self.info_list_model.setItem(row_index, 1, QtGui.QStandardItem(log_time))
                self.info_list_model.setItem(row_index, 2, QtGui.QStandardItem(log_kind))
                self.info_list_model.setItem(row_index, 3, QtGui.QStandardItem(log_cate))
                self.info_list_model.setItem(row_index, 4, QtGui.QStandardItem(log_info))
                self.info_list_model.item(row_index, 0).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter) # AlignCenter
                self.info_list_model.item(row_index, 1).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter) # AlignCenter
                self.info_list_model.item(row_index, 2).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter) # AlignCenter
                self.info_list_model.item(row_index, 3).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter) # AlignCenter
                self.info_list_model.item(row_index, 4).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
                for i in range(len(self.head_name_list)):
                    self.info_list_model.item(row_index, i).setForeground(QtGui.QBrush(log_color))
            
            self.table_view.resizeColumnsToContents()
            self.table_view.scrollToBottom()
            
            self.log_info_index = log_info_count #

    def ChangeInfoMsgColor(self):
        log_color = self.GetLogColor(1) # info
        row_number = self.info_list_model.rowCount()
        for i in range(row_number):
            if self.info_list_model.item(i, 2).text().__str__() == "I":
                for j in range(len(self.head_name_list)):
                    self.info_list_model.item(i, j).setForeground(QtGui.QBrush(log_color))
