
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

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QCheckBox, QDialog, QFileDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QHBoxLayout, QVBoxLayout

import define
import table_stock_list

class BatchOrderItem(object): # 批量委托成分股信息
    def __init__(self, **kwargs):
        self.symbol = kwargs.get("symbol", "") # 证券代码
        self.exchange = kwargs.get("exchange", "") # 交易所，SH：上交所，SZ：深交所
        self.entr_type = kwargs.get("entr_type", 0) # 委托方式，1：限价，2：市价
        self.exch_side = kwargs.get("exch_side", 0) # 交易类型，1：买入，2：卖出
        self.price = kwargs.get("price", 0.0) # 委托价格
        self.amount = kwargs.get("amount", 0) # 委托数量
        self.fill_qty = 0
        self.position_total = 0
        self.position_can_sell = 0

class Panel(QDialog):
    def __init__(self, **kwargs):
        super(Panel, self).__init__()
        self.data_align = [0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1] # 左：-1，中：0，右：1
        self.head_list = ["", "代码", "市场", "委托", "方向", "价格", "数量", "行情", "持仓", "可卖", "单号", "已成", "未成"]
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
        
        self.batch_order_list_b = []
        self.batch_order_dict_b = {}
        self.batch_order_list_s = []
        self.batch_order_dict_s = {}
        
        self.InitUserInterface()

    def __del__(self):
        pass

    def InitUserInterface(self):
        self.setWindowTitle("成交校验面板")
        self.resize(827, 672)
        self.setFont(QFont("SimSun", 9))
        
        self.data_lister_b = table_stock_list.DataLister(self, self.list_id_b, self.data_align, self.head_list, self.head_index_symbol)
        self.data_lister_b.setMinimumWidth(625)
        self.data_lister_b.setMinimumHeight(300)
        
        self.data_lister_s = table_stock_list.DataLister(self, self.list_id_s, self.data_align, self.head_list, self.head_index_symbol)
        self.data_lister_s.setMinimumWidth(625)
        self.data_lister_s.setMinimumHeight(300)
        
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
        self.h_box_layout_order_ctrl.addWidget(self.button_load_orders)
        self.h_box_layout_order_ctrl.addWidget(self.button_clear_order_list)
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

    def HandleLoadOrders(self, data_lister, batch_order_list):
        try:
            data_lister.ClearListItems()
            for batch_order_item in batch_order_list:
                text_entr_type = "-"
                text_exch_side = "-"
                text_check_quote = "-"
                if 1 == batch_order_item.entr_type:
                    text_entr_type = "限价"
                elif 2 == batch_order_item.entr_type:
                    text_entr_type = "市价"
                if 1 == batch_order_item.exch_side:
                    text_exch_side = "买入"
                elif 2 == batch_order_item.exch_side:
                    text_exch_side = "卖出"
                check_box = QCheckBox("")
                check_box.setCheckable(True)
                data_lister.data_list.append([check_box, batch_order_item.symbol, batch_order_item.exchange, text_entr_type, text_exch_side, 
                                                   batch_order_item.price, batch_order_item.amount, text_check_quote, batch_order_item.position_total, 
                                                   batch_order_item.position_can_sell, "-", 0, batch_order_item.amount])
            data_lister.data_list_model.setDataList(data_lister.data_list)
            data_lister.resizeColumnsToContents()
            data_lister.setColumnWidth(0, 20) # 选择列宽度
            data_lister.sortByColumn(self.head_index_symbol, Qt.AscendingOrder) # 按照 symbol 排序
        except Exception as e:
            print("HandleLoadOrders：", e)

    def ReadOrderListFile(self, exch_side_should, file_path):
        batch_order_list = []
        batch_order_dict = {}
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
                    entr_type = xls_sheet.row(i)[2].value
                    exch_side = xls_sheet.row(i)[3].value
                    price = xls_sheet.row(i)[4].value
                    amount = xls_sheet.row(i)[5].value
                    if symbol in batch_order_dict.keys():
                        print("读取批量委托证券列表文件时 %s 已经存在！" % symbol)
                    elif exch_side != exch_side_should:
                        print("读取批量委托证券列表文件时 %s 买卖方向错误！" % symbol)
                    else:
                        batch_order_item = BatchOrderItem(exchange = exchange, symbol = symbol, entr_type = entr_type, exch_side = exch_side, price = price, amount = amount)
                        batch_order_list.append(batch_order_item)
                        batch_order_dict[symbol] = len(batch_order_list) - 1 # 下标索引
            #for item in batch_order_list:
            #    print(item.ToString())
            print("导入批量委托证券 %d 个。%s" % (len(batch_order_list), file_path))
        else:
            print("读取批量委托证券列表文件时路径为空！")
        return batch_order_list, batch_order_dict

    def OnButtonChooseOrderListFile(self, exch_side):
        dlg_file = QFileDialog.getOpenFileName(None, caption = "选择委托列表文件...", directory = self.order_list_folder, filter = "Order List Files(*.xls*)")
        if dlg_file != "":
            file_path = dlg_file[0].__str__()
            if file_path != "":
                file_name = os.path.basename(file_path)
                if file_name != "":
                    self.order_list_folder = os.path.dirname(file_path)
                    if exch_side == define.DEF_EXCHSIDE_BUY:
                        self.edits_order_list_file_b.setText(file_path)
                    if exch_side == define.DEF_EXCHSIDE_SELL:
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

    def OnButtonLoadOrders(self):
        self.batch_order_list_b = []
        self.batch_order_dict_b = {}
        self.batch_order_list_s = []
        self.batch_order_dict_s = {}
        file_path_b = self.edits_order_list_file_b.text()
        file_path_s = self.edits_order_list_file_s.text()
        self.batch_order_list_b, self.batch_order_dict_b = self.ReadOrderListFile(define.DEF_EXCHSIDE_BUY, file_path_b)
        self.batch_order_list_s, self.batch_order_dict_s = self.ReadOrderListFile(define.DEF_EXCHSIDE_SELL, file_path_s)
        self.HandleLoadOrders(self.data_lister_b, self.batch_order_list_b)
        self.HandleLoadOrders(self.data_lister_s, self.batch_order_list_s)

    def OnButtonClearOrderList(self):
        reply = QMessageBox.question(self, "询问", "清空委托列表？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.batch_order_list_b = []
            self.batch_order_list_s = []
            self.batch_order_dict_b = {}
            self.batch_order_dict_s = {}
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
