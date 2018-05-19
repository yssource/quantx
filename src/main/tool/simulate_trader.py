
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
import random
from datetime import datetime

from PyQt5.QtGui import QColor, QFont, QPalette
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QDoubleSpinBox, QLabel, QLineEdit
from PyQt5.QtWidgets import QPushButton, QRadioButton, QSpinBox, QGridLayout, QHBoxLayout, QVBoxLayout

import define
import dbm_mysql

class Security(object):
    def __init__(self, **kwargs):
        self.inners = kwargs.get("inners", 0) # 内部代码
        self.company = kwargs.get("company", 0) # 公司代码
        self.market = kwargs.get("market", "") #֤ 证券市场
        self.code = kwargs.get("code", "") # 证券代码
        self.name = kwargs.get("name", "") # 证券名称
        self.category = kwargs.get("category", 0) # 证券类别
        self.sector = kwargs.get("sector", 0) # 上市板块
        self.is_st = kwargs.get("is_st", 0) # 是否ST股
        self.list_state = kwargs.get("list_state", 0) # 上市状态
        self.list_date = kwargs.get("list_date", 0) # 上市日期

    def ToString(self):
            return "market：%s, " % self.market + \
                   "code：%s, " % self.code + \
                   "name：%s, " % self.name + \
                   "category：%d, " % self.category + \
                   "sector：%d, " % self.sector + \
                   "is_st：%d" % self.is_st

class QuoteData(object):
    def __init__(self, **kwargs):
        self.inners = kwargs.get("inners", 0) # 内部代码
        self.market = kwargs.get("market", "")
        self.code = kwargs.get("code", "")
        self.name = kwargs.get("name", "")
        self.category = kwargs.get("category", "")
        self.open = kwargs.get("open", 0.0)
        self.high = kwargs.get("high", 0.0)
        self.low = kwargs.get("low", 0.0)
        self.close = kwargs.get("close", 0.0)
        self.pre_close = kwargs.get("pre_close", 0.0)
        self.volume = kwargs.get("volume", 0) # 成交量，股
        self.turnover = kwargs.get("turnover", 0.0) # 成交额，元
        self.trade_count = kwargs.get("trade_count", 0) # 成交笔数
        self.quote_date = kwargs.get("quote_date", 0) # YYYYMMDD
        self.quote_time = kwargs.get("quote_time", 0) # HHMMSSmmm 精度：毫秒

    def ToString(self):
            return "market：%s, " % self.market + \
                   "code：%s, " % self.code + \
                   "name：%s, " % self.name + \
                   "category：%d, " % self.category + \
                   "open：%f, " % self.open + \
                   "high：%f, " % self.high + \
                   "low：%f, " % self.low + \
                   "close：%f, " % self.close + \
                   "pre_close：%f, " % self.pre_close + \
                   "volume：%d, " % self.volume + \
                   "turnover：%f, " % self.turnover + \
                   "trade_count：%d" % self.trade_count

class StockInfo(object):
    def __init__(self, **kwargs):
        self.market = kwargs.get("market", "") #֤ 证券市场
        self.code = kwargs.get("code", "") # 证券代码
        self.name = kwargs.get("name", "") # 证券名称
        self.close = kwargs.get("close", 0.0)

    def ToString(self):
            return "market：%s, " % self.market + \
                   "code：%s, " % self.code + \
                   "name：%s, " % self.name + \
                   "close：%f" % self.close

class SimulateTrader(QDialog):
    def __init__(self, **kwargs):
        super(SimulateTrader, self).__init__()
        self.host = kwargs.get("host", "0.0.0.0")
        self.port = kwargs.get("port", 0)
        self.user = kwargs.get("user", "user")
        self.passwd = kwargs.get("passwd", "123456")
        self.db_clearx = "clearx"
        self.db_financial = "financial"
        self.charset = "utf8"
        self.tb_security_info = "security_info"
        self.tb_pre_quote_stk = "pre_quote_stk"
        self.tb_account_trade = "account_trade"
        
        self.security = {}
        self.quote_data = {}
        self.stock_list = []
        self.trans_id = 0
        self.account_id = "test_account"
        
        self.dbm_clearx = dbm_mysql.DBM_MySQL(host = self.host, port = self.port, user = self.user, passwd = self.passwd, db = self.db_clearx, charset = self.charset) # db_clearx
        self.dbm_financial = dbm_mysql.DBM_MySQL(host = self.host, port = self.port, user = self.user, passwd = self.passwd, db = self.db_financial, charset = self.charset) # db_financial
        
        if self.dbm_clearx.Connect() == True and self.dbm_financial.Connect() == True:
            print("数据库连接成功。")
            self.GetSecurityInfo()
        else:
            print("数据库连接失败！")
        
        self.InitUserInterface()

    def __del__(self):
        pass

    def InitUserInterface(self):
        self.color_red = QPalette()
        self.color_red.setColor(QPalette.WindowText, Qt.red)
        self.color_green = QPalette()
        self.color_green.setColor(QPalette.WindowText, QColor(0, 128, 0))
        self.color_black = QPalette()
        self.color_black.setColor(QPalette.WindowText, Qt.black)
        
        self.list_exchange = [define.DEF_EXCHANGE_STOCK_SH, define.DEF_EXCHANGE_STOCK_SZ]
        self.list_entr_type = [define.DEF_PRICE_TYPE_STOCK_LIMIT, define.DEF_PRICE_TYPE_STOCK_MARKET]
        
        self.setWindowTitle("模拟交易面板")
        self.resize(244, 201)
        self.setFont(QFont("SimSun", 9))
        
        self.label_exchange = QLabel("交易市场")
        self.label_exchange.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_symbol = QLabel("证券代码")
        self.label_symbol.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_name = QLabel("证券名称")
        self.label_name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_entr_type = QLabel("委托方式")
        self.label_entr_type.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_price = QLabel("委托价格")
        self.label_price.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_volume = QLabel("委托数量")
        self.label_volume.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.label_price_unit = QLabel("元")
        self.label_price_unit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_volume_unit = QLabel("股")
        self.label_volume_unit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.combo_box_exchange = QComboBox()
        self.combo_box_exchange.addItems(self.list_exchange)
        self.line_edit_symbol = QLineEdit("")
        self.line_edit_symbol.setStyleSheet("color:red") # 初始红色
        self.line_edit_symbol.setFont(QFont("SimSun", 9))
        self.line_edit_name = QLineEdit("")
        self.line_edit_name.setReadOnly(True)
        self.line_edit_name.setFont(QFont("SimSun", 9))
        self.line_edit_name.setStyleSheet("background-color:rgb(240,240,240);color:red") # 初始红色
        self.line_edit_name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.combo_box_entr_type = QComboBox()
        self.combo_box_entr_type.addItems(self.list_entr_type)
        self.spin_box_price = QDoubleSpinBox()
        self.spin_box_price.setDecimals(4)
        self.spin_box_price.setMinimum(0)
        self.spin_box_price.setMaximum(100000)
        self.spin_box_price.setStyleSheet("color:red") # 初始红色
        self.spin_box_price.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spin_box_volume = QSpinBox()
        self.spin_box_volume.setMinimum(0)
        self.spin_box_volume.setMaximum(1000000)
        self.spin_box_volume.setSingleStep(100)
        self.spin_box_volume.setStyleSheet("color:red") # 初始红色
        self.spin_box_volume.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.grid_layout_essential = QGridLayout()
        self.grid_layout_essential.setContentsMargins(-1, -1, -1, -1)
        self.grid_layout_essential.addWidget(self.label_exchange,  0, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_symbol,    1, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_name,      2, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_entr_type, 3, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_price,     4, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_volume,    5, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.combo_box_exchange,  0, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.line_edit_symbol,    1, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.line_edit_name,      2, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.combo_box_entr_type, 3, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.spin_box_price,      4, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.spin_box_volume,     5, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.label_price_unit,  4, 2, 1, 1)
        self.grid_layout_essential.addWidget(self.label_volume_unit, 5, 2, 1, 1)
        
        self.radio_button_buy = QRadioButton("买 入")
        self.radio_button_buy.setStyleSheet("color:red")
        self.radio_button_buy.setFont(QFont("SimSun", 9))
        self.radio_button_buy.setChecked(True)
        self.radio_button_buy.setFixedWidth(70)
        self.radio_button_sell = QRadioButton("卖 出")
        self.radio_button_sell.setStyleSheet("color:green")
        self.radio_button_sell.setFont(QFont("SimSun", 9))
        self.radio_button_sell.setFixedWidth(70)
        self.button_place_order = QPushButton("下 单")
        self.button_place_order.setFont(QFont("SimSun", 9))
        self.button_place_order.setStyleSheet("font:bold;color:red") # 初始红色
        self.button_place_order.setFixedWidth(70)
        
        self.h_box_layout_order_buttons = QHBoxLayout()
        self.h_box_layout_order_buttons.setContentsMargins(-1, -1, -1, -1)
        self.h_box_layout_order_buttons.addStretch(1)
        self.h_box_layout_order_buttons.addWidget(self.radio_button_buy)
        self.h_box_layout_order_buttons.addStretch(1)
        self.h_box_layout_order_buttons.addWidget(self.radio_button_sell)
        self.h_box_layout_order_buttons.addStretch(1)
        self.h_box_layout_order_buttons.addWidget(self.button_place_order)
        self.h_box_layout_order_buttons.addStretch(1)
        
        self.v_box_layout_order = QVBoxLayout()
        self.v_box_layout_order.setContentsMargins(-1, -1, -1, -1)
        self.v_box_layout_order.addLayout(self.grid_layout_essential)
        self.v_box_layout_order.addLayout(self.h_box_layout_order_buttons)
        
        self.setLayout(self.v_box_layout_order)
        
        self.button_place_order.clicked.connect(self.OnButtonPlaceOrder)

    def OnChangeBuySell(self, exch_side):
        if exch_side == 1: # buy
            self.line_edit_symbol.setStyleSheet("color:red")
            self.line_edit_name.setStyleSheet("background-color:rgb(240,240,240);color:red")
            self.spin_box_price.setStyleSheet("color:red")
            self.spin_box_volume.setStyleSheet("color:red")
            self.button_place_order.setStyleSheet("font:bold;color:red")
        if exch_side == 2: # sell
            self.line_edit_symbol.setStyleSheet("color:green")
            self.line_edit_name.setStyleSheet("background-color:rgb(240,240,240);color:green")
            self.spin_box_price.setStyleSheet("color:green")
            self.spin_box_volume.setStyleSheet("color:green")
            self.button_place_order.setStyleSheet("font:bold;color:green")

    def OnButtonPlaceOrder(self):
        stock_count = len(self.stock_list)
        if stock_count > 0:
            min_index = 0
            max_index = len(self.stock_list)
            random.seed()
            stock_index = random.randint(min_index, max_index)
            stock = self.stock_list[stock_index]
            print(stock.ToString())
            
            self.line_edit_symbol.setText(stock.code)
            self.line_edit_name.setText(stock.name)
            if stock.market == "SH":
                self.combo_box_exchange.setCurrentIndex(0)
            elif stock.market == "SZ":
                self.combo_box_exchange.setCurrentIndex(1)
            self.spin_box_price.setValue(stock.close)
            volume = random.randint(1, 99) * 100
            self.spin_box_volume.setValue(volume)
            self.combo_box_entr_type.setCurrentIndex(0)
            exch_side = random.randint(1, 2)
            if exch_side == 1:
                self.radio_button_buy.setChecked(True)
                self.radio_button_sell.setChecked(False)
            elif exch_side == 2:
                self.radio_button_buy.setChecked(False)
                self.radio_button_sell.setChecked(True)
            self.OnChangeBuySell(exch_side)
            
            if self.dbm_clearx.Connect() == True:
                self.trans_id += 1
                dbm = self.dbm_clearx
                sql = "INSERT INTO %s (trade_time, account_id, trans_id, market, symbol, name, direction, amount, price) VALUES ('%s', '%s', '%d', '%s', '%s', '%s', %d, %d, %f)" \
                      % (self.tb_account_trade, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), self.account_id, self.trans_id, stock.market, stock.code, stock.name, exch_side, volume, stock.close)
                if dbm.ExecuteSql(sql) == True:
                    print("增加交易记录成功。")
                else:
                    print("增加交易记录失败！")
            else:
                print("数据库尚未连接！")
        else:
            print("证券列表为空！")

    def GetSecurityInfo(self):
        self.security = {}
        self.quote_data = {}
        self.stock_list = []
        
        dbm = self.dbm_financial
        sql = "SELECT inners, company, market, code, name, category, sector, is_st, list_state, list_date " + \
              "FROM %s WHERE category > 0 AND category < 5 AND list_state = 1 ORDER BY market ASC, code ASC" % self.tb_security_info
        result = dbm.QueryAllSql(sql)
        if result != None:
            rows = list(result)
            if len(rows) > 0:
                for (inners, company, market, code, name, category, sector, is_st, list_state, list_date) in rows:
                    self.security[market + code] = Security(inners = inners, company = company, market = market, code = code, name = name, category = category, 
                                                            sector = sector, is_st = is_st, list_state = list_state, list_date = list_date)
                #for key, value in self.security.iteritems():
                #    print(key, value.ToString())
            else:
                print("证券信息数据为空！")
        else:
            print("获取证券信息数据失败！")
        sql = "SELECT inners, market, code, name, category, open, high, low, close, pre_close, volume, turnover, trade_count, quote_date, quote_time " + \
              "FROM %s ORDER BY market ASC, code ASC" % self.tb_pre_quote_stk
        result = dbm.QueryAllSql(sql)
        if result != None:
            rows = list(result)
            if len(rows) > 0:
                for (inners, market, code, name, category, open, high, low, close, pre_close, volume, turnover, trade_count, quote_date, quote_time) in rows:
                    self.quote_data[market + code] = QuoteData(inners = inners, market = market, code = code, name = name, category = category, 
                                                               open = open, high = high, low = low, close = close, pre_close = pre_close, volume = volume, 
                                                               turnover = turnover, trade_count = trade_count, quote_date = quote_date, quote_time = quote_time)
                #for key, value in self.quote_data.iteritems():
                #    print(key, value.ToString())
            else:
                print("昨日行情数据为空！")
        else:
            print("获取昨日行情数据失败！")
        for key, value in self.security.iteritems():
            if key in self.quote_data.keys():
                quote = self.quote_data[key]
                self.stock_list.append(StockInfo(market = value.market, code = value.code, name = value.name, close = quote.close))
        #for stock in self.stock_list:
        #    print(stock.ToString())

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    simulate_trader = SimulateTrader(host = "10.0.7.53", port = 3306, user = "root", passwd = "root") # 测试
    #simulate_trader = SimulateTrader(host = "10.0.7.80", port = 3306, user = "root", passwd = "root") # 生产
    simulate_trader.show()
    sys.exit(app.exec_())
