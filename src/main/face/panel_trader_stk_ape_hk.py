
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

from PyQt5.QtGui import QColor, QFont, QPalette
from PyQt5.QtCore import QEvent, Qt #QString
from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QDoubleSpinBox, QLabel, QLineEdit, QMessageBox
from PyQt5.QtWidgets import QPushButton, QRadioButton, QSpinBox, QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout

import define
import logger
import center
import trader
import basicx

class Panel(QDialog):
    def __init__(self, **kwargs):
        super(Panel, self).__init__()
        self.strategy = kwargs.get("strategy", "")
        self.version_info = "V0.1.0-Beta Build 20181015"
        self.log_text = ""
        self.log_cate = "Panel_Trader_STK_APE_HK"
        self.logger = logger.Logger()
        
        self.InitUserInterface()
        
        self.symbol = ""
        self.exchange = "" # HK
        self.trader = None # 策略中赋值
        self.subscribe = False # 行情订阅标志
        self.center = center.Center()
        self.basicx = basicx.BasicX()
        
        self.quote_data = None
        self.price_round_stock = 3 # 小数位数
        self.price_round_index = 3 # 小数位数
        
        self.trade_unit_dict = {} # 买卖单位
        self.min_price_chg_dict = {} # 最小变动价格
        self.security_name_dict = {} # 证券名称
        self.component_hsggt_hgt_dict = {} # 沪港通成分股
        self.component_hsggt_sgt_dict = {} # 深港通成分股

    def OnWorking(self): # 供具体策略继承调用，在 运行 前执行一些操作
        if self.subscribe == False:
            self.center.RegQuoteSub(self.strategy, self.OnQuoteStock, "stock_hgt")
            self.center.RegQuoteSub(self.strategy, self.OnQuoteStock, "stock_sgt")
            self.subscribe = True
        self.trader = trader.Trader().GetTrader("hbzq_ape") # 华宝顶点 APE
        if self.trader == None:
            self.logger.SendMessage("E", 4, self.log_cate, "获取标识为 hbzq_ape 的交易服务失败！", "M")
        
        self.trade_unit_dict = {}
        self.min_price_chg_dict = {}
        self.security_name_dict = {}
        result = self.basicx.GetSecurityInfo_HK()
        if not result.empty:
            for index, row in result.iterrows():
                key_security_info = row["market"] + row["code"]
                self.trade_unit_dict[key_security_info] = row["trade_unit"]
                self.min_price_chg_dict[key_security_info] = row["min_price_chg"]
                self.security_name_dict[key_security_info] = row["name"]
            self.log_text = "获取 H股证券信息 %d 个。" % len(self.security_name_dict)
            self.logger.SendMessage("pron", 2, self.log_cate, self.log_text, "T")
        else:
            self.logger.SendMessage("W", 3, self.log_cate, "获取 H股证券信息 为空！", "T")
        
        self.component_hsggt_hgt_dict = {}
        self.component_hsggt_sgt_dict = {}
        result = self.basicx.GetComponentHSGGT()
        if not result.empty:
            for index, row in result.iterrows():
                key_component_hsggt = row["market"] + row["code"]
                if row["comp_type"] == 1: # 沪港通
                    self.component_hsggt_hgt_dict[key_component_hsggt] = key_component_hsggt
                if row["comp_type"] == 4: # 深港通
                    self.component_hsggt_sgt_dict[key_component_hsggt] = key_component_hsggt
            self.log_text = "获取 沪港通成分股 %d 个。" % len(self.component_hsggt_hgt_dict)
            self.logger.SendMessage("pron", 2, self.log_cate, self.log_text, "T")
            self.log_text = "获取 深港通成分股 %d 个。" % len(self.component_hsggt_sgt_dict)
            self.logger.SendMessage("pron", 2, self.log_cate, self.log_text, "T")
        else:
            self.logger.SendMessage("W", 3, self.log_cate, "获取 沪深港通成分股 为空！", "T")

    def OnSuspend(self): # 供具体策略继承调用，在 暂停 前执行一些操作
        pass

    def OnContinue(self): # 供具体策略继承调用，在 继续 前执行一些操作
        pass

    def OnTerminal(self): # 供具体策略继承调用，在 停止 前执行一些操作
        if self.subscribe == True:
            self.center.DelQuoteSub(self.strategy, "stock_hgt")
            self.center.DelQuoteSub(self.strategy, "stock_sgt")
            self.subscribe = False

    def event(self, event):
        if event.type() == define.DEF_EVENT_TRADER_STK_APE_HK_UPDATE_QUOTE:
            if self.quote_data != None:
                self.OnUpdateQuote(self.quote_data, self.price_round_stock)
        return QDialog.event(self, event)

    def OnTraderEvent(self, trader, ret_func, task_item): # 交易模块事件通知，供具体策略继承调用
        if ret_func == define.trade_placeorder_hk_s_func: # HK
            self.log_text = "%s：%s %d：%d" % (self.strategy, trader, ret_func, task_item.order.order_id)
            self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")

    def OnQuoteStock(self, msg): # 行情触发
        try:
            str_code = msg.data[0].decode()
            if str_code == self.symbol:
                self.quote_data = msg.data
                QApplication.postEvent(self, QEvent(define.DEF_EVENT_TRADER_STK_APE_HK_UPDATE_QUOTE)) # postEvent异步，sendEvent同步
        except Exception as e:
            self.log_text = "%s：函数 OnQuoteStock 异常！%s" % (self.strategy, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "M")

    def InitUserInterface(self):
        self.color_red = QPalette()
        self.color_red.setColor(QPalette.WindowText, Qt.red)
        self.color_green = QPalette()
        self.color_green.setColor(QPalette.WindowText, QColor(0, 128, 0))
        self.color_black = QPalette()
        self.color_black.setColor(QPalette.WindowText, Qt.black)
        
        self.list_exchange = [define.DEF_EXCHANGE_STOCK_HGT, define.DEF_EXCHANGE_STOCK_SGT]
        self.list_entr_type = [define.DEF_PRICE_TYPE_STOCK_HK_BOOST_LIMIT, define.DEF_PRICE_TYPE_STOCK_HK_AUCTION_LIMIT, define.DEF_PRICE_TYPE_STOCK_HK_ODDMENT]
        
        self.setWindowTitle("手动交易-股票-APE-H股 %s" % self.version_info)
        self.resize(380, 300)
        self.setFont(QFont("SimSun", 9))
        
        self.label_exchange = QLabel("交易市场")
        self.label_exchange.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_symbol = QLabel("证券代码")
        self.label_symbol.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_name = QLabel("证券名称")
        self.label_name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_entr_type = QLabel("委托方式")
        self.label_entr_type.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_can_use = QLabel("可用金额")
        self.label_can_use.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_can_sell = QLabel("可用数量")
        self.label_can_sell.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_price = QLabel("委托价格")
        self.label_price.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_volume = QLabel("委托数量")
        self.label_volume.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.label_can_use_unit = QLabel("元")
        self.label_can_use_unit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_can_sell_unit = QLabel("股")
        self.label_can_sell_unit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_price_unit = QLabel("元")
        self.label_price_unit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_volume_unit = QLabel("股")
        self.label_volume_unit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.line_edit_tips_exchange = QLineEdit("")
        self.line_edit_tips_exchange.setReadOnly(True)
        self.line_edit_tips_exchange.setFixedWidth(60)
        self.line_edit_tips_exchange.setToolTip("沪深港通")
        self.line_edit_tips_exchange.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.line_edit_tips_exchange.setStyleSheet("background-color:rgb(240,240,240)")
        self.line_edit_tips_trade_unit = QLineEdit("0")
        self.line_edit_tips_trade_unit.setReadOnly(True)
        self.line_edit_tips_trade_unit.setFixedWidth(42)
        self.line_edit_tips_trade_unit.setToolTip("买卖单位")
        self.line_edit_tips_trade_unit.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.line_edit_tips_trade_unit.setStyleSheet("background-color:rgb(240,240,240)")
        self.line_edit_tips_min_price_chg = QLineEdit("0.0")
        self.line_edit_tips_min_price_chg.setReadOnly(True)
        self.line_edit_tips_min_price_chg.setFixedWidth(42)
        self.line_edit_tips_min_price_chg.setToolTip("最小变动价格")
        self.line_edit_tips_min_price_chg.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.line_edit_tips_min_price_chg.setStyleSheet("background-color:rgb(240,240,240)")
        
        self.combo_exchange = QComboBox()
        self.combo_exchange.addItems(self.list_exchange)
        self.line_edit_symbol = QLineEdit("")
        self.line_edit_symbol.setStyleSheet("color:red") # 初始红色
        self.line_edit_symbol.setFont(QFont("SimSun", 9))
        self.line_edit_name = QLineEdit("")
        self.line_edit_name.setReadOnly(True)
        self.line_edit_name.setFont(QFont("SimSun", 9))
        self.line_edit_name.setStyleSheet("background-color:rgb(240,240,240);color:red") # 初始红色
        self.line_edit_name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.combo_entr_type = QComboBox()
        self.combo_entr_type.addItems(self.list_entr_type)
        self.line_edit_can_use = QLineEdit("0.00")
        self.line_edit_can_use.setReadOnly(True)
        self.line_edit_can_use.setStyleSheet("background-color:rgb(240,240,240)")
        self.line_edit_can_use.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.line_edit_can_sell = QLineEdit("0")
        self.line_edit_can_sell.setReadOnly(True)
        self.line_edit_can_sell.setStyleSheet("background-color:rgb(240,240,240)")
        self.line_edit_can_sell.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spin_price = QDoubleSpinBox()
        self.spin_price.setDecimals(4)
        self.spin_price.setMinimum(0)
        self.spin_price.setMaximum(100000)
        self.spin_price.setStyleSheet("color:red") # 初始红色
        self.spin_price.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spin_volume = QSpinBox()
        self.spin_volume.setMinimum(0)
        self.spin_volume.setMaximum(1000000)
        self.spin_volume.setSingleStep(100)
        self.spin_volume.setStyleSheet("color:red") # 初始红色
        self.spin_volume.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.grid_layout_essential = QGridLayout()
        self.grid_layout_essential.setContentsMargins(-1, -1, -1, -1)
        self.grid_layout_essential.addWidget(self.label_exchange,  0, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_symbol,    1, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_name,      2, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_entr_type, 3, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_can_use,   4, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_can_sell,  5, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_price,     6, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_volume,    7, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.combo_exchange,     0, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.line_edit_symbol,   1, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.line_edit_name,     2, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.combo_entr_type,    3, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.line_edit_can_use,  4, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.line_edit_can_sell, 5, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.spin_price,         6, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.spin_volume,        7, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.line_edit_tips_exchange, 1, 2, 1, 2)
        self.grid_layout_essential.addWidget(self.label_can_use_unit,      4, 2, 1, 1)
        self.grid_layout_essential.addWidget(self.label_can_sell_unit,     5, 2, 1, 1)
        self.grid_layout_essential.addWidget(self.label_price_unit,        6, 2, 1, 1)
        self.grid_layout_essential.addWidget(self.label_volume_unit,       7, 2, 1, 1)
        self.grid_layout_essential.addWidget(self.line_edit_tips_min_price_chg, 6, 3, 1, 1)
        self.grid_layout_essential.addWidget(self.line_edit_tips_trade_unit,    7, 3, 1, 1)
        
        self.radio_button_buy = QRadioButton("买 入")
        self.radio_button_buy.setStyleSheet("color:red")
        self.radio_button_buy.setFont(QFont("SimSun", 9))
        self.radio_button_buy.setChecked(True)
        self.radio_button_buy.setFixedWidth(70)
        self.radio_button_sell = QRadioButton("卖 出")
        self.radio_button_sell.setStyleSheet("color:green")
        self.radio_button_sell.setFont(QFont("SimSun", 9))
        self.radio_button_sell.setFixedWidth(70)
        self.button_place_order = QPushButton("买 入") # 初始买入
        self.button_place_order.setFont(QFont("SimSun", 9))
        self.button_place_order.setStyleSheet("font:bold;color:red") # 初始红色
        self.button_place_order.setFixedWidth(70)
        
        self.label_order_id = QLabel("撤单委托编号")
        self.label_order_id.setFixedWidth(70)
        self.label_order_id.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.line_edit_order_id = QLineEdit("")
        self.line_edit_order_id.setFixedWidth(70)
        self.line_edit_order_id.setStyleSheet("color:blue")
        self.line_edit_order_id.setFont(QFont("SimSun", 9))
        self.line_edit_order_id.setToolTip("注意选择正确的交易市场信息")
        self.button_cancel_order = QPushButton("撤 单")
        self.button_cancel_order.setFont(QFont("SimSun", 9))
        self.button_cancel_order.setStyleSheet("font:bold;color:blue")
        self.button_cancel_order.setFixedWidth(70)
        
        self.h_box_layout_order_buttons = QHBoxLayout()
        self.h_box_layout_order_buttons.setContentsMargins(-1, -1, -1, -1)
        self.h_box_layout_order_buttons.addStretch(1)
        self.h_box_layout_order_buttons.addWidget(self.radio_button_buy)
        self.h_box_layout_order_buttons.addStretch(1)
        self.h_box_layout_order_buttons.addWidget(self.radio_button_sell)
        self.h_box_layout_order_buttons.addStretch(1)
        self.h_box_layout_order_buttons.addWidget(self.button_place_order)
        self.h_box_layout_order_buttons.addStretch(1)
        
        self.h_box_layout_cancel_order = QHBoxLayout()
        self.h_box_layout_cancel_order.setContentsMargins(-1, -1, -1, -1) #
        self.h_box_layout_cancel_order.addStretch(1)
        self.h_box_layout_cancel_order.addWidget(self.label_order_id)
        self.h_box_layout_cancel_order.addStretch(1)
        self.h_box_layout_cancel_order.addWidget(self.line_edit_order_id)
        self.h_box_layout_cancel_order.addStretch(1)
        self.h_box_layout_cancel_order.addWidget(self.button_cancel_order)
        self.h_box_layout_cancel_order.addStretch(1)
        
        self.v_box_layout_order = QVBoxLayout()
        self.v_box_layout_order.setContentsMargins(-1, -1, -1, -1)
        self.v_box_layout_order.addLayout(self.grid_layout_essential)
        self.v_box_layout_order.addLayout(self.h_box_layout_order_buttons)
        self.v_box_layout_order.addLayout(self.h_box_layout_cancel_order)
        
        self.label_high_limit = QLabel("涨停")
        self.label_ask_5 = QLabel("卖五")
        self.label_ask_4 = QLabel("卖四")
        self.label_ask_3 = QLabel("卖三")
        self.label_ask_2 = QLabel("卖二")
        self.label_ask_1 = QLabel("卖一")
        self.label_last = QLabel("最新")
        self.label_last.setMinimumWidth(35)
        self.label_bid_1 = QLabel("买一")
        self.label_bid_2 = QLabel("买二")
        self.label_bid_3 = QLabel("买三")
        self.label_bid_4 = QLabel("买四")
        self.label_bid_5 = QLabel("买五")
        self.label_low_limit = QLabel("跌停")
        
        self.label_high_limit.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_5.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_4.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_3.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_last.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_3.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_4.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_5.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_low_limit.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.label_high_limit_price = QLabel("0.000")
        self.label_high_limit_price.setMinimumWidth(60)
        self.label_ask_price_5 = QLabel("0.000")
        self.label_ask_price_4 = QLabel("0.000")
        self.label_ask_price_3 = QLabel("0.000")
        self.label_ask_price_2 = QLabel("0.000")
        self.label_ask_price_1 = QLabel("0.000")
        self.label_ask_volume_5 = QLabel("0")
        self.label_ask_volume_4 = QLabel("0")
        self.label_ask_volume_3 = QLabel("0")
        self.label_ask_volume_2 = QLabel("0")
        self.label_ask_volume_1 = QLabel("0")
        self.label_last_price = QLabel("0.000")
        self.label_last_price.setMinimumWidth(60)
        self.label_last_up_down = QLabel("0.00%")
        self.label_last_up_down.setMinimumWidth(60)
        self.label_bid_price_1 = QLabel("0.000")
        self.label_bid_price_2 = QLabel("0.000")
        self.label_bid_price_3 = QLabel("0.000")
        self.label_bid_price_4 = QLabel("0.000")
        self.label_bid_price_5 = QLabel("0.000")
        self.label_bid_volume_1 = QLabel("0")
        self.label_bid_volume_2 = QLabel("0")
        self.label_bid_volume_3 = QLabel("0")
        self.label_bid_volume_4 = QLabel("0")
        self.label_bid_volume_5 = QLabel("0")
        self.label_low_limit_price = QLabel("0.000")
        self.label_low_limit_price.setMinimumWidth(60)
        
        self.label_high_limit_price.setPalette(self.color_red)
        self.label_ask_price_5.setPalette(self.color_green)
        self.label_ask_price_4.setPalette(self.color_green)
        self.label_ask_price_3.setPalette(self.color_green)
        self.label_ask_price_2.setPalette(self.color_green)
        self.label_ask_price_1.setPalette(self.color_green)
        self.label_ask_volume_5.setPalette(self.color_green)
        self.label_ask_volume_4.setPalette(self.color_green)
        self.label_ask_volume_3.setPalette(self.color_green)
        self.label_ask_volume_2.setPalette(self.color_green)
        self.label_ask_volume_1.setPalette(self.color_green)
        self.label_last_price.setPalette(self.color_black)
        self.label_last_up_down.setPalette(self.color_black)
        self.label_bid_price_1.setPalette(self.color_red)
        self.label_bid_price_2.setPalette(self.color_red)
        self.label_bid_price_3.setPalette(self.color_red)
        self.label_bid_price_4.setPalette(self.color_red)
        self.label_bid_price_5.setPalette(self.color_red)
        self.label_bid_volume_1.setPalette(self.color_red)
        self.label_bid_volume_2.setPalette(self.color_red)
        self.label_bid_volume_3.setPalette(self.color_red)
        self.label_bid_volume_4.setPalette(self.color_red)
        self.label_bid_volume_5.setPalette(self.color_red)
        self.label_low_limit_price.setPalette(self.color_green)
        
        self.label_high_limit_price.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_price_5.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_price_4.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_price_3.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_price_2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_price_1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_volume_5.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_volume_4.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_volume_3.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_volume_2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_ask_volume_1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_last_price.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_last_up_down.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_price_1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_price_2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_price_3.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_price_4.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_price_5.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_volume_1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_volume_2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_volume_3.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_volume_4.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_bid_volume_5.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_low_limit_price.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.grid_layout_quote = QGridLayout()
        self.grid_layout_quote.addWidget(self.label_high_limit, 0, 0) #
        self.grid_layout_quote.addWidget(self.label_ask_5,      1, 0)
        self.grid_layout_quote.addWidget(self.label_ask_4,      2, 0)
        self.grid_layout_quote.addWidget(self.label_ask_3,      3, 0)
        self.grid_layout_quote.addWidget(self.label_ask_2,      4, 0)
        self.grid_layout_quote.addWidget(self.label_ask_1,      5, 0)
        self.grid_layout_quote.addWidget(self.label_last,       6, 0) #
        self.grid_layout_quote.addWidget(self.label_bid_1,      7, 0)
        self.grid_layout_quote.addWidget(self.label_bid_2,      8, 0)
        self.grid_layout_quote.addWidget(self.label_bid_3,      9, 0)
        self.grid_layout_quote.addWidget(self.label_bid_4,     10, 0)
        self.grid_layout_quote.addWidget(self.label_bid_5,     11, 0)
        self.grid_layout_quote.addWidget(self.label_low_limit, 12, 0) #
        self.grid_layout_quote.addWidget(self.label_high_limit_price, 0, 1) #
        self.grid_layout_quote.addWidget(self.label_ask_price_5,      1, 1)
        self.grid_layout_quote.addWidget(self.label_ask_price_4,      2, 1)
        self.grid_layout_quote.addWidget(self.label_ask_price_3,      3, 1)
        self.grid_layout_quote.addWidget(self.label_ask_price_2,      4, 1)
        self.grid_layout_quote.addWidget(self.label_ask_price_1,      5, 1)
        self.grid_layout_quote.addWidget(self.label_last_price,       6, 1) #
        self.grid_layout_quote.addWidget(self.label_bid_price_1,      7, 1)
        self.grid_layout_quote.addWidget(self.label_bid_price_2,      8, 1)
        self.grid_layout_quote.addWidget(self.label_bid_price_3,      9, 1)
        self.grid_layout_quote.addWidget(self.label_bid_price_4,     10, 1)
        self.grid_layout_quote.addWidget(self.label_bid_price_5,     11, 1)
        self.grid_layout_quote.addWidget(self.label_low_limit_price, 12, 1) #
        self.grid_layout_quote.addWidget(self.label_ask_volume_5,  1, 2)
        self.grid_layout_quote.addWidget(self.label_ask_volume_4,  2, 2)
        self.grid_layout_quote.addWidget(self.label_ask_volume_3,  3, 2)
        self.grid_layout_quote.addWidget(self.label_ask_volume_2,  4, 2)
        self.grid_layout_quote.addWidget(self.label_ask_volume_1,  5, 2)
        self.grid_layout_quote.addWidget(self.label_last_up_down,  6, 2) #
        self.grid_layout_quote.addWidget(self.label_bid_volume_1,  7, 2)
        self.grid_layout_quote.addWidget(self.label_bid_volume_2,  8, 2)
        self.grid_layout_quote.addWidget(self.label_bid_volume_3,  9, 2)
        self.grid_layout_quote.addWidget(self.label_bid_volume_4, 10, 2)
        self.grid_layout_quote.addWidget(self.label_bid_volume_5, 11, 2)
        
        self.main_text_edit_bottom = QTextEdit(self)
        self.main_text_edit_bottom.setText("")
        self.main_text_edit_bottom.setFont(QFont("SimSun", 9))
        
        self.h_box_layout_1 = QHBoxLayout()
        self.h_box_layout_1.addLayout(self.v_box_layout_order)
        self.h_box_layout_1.addLayout(self.grid_layout_quote)
        
        self.h_box_layout_2 = QHBoxLayout()
        self.h_box_layout_2.setContentsMargins(-1, -1, -1, -1)
        self.h_box_layout_2.addWidget(self.main_text_edit_bottom)
        
        self.v_box_layout_mian = QVBoxLayout()
        self.v_box_layout_mian.setContentsMargins(-1, -1, -1, -1)
        self.v_box_layout_mian.addLayout(self.h_box_layout_1)
        self.v_box_layout_mian.addLayout(self.h_box_layout_2)
        
        self.setLayout(self.v_box_layout_mian)
        
        self.combo_exchange.activated[str].connect(self.OnChangeExchange)
        self.line_edit_symbol.editingFinished.connect(self.OnChangeSymbol)
        self.radio_button_buy.clicked.connect(self.OnChangeBuySell)
        self.radio_button_sell.clicked.connect(self.OnChangeBuySell)
        self.button_place_order.clicked.connect(self.OnButtonPlaceOrder)
        self.button_cancel_order.clicked.connect(self.OnButtonCancelOrder)

    def OnChangeExchange(self, str_exchange):
        self.symbol = ""
        self.exchange = ""
        self.line_edit_symbol.setText("")
        self.line_edit_name.setText("")
        self.OnChangeSymbol()

    def OnChangeSymbol(self):
        self.exchange = ""
        self.symbol = self.line_edit_symbol.text() #str(unicode(self.line_edit_symbol.text(), "gb2312"))
        
        self.spin_price.setValue(0)
        self.spin_volume.setValue(0)
        
        self.label_high_limit_price.setText("0.000")
        self.label_ask_price_5.setText("0.000")
        self.label_ask_price_4.setText("0.000")
        self.label_ask_price_3.setText("0.000")
        self.label_ask_price_2.setText("0.000")
        self.label_ask_price_1.setText("0.000")
        self.label_ask_volume_5.setText("0")
        self.label_ask_volume_4.setText("0")
        self.label_ask_volume_3.setText("0")
        self.label_ask_volume_2.setText("0")
        self.label_ask_volume_1.setText("0")
        self.label_last_price.setText("0.000")
        self.label_last_up_down.setText("0.00%")
        self.label_bid_price_1.setText("0.000")
        self.label_bid_price_2.setText("0.000")
        self.label_bid_price_3.setText("0.000")
        self.label_bid_price_4.setText("0.000")
        self.label_bid_price_5.setText("0.000")
        self.label_bid_volume_1.setText("0")
        self.label_bid_volume_2.setText("0")
        self.label_bid_volume_3.setText("0")
        self.label_bid_volume_4.setText("0")
        self.label_bid_volume_5.setText("0")
        self.label_low_limit_price.setText("0.000")
        
        dict_key = "HK" + self.symbol
        tips_exchange = ""
        if dict_key in self.security_name_dict.keys():
            tips_exchange = "HK"
            self.line_edit_name.setText(self.security_name_dict[dict_key])
        if dict_key in self.component_hsggt_hgt_dict.keys():
            if dict_key in self.component_hsggt_sgt_dict.keys():
                tips_exchange = "HGT SGT"
            else:
                tips_exchange = "HGT"
        elif dict_key in self.component_hsggt_sgt_dict.keys():
            tips_exchange = "SGT"
        self.line_edit_tips_exchange.setText(tips_exchange)
        tips_trade_unit = "0"
        if dict_key in self.trade_unit_dict.keys():
            tips_trade_unit = "%d" % self.trade_unit_dict[dict_key]
        self.line_edit_tips_trade_unit.setText(tips_trade_unit)
        tips_min_price_chg = "0.0"
        if dict_key in self.min_price_chg_dict.keys():
            tips_min_price_chg = "%.3f" % self.min_price_chg_dict[dict_key]
        self.line_edit_tips_min_price_chg.setText(tips_min_price_chg)

    def OnChangeBuySell(self):
        if self.radio_button_buy.isChecked():
            self.line_edit_symbol.setStyleSheet("color:red")
            self.line_edit_name.setStyleSheet("background-color:rgb(240,240,240);color:red")
            self.spin_price.setStyleSheet("color:red")
            self.spin_volume.setStyleSheet("color:red")
            self.button_place_order.setStyleSheet("font:bold;color:red")
            self.button_place_order.setText("买 入")
        if self.radio_button_sell.isChecked():
            self.line_edit_symbol.setStyleSheet("color:green")
            self.line_edit_name.setStyleSheet("background-color:rgb(240,240,240);color:green")
            self.spin_price.setStyleSheet("color:green")
            self.spin_volume.setStyleSheet("color:green")
            self.button_place_order.setStyleSheet("font:bold;color:green")
            self.button_place_order.setText("卖 出")

    def OnUpdateQuote(self, data, price_round):
        try:
            self.exchange = data[3].decode() # 证券市场
            self.line_edit_name.setText(str(data[1].decode("gbk"))) # 证券名称 #QString.fromLocal8Bit(data[1].decode("gbk")) # 含中文
            #self.label_ask_price_5.setText(str(round(data[13][4], price_round)))
            #self.label_ask_price_4.setText(str(round(data[13][3], price_round)))
            #self.label_ask_price_3.setText(str(round(data[13][2], price_round)))
            #self.label_ask_price_2.setText(str(round(data[13][1], price_round)))
            self.label_ask_price_1.setText(str(round(data[13][0], price_round)))
            #self.label_ask_volume_5.setText(str(data[14][4]))
            #self.label_ask_volume_4.setText(str(data[14][3]))
            #self.label_ask_volume_3.setText(str(data[14][2]))
            #self.label_ask_volume_2.setText(str(data[14][1]))
            self.label_ask_volume_1.setText(str(data[14][0]))
            self.label_bid_price_1.setText(str(round(data[15][0], price_round)))
            #self.label_bid_price_2.setText(str(round(data[15][1], price_round)))
            #self.label_bid_price_3.setText(str(round(data[15][2], price_round)))
            #self.label_bid_price_4.setText(str(round(data[15][3], price_round)))
            #self.label_bid_price_5.setText(str(round(data[15][4], price_round)))
            self.label_bid_volume_1.setText(str(data[16][0]))
            #self.label_bid_volume_2.setText(str(data[16][1]))
            #self.label_bid_volume_3.setText(str(data[16][2]))
            #self.label_bid_volume_4.setText(str(data[16][3]))
            #self.label_bid_volume_5.setText(str(data[16][4]))
            self.label_high_limit_price.setText(str(round(data[17], price_round))) # 涨停价
            self.label_low_limit_price.setText(str(round(data[18], price_round))) # 跌停价
            self.label_last_price.setText(str(round(data[5], price_round))) # 最新价
            if data[10] > 0.0: # 昨收价
                f_last_up_down = (data[5] / data[10]) - 1.0
                self.label_last_up_down.setText(("%.2f%%" % (f_last_up_down * 100.0)))
                if f_last_up_down > 0.0:
                    self.label_last_up_down.setPalette(self.color_red)
                elif f_last_up_down < 0.0:
                    self.label_last_up_down.setPalette(self.color_green)
                else:
                    self.label_last_up_down.setPalette(self.color_black)
            else:
                self.label_last_up_down.setText("0.00%")
        except Exception as e:
            self.log_text = "%s：函数 OnUpdateQuote 异常！%s" % (self.strategy, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "M")

    def OnButtonPlaceOrder(self):
        if self.trader != None:
            if self.trader.IsTraderReady() == False:
                self.logger.SendMessage("E", 4, self.log_cate, "交易服务尚未开启！", "M")
            else:
                if self.line_edit_symbol.text() == "":
                    QMessageBox.warning(self, "提示", "证券代码为空！", QMessageBox.Ok)
                    return
                str_symbol = self.line_edit_symbol.text() #str(unicode(self.line_edit_symbol.text(), "gb2312"))
                str_exchange = ""
                if self.combo_exchange.currentText() == define.DEF_EXCHANGE_STOCK_HGT:
                    str_exchange = "SH"
                elif self.combo_exchange.currentText() == define.DEF_EXCHANGE_STOCK_SGT:
                    str_exchange = "SZ"
                f_price = self.spin_price.value()
                n_amount = self.spin_volume.value()
                n_entr_type = 0
                if self.combo_entr_type.currentText() == define.DEF_PRICE_TYPE_STOCK_HK_AUCTION_LIMIT:
                    n_entr_type = 1
                elif self.combo_entr_type.currentText() == define.DEF_PRICE_TYPE_STOCK_HK_BOOST_LIMIT:
                    n_entr_type = 2
                elif self.combo_entr_type.currentText() == define.DEF_PRICE_TYPE_STOCK_HK_ODDMENT:
                    n_entr_type = 3
                n_exch_side = 0
                if self.radio_button_buy.isChecked():
                    n_exch_side = 1
                elif self.radio_button_sell.isChecked():
                    n_exch_side = 2
                trade_unit = int(self.line_edit_tips_trade_unit.text())
                min_price_chg = float(self.line_edit_tips_min_price_chg.text())
                if trade_unit <= 0:
                    QMessageBox.warning(self, "提示", "没有 买卖单位 信息！", QMessageBox.Ok)
                    return
                else: # trade_unit > 0
                    if n_amount < trade_unit:
                        QMessageBox.warning(self, "提示", "委托数量 < 买卖单位 %d！" % trade_unit, QMessageBox.Ok)
                        return
                    if n_entr_type == 1 or n_entr_type == 2: # 竞价限价、增强限价
                        if n_amount % trade_unit != 0:
                            QMessageBox.warning(self, "提示", "委托数量不为 %d 的整数倍！" % trade_unit, QMessageBox.Ok)
                            return
                if min_price_chg <= 0.0:
                    QMessageBox.warning(self, "提示", "没有 最小变动价格 信息！", QMessageBox.Ok)
                    return
                else: # min_price_chg > 0.0
                    if f_price < min_price_chg:
                        QMessageBox.warning(self, "提示", "委托价格 < 最小变动价格 %.3f！" % min_price_chg, QMessageBox.Ok)
                        return
                    if (f_price * 1000) % (min_price_chg * 1000) != 0: # min_price_chg 最小 0.001
                        QMessageBox.warning(self, "提示", "委托价格不为 %.3f 的整数倍！" % min_price_chg, QMessageBox.Ok)
                        return
                order = self.trader.Order(symbol = str_symbol, exchange = "HK", price = f_price, amount = n_amount, entr_type = n_entr_type, exch_side = n_exch_side)
                task_place = self.trader.PlaceOrderHK(order, str_exchange, self.strategy) # HK
                QMessageBox.information(self, "提示", "委托下单提交完成。", QMessageBox.Ok)
        else:
            self.logger.SendMessage("E", 4, self.log_cate, "交易服务尚未获取！", "M")

    def OnButtonCancelOrder(self):
        if self.trader != None:
            if self.trader.IsTraderReady() == False:
                self.logger.SendMessage("E", 4, self.log_cate, "交易服务尚未开启！", "M")
            else:
                if self.line_edit_order_id.text() == "":
                    QMessageBox.warning(self, "提示", "撤单委托编号为空！", QMessageBox.Ok)
                    return
                str_exchange = "" # 注意会取 self.combo_exchange 的值
                if self.combo_exchange.currentText() == define.DEF_EXCHANGE_STOCK_HGT:
                    str_exchange = "SH"
                elif self.combo_exchange.currentText() == define.DEF_EXCHANGE_STOCK_SGT:
                    str_exchange = "SZ"
                order = self.trader.Order()
                order.exchange = "HK" #
                order.order_id = int(self.line_edit_order_id.text()) # int
                task_cancel = self.trader.CancelOrderHK(order, str_exchange, self.strategy) # HK
                QMessageBox.information(self, "提示", "委托撤单提交完成。", QMessageBox.Ok)
        else:
            self.logger.SendMessage("E", 4, self.log_cate, "交易服务尚未获取！", "M")

####################################################################################################

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    panel = Panel(strategy = "Strategy_Trader_STK_APE_HK")
    panel.show()
    sys.exit(app.exec_())
