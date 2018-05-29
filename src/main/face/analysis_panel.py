
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
import time
import datetime
import operator
import threading
from datetime import datetime, date

from PyQt5.QtGui import QFont
from PyQt5.QtCore import QAbstractTableModel, QDateTime, QEvent, Qt
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QCheckBox, QComboBox, QDateTimeEdit, QDialog, QDoubleSpinBox, QFileDialog, QGroupBox, QLabel
from PyQt5.QtWidgets import QLineEdit, QHeaderView, QMessageBox, QProgressBar, QPushButton, QRadioButton, QTableView, QTextEdit, QHBoxLayout, QVBoxLayout

import config
import define
import common
import logger
import analys
import basicx
import assess

class DataTableModel(QAbstractTableModel): # 第一列为选择框控件
    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self.parent = parent
        self.head_list = []
        self.data_list = []
        self.data_dict = {} # 按索引保存所在行
        self.index_column = 0

    def setHeadList(self, head_list):
        self.head_list = head_list

    def setDataList(self, data_list):
        self.data_list = data_list
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(None), self.columnCount(None)))
        self.layoutChanged.emit()
        self.data_dict = {} #
        for i in range(len(self.data_list)):
            self.data_dict[self.data_list[i][self.index_column]] = i

    def setIndexColumn(self, col):
        self.index_column = col

    def rowCount(self, parent):
        return len(self.data_list)

    def columnCount(self, parent):
        return len(self.head_list)

    def data(self, index, role):
        if not index.isValid():
            return None
        value = None
        if index.column() == 0:
            value = self.data_list[index.row()][index.column()].text()
        else:
            value = self.data_list[index.row()][index.column()]
        if role == Qt.EditRole:
            return value
        elif role == Qt.DisplayRole:
            return value
        elif role == Qt.CheckStateRole:
            if index.column() == 0:
                if self.data_list[index.row()][index.column()].isChecked():
                    return Qt.Checked
                else:
                    return Qt.Unchecked
        elif role == Qt.FontRole:
            pass
        elif role == Qt.TextAlignmentRole: # 显示布局
            if -1 == self.parent.data_align[index.column()]:
                return Qt.AlignVCenter | Qt.AlignLeft
            elif 1 == self.parent.data_align[index.column()]:
                return Qt.AlignVCenter | Qt.AlignRight
            else:
                return Qt.AlignVCenter | Qt.AlignHCenter
        elif role == Qt.BackgroundRole:
            pass
        elif role == Qt.BackgroundColorRole:
            pass
        elif role == Qt.ForegroundRole:
            pass
        elif role == Qt.TextColorRole:
            pass
        elif role == Qt.CheckStateRole:
            pass
        elif role == Qt.InitialSortOrderRole:
            pass

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.head_list[col]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return col + 1
        return None

    def sort(self, col, order):
        if col != 0:
            self.layoutAboutToBeChanged.emit()
            self.data_list = sorted(self.data_list, key = operator.itemgetter(col))
            if order == Qt.DescendingOrder:
                self.data_list.reverse()
            self.layoutChanged.emit()
            self.data_dict = {} #
            for i in range(len(self.data_list)):
                self.data_dict[self.data_list[i][self.index_column]] = i

    def flags(self, index):
        if not index.isValid():
            return None
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == Qt.CheckStateRole and index.column() == 0:
            if value == Qt.Checked:
                self.data_list[index.row()][index.column()].setChecked(True)
            else:
                self.data_list[index.row()][index.column()].setChecked(False)
        self.dataChanged.emit(index, index)
        return True

    def getRowIndex(self, key):
        if key in self.data_dict.keys():
            return self.data_dict[key]
        else:
            return -1

    def setCellText(self, key, col, text):
        if key in self.data_dict.keys() and col < len(self.head_list):
            self.setData(self.createIndex(self.data_dict[key], col), text, Qt.DisplayRole)

    def getCellText(self, row, col):
        if row < len(self.data_list) and col < len(self.head_list):
            return self.data(self.createIndex(row, col), Qt.DisplayRole)
        return ""

    def setAllCheck(self, check):
        for item in self.data_list:
            item[0].setChecked(check)
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(None), self.columnCount(None)))
        self.layoutChanged.emit()

    def getAllCheck(self):
        return filter(lambda x: x[0].isChecked() == True, self.data_list)

class DataLister(QTableView):
    def __init__(self, parent):
        super(DataLister, self).__init__(parent)
        self.parent = parent
        self.basicx = basicx.BasicX()
        self.data_list = []
        self.data_align = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # 必须 # 左：-1，中：0，右：1
        self.head_list = ["", "市场", "代码", "名称", "类别", "板块", "ST股", "状态", "上市", "1_D", "1_M"]
        self.head_index_code = 2
        
        self.InitUserInterface()

    def InitUserInterface(self):
        self.setFont(QFont("SimSun", 9))
        self.setShowGrid(False)
        self.setSortingEnabled(True) # 设置表头排序
        self.setEditTriggers(QAbstractItemView.NoEditTriggers) # 禁止编辑
        self.setSelectionBehavior(QAbstractItemView.SelectRows) # 选中整行
        self.setSelectionMode(QAbstractItemView.SingleSelection) # 选择方式 # 只允许选单行
        self.setAlternatingRowColors(True) # 隔行变色
        self.setContextMenuPolicy(Qt.CustomContextMenu) # 右键菜单
        self.customContextMenuRequested.connect(self.OnContextMenu) # 菜单触发
        self.vertical_header = self.verticalHeader() # 垂直表头
        self.vertical_header.setDefaultAlignment(Qt.AlignCenter) # 显示居中
        self.vertical_header.setVisible(True)
        self.vertical_header.setDefaultSectionSize(17)
        self.vertical_header.setSectionResizeMode(QHeaderView.Fixed) # 固定行高
        self.horizontal_header = self.horizontalHeader() # 水平表头
        self.horizontal_header.setDefaultAlignment(Qt.AlignCenter) # 显示居中
        self.data_list_model = DataTableModel(self)
        self.data_list_model.setHeadList(self.head_list)
        self.data_list_model.setIndexColumn(self.head_index_code) # 根据 code 索引
        self.setModel(self.data_list_model)
        #self.clicked.connect(self.OnClicked)
        self.resizeColumnsToContents()

    def OnClicked(self, item):
        print("row：%d" % item.row())
        content = item.data()
        print(content, "clicked：{}".format(content))

    def mouseDoubleClickEvent(self, event):
        QTableView.mouseDoubleClickEvent(self, event)
        pos = event.pos()
        item = self.indexAt(pos)
        if item and item.row() >= 0:
            code = self.data_list_model.getCellText(item.row(), self.head_index_code)
            print(code)

    def OnContextMenu(self, pos):
        index = self.indexAt(pos)
        if index and index.row() >= 0:
            self.parent.ShowContextMenu(index)
        else:
            self.parent.ShowContextMenu(None)

    def ClearListItems(self):
        self.data_list = []
        self.data_list_model.setDataList(self.data_list)

    def GetRowIndex(self, key):
        return self.data_list_model.getRowIndex(key)

    def SetCellText(self, key, col, text):
        self.data_list_model.setCellText(key, col, text)

    def GetCellText(self, row, col):
        return self.data_list_model.getCellText(row, col)

    def SetAllCheck(self, check):
        self.data_list_model.setAllCheck(check)

    def GetAllCheck(self):
        return self.data_list_model.getAllCheck()

    def OnActionRefresh(self):
        self.ClearListItems()
        self.OnReloadSecurityInfo()

    def OnReloadSecurityInfo(self):
        self.table_dict_daily = {}
        result_table_daily = self.basicx.GetTables_Stock_Daily()
        if not result_table_daily.empty:
            for index, row in result_table_daily.iterrows():
                self.table_dict_daily[row["table"]] = row["table"]
        self.table_dict_kline_1_m = {}
        result_table_kline_1_m = self.basicx.GetTables_Stock_Kline_1_M()
        if not result_table_kline_1_m.empty:
            for index, row in result_table_kline_1_m.iterrows():
                self.table_dict_kline_1_m[row["table"]] = row["table"]
        result = self.basicx.GetSecurityInfo()
        if not result.empty:
            for index, row in result.iterrows():
                if self.parent.check_box_security_category_0.isChecked() == False and row["category"] == define.DEF_SECURITY_INFO_CATEGORY_0: # 未知
                    continue
                if self.parent.check_box_security_category_1.isChecked() == False and row["category"] == define.DEF_SECURITY_INFO_CATEGORY_1: # 沪A主板
                    continue
                if self.parent.check_box_security_category_2.isChecked() == False and row["category"] == define.DEF_SECURITY_INFO_CATEGORY_2: # 深A主板
                    continue
                if self.parent.check_box_security_category_3.isChecked() == False and row["category"] == define.DEF_SECURITY_INFO_CATEGORY_3: # 深A中小板
                    continue
                if self.parent.check_box_security_category_4.isChecked() == False and row["category"] == define.DEF_SECURITY_INFO_CATEGORY_4: # 深A创业板
                    continue
                if self.parent.check_box_security_category_5.isChecked() == False and row["category"] == define.DEF_SECURITY_INFO_CATEGORY_5: # 沪ETF基金
                    continue
                if self.parent.check_box_security_category_6.isChecked() == False and row["category"] == define.DEF_SECURITY_INFO_CATEGORY_6: # 深ETF基金
                    continue
                if self.parent.check_box_security_category_7.isChecked() == False and row["category"] == define.DEF_SECURITY_INFO_CATEGORY_7: # 沪LOF基金
                    continue
                if self.parent.check_box_security_category_8.isChecked() == False and row["category"] == define.DEF_SECURITY_INFO_CATEGORY_8: # 深LOF基金
                    continue
                if self.parent.check_box_security_category_9.isChecked() == False and row["category"] == define.DEF_SECURITY_INFO_CATEGORY_9: # 沪分级子基金
                    continue
                if self.parent.check_box_security_category_10.isChecked() == False and row["category"] == define.DEF_SECURITY_INFO_CATEGORY_10: # 深分级子基金
                    continue
                if self.parent.check_box_security_category_11.isChecked() == False and row["category"] == define.DEF_SECURITY_INFO_CATEGORY_11: # 沪封闭式基金
                    continue
                if self.parent.check_box_security_category_12.isChecked() == False and row["category"] == define.DEF_SECURITY_INFO_CATEGORY_12: # 深封闭式基金
                    continue
                if self.parent.check_box_security_list_state_1.isChecked() == False and row["list_state"] == define.DEF_SECURITY_INFO_LIST_STATE_1: # 上市
                    continue
                if self.parent.check_box_security_list_state_2.isChecked() == False and row["list_state"] == define.DEF_SECURITY_INFO_LIST_STATE_2: # 暂停
                    continue
                if self.parent.check_box_security_list_state_3.isChecked() == False and row["list_state"] == define.DEF_SECURITY_INFO_LIST_STATE_3: # 终止
                    continue
                if self.parent.check_box_security_list_state_4.isChecked() == False and row["list_state"] == define.DEF_SECURITY_INFO_LIST_STATE_4: # 其他
                    continue
                if self.parent.check_box_security_list_state_5.isChecked() == False and row["list_state"] == define.DEF_SECURITY_INFO_LIST_STATE_5: # 交易
                    continue
                if self.parent.check_box_security_list_state_6.isChecked() == False and row["list_state"] == define.DEF_SECURITY_INFO_LIST_STATE_6: # 停牌
                    continue
                if self.parent.check_box_security_list_state_7.isChecked() == False and row["list_state"] == define.DEF_SECURITY_INFO_LIST_STATE_7: # 摘牌
                    continue
                if self.parent.check_box_security_st_non.isChecked() == True and row["is_st"] == define.DEF_SECURITY_INFO_ST_NON: # 非ST股
                    continue
                if self.parent.check_box_security_st_use.isChecked() == True and row["is_st"] == define.DEF_SECURITY_INFO_ST_USE: # 仅ST股
                    continue
                exist_data_table_daily = False
                exist_data_table_kline_1_m = False
                exist_data_table_flag_daily = "-"
                exist_data_table_flag_kline_1_m = "-"
                table_name_daily = "stock_daily_%s_%s" % (row["market"].lower(), row["code"])
                table_name_kline_1_m = "stock_kline_1_m_%s_%s" % (row["market"].lower(), row["code"])
                if table_name_daily in self.table_dict_daily.keys():
                    exist_data_table_daily = True
                    exist_data_table_flag_daily = "Y"
                if table_name_kline_1_m in self.table_dict_kline_1_m.keys():
                    exist_data_table_kline_1_m = True
                    exist_data_table_flag_kline_1_m = "Y"
                if self.parent.check_box_security_data_daily.isChecked() == True and exist_data_table_daily == False: # 日线
                    continue
                if self.parent.check_box_security_data_kline_1_m.isChecked() == True and exist_data_table_kline_1_m == False: # 1分钟线
                    continue
                check_box = QCheckBox("")
                check_box.setChecked(True)
                self.data_list.append([check_box, row["market"], row["code"], row["name"], 
                                      common.TransSecurityCategory(row["category"]), common.TransSecuritySector(row["sector"]), 
                                      common.TransSecurityST(row["is_st"]), common.TransSecurityListState(row["list_state"]), 
                                      str(row["list_date"]), exist_data_table_flag_daily, exist_data_table_flag_kline_1_m])
            self.data_list_model.setDataList(self.data_list)
            self.resizeColumnsToContents()
            self.setColumnWidth(0, 20) # 选择列宽度
            self.sortByColumn(self.head_index_code, Qt.AscendingOrder) # 按照 code 排序

class AnalysisPanel(QDialog):
    def __init__(self, parent):
        super(AnalysisPanel, self).__init__(parent)
        self.parent = parent
        self.log_text = ""
        self.log_cate = "AnalysisPanel"
        self.config = config.Config()
        self.logger = logger.Logger()
        self.basicx = basicx.BasicX()
        self.analysis_progress = 0
        self.get_quote_data_progress = 0
        self.getting = False
        self.suspend = False
        self.analysis_trading_day_list = [] # 存储交易日期date
        self.analysis_trading_day_dict = {} # 用于交易日数计算
        self.daily_report_folder = ""
        self.assess = assess.Assess(data_folder = self.config.cfg_main.data_folder, save_folder = self.config.cfg_anal.save_folder)
        
        self.InitUserInterface()

    def __del__(self):
        pass

    def InitUserInterface(self):
        self.data_lister = DataLister(self)
        self.data_lister.setMinimumWidth(500)
        
        self.check_box_security_check_all = QCheckBox()
        self.check_box_security_check_all.setText("全选")
        self.check_box_security_check_all.setChecked(self.config.cfg_anal.filter_security_check_all)
        
        self.check_box_security_category_0 = QCheckBox()
        self.check_box_security_category_0.setText("未知")
        self.check_box_security_category_0.setChecked(self.config.cfg_anal.filter_security_category_0)
        
        self.check_box_security_category_1 = QCheckBox()
        self.check_box_security_category_1.setText("沪A主板")
        self.check_box_security_category_1.setChecked(self.config.cfg_anal.filter_security_category_1)
        
        self.check_box_security_category_2 = QCheckBox()
        self.check_box_security_category_2.setText("深A主板")
        self.check_box_security_category_2.setChecked(self.config.cfg_anal.filter_security_category_2)
        
        self.check_box_security_category_3 = QCheckBox()
        self.check_box_security_category_3.setText("深A中小板")
        self.check_box_security_category_3.setChecked(self.config.cfg_anal.filter_security_category_3)
        
        self.check_box_security_category_4 = QCheckBox()
        self.check_box_security_category_4.setText("深A创业板")
        self.check_box_security_category_4.setChecked(self.config.cfg_anal.filter_security_category_4)
        
        self.check_box_security_category_5 = QCheckBox()
        self.check_box_security_category_5.setText("沪ETF基金")
        self.check_box_security_category_5.setChecked(self.config.cfg_anal.filter_security_category_5)
        
        self.check_box_security_category_6 = QCheckBox()
        self.check_box_security_category_6.setText("深ETF基金")
        self.check_box_security_category_6.setChecked(self.config.cfg_anal.filter_security_category_6)
        
        self.check_box_security_category_7 = QCheckBox()
        self.check_box_security_category_7.setText("沪LOF基金")
        self.check_box_security_category_7.setChecked(self.config.cfg_anal.filter_security_category_7)
        
        self.check_box_security_category_8 = QCheckBox()
        self.check_box_security_category_8.setText("深LOF基金")
        self.check_box_security_category_8.setChecked(self.config.cfg_anal.filter_security_category_8)
        
        self.check_box_security_category_9 = QCheckBox()
        self.check_box_security_category_9.setText("沪分级子基金")
        self.check_box_security_category_9.setChecked(self.config.cfg_anal.filter_security_category_9)
        
        self.check_box_security_category_10 = QCheckBox()
        self.check_box_security_category_10.setText("深分级子基金")
        self.check_box_security_category_10.setChecked(self.config.cfg_anal.filter_security_category_10)
        
        self.check_box_security_category_11 = QCheckBox()
        self.check_box_security_category_11.setText("沪封闭式基金")
        self.check_box_security_category_11.setChecked(self.config.cfg_anal.filter_security_category_11)
        
        self.check_box_security_category_12 = QCheckBox()
        self.check_box_security_category_12.setText("深封闭式基金")
        self.check_box_security_category_12.setChecked(self.config.cfg_anal.filter_security_category_12)
        
        self.check_box_security_list_state_1 = QCheckBox()
        self.check_box_security_list_state_1.setText("上市")
        self.check_box_security_list_state_1.setChecked(self.config.cfg_anal.filter_security_list_state_1)
        
        self.check_box_security_list_state_2 = QCheckBox()
        self.check_box_security_list_state_2.setText("暂停")
        self.check_box_security_list_state_2.setChecked(self.config.cfg_anal.filter_security_list_state_2)
        
        self.check_box_security_list_state_3 = QCheckBox()
        self.check_box_security_list_state_3.setText("终止")
        self.check_box_security_list_state_3.setChecked(self.config.cfg_anal.filter_security_list_state_3)
        
        self.check_box_security_list_state_4 = QCheckBox()
        self.check_box_security_list_state_4.setText("其他")
        self.check_box_security_list_state_4.setChecked(self.config.cfg_anal.filter_security_list_state_4)
        
        self.check_box_security_list_state_5 = QCheckBox()
        self.check_box_security_list_state_5.setText("交易")
        self.check_box_security_list_state_5.setChecked(self.config.cfg_anal.filter_security_list_state_5)
        
        self.check_box_security_list_state_6 = QCheckBox()
        self.check_box_security_list_state_6.setText("停牌")
        self.check_box_security_list_state_6.setChecked(self.config.cfg_anal.filter_security_list_state_6)
        
        self.check_box_security_list_state_7 = QCheckBox()
        self.check_box_security_list_state_7.setText("摘牌")
        self.check_box_security_list_state_7.setChecked(self.config.cfg_anal.filter_security_list_state_7)
        
        self.check_box_security_st_non = QCheckBox()
        self.check_box_security_st_non.setText("非ST股")
        self.check_box_security_st_non.setChecked(self.config.cfg_anal.filter_security_st_non)
        
        self.check_box_security_st_use = QCheckBox()
        self.check_box_security_st_use.setText("仅ST股")
        self.check_box_security_st_use.setChecked(self.config.cfg_anal.filter_security_st_use)
        
        self.check_box_security_data_daily = QCheckBox()
        self.check_box_security_data_daily.setText("1_D")
        self.check_box_security_data_daily.setChecked(self.config.cfg_anal.filter_security_data_daily)
        
        self.check_box_security_data_kline_1_m = QCheckBox()
        self.check_box_security_data_kline_1_m.setText("1_M")
        self.check_box_security_data_kline_1_m.setChecked(self.config.cfg_anal.filter_security_data_kline_1_m)
        
        self.button_get_symbol_list = QPushButton("更新证券列表")
        self.button_get_symbol_list.setFont(QFont("SimSun", 9))
        self.button_get_symbol_list.setMaximumSize(90, 25)
        
        self.button_save_panel_config = QPushButton("保存参数设置")
        self.button_save_panel_config.setFont(QFont("SimSun", 9))
        self.button_save_panel_config.setMaximumSize(90, 25)
        
        self.check_box_security_check_all.clicked.connect(self.HandleSecurityCheckAll)
        self.button_get_symbol_list.clicked.connect(self.OnClickButtonGetSymbolList)
        self.button_save_panel_config.clicked.connect(self.OnClickButtonSavePanelConfig)
        
        self.label_stock_commission = QLabel("个股佣金费率:")
        self.label_stock_commission.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_stock_commission_bid = QLabel("买")
        self.label_stock_commission_bid.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_stock_commission_ask = QLabel("卖")
        self.label_stock_commission_ask.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.spin_stock_commission_bid = QDoubleSpinBox()
        self.spin_stock_commission_bid.setDecimals(4)
        self.spin_stock_commission_bid.setMinimum(0.0)
        self.spin_stock_commission_bid.setMaximum(1.0)
        self.spin_stock_commission_bid.setSingleStep(0.0001)
        self.spin_stock_commission_bid.setValue(self.config.cfg_anal.stock_commission_bid)
        self.spin_stock_commission_bid.setMinimumWidth(65)
        self.spin_stock_commission_bid.setMaximumWidth(65)
        self.spin_stock_commission_bid.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spin_stock_commission_bid.setToolTip("个股佣金费率-买入")
        self.spin_stock_commission_ask = QDoubleSpinBox()
        self.spin_stock_commission_ask.setDecimals(4)
        self.spin_stock_commission_ask.setMinimum(0.0)
        self.spin_stock_commission_ask.setMaximum(1.0)
        self.spin_stock_commission_ask.setSingleStep(0.0001)
        self.spin_stock_commission_ask.setValue(self.config.cfg_anal.stock_commission_ask)
        self.spin_stock_commission_ask.setMinimumWidth(65)
        self.spin_stock_commission_ask.setMaximumWidth(65)
        self.spin_stock_commission_ask.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spin_stock_commission_ask.setToolTip("个股佣金费率-卖出")
        
        self.label_stock_stamp_tax = QLabel("个股印花税率:")
        self.label_stock_stamp_tax.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_stock_stamp_tax_bid = QLabel("买")
        self.label_stock_stamp_tax_bid.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_stock_stamp_tax_ask = QLabel("卖")
        self.label_stock_stamp_tax_ask.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.spin_stock_stamp_tax_bid = QDoubleSpinBox()
        self.spin_stock_stamp_tax_bid.setDecimals(4)
        self.spin_stock_stamp_tax_bid.setMinimum(0.0)
        self.spin_stock_stamp_tax_bid.setMaximum(1.0)
        self.spin_stock_stamp_tax_bid.setSingleStep(0.0001)
        self.spin_stock_stamp_tax_bid.setValue(self.config.cfg_anal.stock_stamp_tax_bid)
        self.spin_stock_stamp_tax_bid.setMinimumWidth(65)
        self.spin_stock_stamp_tax_bid.setMaximumWidth(65)
        self.spin_stock_stamp_tax_bid.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spin_stock_stamp_tax_bid.setToolTip("个股印花税率-买入")
        self.spin_stock_stamp_tax_ask = QDoubleSpinBox()
        self.spin_stock_stamp_tax_ask.setDecimals(4)
        self.spin_stock_stamp_tax_ask.setMinimum(0.0)
        self.spin_stock_stamp_tax_ask.setMaximum(1.0)
        self.spin_stock_stamp_tax_ask.setSingleStep(0.0001)
        self.spin_stock_stamp_tax_ask.setValue(self.config.cfg_anal.stock_stamp_tax_ask)
        self.spin_stock_stamp_tax_ask.setMinimumWidth(65)
        self.spin_stock_stamp_tax_ask.setMaximumWidth(65)
        self.spin_stock_stamp_tax_ask.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spin_stock_stamp_tax_ask.setToolTip("个股印花税率-卖出")
        
        self.label_stock_transfer_fee = QLabel("个股过户费率:")
        self.label_stock_transfer_fee.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_stock_transfer_fee_bid = QLabel("买")
        self.label_stock_transfer_fee_bid.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_stock_transfer_fee_ask = QLabel("卖")
        self.label_stock_transfer_fee_ask.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.spin_stock_transfer_fee_bid = QDoubleSpinBox()
        self.spin_stock_transfer_fee_bid.setDecimals(4)
        self.spin_stock_transfer_fee_bid.setMinimum(0.0)
        self.spin_stock_transfer_fee_bid.setMaximum(1.0)
        self.spin_stock_transfer_fee_bid.setSingleStep(0.0001)
        self.spin_stock_transfer_fee_bid.setValue(self.config.cfg_anal.stock_transfer_fee_bid)
        self.spin_stock_transfer_fee_bid.setMinimumWidth(65)
        self.spin_stock_transfer_fee_bid.setMaximumWidth(65)
        self.spin_stock_transfer_fee_bid.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spin_stock_transfer_fee_bid.setToolTip("个股过户费率-买入")
        self.spin_stock_transfer_fee_ask = QDoubleSpinBox()
        self.spin_stock_transfer_fee_ask.setDecimals(4)
        self.spin_stock_transfer_fee_ask.setMinimum(0.0)
        self.spin_stock_transfer_fee_ask.setMaximum(1.0)
        self.spin_stock_transfer_fee_ask.setSingleStep(0.0001)
        self.spin_stock_transfer_fee_ask.setValue(self.config.cfg_anal.stock_transfer_fee_ask)
        self.spin_stock_transfer_fee_ask.setMinimumWidth(65)
        self.spin_stock_transfer_fee_ask.setMaximumWidth(65)
        self.spin_stock_transfer_fee_ask.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spin_stock_transfer_fee_ask.setToolTip("个股过户费率-卖出")
        
        self.h_box_stock_commission = QHBoxLayout()
        self.h_box_stock_commission.setContentsMargins(0, 0, 0, 0)
        self.h_box_stock_commission.addWidget(self.label_stock_commission)
        self.h_box_stock_commission.addWidget(self.label_stock_commission_bid)
        self.h_box_stock_commission.addWidget(self.spin_stock_commission_bid)
        self.h_box_stock_commission.addWidget(self.label_stock_commission_ask)
        self.h_box_stock_commission.addWidget(self.spin_stock_commission_ask)
        self.h_box_stock_commission.addStretch(1)
        
        self.h_box_stock_stamp_tax = QHBoxLayout()
        self.h_box_stock_stamp_tax.setContentsMargins(0, 0, 0, 0)
        self.h_box_stock_stamp_tax.addWidget(self.label_stock_stamp_tax)
        self.h_box_stock_stamp_tax.addWidget(self.label_stock_stamp_tax_bid)
        self.h_box_stock_stamp_tax.addWidget(self.spin_stock_stamp_tax_bid)
        self.h_box_stock_stamp_tax.addWidget(self.label_stock_stamp_tax_ask)
        self.h_box_stock_stamp_tax.addWidget(self.spin_stock_stamp_tax_ask)
        self.h_box_stock_stamp_tax.addStretch(1)
        
        self.h_box_stock_transfer_fee = QHBoxLayout()
        self.h_box_stock_transfer_fee.setContentsMargins(0, 0, 0, 0)
        self.h_box_stock_transfer_fee.addWidget(self.label_stock_transfer_fee)
        self.h_box_stock_transfer_fee.addWidget(self.label_stock_transfer_fee_bid)
        self.h_box_stock_transfer_fee.addWidget(self.spin_stock_transfer_fee_bid)
        self.h_box_stock_transfer_fee.addWidget(self.label_stock_transfer_fee_ask)
        self.h_box_stock_transfer_fee.addWidget(self.spin_stock_transfer_fee_ask)
        self.h_box_stock_transfer_fee.addStretch(1)
        
        self.h_box_fees_1 = QHBoxLayout()
        self.h_box_fees_1.setContentsMargins(0, 0, 0, 0)
        self.h_box_fees_1.addLayout(self.h_box_stock_commission)
        self.h_box_fees_1.addStretch(1)
        
        self.h_box_fees_2 = QHBoxLayout()
        self.h_box_fees_2.setContentsMargins(0, 0, 0, 0)
        self.h_box_fees_2.addLayout(self.h_box_stock_stamp_tax)
        self.h_box_fees_2.addStretch(1)
        
        self.h_box_fees_3 = QHBoxLayout()
        self.h_box_fees_3.setContentsMargins(0, 0, 0, 0)
        self.h_box_fees_3.addLayout(self.h_box_stock_transfer_fee)
        self.h_box_fees_3.addStretch(1)
        
        self.v_box_fees_setting = QVBoxLayout()
        self.v_box_fees_setting.setContentsMargins(0, 0, 0, 0)
        self.v_box_fees_setting.addLayout(self.h_box_fees_1)
        self.v_box_fees_setting.addLayout(self.h_box_fees_2)
        self.v_box_fees_setting.addLayout(self.h_box_fees_3)
        self.v_box_fees_setting.addStretch(1)
        
        self.group_box_fees_setting = QGroupBox()
        self.group_box_fees_setting.setMinimumWidth(520)
        self.group_box_fees_setting.setLayout(self.v_box_fees_setting)
        
        self.label_name = QLabel()
        self.label_name.setText("名称:")
        self.edits_name = QLineEdit(self)
        self.edits_name.setMinimumWidth(200)
        self.edits_name.setReadOnly(True)
        self.label_type = QLabel()
        self.label_type.setText("类型:")
        self.edits_type = QLineEdit(self)
        self.edits_type.setMinimumWidth(200)
        self.edits_type.setReadOnly(True)
        self.label_path = QLabel()
        self.label_path.setText("路径:")
        self.edits_path = QLineEdit(self)
        self.edits_path.setMinimumWidth(200)
        self.edits_path.setReadOnly(True)
        self.edits_info = QTextEdit(self)
        self.edits_info.setMaximumHeight(50)
        self.edits_info.setReadOnly(True)
        
        self.label_ignore = QLabel("提示忽略:")
        
        self.check_box_ignore_user_tips = QCheckBox()
        self.check_box_ignore_user_tips.setText("效率优化")
        self.check_box_ignore_user_tips.setChecked(self.config.cfg_anal.ignore_user_tips)
        
        self.check_box_ignore_local_file_loss = QCheckBox()
        self.check_box_ignore_local_file_loss.setText("文件缺失")
        self.check_box_ignore_local_file_loss.setChecked(self.config.cfg_anal.ignore_local_file_loss)
        
        self.check_box_ignore_exrights_data_loss = QCheckBox()
        self.check_box_ignore_exrights_data_loss.setText("除权缺失")
        self.check_box_ignore_exrights_data_loss.setChecked(self.config.cfg_anal.ignore_ex_rights_data_loss)
        
        self.check_box_ignore_local_data_imperfect = QCheckBox()
        self.check_box_ignore_local_data_imperfect.setText("数据瑕疵")
        self.check_box_ignore_local_data_imperfect.setChecked(self.config.cfg_anal.ignore_local_data_imperfect)
        
        self.label_analysis_date = QLabel("回测周期:")
        self.combo_box_analysis_date_s = QComboBox()
        self.combo_box_analysis_date_s.setMinimumWidth(83)
        self.label_analysis_date_count = QLabel("0")
        self.label_analysis_date_count.setMinimumWidth(25)
        self.label_analysis_date_count.setAlignment(Qt.AlignCenter)
        self.combo_box_analysis_date_e = QComboBox()
        self.combo_box_analysis_date_e.setMinimumWidth(83)
        self.radio_button_analysis_date_daily = QRadioButton("1_D")
        self.radio_button_analysis_date_kline_1_m = QRadioButton("1_M")
        self.radio_button_analysis_date_daily.setChecked(True)
        
        self.combo_box_analysis_date_s.activated[str].connect(self.OnComboBoxAnalysisDate)
        self.combo_box_analysis_date_e.activated[str].connect(self.OnComboBoxAnalysisDate)
        
        self.progress_bar_analysis = QProgressBar()
        self.progress_bar_analysis.setAlignment(Qt.AlignCenter) # 百分比居中显示
        self.progress_bar_analysis.setStyleSheet("QProgressBar{color:black;}""QProgressBar::chunk{background-color:gray;}");
        self.progress_bar_analysis.setMinimum(0)
        self.progress_bar_analysis.setMaximum(100)
        self.progress_bar_analysis.setValue(0)
        #self.progress_bar_analysis.setStyleSheet("QProgressBar{border:1px solid grey; border-radius:5px; text-align:center;}"
        #                               "QProgressBar::chunk{background-color:#CD96CD; width:10px; margin:0.5px;}");
        
        self.button_reload = QPushButton("加 载")
        self.button_reload.setFont(QFont("SimSun", 9))
        self.button_reload.setMaximumSize(50, 25)
        self.button_run = QPushButton("运 行")
        self.button_run.setFont(QFont("SimSun", 9))
        self.button_run.setMaximumSize(50, 25)
        self.button_suspend = QPushButton("暂 停")
        self.button_suspend.setFont(QFont("SimSun", 9))
        self.button_suspend.setMaximumSize(50, 25)
        self.button_continue = QPushButton("继 续")
        self.button_continue.setFont(QFont("SimSun", 9))
        self.button_continue.setMaximumSize(50, 25)
        self.button_stop = QPushButton("停 止")
        self.button_stop.setFont(QFont("SimSun", 9))
        self.button_stop.setMaximumSize(50, 25)
        self.button_unload = QPushButton("卸 载")
        self.button_unload.setFont(QFont("SimSun", 9))
        self.button_unload.setMaximumSize(50, 25)
        
        self.button_reload.clicked.connect(self.OnClickButtonAnalysisReload)
        self.button_run.clicked.connect(self.OnClickButtonAnalysisRun)
        self.button_suspend.clicked.connect(self.OnClickButtonAnalysisSuspend)
        self.button_continue.clicked.connect(self.OnClickButtonAnalysisContinue)
        self.button_stop.clicked.connect(self.OnClickButtonAnalysisStop)
        self.button_unload.clicked.connect(self.OnClickButtonAnalysisUnload)
        
        self.button_get_trading_day = QPushButton("交易日期")
        self.button_get_trading_day.setFont(QFont("SimSun", 9))
        self.button_get_trading_day.setMaximumSize(64, 25)
        
        self.button_get_security_info = QPushButton("证券信息")
        self.button_get_security_info.setFont(QFont("SimSun", 9))
        self.button_get_security_info.setMaximumSize(64, 25)
        
        self.button_get_capital_data = QPushButton("股本结构")
        self.button_get_capital_data.setFont(QFont("SimSun", 9))
        self.button_get_capital_data.setMaximumSize(64, 25)
        
        self.button_get_exrights_data = QPushButton("除权数据")
        self.button_get_exrights_data.setFont(QFont("SimSun", 9))
        self.button_get_exrights_data.setMaximumSize(64, 25)
        
        self.dt_edit_get_quote_data_s = QDateTimeEdit()
        self.dt_edit_get_quote_data_s.setCalendarPopup(True)
        self.dt_edit_get_quote_data_s.setDisplayFormat("yyyy-MM-dd")
        self.dt_edit_get_quote_data_s.setDateTime(QDateTime.fromString(self.config.cfg_anal.date_get_quote_data_s, "yyyyMMdd"))
        
        self.dt_edit_get_quote_data_e = QDateTimeEdit()
        self.dt_edit_get_quote_data_e.setCalendarPopup(True)
        self.dt_edit_get_quote_data_e.setDisplayFormat("yyyy-MM-dd")
        self.dt_edit_get_quote_data_e.setDateTime(QDateTime.fromString(self.config.cfg_anal.date_get_quote_data_e, "yyyyMMdd"))
        
        self.button_get_stock_daily = QPushButton("1_D 数据")
        self.button_get_stock_daily.setFont(QFont("SimSun", 9))
        self.button_get_stock_daily.setMaximumSize(64, 25)
        
        self.button_get_stock_kline_1_m = QPushButton("1_M 数据")
        self.button_get_stock_kline_1_m.setFont(QFont("SimSun", 9))
        self.button_get_stock_kline_1_m.setMaximumSize(64, 25)
        
        self.progress_bar_get_quote_data = QProgressBar()
        self.progress_bar_get_quote_data.setAlignment(Qt.AlignCenter) # 百分比居中显示
        self.progress_bar_get_quote_data.setStyleSheet("QProgressBar{color:black;}""QProgressBar::chunk{background-color:gray;}");
        self.progress_bar_get_quote_data.setMinimum(0)
        self.progress_bar_get_quote_data.setMaximum(100)
        self.progress_bar_get_quote_data.setValue(0)
        self.progress_bar_get_quote_data.setMaximumSize(95, 21)
        
        self.button_get_data_suspend = QPushButton("暂 停")
        self.button_get_data_suspend.setFont(QFont("SimSun", 9))
        self.button_get_data_suspend.setMaximumSize(50, 25)
        
        self.button_get_data_stop = QPushButton("停 止")
        self.button_get_data_stop.setFont(QFont("SimSun", 9))
        self.button_get_data_stop.setMaximumSize(50, 25)
        
        self.button_get_trading_day.clicked.connect(self.OnClickButtonGetTradingDay)
        self.button_get_security_info.clicked.connect(self.OnClickButtonGetSecurityInfo)
        self.button_get_capital_data.clicked.connect(self.OnClickButtonGetCapitalData)
        self.button_get_exrights_data.clicked.connect(self.OnClickButtonGetExRightsData)
        self.button_get_stock_daily.clicked.connect(self.OnClickButtonGetStockDaily)
        self.button_get_stock_kline_1_m.clicked.connect(self.OnClickButtonGetStockKline_1_M)
        self.button_get_data_suspend.clicked.connect(self.OnClickButtonGetDataSuspend)
        self.button_get_data_stop.clicked.connect(self.OnClickButtonGetDataStop)
        
        self.label_daily_report_file = QLabel()
        self.label_daily_report_file.setText(" 历史净值:")
        
        self.line_edit_daily_report_file = QLineEdit(self)
        self.line_edit_daily_report_file.setMinimumWidth(320)
        self.line_edit_daily_report_file.setReadOnly(True)
        
        self.button_daily_report_load = QPushButton("导入文件")
        self.button_daily_report_load.setFont(QFont("SimSun", 9))
        self.button_daily_report_load.setMaximumSize(64, 25)
        self.button_daily_report_load.setEnabled(True)
        
        self.line_edit_daily_report_evaluate_account = QLineEdit(self)
        self.line_edit_daily_report_evaluate_account.setMinimumWidth(60)
        self.line_edit_daily_report_evaluate_account.setReadOnly(False)
        self.line_edit_daily_report_evaluate_account.setToolTip("模型评估净值账号")
        self.line_edit_daily_report_evaluate_account.setText(self.config.cfg_anal.account_daily_report)
        
        self.dt_edit_daily_report_evaluate_s = QDateTimeEdit()
        self.dt_edit_daily_report_evaluate_s.setCalendarPopup(True)
        self.dt_edit_daily_report_evaluate_s.setDisplayFormat("yyyy-MM-dd")
        self.dt_edit_daily_report_evaluate_s.setDateTime(QDateTime.fromString(self.config.cfg_anal.date_daily_report_s, "yyyyMMdd"))
        self.dt_edit_daily_report_evaluate_s.setToolTip("模型评估起始日期")
        
        self.dt_edit_daily_report_evaluate_e = QDateTimeEdit()
        self.dt_edit_daily_report_evaluate_e.setCalendarPopup(True)
        self.dt_edit_daily_report_evaluate_e.setDisplayFormat("yyyy-MM-dd")
        self.dt_edit_daily_report_evaluate_e.setDateTime(QDateTime.fromString(self.config.cfg_anal.date_daily_report_e, "yyyyMMdd"))
        self.dt_edit_daily_report_evaluate_e.setToolTip("模型评估终止日期")
        
        self.button_daily_report_evaluate = QPushButton("模型评估")
        self.button_daily_report_evaluate.setFont(QFont("SimSun", 9))
        self.button_daily_report_evaluate.setMaximumSize(64, 25)
        self.button_daily_report_evaluate.setEnabled(False)
        
        self.button_daily_report_load.clicked.connect(self.OnClickButtonDailyReportLoad)
        self.button_daily_report_evaluate.clicked.connect(self.OnClickButtonDailyReportEvaluate)
        
        self.edits_right_1 = QTextEdit(self)
        self.edits_right_1.setMinimumWidth(788)
        
        self.edits_right_2 = QTextEdit(self)
        self.edits_right_2.setMinimumWidth(788)
        
        self.edits_right_3 = QTextEdit(self)
        self.edits_right_3.setMinimumWidth(788)
        
        self.h_box_data_list = QHBoxLayout()
        self.h_box_data_list.setContentsMargins(0, 0, 0, 0)
        self.h_box_data_list.addWidget(self.data_lister)
        
        self.h_box_security_setting_1 = QHBoxLayout()
        self.h_box_security_setting_1.setContentsMargins(0, 0, 0, 0)
        self.h_box_security_setting_1.addWidget(self.check_box_security_check_all)
        self.h_box_security_setting_1.addWidget(QLabel("| "))
        self.h_box_security_setting_1.addWidget(self.check_box_security_category_1)
        self.h_box_security_setting_1.addWidget(self.check_box_security_category_2)
        self.h_box_security_setting_1.addWidget(self.check_box_security_category_3)
        self.h_box_security_setting_1.addWidget(self.check_box_security_category_4)
        self.h_box_security_setting_1.addWidget(self.check_box_security_category_5)
        self.h_box_security_setting_1.addWidget(self.check_box_security_category_6)
        self.h_box_security_setting_1.addStretch(1)
        
        self.h_box_security_setting_2 = QHBoxLayout()
        self.h_box_security_setting_2.setContentsMargins(0, 0, 0, 0)
        self.h_box_security_setting_2.addWidget(self.check_box_security_category_0)
        self.h_box_security_setting_2.addWidget(QLabel("| "))
        self.h_box_security_setting_2.addWidget(self.check_box_security_category_7)
        self.h_box_security_setting_2.addWidget(self.check_box_security_category_8)
        self.h_box_security_setting_2.addWidget(self.check_box_security_category_9)
        self.h_box_security_setting_2.addWidget(self.check_box_security_category_10)
        self.h_box_security_setting_2.addWidget(self.check_box_security_category_11)
        self.h_box_security_setting_2.addWidget(self.check_box_security_category_12)
        self.h_box_security_setting_2.addStretch(1)
        
        self.h_box_security_setting_3 = QHBoxLayout()
        self.h_box_security_setting_3.setContentsMargins(0, 0, 0, 0)
        self.h_box_security_setting_3.addWidget(self.check_box_security_list_state_1)
        self.h_box_security_setting_3.addWidget(self.check_box_security_list_state_2)
        self.h_box_security_setting_3.addWidget(self.check_box_security_list_state_3)
        self.h_box_security_setting_3.addWidget(self.check_box_security_list_state_4)
        self.h_box_security_setting_3.addWidget(self.check_box_security_list_state_5)
        self.h_box_security_setting_3.addWidget(self.check_box_security_list_state_6)
        self.h_box_security_setting_3.addWidget(self.check_box_security_list_state_7)
        self.h_box_security_setting_3.addWidget(QLabel("| "))
        self.h_box_security_setting_3.addWidget(self.check_box_security_st_non)
        self.h_box_security_setting_3.addWidget(self.check_box_security_st_use)
        self.h_box_security_setting_3.addWidget(QLabel("| "))
        self.h_box_security_setting_3.addWidget(self.check_box_security_data_daily)
        self.h_box_security_setting_3.addWidget(self.check_box_security_data_kline_1_m)
        self.h_box_security_setting_3.addWidget(QLabel("| "))
        self.h_box_security_setting_3.addWidget(self.button_get_symbol_list)
        self.h_box_security_setting_3.addWidget(self.button_save_panel_config)
        self.h_box_security_setting_3.addStretch(1)
        
        self.h_box_analysis_name = QHBoxLayout()
        self.h_box_analysis_name.setContentsMargins(0, 0, 0, 0)
        self.h_box_analysis_name.addWidget(self.label_name)
        self.h_box_analysis_name.addWidget(self.edits_name)
        
        self.h_box_analysis_type = QHBoxLayout()
        self.h_box_analysis_type.setContentsMargins(0, 0, 0, 0)
        self.h_box_analysis_type.addWidget(self.label_type)
        self.h_box_analysis_type.addWidget(self.edits_type)
        
        self.h_box_analysis_path = QHBoxLayout()
        self.h_box_analysis_path.setContentsMargins(0, 0, 0, 0)
        self.h_box_analysis_path.addWidget(self.label_path)
        self.h_box_analysis_path.addWidget(self.edits_path)
        
        self.h_box_ignore_infos = QHBoxLayout()
        self.h_box_ignore_infos.setContentsMargins(0, 0, 0, 0)
        self.h_box_ignore_infos.addWidget(self.label_ignore)
        self.h_box_ignore_infos.addWidget(self.check_box_ignore_user_tips)
        self.h_box_ignore_infos.addWidget(self.check_box_ignore_local_file_loss)
        self.h_box_ignore_infos.addWidget(self.check_box_ignore_exrights_data_loss)
        self.h_box_ignore_infos.addWidget(self.check_box_ignore_local_data_imperfect)
        self.h_box_ignore_infos.addStretch(1)
        
        self.h_box_analysis_date = QHBoxLayout()
        self.h_box_analysis_date.setContentsMargins(0, 0, 0, 0)
        self.h_box_analysis_date.addWidget(self.label_analysis_date)
        self.h_box_analysis_date.addWidget(self.combo_box_analysis_date_s)
        self.h_box_analysis_date.addWidget(self.label_analysis_date_count)
        self.h_box_analysis_date.addWidget(self.combo_box_analysis_date_e)
        self.h_box_analysis_date.addWidget(self.radio_button_analysis_date_daily)
        self.h_box_analysis_date.addWidget(self.radio_button_analysis_date_kline_1_m)
        self.h_box_analysis_date.addStretch(1)
        
        self.v_box_analysis_info = QVBoxLayout()
        self.v_box_analysis_info.setContentsMargins(0, 0, 0, 0)
        self.v_box_analysis_info.addLayout(self.h_box_analysis_name)
        self.v_box_analysis_info.addLayout(self.h_box_analysis_type)
        self.v_box_analysis_info.addLayout(self.h_box_analysis_path)
        self.v_box_analysis_info.addWidget(self.edits_info)
        self.v_box_analysis_info.addLayout(self.h_box_ignore_infos)
        self.v_box_analysis_info.addLayout(self.h_box_analysis_date)
        self.v_box_analysis_info.addWidget(self.progress_bar_analysis)
        
        self.h_box_analysis_ctrl = QHBoxLayout()
        self.h_box_analysis_ctrl.setContentsMargins(0, 0, 0, 0)
        self.h_box_analysis_ctrl.addWidget(self.button_reload)
        self.h_box_analysis_ctrl.addStretch(1)
        self.h_box_analysis_ctrl.addWidget(self.button_run)
        self.h_box_analysis_ctrl.addStretch(1)
        self.h_box_analysis_ctrl.addWidget(self.button_suspend)
        self.h_box_analysis_ctrl.addStretch(1)
        self.h_box_analysis_ctrl.addWidget(self.button_continue)
        self.h_box_analysis_ctrl.addStretch(1)
        self.h_box_analysis_ctrl.addWidget(self.button_stop)
        self.h_box_analysis_ctrl.addStretch(1)
        self.h_box_analysis_ctrl.addWidget(self.button_unload)
        
        self.v_box_analysis = QVBoxLayout()
        self.v_box_analysis.setContentsMargins(0, 0, 0, 0)
        self.v_box_analysis.addLayout(self.v_box_analysis_info)
        self.v_box_analysis.addLayout(self.h_box_analysis_ctrl)
        
        self.h_box_operate = QHBoxLayout()
        self.h_box_operate.setContentsMargins(0, 0, 0, 0)
        self.h_box_operate.addWidget(self.group_box_fees_setting)
        self.h_box_operate.addLayout(self.v_box_analysis)
        
        self.h_box_get_data = QHBoxLayout()
        self.h_box_get_data.setContentsMargins(0, 0, 0, 0)
        self.h_box_get_data.addWidget(self.button_get_trading_day)
        self.h_box_get_data.addWidget(self.button_get_security_info)
        self.h_box_get_data.addWidget(self.button_get_capital_data)
        self.h_box_get_data.addWidget(self.button_get_exrights_data)
        self.h_box_get_data.addWidget(self.dt_edit_get_quote_data_s)
        self.h_box_get_data.addWidget(self.dt_edit_get_quote_data_e)
        self.h_box_get_data.addWidget(self.button_get_stock_daily)
        self.h_box_get_data.addWidget(self.button_get_stock_kline_1_m)
        self.h_box_get_data.addWidget(self.progress_bar_get_quote_data)
        self.h_box_get_data.addWidget(self.button_get_data_suspend)
        self.h_box_get_data.addWidget(self.button_get_data_stop)
        self.h_box_get_data.addStretch(1)
        
        self.h_box_daily_report_evaluate = QHBoxLayout()
        self.h_box_daily_report_evaluate.setContentsMargins(0, 0, 0, 0)
        self.h_box_daily_report_evaluate.addWidget(self.label_daily_report_file)
        self.h_box_daily_report_evaluate.addWidget(self.line_edit_daily_report_file)
        self.h_box_daily_report_evaluate.addWidget(self.button_daily_report_load)
        self.h_box_daily_report_evaluate.addWidget(self.line_edit_daily_report_evaluate_account)
        self.h_box_daily_report_evaluate.addWidget(self.dt_edit_daily_report_evaluate_s)
        self.h_box_daily_report_evaluate.addWidget(self.dt_edit_daily_report_evaluate_e)
        self.h_box_daily_report_evaluate.addWidget(self.button_daily_report_evaluate)
        
        self.v_box_left = QVBoxLayout()
        self.v_box_left.setContentsMargins(0, 0, 0, 0)
        self.v_box_left.addLayout(self.h_box_data_list)
        self.v_box_left.addLayout(self.h_box_security_setting_1)
        self.v_box_left.addLayout(self.h_box_security_setting_2)
        self.v_box_left.addLayout(self.h_box_security_setting_3)
        self.v_box_left.addLayout(self.h_box_get_data)
        self.v_box_left.addLayout(self.h_box_operate)
        self.v_box_left.addLayout(self.h_box_daily_report_evaluate)
        self.v_box_left.addStretch(1)
        
        self.v_box_right = QVBoxLayout()
        self.v_box_right.setContentsMargins(0, 0, 0, 0)
        self.v_box_right.addWidget(self.edits_right_1)
        self.v_box_right.addWidget(self.edits_right_2)
        self.v_box_right.addWidget(self.edits_right_3)
        self.v_box_right.addStretch(1)
        
        self.h_box = QHBoxLayout()
        self.h_box.setContentsMargins(0, 0, 0, 0)
        self.h_box.addLayout(self.v_box_left)
        self.h_box.addLayout(self.v_box_right)
        
        self.v_box = QVBoxLayout()
        self.v_box.setContentsMargins(0, 0, 0, 0)
        self.v_box.addLayout(self.h_box)
        self.v_box.addStretch(1)
        
        self.setLayout(self.v_box)
        
        self.HandleButtonState("卸载")

    def ShowContextMenu(self, index):
        if index != None: # 选中行
            print(self.data_lister.GetCellText(index.row(), self.data_lister.head_index_code))
        else: # 未选中
            pass

    def event(self, event):
        if event.type() == define.DEF_EVENT_SET_ANALYSIS_PROGRESS:
            self.OnSetAnalysisProgress()
        elif event.type() == define.DEF_EVENT_SET_ANALYSIS_PROGRESS_ERROR:
            self.OnSetAnalysisProgressError()
        elif event.type() == define.DEF_EVENT_SET_ANALYSIS_GET_QUOTE_DATA_PROGRESS:
            self.OnSetAnalysisGetQuoteDataProgress()
        elif event.type() == define.DEF_EVENT_SET_ANALYSIS_GET_QUOTE_DATA_PROGRESS_ERROR:
            self.OnSetAnalysisGetQuoteDataProgressError()
        return QDialog.event(self, event)

    def HandleSecurityCheckAll(self):
        self.data_lister.SetAllCheck(self.check_box_security_check_all.isChecked())

    def OnClickButtonGetSymbolList(self):
        self.data_lister.OnActionRefresh()
        self.check_box_security_check_all.setChecked(True) # 刷新后默认全选

    def OnClickButtonSavePanelConfig(self):
        self.config.cfg_anal.filter_security_check_all = self.check_box_security_check_all.isChecked()
        self.config.cfg_anal.filter_security_category_0 = self.check_box_security_category_0.isChecked()
        self.config.cfg_anal.filter_security_category_1 = self.check_box_security_category_1.isChecked()
        self.config.cfg_anal.filter_security_category_2 = self.check_box_security_category_2.isChecked()
        self.config.cfg_anal.filter_security_category_3 = self.check_box_security_category_3.isChecked()
        self.config.cfg_anal.filter_security_category_4 = self.check_box_security_category_4.isChecked()
        self.config.cfg_anal.filter_security_category_5 = self.check_box_security_category_5.isChecked()
        self.config.cfg_anal.filter_security_category_6 = self.check_box_security_category_6.isChecked()
        self.config.cfg_anal.filter_security_category_7 = self.check_box_security_category_7.isChecked()
        self.config.cfg_anal.filter_security_category_8 = self.check_box_security_category_8.isChecked()
        self.config.cfg_anal.filter_security_category_9 = self.check_box_security_category_9.isChecked()
        self.config.cfg_anal.filter_security_category_10 = self.check_box_security_category_10.isChecked()
        self.config.cfg_anal.filter_security_category_11 = self.check_box_security_category_11.isChecked()
        self.config.cfg_anal.filter_security_category_12 = self.check_box_security_category_12.isChecked()
        self.config.cfg_anal.filter_security_list_state_1 = self.check_box_security_list_state_1.isChecked()
        self.config.cfg_anal.filter_security_list_state_2 = self.check_box_security_list_state_2.isChecked()
        self.config.cfg_anal.filter_security_list_state_3 = self.check_box_security_list_state_3.isChecked()
        self.config.cfg_anal.filter_security_list_state_4 = self.check_box_security_list_state_4.isChecked()
        self.config.cfg_anal.filter_security_list_state_5 = self.check_box_security_list_state_5.isChecked()
        self.config.cfg_anal.filter_security_list_state_6 = self.check_box_security_list_state_6.isChecked()
        self.config.cfg_anal.filter_security_list_state_7 = self.check_box_security_list_state_7.isChecked()
        self.config.cfg_anal.filter_security_st_non = self.check_box_security_st_non.isChecked()
        self.config.cfg_anal.filter_security_st_use = self.check_box_security_st_use.isChecked()
        self.config.cfg_anal.filter_security_data_daily = self.check_box_security_data_daily.isChecked()
        self.config.cfg_anal.filter_security_data_kline_1_m = self.check_box_security_data_kline_1_m.isChecked()
        self.config.cfg_anal.date_get_quote_data_s = self.dt_edit_get_quote_data_s.dateTime().toString("yyyyMMdd")
        self.config.cfg_anal.date_get_quote_data_e = self.dt_edit_get_quote_data_e.dateTime().toString("yyyyMMdd")
        self.config.cfg_anal.ignore_user_tips = self.check_box_ignore_user_tips.isChecked()
        self.config.cfg_anal.ignore_local_file_loss = self.check_box_ignore_local_file_loss.isChecked()
        self.config.cfg_anal.ignore_ex_rights_data_loss = self.check_box_ignore_exrights_data_loss.isChecked()
        self.config.cfg_anal.ignore_local_data_imperfect = self.check_box_ignore_local_data_imperfect.isChecked()
        str_trading_day_s = str(self.combo_box_analysis_date_s.currentText())
        str_trading_day_e = str(self.combo_box_analysis_date_e.currentText())
        self.config.cfg_anal.stock_commission_bid = self.spin_stock_commission_bid.value()
        self.config.cfg_anal.stock_commission_ask = self.spin_stock_commission_ask.value()
        self.config.cfg_anal.stock_stamp_tax_bid = self.spin_stock_stamp_tax_bid.value()
        self.config.cfg_anal.stock_stamp_tax_ask = self.spin_stock_stamp_tax_ask.value()
        self.config.cfg_anal.stock_transfer_fee_bid = self.spin_stock_transfer_fee_bid.value()
        self.config.cfg_anal.stock_transfer_fee_ask = self.spin_stock_transfer_fee_ask.value()
        if str_trading_day_s != "" and str_trading_day_e != "":
            self.config.cfg_anal.date_analysis_test_s = str_trading_day_s.replace("-", "")
            self.config.cfg_anal.date_analysis_test_e = str_trading_day_e.replace("-", "")
        #self.config.cfg_anal.save_folder
        #self.config.cfg_anal.benchmark_rate
        #self.config.cfg_anal.trading_days_year
        self.config.cfg_anal.date_daily_report_s = self.dt_edit_daily_report_evaluate_s.dateTime().toString("yyyyMMdd")
        self.config.cfg_anal.date_daily_report_e = self.dt_edit_daily_report_evaluate_e.dateTime().toString("yyyyMMdd")
        self.config.cfg_anal.account_daily_report = self.line_edit_daily_report_evaluate_account.text()
        try:
            self.config.SaveConfig_Anal(self.config.cfg_anal, define.CFG_FILE_PATH_ANAL)
        except Exception as e:
            self.log_text = "模型回测保存参数设置发生异常！%s" % e
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def OnComboBoxAnalysisDate(self, text):
        str_trading_day_s = str(self.combo_box_analysis_date_s.currentText())
        str_trading_day_e = str(self.combo_box_analysis_date_e.currentText())
        if str_trading_day_s != "" and str_trading_day_e != "":
            pos_trading_day_s = self.analysis_trading_day_dict[str_trading_day_s] # 肯定存在
            pos_trading_day_e = self.analysis_trading_day_dict[str_trading_day_e] # 肯定存在
            self.label_analysis_date_count.setText("%d" % (pos_trading_day_e - pos_trading_day_s))

    def OnClickButtonAnalysisReload(self):
        self.HandleAnalysisUserControl("加载")

    def OnClickButtonAnalysisRun(self):
        self.HandleAnalysisUserControl("运行")

    def OnClickButtonAnalysisSuspend(self):
        self.HandleAnalysisUserControl("暂停")

    def OnClickButtonAnalysisContinue(self):
        self.HandleAnalysisUserControl("继续")

    def OnClickButtonAnalysisStop(self):
        self.HandleAnalysisUserControl("停止")

    def OnClickButtonAnalysisUnload(self):
        self.HandleAnalysisUserControl("卸载")

    def HandleAnalysisUserControl(self, str_type):
        self.analys = analys.Analys()
        if str_type == "加载":
            self.analys.OnReloadAnalysis()
            if self.analys.analysis_info != None:
                self.analys.analysis_info.instance.analysis_panel = self # 必须
                self.LoadAnalysisDate() #
            self.HandleButtonState(str_type)
        else:
            analysis_info = self.analys.analysis_info
            if None == analysis_info:
                QMessageBox.information(self, "提示", "回测模型尚未加载，无法%s。" % str_type, QMessageBox.Ok)
                return
            else:
                dlg = None
                if str_type == "运行":
                    if analysis_info.state != define.USER_CTRL_LOAD and analysis_info.state != define.USER_CTRL_STOP:
                        dlg = QMessageBox.information(self, "提示", "%s：状态不是已加载或已停止，无需运行。" % analysis_info.analysis, QMessageBox.Ok)
                elif str_type == "暂停":
                    if analysis_info.state != define.USER_CTRL_EXEC:
                        dlg = QMessageBox.information(self, "提示", "%s：状态不是运行中，无需暂停。" % analysis_info.analysis, QMessageBox.Ok)
                elif str_type == "继续":
                    if analysis_info.state != define.USER_CTRL_WAIT:
                        dlg = QMessageBox.information(self, "提示", "%s：状态不是已暂停，无需继续。" % analysis_info.analysis, QMessageBox.Ok)
                elif str_type == "停止":
                    if analysis_info.state != define.USER_CTRL_EXEC and analysis_info.state != define.USER_CTRL_WAIT and analysis_info.state != define.USER_CTRL_FAIL:
                        dlg = QMessageBox.information(self, "提示", "%s：状态不是运行中或已暂停或已异常，无需停止。" % analysis_info.analysis, QMessageBox.Ok)
                elif str_type == "卸载":
                    if analysis_info.state != define.USER_CTRL_LOAD and analysis_info.state != define.USER_CTRL_STOP:
                        dlg = QMessageBox.information(self, "提示", "%s：请先停止策略运行，再进行卸载。" % analysis_info.analysis, QMessageBox.Ok)
                if dlg != None:
                    return
                reply = QMessageBox.question(self, "询问", "确定 %s 模型 %s ？" % (str_type, analysis_info.analysis), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    if str_type == "卸载":
                        self.analys.OnUnloadAnalysis(analysis_info)
                    else:
                        if str_type == "运行":
                            self.basicx.IgnoreUserTips(self.check_box_ignore_user_tips.isChecked())
                            self.basicx.IgnoreLocalFileLoss(self.check_box_ignore_local_file_loss.isChecked())
                            self.basicx.IgnoreExRightsDataLoss(self.check_box_ignore_exrights_data_loss.isChecked())
                            self.basicx.IgnoreLocalDataImperfect(self.check_box_ignore_local_data_imperfect.isChecked())
                            
                            symbol_list = []
                            checked_rows_list = self.data_lister.GetAllCheck()
                            for row in checked_rows_list:
                                symbol_list.append({"market":row[1], "code":row[2]})
                            self.analys.SetSymbolList(symbol_list) # 必须
                            
                            trading_day_list = []
                            str_trading_day_s = str(self.combo_box_analysis_date_s.currentText())
                            str_trading_day_e = str(self.combo_box_analysis_date_e.currentText())
                            if str_trading_day_s != "" and str_trading_day_e != "":
                                pos_trading_day_s = self.analysis_trading_day_dict[str_trading_day_s] # 肯定存在
                                pos_trading_day_e = self.analysis_trading_day_dict[str_trading_day_e] # 肯定存在
                                if pos_trading_day_s <= pos_trading_day_e:
                                    trading_day_list = self.analysis_trading_day_list[pos_trading_day_s : pos_trading_day_e + 1]
                            self.analys.SetTradingDayList(trading_day_list) # 必须
                            
                            trade_fees = analys.TradeFees(stock_commission_bid = self.spin_stock_commission_bid.value(), 
                                                          stock_commission_ask = self.spin_stock_commission_ask.value(), 
                                                          stock_stamp_tax_bid = self.spin_stock_stamp_tax_bid.value(), 
                                                          stock_stamp_tax_ask = self.spin_stock_stamp_tax_ask.value(), 
                                                          stock_transfer_fee_bid = self.spin_stock_transfer_fee_bid.value(), 
                                                          stock_transfer_fee_ask = self.spin_stock_transfer_fee_ask.value())
                            self.analys.SetTradeFees(trade_fees) # 必须
                        
                        self.analys.OnChangeAnalysisState(analysis_info, str_type)
                    self.HandleButtonState(str_type)

    def LoadAnalysisDate(self):
        count = 0
        self.analysis_trading_day_list = []
        self.analysis_trading_day_dict = {}
        result = self.basicx.GetTradingDay()
        if not result.empty:
            for index, row in result.iterrows():
                if 83 == row["market"] and 1 == row["trading_day"]:
                    natural_date = row["natural_date"]
                    if natural_date.year >= 2010 and natural_date <= date.today():
                        str_trading_date = natural_date.strftime("%Y-%m-%d")
                        self.combo_box_analysis_date_s.addItem(str_trading_date)
                        self.combo_box_analysis_date_e.addItem(str_trading_date)
                        self.analysis_trading_day_list.append(natural_date)
                        self.analysis_trading_day_dict[str_trading_date] = count
                        count += 1
            str_date_analysis_test_s = datetime.strptime(self.config.cfg_anal.date_analysis_test_s, "%Y%m%d").strftime("%Y-%m-%d")
            str_date_analysis_test_e = datetime.strptime(self.config.cfg_anal.date_analysis_test_e, "%Y%m%d").strftime("%Y-%m-%d")
            if str_date_analysis_test_s in self.analysis_trading_day_dict.keys():
                self.combo_box_analysis_date_s.setCurrentIndex(self.analysis_trading_day_dict[str_date_analysis_test_s])
            if str_date_analysis_test_e in self.analysis_trading_day_dict.keys():
                self.combo_box_analysis_date_e.setCurrentIndex(self.analysis_trading_day_dict[str_date_analysis_test_e])
            self.OnComboBoxAnalysisDate("") # 计算一下间隔交易日数

    def OnSetAnalysisProgress(self):
        self.progress_bar_analysis.setValue(self.analysis_progress)

    def OnSetAnalysisProgressError(self):
        self.progress_bar_analysis.setStyleSheet("QProgressBar{color:green;}""QProgressBar::chunk{background-color:red;}");

    def OnSetAnalysisGetQuoteDataProgress(self):
        self.progress_bar_get_quote_data.setValue(self.get_quote_data_progress)

    def OnSetAnalysisGetQuoteDataProgressError(self):
        self.progress_bar_get_quote_data.setStyleSheet("QProgressBar{color:green;}""QProgressBar::chunk{background-color:red;}");

    def OnClickButtonGetTradingDay(self):
        result = self.basicx.GetTradingDay()
        if not result.empty:
            self.logger.SendMessage("H", 2, self.log_cate, "交易日期 下载完成。", "S")
        else:
            self.logger.SendMessage("w", 3, self.log_cate, "交易日期 下载为空！", "S")

    def OnClickButtonGetSecurityInfo(self):
        result = self.basicx.GetSecurityInfo()
        if not result.empty:
            self.logger.SendMessage("H", 2, self.log_cate, "证券信息 下载完成。", "S")
        else:
            self.logger.SendMessage("w", 3, self.log_cate, "证券信息 下载为空！", "S")

    def OnClickButtonGetCapitalData(self):
        result = self.basicx.GetCapitalData()
        if not result.empty:
            self.logger.SendMessage("H", 2, self.log_cate, "股本结构 下载完成。", "S")
        else:
            self.logger.SendMessage("W", 3, self.log_cate, "股本结构 下载为空！", "S")

    def OnClickButtonGetExRightsData(self):
        result = self.basicx.GetExRightsData()
        if not result.empty:
            self.logger.SendMessage("H", 2, self.log_cate, "除权数据 下载完成。", "S")
        else:
            self.logger.SendMessage("W", 3, self.log_cate, "除权数据 下载为空！", "S")

    def OnClickButtonGetStockDaily(self):
        self.get_quote_data_progress = 0
        self.progress_bar_get_quote_data.setValue(0)
        self.getting = True
        self.suspend = False
        self.button_get_data_suspend.setText("暂停")
        self.progress_bar_get_quote_data.setStyleSheet("QProgressBar{color:blue;}""QProgressBar::chunk{background-color:green;}");
        self.thread_back_test = threading.Thread(target = self.Thread_GetStockDaily)
        self.thread_back_test.start()
        self.button_get_security_info.setEnabled(False)
        self.button_get_capital_data.setEnabled(False)
        self.button_get_exrights_data.setEnabled(False)
        self.button_get_stock_daily.setEnabled(False)
        self.button_get_stock_kline_1_m.setEnabled(False)

    def Thread_GetStockDaily(self):
        total_task = 0
        finish_task = 0
        success_task = 0
        date_s = int(self.dt_edit_get_quote_data_s.dateTime().toString("yyyyMMdd"))
        date_e = int(self.dt_edit_get_quote_data_e.dateTime().toString("yyyyMMdd"))
        try:
            result_table_daily = self.basicx.GetTables_Stock_Daily()
            if not result_table_daily.empty:
                total_task = result_table_daily.shape[0]
                for index, row in result_table_daily.iterrows():
                    market_code = row["table"].replace("stock_daily_", "").split("_") # ["sh", "600000"]、["sz", "000001"]
                    stock_daily = self.basicx.GetStockDaily(market_code[0], market_code[1], date_s, date_e)
                    if not stock_daily.empty:
                        success_task += 1
                    finish_task += 1
                    progress = round(float(finish_task) / float(total_task) * 100.0) # 如果 total_task 为 0 不会进入循环的
                    if self.get_quote_data_progress != progress: # 减少进度刷新
                        self.get_quote_data_progress = progress
                    QApplication.postEvent(self, QEvent(define.DEF_EVENT_SET_ANALYSIS_GET_QUOTE_DATA_PROGRESS))
                    if False == self.getting:
                        break
                    while True == self.suspend:
                        time.sleep(1.0)
        except Exception as e:
            QApplication.postEvent(self, QEvent(define.DEF_EVENT_SET_ANALYSIS_GET_QUOTE_DATA_PROGRESS_ERROR))
            self.logger.SendMessage("E", 4, self.log_cate, "数据 1_D 下载发生异常！%s" % e, "S")
        self.log_text = "1_D 数据 下载完成。总计：%d，下载：%d，缺失：%d。" % (total_task, success_task, total_task - success_task)
        self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "S")

    def OnClickButtonGetStockKline_1_M(self):
        self.get_quote_data_progress = 0
        self.progress_bar_get_quote_data.setValue(0)
        self.getting = True
        self.suspend = False
        self.button_get_data_suspend.setText("暂停")
        self.progress_bar_get_quote_data.setStyleSheet("QProgressBar{color:blue;}""QProgressBar::chunk{background-color:green;}");
        self.thread_back_test = threading.Thread(target = self.Thread_GetStockKline_1_M)
        self.thread_back_test.start()
        self.button_get_security_info.setEnabled(False)
        self.button_get_capital_data.setEnabled(False)
        self.button_get_exrights_data.setEnabled(False)
        self.button_get_stock_daily.setEnabled(False)
        self.button_get_stock_kline_1_m.setEnabled(False)

    def Thread_GetStockKline_1_M(self):
        total_task = 0
        finish_task = 0
        success_task = 0
        date_s = int(self.dt_edit_get_quote_data_s.dateTime().toString("yyyyMMdd"))
        date_e = int(self.dt_edit_get_quote_data_e.dateTime().toString("yyyyMMdd"))
        try:
            result_table_kline_1_m = self.basicx.GetTables_Stock_Kline_1_M()
            if not result_table_kline_1_m.empty:
                total_task = result_table_kline_1_m.shape[0]
                for index, row in result_table_kline_1_m.iterrows():
                    market_code = row["table"].replace("stock_kline_1_m_", "").split("_") # ["sh", "600000"]、["sz", "000001"]
                    stock_kline_1_m = self.basicx.GetStockKline_1_M(market_code[0], market_code[1], date_s, date_e)
                    if not stock_kline_1_m.empty:
                        success_task += 1
                    finish_task += 1
                    progress = round(float(finish_task) / float(total_task) * 100.0)
                    if self.get_quote_data_progress != progress: # 减少进度刷新
                        self.get_quote_data_progress = progress
                    QApplication.postEvent(self, QEvent(define.DEF_EVENT_SET_ANALYSIS_GET_QUOTE_DATA_PROGRESS))
                    if False == self.getting:
                        break
                    while True == self.suspend:
                        time.sleep(1.0)
        except Exception as e:
            QApplication.postEvent(self, QEvent(define.DEF_EVENT_SET_ANALYSIS_GET_QUOTE_DATA_PROGRESS_ERROR))
            self.logger.SendMessage("E", 4, self.log_cate, "数据 1_M 下载发生异常！%s" % e, "S")
        self.log_text = "1_M 数据 下载完成。总计：%d，下载：%d，缺失：%d。" % (total_task, success_task, total_task - success_task)
        self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "S")

    def OnClickButtonGetDataSuspend(self):
        if self.suspend == False:
            self.suspend = True
            self.button_get_data_suspend.setText("继续")
            self.progress_bar_get_quote_data.setStyleSheet("QProgressBar{color:blue;}""QProgressBar::chunk{background-color:orange;}"); # 暂停
        else:
            self.suspend = False
            self.button_get_data_suspend.setText("暂停")
            self.progress_bar_get_quote_data.setStyleSheet("QProgressBar{color:blue;}""QProgressBar::chunk{background-color:green;}"); # 运行

    def OnClickButtonGetDataStop(self):
        self.getting = False
        self.suspend = False
        self.button_get_data_suspend.setText("暂停")
        self.progress_bar_get_quote_data.setStyleSheet("QProgressBar{color:blue;}""QProgressBar::chunk{background-color:gray;}"); # 停止
        self.button_get_security_info.setEnabled(True)
        self.button_get_capital_data.setEnabled(True)
        self.button_get_exrights_data.setEnabled(True)
        self.button_get_stock_daily.setEnabled(True)
        self.button_get_stock_kline_1_m.setEnabled(True)

    def HandleButtonState(self, str_type):
        self.analys = analys.Analys()
        if str_type == "加载":
            analysis_info = self.analys.analysis_info
            if analysis_info != None:
                self.button_reload.setEnabled(False)
                self.button_run.setEnabled(True)
                self.button_suspend.setEnabled(False)
                self.button_continue.setEnabled(False)
                self.button_stop.setEnabled(False)
                self.button_unload.setEnabled(True)
                self.edits_name.setText(analysis_info.analysis)
                self.edits_type.setText(analysis_info.name)
                self.edits_info.setText(analysis_info.introduction)
                self.edits_path.setText(analysis_info.filePath)
                self.progress_bar_analysis.setStyleSheet("QProgressBar{color:black;}""QProgressBar::chunk{background-color:gray;}");
        elif str_type == "运行":
            self.button_reload.setEnabled(False)
            self.button_run.setEnabled(False)
            self.button_suspend.setEnabled(True)
            self.button_continue.setEnabled(False)
            self.button_stop.setEnabled(True)
            self.button_unload.setEnabled(False)
            self.progress_bar_analysis.setValue(0)
            self.progress_bar_analysis.setStyleSheet("QProgressBar{color:blue;}""QProgressBar::chunk{background-color:green;}");
            self.button_get_symbol_list.setEnabled(False)
            self.check_box_security_check_all.setEnabled(False) # 不设也没事
        elif str_type == "暂停":
            self.button_reload.setEnabled(False)
            self.button_run.setEnabled(False)
            self.button_suspend.setEnabled(False)
            self.button_continue.setEnabled(True)
            self.button_stop.setEnabled(False)
            self.button_unload.setEnabled(False)
            self.progress_bar_analysis.setStyleSheet("QProgressBar{color:blue;}""QProgressBar::chunk{background-color:orange;}");
        elif str_type == "继续":
            self.button_reload.setEnabled(False)
            self.button_run.setEnabled(False)
            self.button_suspend.setEnabled(True)
            self.button_continue.setEnabled(False)
            self.button_stop.setEnabled(True)
            self.button_unload.setEnabled(False)
            self.progress_bar_analysis.setStyleSheet("QProgressBar{color:blue;}""QProgressBar::chunk{background-color:green;}");
        elif str_type == "停止":
            self.button_reload.setEnabled(False)
            self.button_run.setEnabled(True)
            self.button_suspend.setEnabled(False)
            self.button_continue.setEnabled(False)
            self.button_stop.setEnabled(False)
            self.button_unload.setEnabled(True)
            self.progress_bar_analysis.setStyleSheet("QProgressBar{color:blue;}""QProgressBar::chunk{background-color:gray;}");
            self.button_get_symbol_list.setEnabled(True)
            self.check_box_security_check_all.setEnabled(True)
        elif str_type == "卸载":
            self.button_reload.setEnabled(True)
            self.button_run.setEnabled(False)
            self.button_suspend.setEnabled(False)
            self.button_continue.setEnabled(False)
            self.button_stop.setEnabled(False)
            self.button_unload.setEnabled(False)
            self.edits_name.setText("")
            self.edits_type.setText("")
            self.edits_info.setText("")
            self.edits_path.setText("")
            self.progress_bar_analysis.setValue(0)
            self.progress_bar_analysis.setStyleSheet("QProgressBar{color:black;}""QProgressBar::chunk{background-color:gray;}");
            self.combo_box_analysis_date_s.clear()
            self.combo_box_analysis_date_e.clear()
            self.label_analysis_date_count.setText("0")

    def OnClickButtonDailyReportLoad(self):
        dlg_file = QFileDialog.getOpenFileName(None, caption = "选择净值文件...", directory = self.daily_report_folder, filter = "Excel Files(*.xls*)")
        if dlg_file != "":
            file_path = dlg_file[0].__str__()
            if file_path != "":
                self.daily_report_folder = os.path.dirname(file_path)
                self.line_edit_daily_report_file.setText(file_path)
                ret = self.assess.SaveDailyReport(file_path)
                if ret == True:
                    self.button_daily_report_evaluate.setEnabled(True)

    # 函数 assess.StrategyEvaluation() 中 valuex.MakeNetValueCompare() 的 plot 画图只能在主线程做，不然会报错
    def OnClickButtonDailyReportEvaluate(self):
        self.button_daily_report_evaluate.setEnabled(False)
        try:
            account_daily_report = self.line_edit_daily_report_evaluate_account.text()
            date_daily_report_s = int(self.dt_edit_daily_report_evaluate_s.dateTime().toString("yyyyMMdd"))
            date_daily_report_e = int(self.dt_edit_daily_report_evaluate_e.dateTime().toString("yyyyMMdd"))
            daily_report = self.assess.GetDailyReport(account_daily_report, date_daily_report_s, date_daily_report_e)
            if not daily_report.empty:
                self.assess.StrategyEvaluation(daily_report)
            else:
                self.log_text = "选取的账号和时间段净值数据为空！"
                self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "A")
        except Exception as e:
            self.log_text = "根据每日净值进行模型评估发生异常！%s" % e
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "A")
        self.button_daily_report_evaluate.setEnabled(True)
