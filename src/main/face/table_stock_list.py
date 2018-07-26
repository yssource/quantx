
# -*- coding: utf-8 -*-

# Copyright (c) 2018-2018 the QuantX authors
# All rights reserved.
#
# The project sponsor and lead author is Xu Rendong.
# E-mail: xrd@ustc.edu, QQ: 277195007, WeChat: ustc_xrd
# See the contributors file for names of other contributors.
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

import operator

from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableView

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
        # 需要在 emit() 之后再为 self.data_list 列表赋值，否则可能导致程序崩溃
        # 尤其是在已经单击选中一行数据再清空列表赋 [] 给 self.data_list 时
        self.layoutAboutToBeChanged.emit() # 先
        self.data_list = data_list # 后
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
        elif role == Qt.BackgroundRole: # 每行背景颜色
            #return QBrush(QColor(0, 128, 255))
            pass
        elif role == Qt.BackgroundColorRole:
            pass
        elif role == Qt.ForegroundRole: # 每行文字颜色
            #return QBrush(QColor(255, 0, 255))
            pass
        elif role == Qt.TextColorRole:
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
        elif role == Qt.DisplayRole:
            self.data_list[index.row()][index.column()] = value
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
    def __init__(self, parent, list_id, data_align, head_list, index_column):
        super(DataLister, self).__init__(parent)
        self.parent = parent
        self.list_id = list_id
        self.data_list = []
        self.data_align = data_align # 左：-1，中：0，右：1
        self.head_list = head_list
        self.index_column = index_column
        
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
        self.data_list_model.setIndexColumn(self.index_column) # 数据索引
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
            symbol = self.data_list_model.getCellText(item.row(), self.index_column)
            print(symbol)

    def OnContextMenu(self, pos):
        index = self.indexAt(pos)
        if index and index.row() >= 0:
            self.parent.ShowContextMenu(self.list_id, index)
        else:
            self.parent.ShowContextMenu(self.list_id, None)

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
