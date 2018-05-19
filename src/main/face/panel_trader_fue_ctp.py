
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

from PyQt5.QtGui import QColor, QFont, QPalette
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QApplication, QCheckBox, QComboBox, QDialog, QDoubleSpinBox, QGroupBox, QLabel, QLineEdit
from PyQt5.QtWidgets import QMessageBox, QPushButton, QRadioButton, QSpinBox, QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout

import define
import logger
import center
import trader

class Panel(QDialog):
    def __init__(self, **kwargs):
        super(Panel, self).__init__()
        self.strategy = kwargs.get("strategy", "")
        self.version_info = "V0.1.0-Beta Build 20180422"
        self.log_text = ""
        self.log_cate = "Panel_Trader_FUE_CTP"
        self.logger = logger.Logger()
        
        self.InitUserInterface()
        
        self.contract = ""
        self.exchange = ""
        self.trader = None # 策略中赋值
        self.subscribe = False # 行情订阅标志
        self.center = center.Center()
        
        self.quote_data = None
        self.price_round_future = 2 # 小数位数

    def OnWorking(self): # 供具体策略继承调用，在 运行 前执行一些操作
        if self.subscribe == False:
            self.center.RegQuoteSub(self.strategy, self.OnQuoteFuture, "future_np")
            self.subscribe = True
        self.trader = trader.Trader().GetTrader("sqqh")
        if self.trader == None:
            self.logger.SendMessage("E", 4, self.log_cate, "获取标识为 sqqh 的交易服务失败！", "M")

    def OnSuspend(self): # 供具体策略继承调用，在 暂停 前执行一些操作
        pass

    def OnContinue(self): # 供具体策略继承调用，在 继续 前执行一些操作
        pass

    def OnTerminal(self): # 供具体策略继承调用，在 停止 前执行一些操作
        if self.subscribe == True:
            self.center.DelQuoteSub(self.strategy, "future_np")
            self.subscribe = False

    def event(self, event):
        if event.type() == define.DEF_EVENT_TRADER_FUE_CTP_UPDATE_QUOTE:
            if self.quote_data != None:
                self.OnUpdateQuote(self.quote_data, self.price_round_future)
        return QDialog.event(self, event)

    def OnTraderEvent(self, trader, ret_func, task_item): # 交易模块事件通知，供具体策略继承调用
        if ret_func == define.trade_placeorder_f_func:
            self.log_text = "%s：%s %d：%s" % (self.strategy, trader, ret_func, task_item.order.order_id)
            self.logger.SendMessage("H", 2, self.log_cate, self.log_text, "T")

    def OnQuoteFuture(self, msg): # 行情触发
        try:
            str_code = str(msg.data[0])
            if str_code == self.contract:
                self.quote_data = msg
                QApplication.postEvent(self, QEvent(define.DEF_EVENT_TRADER_FUE_CTP_UPDATE_QUOTE)) # postEvent异步，sendEvent同步
        except Exception as e:
            self.log_text = "%s：函数 OnQuoteFuture 异常！%s" % (self.strategy, e)
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "M")

    def InitUserInterface(self):
        self.color_red = QPalette()
        self.color_red.setColor(QPalette.WindowText, Qt.red)
        self.color_green = QPalette()
        self.color_green.setColor(QPalette.WindowText, QColor(0, 128, 0))
        self.color_black = QPalette()
        self.color_black.setColor(QPalette.WindowText, Qt.black)
        
        self.list_exchange = [define.DEF_EXCHANGE_FUTURE_CFFE, define.DEF_EXCHANGE_FUTURE_SHFE, define.DEF_EXCHANGE_FUTURE_CZCE, define.DEF_EXCHANGE_FUTURE_DLCE]
        self.list_entr_type = [define.DEF_PRICE_TYPE_FUTURE_LIMIT, define.DEF_PRICE_TYPE_FUTURE_MARKET]
        
        self.setWindowTitle("手动交易-期货-CTP %s" % self.version_info)
        self.resize(380, 300)
        self.setFont(QFont("SimSun", 9))
        
        self.label_exchange = QLabel("交易市场")
        self.label_exchange.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_contract = QLabel("合约代码")
        self.label_contract.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_entr_type = QLabel("委托方式")
        self.label_entr_type.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_can_use = QLabel("可用金额")
        self.label_can_use.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_can_trade = QLabel("可用数量")
        self.label_can_trade.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_price = QLabel("委托价格")
        self.label_price.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_volume = QLabel("委托数量")
        self.label_volume.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.label_can_use_unit = QLabel("元")
        self.label_can_use_unit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_can_sell_unit_l = QLabel("手")
        self.label_can_sell_unit_l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_can_sell_unit_s = QLabel("手")
        self.label_can_sell_unit_s.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_price_unit = QLabel("元")
        self.label_price_unit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_volume_unit = QLabel("手")
        self.label_volume_unit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.combo_exchange = QComboBox()
        self.combo_exchange.addItems(self.list_exchange)
        self.line_edit_contract = QLineEdit("")
        self.line_edit_contract.setStyleSheet("color:red") # 初始红色
        self.line_edit_contract.setFont(QFont("SimSun", 9))
        self.combo_entr_type = QComboBox()
        self.combo_entr_type.addItems(self.list_entr_type)
        self.line_edit_can_use = QLineEdit("0.00")
        self.line_edit_can_use.setReadOnly(True)
        self.line_edit_can_use.setStyleSheet("background-color:rgb(240,240,240)")
        self.line_edit_can_use.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.line_edit_can_trade_l = QLineEdit("0")
        self.line_edit_can_trade_l.setReadOnly(True)
        self.line_edit_can_trade_l.setStyleSheet("background-color:rgb(240,240,240);color:red")
        self.line_edit_can_trade_l.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.line_edit_can_trade_s = QLineEdit("0")
        self.line_edit_can_trade_s.setReadOnly(True)
        self.line_edit_can_trade_s.setStyleSheet("background-color:rgb(240,240,240);color:green")
        self.line_edit_can_trade_s.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spin_price = QDoubleSpinBox()
        self.spin_price.setDecimals(3)
        self.spin_price.setMinimum(0)
        self.spin_price.setMaximum(500000)
        self.spin_price.setStyleSheet("color:red") # 初始红色
        self.spin_price.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spin_volume = QSpinBox()
        self.spin_volume.setMinimum(0)
        self.spin_volume.setMaximum(10000)
        self.spin_volume.setSingleStep(1)
        self.spin_volume.setStyleSheet("color:red") # 初始红色
        self.spin_volume.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.grid_layout_essential = QGridLayout()
        self.grid_layout_essential.setContentsMargins(-1, -1, -1, -1)
        self.grid_layout_essential.addWidget(self.label_exchange,  0, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_contract,  1, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_entr_type, 2, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_can_use,   3, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_can_trade, 4, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_price,     5, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.label_volume,    6, 0, 1, 1)
        self.grid_layout_essential.addWidget(self.combo_exchange,        0, 1, 1, 3)
        self.grid_layout_essential.addWidget(self.line_edit_contract,    1, 1, 1, 3)
        self.grid_layout_essential.addWidget(self.combo_entr_type,       2, 1, 1, 3)
        self.grid_layout_essential.addWidget(self.line_edit_can_use,     3, 1, 1, 3)
        self.grid_layout_essential.addWidget(self.line_edit_can_trade_l, 4, 1, 1, 1)
        self.grid_layout_essential.addWidget(self.spin_price,            5, 1, 1, 3)
        self.grid_layout_essential.addWidget(self.spin_volume,           6, 1, 1, 3)
        self.grid_layout_essential.addWidget(self.label_can_sell_unit_l, 4, 2, 1, 1)
        self.grid_layout_essential.addWidget(self.line_edit_can_trade_s, 4, 3, 1, 1)
        self.grid_layout_essential.addWidget(self.label_can_use_unit,    3, 4, 1, 1)
        self.grid_layout_essential.addWidget(self.label_can_sell_unit_s, 4, 4, 1, 1)
        self.grid_layout_essential.addWidget(self.label_price_unit,      5, 4, 1, 1)
        self.grid_layout_essential.addWidget(self.label_volume_unit,     6, 4, 1, 1)
        
        self.radio_button_buy_open = QRadioButton("买入开仓")
        self.radio_button_buy_open.setFixedWidth(70)
        self.radio_button_buy_open.setStyleSheet("color:red")
        self.radio_button_buy_open.setFont(QFont("SimSun", 9))
        self.radio_button_buy_open.setChecked(True)
        self.radio_button_sell_open = QRadioButton("卖出开仓")
        self.radio_button_sell_open.setFixedWidth(70)
        self.radio_button_sell_open.setStyleSheet("color:purple")
        self.radio_button_sell_open.setFont(QFont("SimSun", 9))
        self.radio_button_buy_close = QRadioButton("买入平仓")
        self.radio_button_buy_close.setFixedWidth(70)
        self.radio_button_buy_close.setStyleSheet("color:blue")
        self.radio_button_buy_close.setFont(QFont("SimSun", 9))
        self.radio_button_sell_close = QRadioButton("卖出平仓")
        self.radio_button_sell_close.setFixedWidth(70)
        self.radio_button_sell_close.setStyleSheet("color:green")
        self.radio_button_sell_close.setFont(QFont("SimSun", 9))
        self.check_box_close_today = QCheckBox("平今")
        self.check_box_close_today.setFont(QFont("SimSun", 9))
        self.check_box_close_today.setChecked(False)
        self.check_box_close_today.setEnabled(False)
        self.check_box_close_today.setFixedWidth(70)
        self.button_place_order = QPushButton("下 单")
        self.button_place_order.setFont(QFont("SimSun", 9))
        self.button_place_order.setStyleSheet("font:bold;color:red") # 初始红色
        self.button_place_order.setFixedWidth(70)
        self.radio_button_tou_ji = QRadioButton("投机")
        self.radio_button_tou_ji.setFont(QFont("SimSun", 9))
        self.radio_button_tou_ji.setChecked(True)
        self.radio_button_tou_ji.setFixedWidth(70)
        self.radio_button_tao_bao = QRadioButton("套保")
        self.radio_button_tao_bao.setFont(QFont("SimSun", 9))
        self.radio_button_tao_bao.setChecked(False)
        self.radio_button_tao_bao.setEnabled(False)
        self.radio_button_tao_bao.setFixedWidth(70)
        self.radio_button_tao_li = QRadioButton("套利")
        self.radio_button_tao_li.setFont(QFont("SimSun", 9))
        self.radio_button_tao_li.setChecked(False)
        self.radio_button_tao_li.setEnabled(False)
        self.radio_button_tao_li.setFixedWidth(70)
        
        self.label_order_id = QLabel("撤单委托编号")
        self.label_order_id.setFixedWidth(70)
        self.label_order_id.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.line_edit_order_id = QLineEdit("")
        self.line_edit_order_id.setFixedWidth(70)
        self.line_edit_order_id.setStyleSheet("color:blue")
        self.line_edit_order_id.setFont(QFont("SimSun", 9))
        self.button_cancel_order = QPushButton("撤 单")
        self.button_cancel_order.setFont(QFont("SimSun", 9))
        self.button_cancel_order.setStyleSheet("font:bold;color:blue")
        self.button_cancel_order.setFixedWidth(70)
        
        self.h_box_layout_trade_buttons_1 = QHBoxLayout()
        self.h_box_layout_trade_buttons_1.setContentsMargins(-1, -1, -1, -1)
        self.h_box_layout_trade_buttons_1.addStretch(1)
        self.h_box_layout_trade_buttons_1.addWidget(self.radio_button_buy_open)
        self.h_box_layout_trade_buttons_1.addStretch(1)
        self.h_box_layout_trade_buttons_1.addWidget(self.radio_button_sell_open)
        self.h_box_layout_trade_buttons_1.addStretch(1)
        self.h_box_layout_trade_buttons_1.addWidget(self.check_box_close_today)
        self.h_box_layout_trade_buttons_1.addStretch(1)
        
        self.h_box_layout_trade_buttons_2 = QHBoxLayout()
        self.h_box_layout_trade_buttons_2.setContentsMargins(-1, -1, -1, -1)
        self.h_box_layout_trade_buttons_2.addStretch(1)
        self.h_box_layout_trade_buttons_2.addWidget(self.radio_button_buy_close)
        self.h_box_layout_trade_buttons_2.addStretch(1)
        self.h_box_layout_trade_buttons_2.addWidget(self.radio_button_sell_close)
        self.h_box_layout_trade_buttons_2.addStretch(1)
        self.h_box_layout_trade_buttons_2.addWidget(self.button_place_order)
        self.h_box_layout_trade_buttons_2.addStretch(1)
        
        self.v_box_layout_trade_buttons = QVBoxLayout()
        self.v_box_layout_trade_buttons.setContentsMargins(0, 2, 0, 2) #
        self.v_box_layout_trade_buttons.addLayout(self.h_box_layout_trade_buttons_1)
        self.v_box_layout_trade_buttons.addLayout(self.h_box_layout_trade_buttons_2)
        
        self.h_box_layout_trade_buttons_3 = QHBoxLayout()
        self.h_box_layout_trade_buttons_3.setContentsMargins(0, 0, 0, 0) #
        self.h_box_layout_trade_buttons_3.addStretch(1)
        self.h_box_layout_trade_buttons_3.addWidget(self.radio_button_tou_ji)
        self.h_box_layout_trade_buttons_3.addStretch(1)
        self.h_box_layout_trade_buttons_3.addWidget(self.radio_button_tao_bao)
        self.h_box_layout_trade_buttons_3.addStretch(1)
        self.h_box_layout_trade_buttons_3.addWidget(self.radio_button_tao_li)
        self.h_box_layout_trade_buttons_3.addStretch(1)
        
        self.group_box_trade_buttons_1 = QGroupBox()
        self.group_box_trade_buttons_1.setContentsMargins(-1, -1, -1, -1)
        self.group_box_trade_buttons_1.setStyleSheet("QGroupBox{border:none}")
        self.group_box_trade_buttons_1.setLayout(self.v_box_layout_trade_buttons)
        
        self.group_box_trade_buttons_2 = QGroupBox()
        self.group_box_trade_buttons_2.setContentsMargins(-1, -1, -1, -1)
        self.group_box_trade_buttons_2.setStyleSheet("QGroupBox{border:none}")
        self.group_box_trade_buttons_2.setLayout(self.h_box_layout_trade_buttons_3)
        
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
        self.v_box_layout_order.addWidget(self.group_box_trade_buttons_1)
        #self.v_box_layout_order.addWidget(self.group_box_trade_buttons_2) # 目前写死投机
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
        
        self.label_high_limit_price = QLabel("0.00")
        self.label_high_limit_price.setMinimumWidth(60)
        self.label_ask_price_5 = QLabel("0.00")
        self.label_ask_price_4 = QLabel("0.00")
        self.label_ask_price_3 = QLabel("0.00")
        self.label_ask_price_2 = QLabel("0.00")
        self.label_ask_price_1 = QLabel("0.00")
        self.label_ask_volume_5 = QLabel("0")
        self.label_ask_volume_4 = QLabel("0")
        self.label_ask_volume_3 = QLabel("0")
        self.label_ask_volume_2 = QLabel("0")
        self.label_ask_volume_1 = QLabel("0")
        self.label_last_price = QLabel("0.00")
        self.label_last_price.setMinimumWidth(60)
        self.label_last_up_down = QLabel("0.00%")
        self.label_last_up_down.setMinimumWidth(60)
        self.label_bid_price_1 = QLabel("0.00")
        self.label_bid_price_2 = QLabel("0.00")
        self.label_bid_price_3 = QLabel("0.00")
        self.label_bid_price_4 = QLabel("0.00")
        self.label_bid_price_5 = QLabel("0.00")
        self.label_bid_volume_1 = QLabel("0")
        self.label_bid_volume_2 = QLabel("0")
        self.label_bid_volume_3 = QLabel("0")
        self.label_bid_volume_4 = QLabel("0")
        self.label_bid_volume_5 = QLabel("0")
        self.label_low_limit_price = QLabel("0.00")
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
        
        self.h_box_layout_3 = QHBoxLayout()
        self.h_box_layout_3.setContentsMargins(-1, -1, -1, -1)
        self.h_box_layout_3.addWidget(self.main_text_edit_bottom)
        
        self.v_box_layout_mian = QVBoxLayout()
        self.v_box_layout_mian.setContentsMargins(-1, -1, -1, -1)
        self.v_box_layout_mian.addLayout(self.h_box_layout_1)
        self.v_box_layout_mian.addLayout(self.h_box_layout_3)
        
        self.setLayout(self.v_box_layout_mian)
        
        self.combo_exchange.activated[str].connect(self.OnChangeExchange)
        self.line_edit_contract.editingFinished.connect(self.OnChangeSymbol)
        self.radio_button_buy_open.clicked.connect(self.OnChangeTradeType)
        self.radio_button_sell_open.clicked.connect(self.OnChangeTradeType)
        self.radio_button_buy_close.clicked.connect(self.OnChangeTradeType)
        self.radio_button_sell_close.clicked.connect(self.OnChangeTradeType)
        self.button_place_order.clicked.connect(self.OnButtonPlaceOrder)
        self.button_cancel_order.clicked.connect(self.OnButtonCancelOrder)

    def OnChangeExchange(self, str_exchange):
        self.contract = ""
        self.exchange = ""
        self.line_edit_contract.setText("")
        self.OnChangeSymbol()

    def OnChangeSymbol(self):
        self.exchange = ""
        self.contract = self.line_edit_contract.text() #str(unicode(self.line_edit_contract.text(), "gb2312"))
        
        self.spin_price.setValue(0)
        self.spin_volume.setValue(0)
        
        self.label_high_limit_price.setText("0.00")
        self.label_ask_price_5.setText("0.00")
        self.label_ask_price_4.setText("0.00")
        self.label_ask_price_3.setText("0.00")
        self.label_ask_price_2.setText("0.00")
        self.label_ask_price_1.setText("0.00")
        self.label_ask_volume_5.setText("0")
        self.label_ask_volume_4.setText("0")
        self.label_ask_volume_3.setText("0")
        self.label_ask_volume_2.setText("0")
        self.label_ask_volume_1.setText("0")
        self.label_last_price.setText("0.00")
        self.label_last_up_down.setText("0.00%")
        self.label_bid_price_1.setText("0.00")
        self.label_bid_price_2.setText("0.00")
        self.label_bid_price_3.setText("0.00")
        self.label_bid_price_4.setText("0.00")
        self.label_bid_price_5.setText("0.00")
        self.label_bid_volume_1.setText("0")
        self.label_bid_volume_2.setText("0")
        self.label_bid_volume_3.setText("0")
        self.label_bid_volume_4.setText("0")
        self.label_bid_volume_5.setText("0")
        self.label_low_limit_price.setText("0.00")

    def OnChangeTradeType(self):
        if self.radio_button_buy_open.isChecked():
            self.line_edit_contract.setStyleSheet("color:red")
            self.spin_price.setStyleSheet("color:red")
            self.spin_volume.setStyleSheet("color:red")
            self.button_place_order.setStyleSheet("font:bold;color:red")
            self.check_box_close_today.setEnabled(False)
        if self.radio_button_sell_open.isChecked():
            self.line_edit_contract.setStyleSheet("color:purple")
            self.spin_price.setStyleSheet("color:purple")
            self.spin_volume.setStyleSheet("color:purple")
            self.button_place_order.setStyleSheet("font:bold;color:purple")
            self.check_box_close_today.setEnabled(False)
        if self.radio_button_buy_close.isChecked():
            self.line_edit_contract.setStyleSheet("color:blue")
            self.spin_price.setStyleSheet("color:blue")
            self.spin_volume.setStyleSheet("color:blue")
            self.button_place_order.setStyleSheet("font:bold;color:blue")
            self.check_box_close_today.setEnabled(True)
        if self.radio_button_sell_close.isChecked():
            self.line_edit_contract.setStyleSheet("color:green")
            self.spin_price.setStyleSheet("color:green")
            self.spin_volume.setStyleSheet("color:green")
            self.button_place_order.setStyleSheet("font:bold;color:green")
            self.check_box_close_today.setEnabled(True)

    def OnUpdateQuote(self, msg, price_round):
        self.exchange = msg[3] # 证券市场
        self.label_ask_price_5.setText(round(str(msg[13][4]), price_round))
        self.label_ask_price_4.setText(round(str(msg[13][3]), price_round))
        self.label_ask_price_3.setText(round(str(msg[13][2]), price_round))
        self.label_ask_price_2.setText(round(str(msg[13][1]), price_round))
        self.label_ask_price_1.setText(round(str(msg[13][0]), price_round))
        self.label_ask_volume_5.setText(str(msg[14][4]))
        self.label_ask_volume_4.setText(str(msg[14][3]))
        self.label_ask_volume_3.setText(str(msg[14][2]))
        self.label_ask_volume_2.setText(str(msg[14][1]))
        self.label_ask_volume_1.setText(str(msg[14][0]))
        self.label_bid_price_1.setText(round(str(msg[15][0]), price_round))
        self.label_bid_price_2.setText(round(str(msg[15][1]), price_round))
        self.label_bid_price_3.setText(round(str(msg[15][2]), price_round))
        self.label_bid_price_4.setText(round(str(msg[15][3]), price_round))
        self.label_bid_price_5.setText(round(str(msg[15][4]), price_round))
        self.label_bid_volume_1.setText(str(msg[16][0]))
        self.label_bid_volume_2.setText(str(msg[16][1]))
        self.label_bid_volume_3.setText(str(msg[16][2]))
        self.label_bid_volume_4.setText(str(msg[16][3]))
        self.label_bid_volume_5.setText(str(msg[16][4]))
        self.label_high_limit_price.setText(round(str(msg[17]), price_round)) # 涨停价
        self.label_low_limit_price.setText(round(str(msg[18]), price_round)) # 跌停价
        self.label_last_price.setText(round(str(msg[5]), price_round)) # 最新价
        if msg[20] > 0.0: # 昨日结算价
            f_last_up_down = (msg[5] / msg[20]) - 1.0
            self.label_last_up_down.setText(("%.2f%%" % (f_last_up_down * 100.0)))
            if f_last_up_down > 0.0:
                self.label_last_up_down.setPalette(self.color_red)
            elif f_last_up_down < 0.0:
                self.label_last_up_down.setPalette(self.color_green)
            else:
                self.label_last_up_down.setPalette(self.color_black)
        else:
            self.label_last_up_down.setText("0.00%")

    def OnButtonPlaceOrder(self):
        if self.trader != None:
            if self.trader.IsTraderReady() == False:
                self.logger.SendMessage("E", 4, self.log_cate, "交易服务尚未开启！", "M")
                return
            else:
                if self.line_edit_contract.text() == "":
                    QMessageBox.warning(self, "提示", "合约代码为空！", QMessageBox.Ok)
                    return
                str_contract = self.line_edit_contract.text() #str(unicode(self.line_edit_contract.text(), "gb2312"))
                str_exchange = ""
                if self.comboExchange.currentText() == define.DEF_EXCHANGE_FUTURE_CFFE:
                    str_exchange = "CFFE"
                elif self.comboExchange.currentText() == define.DEF_EXCHANGE_FUTURE_SHFE:
                    str_exchange = "SHFE"
                elif self.comboExchange.currentText() == define.DEF_EXCHANGE_FUTURE_CZCE:
                    str_exchange = "CZCE"
                elif self.comboExchange.currentText() == define.DEF_EXCHANGE_FUTURE_DLCE:
                    str_exchange = "DLCE"
                f_price = self.spin_price.value()
                n_amount = self.spin_volume.value()
                n_entr_type = 0
                if self.combo_entr_type.currentText() == define.DEF_PRICE_TYPE_FUTURE_LIMIT:
                    n_entr_type = 1
                elif self.combo_entr_type.currentText() == define.DEF_PRICE_TYPE_FUTURE_MARKET:
                    n_entr_type = 2
                n_exch_side = 0
                n_offset = 0
                if self.radio_button_buy_open.isChecked():
                    n_exch_side = 1
                    n_offset = 1
                elif self.radio_button_sell_open.isChecked():
                    n_exch_side = 2
                    n_offset = 1
                elif self.radio_button_buy_close.isChecked():
                    n_exch_side = 1
                    n_offset = 2
                    if self.check_box_close_today.isChecked():
                        n_offset = 4
                elif self.radio_button_sell_close.isChecked():
                    n_exch_side = 2
                    n_offset = 2
                    if self.check_box_close_today.isChecked():
                        n_offset = 4
                n_hedge = 1 # 写死
                order = self.trader.Order(instrument = str_contract, exchange = str_exchange, price = f_price, amount = n_amount, entr_type = n_entr_type, exch_side = n_exch_side, offset = n_offset, hedge = n_hedge)
                task_place = self.trader.PlaceOrder(order, self.strategy)
                QMessageBox.information(self, "提示", "委托下单提交完成。", QMessageBox.Ok)
                return
        else:
            self.logger.SendMessage("E", 4, self.log_cate, "交易服务尚未获取！", "M")
            return

    def OnButtonCancelOrder(self):
        if self.trader != None:
            if self.trader.IsTraderReady() == False:
                self.logger.SendMessage("E", 4, self.log_cate, "交易服务尚未开启！", "M")
                return
            else:
                if self.line_edit_order_id.text() == "":
                    QMessageBox.warning(self, "提示", "撤单委托编号为空！", QMessageBox.Ok)
                    return
                order = self.trader.Order()
                order.order_id = self.line_edit_order_id.text() #str(unicode(self.line_edit_order_id.text(), "gb2312")) # string
                task_cancel = self.trader.CancelOrder(order, self.strategy)
                QMessageBox.information(self, "提示", "委托撤单提交完成。", QMessageBox.Ok)
                return
        else:
            self.logger.SendMessage("E", 4, self.log_cate, "交易服务尚未获取！", "M")
            return

####################################################################################################

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    panel = Panel("Strategy_Trader_FUE_CTP")
    panel.show()
    sys.exit(app.exec_())
