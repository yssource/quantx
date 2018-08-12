
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

import os
import xlrd
import dbfread

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QCheckBox, QDialog, QFileDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QSizePolicy, QSpacerItem, QHBoxLayout, QVBoxLayout

import define
import table_stock_list

class OrderItem(object): # 委托个股信息
    def __init__(self, **kwargs):
        self.symbol = kwargs.get("symbol", "") # 证券代码
        self.exchange = kwargs.get("exchange", "") # 交易所，SH：上交所，SZ：深交所
        self.entr_type = kwargs.get("entr_type", 0) # 委托方式，1：限价，2：市价
        self.exch_side = kwargs.get("exch_side", 0) # 交易类型，1：买入，2：卖出
        self.price = kwargs.get("price", 0.0) # 委托价格
        self.amount = kwargs.get("amount", 0) # 委托数量
        self.fill_qty = 0
        self.need_qty = 0

    def ToString(self):
        return "symbol：%s, " % self.symbol + \
               "exchange：%s, " % self.exchange + \
               "entr_type：%d, " % self.entr_type + \
               "exch_side：%d, " % self.exch_side + \
               "price：%f, " % self.price + \
               "amount：%d, " % self.amount + \
               "fill_qty：%d, " % self.fill_qty + \
               "need_qty：%d" % self.need_qty

class PositionItem(object): # 持仓个股信息
    def __init__(self, **kwargs):
        self.symbol = kwargs.get("symbol", "") # 证券代码
        self.name = kwargs.get("name", "") # 证券名称
        self.position_total = kwargs.get("position_total", 0) # 今余额
        self.position_can_sell = kwargs.get("position_can_sell", 0) # 可卖量

    def ToString(self):
        return "symbol：%s, " % self.symbol + \
               "name：%s, " % self.name + \
               "position_total：%d, " % self.position_total + \
               "position_can_sell：%d" % self.position_can_sell

class Panel(QDialog):
    def __init__(self, **kwargs):
        super(Panel, self).__init__()
        self.data_align = [0, 0, 0, 0, 0, 1, 1, 1, 1] # 左：-1，中：0，右：1
        self.head_list = ["", "代码", "市场", "委托", "方向", "价格", "数量", "已成", "未成"]
        self.head_index_symbol = 1
        self.head_index_quote = 7
        self.head_index_pos_total = 8
        self.head_index_pos_can_sell = 9
        self.head_index_order_id = 10
        self.head_index_has_fill_qty = 11
        self.head_index_not_fill_qty = 12
        self.list_id_b = 1
        self.list_id_s = 2
        
        self.order_list_folder = ""
        self.position_list_folder = ""
        self.export_file_b = ""
        self.export_file_s = ""
        
        self.order_list_b = []
        self.order_dict_b = {}
        self.order_list_s = []
        self.order_dict_s = {}
        
        self.position_list_a = []
        self.position_dict_a = {}
        self.position_list_z = []
        self.position_dict_z = {}
        
        self.InitUserInterface()

    def __del__(self):
        pass

    def InitUserInterface(self):
        self.setWindowTitle("成交校验面板")
        self.resize(1250, 520)
        self.setFont(QFont("SimSun", 9))
        
        self.spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        self.data_lister_b = table_stock_list.DataLister(self, self.list_id_b, self.data_align, self.head_list, self.head_index_symbol)
        self.data_lister_b.setMinimumWidth(625)
        self.data_lister_b.setMinimumHeight(400)
        
        self.data_lister_s = table_stock_list.DataLister(self, self.list_id_s, self.data_align, self.head_list, self.head_index_symbol)
        self.data_lister_s.setMinimumWidth(625)
        self.data_lister_s.setMinimumHeight(400)
        
        self.label_order_list_file_b = QLabel()
        self.label_order_list_file_b.setText("买入清单:")
        self.edits_order_list_file_b = QLineEdit(self)
        self.edits_order_list_file_b.setMinimumWidth(400)
        self.edits_order_list_file_b.setReadOnly(True)
        self.edits_order_list_file_b.setStyleSheet("color:red")
        self.button_choose_order_list_file_b = QPushButton("选择文件")
        self.button_choose_order_list_file_b.setFont(QFont("SimSun", 9))
        self.button_choose_order_list_file_b.setMinimumSize(60, 22)
        self.button_choose_order_list_file_b.setMaximumSize(60, 22)
        self.button_choose_order_list_file_b.setStyleSheet("color:red")
        self.button_choose_order_list_file_b.setEnabled(True)
        
        self.label_order_list_file_s = QLabel()
        self.label_order_list_file_s.setText("卖出清单:")
        self.edits_order_list_file_s = QLineEdit(self)
        self.edits_order_list_file_s.setMinimumWidth(400)
        self.edits_order_list_file_s.setReadOnly(True)
        self.edits_order_list_file_s.setStyleSheet("color:green")
        self.button_choose_order_list_file_s = QPushButton("选择文件")
        self.button_choose_order_list_file_s.setFont(QFont("SimSun", 9))
        self.button_choose_order_list_file_s.setMinimumSize(60, 22)
        self.button_choose_order_list_file_s.setMaximumSize(60, 22)
        self.button_choose_order_list_file_s.setStyleSheet("color:green")
        self.button_choose_order_list_file_s.setEnabled(True)
        
        self.label_position_list_file_a = QLabel()
        self.label_position_list_file_a.setText("期初持仓:")
        self.edits_position_list_file_a = QLineEdit(self)
        self.edits_position_list_file_a.setMinimumWidth(400)
        self.edits_position_list_file_a.setReadOnly(True)
        self.edits_position_list_file_a.setStyleSheet("color:black")
        self.button_choose_position_list_file_a = QPushButton("选择文件")
        self.button_choose_position_list_file_a.setFont(QFont("SimSun", 9))
        self.button_choose_position_list_file_a.setMinimumSize(60, 22)
        self.button_choose_position_list_file_a.setMaximumSize(60, 22)
        self.button_choose_position_list_file_a.setStyleSheet("color:black")
        self.button_choose_position_list_file_a.setEnabled(True)
        
        self.label_position_list_file_z = QLabel()
        self.label_position_list_file_z.setText("期末持仓:")
        self.edits_position_list_file_z = QLineEdit(self)
        self.edits_position_list_file_z.setMinimumWidth(400)
        self.edits_position_list_file_z.setReadOnly(True)
        self.edits_position_list_file_z.setStyleSheet("color:black")
        self.button_choose_position_list_file_z = QPushButton("选择文件")
        self.button_choose_position_list_file_z.setFont(QFont("SimSun", 9))
        self.button_choose_position_list_file_z.setMinimumSize(60, 22)
        self.button_choose_position_list_file_z.setMaximumSize(60, 22)
        self.button_choose_position_list_file_z.setStyleSheet("color:black")
        self.button_choose_position_list_file_z.setEnabled(True)
        
        self.button_load_orders = QPushButton("导入清单")
        self.button_load_orders.setFont(QFont("SimSun", 9))
        self.button_load_orders.setMinimumSize(60, 22)
        self.button_load_orders.setMaximumSize(60, 22)
        self.button_load_orders.setEnabled(True)
        
        self.button_clear_order_list = QPushButton("清空列表")
        self.button_clear_order_list.setFont(QFont("SimSun", 9))
        self.button_clear_order_list.setMinimumSize(60, 22)
        self.button_clear_order_list.setMaximumSize(60, 22)
        self.button_clear_order_list.setEnabled(True)
        
        self.button_export_orders = QPushButton("导出清单")
        self.button_export_orders.setFont(QFont("SimSun", 9))
        self.button_export_orders.setMinimumSize(60, 22)
        self.button_export_orders.setMaximumSize(60, 22)
        self.button_export_orders.setEnabled(True)
        
        self.button_choose_order_list_file_b.clicked.connect(lambda: self.OnButtonChooseOrderListFile(define.DEF_EXCHSIDE_BUY))
        self.button_choose_order_list_file_s.clicked.connect(lambda: self.OnButtonChooseOrderListFile(define.DEF_EXCHSIDE_SELL))
        self.button_choose_position_list_file_a.clicked.connect(lambda: self.OnButtonChoosePositionListFile("a"))
        self.button_choose_position_list_file_z.clicked.connect(lambda: self.OnButtonChoosePositionListFile("z"))
        self.button_load_orders.clicked.connect(self.OnButtonLoadOrders)
        self.button_clear_order_list.clicked.connect(self.OnButtonClearOrderList)
        self.button_export_orders.clicked.connect(self.OnButtonExportOrders)
        
        self.v_box_layout_data_list_b = QVBoxLayout()
        self.v_box_layout_data_list_b.setContentsMargins(0, 0, 0, 0)
        self.v_box_layout_data_list_b.addWidget(self.data_lister_b)
        
        self.v_box_layout_data_list_s = QVBoxLayout()
        self.v_box_layout_data_list_s.setContentsMargins(0, 0, 0, 0)
        self.v_box_layout_data_list_s.addWidget(self.data_lister_s)
        
        self.h_box_layout_data_list = QHBoxLayout()
        self.h_box_layout_data_list.setContentsMargins(0, 0, 0, 0)
        self.h_box_layout_data_list.addLayout(self.v_box_layout_data_list_b)
        self.h_box_layout_data_list.addLayout(self.v_box_layout_data_list_s)
        
        self.h_box_layout_order_list_file_b = QHBoxLayout()
        self.h_box_layout_order_list_file_b.setContentsMargins(0, 0, 0, 0)
        self.h_box_layout_order_list_file_b.addWidget(self.label_order_list_file_b)
        self.h_box_layout_order_list_file_b.addWidget(self.edits_order_list_file_b)
        self.h_box_layout_order_list_file_b.addWidget(self.button_choose_order_list_file_b)
        self.h_box_layout_order_list_file_b.addStretch(1)
        
        self.h_box_layout_order_list_file_s = QHBoxLayout()
        self.h_box_layout_order_list_file_s.setContentsMargins(0, 0, 0, 0)
        self.h_box_layout_order_list_file_s.addWidget(self.label_order_list_file_s)
        self.h_box_layout_order_list_file_s.addWidget(self.edits_order_list_file_s)
        self.h_box_layout_order_list_file_s.addWidget(self.button_choose_order_list_file_s)
        self.h_box_layout_order_list_file_s.addStretch(1)
        
        self.h_box_layout_order_list_file = QHBoxLayout()
        self.h_box_layout_order_list_file.setContentsMargins(0, 0, 0, 0)
        self.h_box_layout_order_list_file.addLayout(self.h_box_layout_order_list_file_b)
        self.h_box_layout_order_list_file.addLayout(self.h_box_layout_order_list_file_s)
        
        self.h_box_layout_position_list_file_a = QHBoxLayout()
        self.h_box_layout_position_list_file_a.setContentsMargins(0, 0, 0, 0)
        self.h_box_layout_position_list_file_a.addWidget(self.label_position_list_file_a)
        self.h_box_layout_position_list_file_a.addWidget(self.edits_position_list_file_a)
        self.h_box_layout_position_list_file_a.addWidget(self.button_choose_position_list_file_a)
        self.h_box_layout_position_list_file_a.addStretch(1)
        
        self.h_box_layout_position_list_file_z = QHBoxLayout()
        self.h_box_layout_position_list_file_z.setContentsMargins(0, 0, 0, 0)
        self.h_box_layout_position_list_file_z.addWidget(self.label_position_list_file_z)
        self.h_box_layout_position_list_file_z.addWidget(self.edits_position_list_file_z)
        self.h_box_layout_position_list_file_z.addWidget(self.button_choose_position_list_file_z)
        self.h_box_layout_position_list_file_z.addStretch(1)
        
        self.h_box_layout_position_list_file = QHBoxLayout()
        self.h_box_layout_position_list_file.setContentsMargins(0, 0, 0, 0)
        self.h_box_layout_position_list_file.addLayout(self.h_box_layout_position_list_file_a)
        self.h_box_layout_position_list_file.addLayout(self.h_box_layout_position_list_file_z)
        
        self.h_box_layout_order_ctrl = QHBoxLayout()
        self.h_box_layout_order_ctrl.setContentsMargins(0, 0, 0, 0)
        self.h_box_layout_order_ctrl.addStretch(1)
        self.h_box_layout_order_ctrl.addWidget(self.button_load_orders)
        self.h_box_layout_order_ctrl.addItem(self.spacer)
        self.h_box_layout_order_ctrl.addWidget(self.button_clear_order_list)
        self.h_box_layout_order_ctrl.addItem(self.spacer)
        self.h_box_layout_order_ctrl.addWidget(self.button_export_orders)
        self.h_box_layout_order_ctrl.addStretch(1)
        
        self.v_box_layout_basket_order = QVBoxLayout()
        self.v_box_layout_basket_order.setContentsMargins(8, 8, 8, 8)
        self.v_box_layout_basket_order.addLayout(self.h_box_layout_data_list)
        self.v_box_layout_basket_order.addLayout(self.h_box_layout_order_list_file)
        self.v_box_layout_basket_order.addLayout(self.h_box_layout_position_list_file)
        self.v_box_layout_basket_order.addLayout(self.h_box_layout_order_ctrl)
        self.v_box_layout_basket_order.addStretch(1)
        
        self.setLayout(self.v_box_layout_basket_order)

    def ShowContextMenu(self, list_id, index):
        pass

    def HandleLoadOrders(self, data_lister, order_list):
        try:
            data_lister.ClearListItems()
            for order_item in order_list:
                text_entr_type = "-"
                text_exch_side = "-"
                if 1 == order_item.entr_type:
                    text_entr_type = "限价"
                elif 2 == order_item.entr_type:
                    text_entr_type = "市价"
                if 1 == order_item.exch_side:
                    text_exch_side = "买入"
                elif 2 == order_item.exch_side:
                    text_exch_side = "卖出"
                check_box = QCheckBox("")
                check_box.setCheckable(True)
                data_lister.data_list.append([check_box, order_item.symbol, order_item.exchange, text_entr_type, text_exch_side, 
                                                   order_item.price, order_item.amount, order_item.fill_qty, order_item.need_qty])
            data_lister.data_list_model.setDataList(data_lister.data_list)
            data_lister.resizeColumnsToContents()
            data_lister.setColumnWidth(0, 20) # 选择列宽度
            data_lister.sortByColumn(self.head_index_symbol, Qt.AscendingOrder) # 按照 symbol 排序
        except Exception as e:
            print("HandleLoadOrders：", e)

    def ReadOrderListFile(self, exch_side_should, file_path):
        order_list = []
        order_dict = {}
        if file_path != "":
            xls_file = xlrd.open_workbook(file_path)
            xls_sheet = xls_file.sheet_by_name("Sheet1")
            xls_rows = xls_sheet.nrows
            xls_cols = xls_sheet.ncols
            if xls_rows < 2:
                print("批量委托清单文件 %s 行数异常！" % file_path)
                return
            if xls_cols < 6:
                print("批量委托清单文件 %s 列数异常！" % file_path)
                return
            for i in range(xls_rows):
                if i > 0:
                    symbol = str(xls_sheet.row(i)[0].value) # 避免代码变成数字
                    exchange = str(xls_sheet.row(i)[1].value)
                    entr_type = int(xls_sheet.row(i)[2].value)
                    exch_side = int(xls_sheet.row(i)[3].value)
                    price = float(xls_sheet.row(i)[4].value)
                    amount = int(xls_sheet.row(i)[5].value)
                    if symbol in order_dict.keys():
                        print("读取批量委托证券列表文件时 %s 已经存在！" % symbol)
                    elif exch_side != exch_side_should:
                        print("读取批量委托证券列表文件时 %s 买卖方向错误！" % symbol)
                    else:
                        order_item = OrderItem(symbol = symbol, exchange = exchange, entr_type = entr_type, exch_side = exch_side, price = price, amount = amount)
                        order_list.append(order_item)
                        order_dict[symbol] = len(order_list) - 1 # 下标索引
            #for item in order_list:
            #    print(item.ToString())
            print("导入批量委托证券 %d 个。%s" % (len(order_list), file_path))
        else:
            print("读取批量委托证券列表文件时路径为空！")
        return order_list, order_dict

    def ReadPositionListFile(self, file_path):
        position_list = []
        position_dict = {}
        if file_path != "":
            table = dbfread.DBF(file_path, load = True, encoding = "GBK") # GBK
            for record in table: # table.deleted 为加了删除标志的记录
                symbol = str(record["证券代码"]) # 避免代码变成数字
                name = str(record["证券名称"])
                position_total = int(record["今余额"])
                position_can_sell = int(record["可卖量"])
                position_item = PositionItem(symbol = symbol, name = name, position_total = position_total, position_can_sell = position_can_sell)
                position_list.append(position_item)
                position_dict[symbol] = len(position_list) - 1 # 下标索引
            #for item in position_list:
            #    print(item.ToString())
            print("导入持仓 %d 个。%s" % (len(position_list), file_path))
        else:
            print("读取持仓列表文件时路径为空！")
        return position_list, position_dict

    def OnButtonChooseOrderListFile(self, exch_side):
        dlg_file = QFileDialog.getOpenFileName(None, caption = "选择委托列表文件...", directory = self.order_list_folder, filter = "Order List Files(*.xls*)")
        if dlg_file != "":
            file_path = dlg_file[0].__str__()
            if file_path != "":
                file_name = os.path.basename(file_path)
                if file_name != "":
                    self.order_list_folder = os.path.dirname(file_path)
                    if exch_side == define.DEF_EXCHSIDE_BUY:
                        self.export_file_b = file_name.split(".")[0] + "_export.xls"
                        self.edits_order_list_file_b.setText(file_path)
                    if exch_side == define.DEF_EXCHSIDE_SELL:
                        self.export_file_s = file_name.split(".")[0] + "_export.xls"
                        self.edits_order_list_file_s.setText(file_path)

    def OnButtonChoosePositionListFile(self, file_type):
        dlg_file = QFileDialog.getOpenFileName(None, caption = "选择持仓列表文件...", directory = self.position_list_folder, filter = "Position List Files(*.dbf)")
        if dlg_file != "":
            file_path = dlg_file[0].__str__()
            if file_path != "":
                file_name = os.path.basename(file_path)
                if file_name != "":
                    self.position_list_folder = os.path.dirname(file_path)
                    if file_type == "a":
                        self.edits_position_list_file_a.setText(file_path)
                    if file_type == "z":
                        self.edits_position_list_file_z.setText(file_path)

    def CalcFillQty(self, symbol):
        src_pos = 0
        ret_pos = 0
        if symbol in self.position_dict_a.keys():
            position_item = self.position_list_a[self.position_dict_a[symbol]]
            src_pos = position_item.position_total
        if symbol in self.position_dict_z.keys():
            position_item = self.position_list_z[self.position_dict_z[symbol]]
            ret_pos = position_item.position_total
        return ret_pos - src_pos

    def OnButtonLoadOrders(self):
        self.order_list_b = []
        self.order_list_s = []
        self.order_dict_b = {}
        self.order_dict_s = {}
        self.position_list_a = []
        self.position_list_z = []
        self.position_dict_a = {}
        self.position_dict_z = {}
        file_path_order_b = self.edits_order_list_file_b.text()
        file_path_order_s = self.edits_order_list_file_s.text()
        file_path_position_a = self.edits_position_list_file_a.text()
        file_path_position_z = self.edits_position_list_file_z.text()
        self.order_list_b, self.order_dict_b = self.ReadOrderListFile(define.DEF_EXCHSIDE_BUY, file_path_order_b)
        self.order_list_s, self.order_dict_s = self.ReadOrderListFile(define.DEF_EXCHSIDE_SELL, file_path_order_s)
        self.position_list_a, self.position_dict_a = self.ReadPositionListFile(file_path_position_a)
        self.position_list_z, self.position_dict_z = self.ReadPositionListFile(file_path_position_z)
        #for position_item in self.position_list_a: # 全部卖出仍会存在
        #    if not position_item.symbol in self.position_dict_z.keys():
        #        print("期初 持仓 %s 不在 期末 持仓中！" % position_item.symbol)
        #for position_item in self.position_list_z: # 可能是新买入的
        #    if not position_item.symbol in self.position_dict_a.keys():
        #        print("期末 持仓 %s 不在 期初 持仓中！" % position_item.symbol)
        for order_item in self.order_list_b: # 买入委托
            order_item.fill_qty = self.CalcFillQty(order_item.symbol) # 期末 - 期初
            order_item.need_qty = order_item.amount - order_item.fill_qty
        for order_item in self.order_list_s: # 卖出委托
            order_item.fill_qty = -self.CalcFillQty(order_item.symbol) # -(期末 - 期初)
            order_item.need_qty = order_item.amount - order_item.fill_qty
        self.HandleLoadOrders(self.data_lister_b, self.order_list_b)
        self.HandleLoadOrders(self.data_lister_s, self.order_list_s)

    def OnButtonClearOrderList(self):
        reply = QMessageBox.question(self, "询问", "清空委托列表？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.order_list_b = []
            self.order_list_s = []
            self.order_dict_b = {}
            self.order_dict_s = {}
            self.position_list_a = []
            self.position_list_z = []
            self.position_dict_a = {}
            self.position_dict_z = {}
            self.data_lister_b.ClearListItems()
            self.data_lister_s.ClearListItems()
            self.edits_order_list_file_b.setText("")
            self.edits_order_list_file_s.setText("")
            self.edits_position_list_file_a.setText("")
            self.edits_position_list_file_z.setText("")

    def OnButtonExportOrders(self):
        print("OnButtonExportOrders")

####################################################################################################

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    panel = Panel()
    panel.show()
    sys.exit(app.exec_())
