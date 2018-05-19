
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

import numpy

APP_TITLE_EN = "QuantX" # 英文名称
APP_TITLE_CN = "量 化 交 易 客 户 端" # 中文名称
APP_VERSION = "V0.1.0-Beta Build 20180517" # 版本信息
APP_DEVELOPER = "Developed by the X-Lab." # 开发者声明
APP_COMPANY = "X-Lab (Shanghai) Co., Ltd." # 公司声明
APP_COPYRIGHT = "Copyright 2018-2018 X-Lab All Rights Reserved." # 版权声明
APP_HOMEURL = "http://www.xlab.com" # 主页链接

TRAY_POP_START_TITLE = "QuantX"
TRAY_POP_TITLE_INFO = "系统信息："
TRAY_POP_TITLE_WARN = "系统警告："
TRAY_POP_TITLE_ERROR = "系统异常："

DEF_MAIN_WINDOW_H = 900
DEF_MAIN_WINDOW_W = 1600

DEF_TROY_OUNCE = 31.103477 # 金衡盎司，克

DEF_LOG_SHOW_TYPE_S = "S"
DEF_LOG_SHOW_TYPE_T = "T"
DEF_LOG_SHOW_TYPE_M = "M"
DEF_LOG_SHOW_TYPE_A = "A"
DEF_LOG_SHOW_TYPE_SPBSA = 5

USER_CTRL_LOAD = 0 # 已经加载
USER_CTRL_EXEC = 1 # 正常执行
USER_CTRL_WAIT = 2 # 等待执行
USER_CTRL_STOP = 3 # 终止执行
USER_CTRL_FAIL = 4 # 发生异常

CFG_FILE_PATH_MAIN = "../etcs/cfg_main.ini"
CFG_FILE_PATH_ANAL = "../etcs/cfg_anal.ini"
CFG_FILE_PATH_RISK = "../etcs/cfg_risk.ini"

TASK_STATUS_FAIL = -1 # 执行失败
TASK_STATUS_WAIT = 0 # 等待执行
TASK_STATUS_EXEC = 1 # 正在执行
TASK_STATUS_OVER = 2 # 执行完成

DEF_EXCHSIDE_NET = 0 # 净，只用于 LTS 持仓查询
DEF_EXCHSIDE_BUY = 1 # 买入
DEF_EXCHSIDE_SELL = 2 # 卖出
DEF_OFFSET_OPEN = 1 # 开仓
DEF_OFFSET_CLOSE = 2 # 平仓

DEF_EXCHANGE_STOCK_SH = "上交所"
DEF_EXCHANGE_STOCK_SZ = "深交所"
DEF_PRICE_TYPE_STOCK_LIMIT = "限价"
DEF_PRICE_TYPE_STOCK_MARKET = "市价"

DEF_EXCHANGE_FUTURE_CFFE = "中金所"
DEF_EXCHANGE_FUTURE_SHFE = "上期所"
DEF_EXCHANGE_FUTURE_CZCE = "郑商所"
DEF_EXCHANGE_FUTURE_DLCE = "大商所"
DEF_PRICE_TYPE_FUTURE_LIMIT = "限价"
DEF_PRICE_TYPE_FUTURE_MARKET = "市价"

DEF_TRADING_DAY_MARKET_SH_SZ = 83 # 沪深交易所

DEF_SECURITY_INFO_CATEGORY_0 = 0 # 未知
DEF_SECURITY_INFO_CATEGORY_1 = 1 # 沪A主板
DEF_SECURITY_INFO_CATEGORY_2 = 2 # 深A主板
DEF_SECURITY_INFO_CATEGORY_3 = 3 # 深A中小板
DEF_SECURITY_INFO_CATEGORY_4 = 4 # 深A创业板
DEF_SECURITY_INFO_CATEGORY_5 = 5 # 沪ETF基金
DEF_SECURITY_INFO_CATEGORY_6 = 6 # 深ETF基金
DEF_SECURITY_INFO_CATEGORY_7 = 7 # 沪LOF基金
DEF_SECURITY_INFO_CATEGORY_8 = 8 # 深LOF基金
DEF_SECURITY_INFO_CATEGORY_9 = 9 # 沪分级子基金
DEF_SECURITY_INFO_CATEGORY_10 = 10 # 深分级子基金
DEF_SECURITY_INFO_CATEGORY_11 = 11 # 沪封闭式基金
DEF_SECURITY_INFO_CATEGORY_12 = 12 # 深封闭式基金

DEF_SECURITY_INFO_SECTOR_MAIN = 1 # 主板
DEF_SECURITY_INFO_SECTOR_SMALL = 2 # 中小板
DEF_SECURITY_INFO_SECTOR_START = 3 # 创业板
DEF_SECURITY_INFO_SECTOR_UNKNOW = 0 # 未知板块

DEF_SECURITY_INFO_LIST_STATE_1 = 1 # 上市
DEF_SECURITY_INFO_LIST_STATE_2 = 2 # 暂停
DEF_SECURITY_INFO_LIST_STATE_3 = 3 # 终止
DEF_SECURITY_INFO_LIST_STATE_4 = 4 # 其他
DEF_SECURITY_INFO_LIST_STATE_5 = 5 # 交易
DEF_SECURITY_INFO_LIST_STATE_6 = 6 # 停牌
DEF_SECURITY_INFO_LIST_STATE_7 = 7 # 摘牌

DEF_SECURITY_INFO_ST_NON = 1 # 非ST股
DEF_SECURITY_INFO_ST_USE = 0 # 仅ST股

quote_subscibe_func = 100001 # 行情订阅
quote_unsubscibe_func = 100002 # 行情退订
quote_status_info_func = 100009 # 行情状态

stock_tdf_market_s_func = 910001 # TDF 个股快照
stock_tdf_market_i_func = 910002 # TDF 指数快照
stock_tdf_market_t_func = 910003 # TDF 逐笔成交
stock_ltb_market_s_func = 910006 # LTB 个股快照
stock_ltb_market_i_func = 910007 # LTB 指数快照
stock_ltb_market_t_func = 910008 # LTB 逐笔成交
stock_ltp_market_s_func = 910011 # LTP 个股快照
stock_ltp_market_i_func = 910012 # LTP 指数快照
stock_ltp_market_t_func = 910013 # LTP 逐笔成交
future_np_market_func = 920001 # 内盘 期货快照

trade_userlogin_s_func = 110001 # 股票用户登录
trade_userlogout_s_func = 110002 # 股票用户登出
trade_subscibe_s_func = 110003 # 股票消息订阅
trade_unsubscibe_s_func = 110004 # 股票消息退订
trade_placeorder_s_func = 120001 # 股票单个证券委托下单
trade_cancelorder_s_func = 120002 # 股票单个证券委托撤单
trade_placeorderbatch_s_func = 120003 # 股票批量证券委托下单
trade_cancelorderbatch_s_func = 120004 # 股票批量证券委托撤单
trade_querycapital_s_func = 130002 # 股票查询客户资金
trade_queryposition_s_func = 130004 # 股票查询客户持仓
trade_queryorder_s_func = 130005 # 股票查询客户当日委托
trade_querytrans_s_func = 130006 # 股票查询客户当日成交
trade_queryetfbase_s_func = 130008 # 股票查询ETF基本信息
trade_queryetfdetail_s_func = 130009 # 股票查询ETF成分股信息
trade_orderreply_s_func = 190001 # 股票报单回报
trade_transreply_s_func = 190002 # 股票成交回报
trade_cancelreply_s_func = 190003 # 股票撤单回报

order_status_s_before_place = 0 # 尚未申报
order_status_s_doing_place = 1 # 正在申报
order_status_s_wait_trans = 2 # 已报未成
order_status_s_error_place = 3 # 非法委托
order_status_s_capital_auth = 4 # 资金授权
order_status_s_part_trans = 5 # 部分成交
order_status_s_entire_trans = 6 # 全部成交
order_status_s_part_cancel = 7 # 部成部撤
order_status_s_entire_cancel = 8 # 全部撤单
order_status_s_error_cancel = 9 # 撤单未成
order_status_s_manual_place = 10 # 人工申报

trade_userlogin_f_func = 210001 # 期货用户登录
trade_userlogout_f_func = 210002 # 期货用户登出
trade_subscibe_f_func = 210003 # 期货消息订阅
trade_unsubscibe_f_func = 210004 # 期货消息退订
trade_placeorder_f_func = 220001 # 期货单个合约委托下单
trade_cancelorder_f_func = 220002 # 期货单个合约委托撤单
trade_placecombinorder_f_func = 220003 # 期货组合合约委托下单
trade_querycapital_f_func = 230002 # 期货查询客户资金
trade_queryposition_f_func = 230004 # 期货查询客户持仓
trade_queryorder_f_func = 230005 # 期货查询客户当日委托
trade_querytrans_f_func = 230006 # 期货查询客户当日成交
trade_queryinstrument_f_func = 230009 # 期货查询期货合约
trade_querypositiondetail_f_func = 230010 # 期货查询客户持仓明细
trade_orderreply_f_func = 290001 # 期货报单回报
trade_transreply_f_func = 290002 # 期货成交回报
trade_riskinform_f_func = 290009 # 期货风控通知

order_status_f_before_place = 0 # 尚未申报
order_status_f_doing_place = 1 # 正在申报
order_status_f_error_place = 2 # 非法委托
order_status_f_wait_trans = 3 # 已报未成
order_status_f_part_trans = 4 # 部分成交
order_status_f_entire_trans = 5 # 全部成交
order_status_f_wait_cancel = 6 # 等待撤单
order_status_f_part_cancel = 7 # 部成部撤
order_status_f_entire_cancel = 8 # 全部撤单
order_status_f_error_cancel = 9 # 撤单未成
order_status_f_wait_alter = 10 # 等待修改
order_status_f_notyet_trigger = 11 # 尚未触发
order_status_f_already_trigger = 12 # 已经触发
order_status_f_auto_hangup = 13 # 自动挂起
order_status_f_unknown = 14 # 未知状态

DEF_ICON_MAIN_WINDOW = ":/pics/quantx_logo.ico"
DEF_ICON_ABOUT_DIALOG = ":/pics/quantx_logo.ico"
#------------------------------------------------------
DEF_ICON_SYSTEM_TRAY = ":/pics/quantx_logo.ico"
#------------------------------------------------------
DEF_ICON_ACTION_EXIT = ":/pics/quantx_logo.ico"
DEF_ICON_ACTION_ABOUT = ":/pics/quantx_logo.ico"
DEF_ICON_ACTION_SHOW = ":/pics/quantx_logo.ico"
DEF_ICON_ACTION_HIDE = ":/pics/quantx_logo.ico"
DEF_ICON_MENU_VIEW_TOOLER = ":/pics/quantx_logo.ico"
DEF_ICON_MENU_VIEW_DOCKER = ":/pics/quantx_logo.ico"
DEF_ICON_MENU_VIEW_TABSER = ":/pics/quantx_logo.ico"
DEF_ICON_MENU_VIEW_SKINER = ":/pics/quantx_logo.ico"
#------------------------------------------------------
DEF_ICON_LOG_INFO_ITEM = ":/pics/quantx_logo.ico"
DEF_ICON_LOG_INFO_MENU_CLEAR = ":/pics/quantx_logo.ico"
DEF_ICON_LOG_INFO_MENU_EXPORT = ":/pics/quantx_logo.ico"
#------------------------------------------------------
DEF_ICON_MAIN_TAB_SHOW = ":/pics/action_main_tab_show.ico"
DEF_ICON_MAIN_TAB_HIDE = ":/pics/action_main_tab_hide.ico"
#------------------------------------------------------
DEF_ICON_STRATEGY_LOAD = ":/pics/strategy_reload.ico"
DEF_ICON_STRATEGY_EXEC = ":/pics/strategy_working.ico"
DEF_ICON_STRATEGY_WAIT = ":/pics/strategy_suspend.ico"
DEF_ICON_STRATEGY_STOP = ":/pics/strategy_terminal.ico"
DEF_ICON_STRATEGY_FAIL = ":/pics/strategy_abnormal.ico"
DEF_ICON_STRATEGY_NULL = ":/pics/strategy_abnormal.ico"
DEF_ICON_STRATEGY_MENU_REFRESH = ":/pics/quantx_logo.ico"
DEF_ICON_STRATEGY_MENU_EXPORT = ":/pics/quantx_logo.ico"

DEF_TEXT_MAIN_TAB_NAME_1 = "策略管理"
DEF_TEXT_MAIN_TAB_NAME_2 = "模型回测"
DEF_TEXT_MAIN_TAB_NAME_3 = "本地风控"

#from PyQt5.QtCore import QEvent
#DEF_EVENT = QEvent.registerEventType(QEvent.User + 1) # QEvent.User 为 1000，QEvent::MaxUser 为 65535
DEF_EVENT_LOG_INFO_PRINT = 1001
DEF_EVENT_SET_ANALYSIS_PROGRESS = 1002
DEF_EVENT_SET_ANALYSIS_PROGRESS_ERROR = 1003
DEF_EVENT_SET_ANALYSIS_GET_QUOTE_DATA_PROGRESS = 1004
DEF_EVENT_SET_ANALYSIS_GET_QUOTE_DATA_PROGRESS_ERROR = 1005
DEF_EVENT_TRADER_FUE_CTP_UPDATE_QUOTE = 1006
DEF_EVENT_TRADER_STK_APE_UPDATE_QUOTE = 1007
DEF_EVENT_SPREAD_FUE_CTP_UPDATE_QUOTE = 1008

# 目前服务端还没有使用 Unicode，标注 gbk 的字段使用时需要 .decode()，标注 gbk 中文 的字段使用时需要 .decode("gbk")

# 股票类：宏汇个股快照 # 字节：314
stock_tdf_market_s_size = 314
stock_tdf_market_s_type = numpy.dtype([
                      ("Code", "S8"), # 证券代码 # gbk
                      ("Name", "S24"), # 证券名称 # gbk 中文
                      ("Type", "S6"), # 证券类型 # gbk
                      ("Market", "S6"), # 证券市场 # gbk
                      ("Status", "S2"), # 证券状态 # gbk
                      ("Last", numpy.uint32), # 最新价 //10000
                      ("Open", numpy.uint32), # 开盘价 //10000
                      ("High", numpy.uint32), # 最高价 //10000
                      ("Low", numpy.uint32), # 最低价 //10000
                      ("Close", numpy.uint32), # 收盘价 //10000
                      ("PreClose", numpy.uint32), # 昨收价 //10000
                      ("Volume", numpy.int64), # 成交量
                      ("Turnover", numpy.int64), # 成交额 //10000
                      ("AskPrice", numpy.uint32, (10,)), # 申卖价 //10000
                      ("AskVolume", numpy.int32, (10,)), # 申卖量
                      ("BidPrice", numpy.uint32, (10,)), # 申买价 //10000
                      ("BidVolume", numpy.int32, (10,)), # 申买量
                      ("HighLimit", numpy.uint32), # 涨停价 //10000
                      ("LowLimit", numpy.uint32), # 跌停价 //10000
                      ("TotalBidVol", numpy.int64), # 总买量
                      ("TotalAskVol", numpy.int64), # 总卖量
                      ("WeightedAvgBidPrice", numpy.uint32), # 加权平均委买价格 //10000
                      ("WeightedAvgAskPrice", numpy.uint32), # 加权平均委卖价格 //10000
                      ("TradeCount", numpy.int32), # 成交笔数
                      ("IOPV", numpy.int32), # IOPV净值估值 //10000
                      ("YieldRate", numpy.int32), # 到期收益率 //10000
                      ("PeRate_1", numpy.int32), # 市盈率 1 //10000
                      ("PeRate_2", numpy.int32), # 市盈率 2 //10000
                      ("Units", numpy.int32), # 计价单位
                      ("QuoteTime", numpy.int32), # 行情时间 # HHMMSSmmm 精度：毫秒
                      ("LocalTime", numpy.int32), # 本地时间 # HHMMSSmmm 精度：毫秒
                      ("LocalIndex", numpy.uint32)]) # 本地序号
stock_tdf_market_s_type_src = numpy.dtype([
                      ("Code", "S8"), # 证券代码 # gbk
                      ("Name", "S24"), # 证券名称 # gbk 中文
                      ("Type", "S6"), # 证券类型 # gbk
                      ("Market", "S6"), # 证券市场 # gbk
                      ("Status", "S2"), # 证券状态 # gbk
                      ("Last", numpy.float64), # 最新价 //10000
                      ("Open", numpy.float64), # 开盘价 //10000
                      ("High", numpy.float64), # 最高价 //10000
                      ("Low", numpy.float64), # 最低价 //10000
                      ("Close", numpy.float64), # 收盘价 //10000
                      ("PreClose", numpy.float64), # 昨收价 //10000
                      ("Volume", numpy.int64), # 成交量
                      ("Turnover", numpy.float64), # 成交额 //10000
                      ("AskPrice", numpy.float64, (10,)), # 申卖价 //10000
                      ("AskVolume", numpy.int32, (10,)), # 申卖量
                      ("BidPrice", numpy.float64, (10,)), # 申买价 //10000
                      ("BidVolume", numpy.int32, (10,)), # 申买量
                      ("HighLimit", numpy.float64), # 涨停价 //10000
                      ("LowLimit", numpy.float64), # 跌停价 //10000
                      ("TotalBidVol", numpy.int64), # 总买量
                      ("TotalAskVol", numpy.int64), # 总卖量
                      ("WeightedAvgBidPrice", numpy.float64), # 加权平均委买价格 //10000
                      ("WeightedAvgAskPrice", numpy.float64), # 加权平均委卖价格 //10000
                      ("TradeCount", numpy.int32), # 成交笔数
                      ("IOPV", numpy.float64), # IOPV净值估值 //10000
                      ("YieldRate", numpy.float64), # 到期收益率 //10000
                      ("PeRate_1", numpy.float64), # 市盈率 1 //10000
                      ("PeRate_2", numpy.float64), # 市盈率 2 //10000
                      ("Units", numpy.int32), # 计价单位
                      ("QuoteTime", numpy.int32), # 行情时间 # HHMMSSmmm 精度：毫秒
                      ("LocalTime", numpy.int32), # 本地时间 # HHMMSSmmm 精度：毫秒
                      ("LocalIndex", numpy.uint32)]) # 本地序号

# 股票类：宏汇指数快照 # 字节：98
stock_tdf_market_i_size = 98
stock_tdf_market_i_type = numpy.dtype([
                      ("Code", "S8"), # 指数代码 # gbk
                      ("Name", "S24"), # 指数名称 # gbk 中文
                      ("Type", "S6"), # 指数类型 # gbk
                      ("Market", "S6"), # 指数市场 # gbk
                      ("Status", "S2"), # 指数状态 # gbk
                      ("Last", numpy.int32), # 最新指数 //10000
                      ("Open", numpy.int32), # 开盘指数 //10000
                      ("High", numpy.int32), # 最高指数 //10000
                      ("Low", numpy.int32), # 最低指数 //10000
                      ("Close", numpy.int32), # 收盘指数 //10000
                      ("PreClose", numpy.int32), # 昨收指数 //10000
                      ("Volume", numpy.int64), # 成交量
                      ("Turnover", numpy.int64), # 成交额 //10000
                      ("QuoteTime", numpy.int32), # 行情时间 # HHMMSSmmm 精度：毫秒
                      ("LocalTime", numpy.int32), # 本地时间 # HHMMSSmmm 精度：毫秒
                      ("LocalIndex", numpy.uint32)]) # 本地序号
stock_tdf_market_i_type_src = numpy.dtype([
                      ("Code", "S8"), # 指数代码 # gbk
                      ("Name", "S24"), # 指数名称 # gbk 中文
                      ("Type", "S6"), # 指数类型 # gbk
                      ("Market", "S6"), # 指数市场 # gbk
                      ("Status", "S2"), # 指数状态 # gbk
                      ("Last", numpy.float64), # 最新指数 //10000
                      ("Open", numpy.float64), # 开盘指数 //10000
                      ("High", numpy.float64), # 最高指数 //10000
                      ("Low", numpy.float64), # 最低指数 //10000
                      ("Close", numpy.float64), # 收盘指数 //10000
                      ("PreClose", numpy.float64), # 昨收指数 //10000
                      ("Volume", numpy.int64), # 成交量
                      ("Turnover", numpy.float64), # 成交额 //10000
                      ("QuoteTime", numpy.int32), # 行情时间 # HHMMSSmmm 精度：毫秒
                      ("LocalTime", numpy.int32), # 本地时间 # HHMMSSmmm 精度：毫秒
                      ("LocalIndex", numpy.uint32)]) # 本地序号

# 股票类：宏汇逐笔成交 # 字节：76
stock_tdf_market_t_size = 76
stock_tdf_market_t_type = numpy.dtype([
                      ("Code", "S8"), # 证券代码 # gbk
                      ("Name", "S24"), # 证券名称 # gbk 中文
                      ("Type", "S6"), # 证券类型 # gbk
                      ("Market", "S6"), # 证券市场 # gbk
                      ("Index", numpy.int32), # 成交编号
                      ("Price", numpy.uint32), # 成交价 //10000
                      ("Volume", numpy.int32), # 成交量
                      ("Turnover", numpy.int64), # 成交额 //10000
                      ("TransTime", numpy.int32), # 成交时间 # HHMMSSmmm 精度：毫秒
                      ("LocalTime", numpy.int32), # 本地时间 # HHMMSSmmm 精度：毫秒
                      ("LocalIndex", numpy.uint32)]) # 本地序号
stock_tdf_market_t_type_src = numpy.dtype([
                      ("Code", "S8"), # 证券代码 # gbk
                      ("Name", "S24"), # 证券名称 # gbk 中文
                      ("Type", "S6"), # 证券类型 # gbk
                      ("Market", "S6"), # 证券市场 # gbk
                      ("Index", numpy.int32), # 成交编号
                      ("Price", numpy.float64), # 成交价 //10000
                      ("Volume", numpy.int32), # 成交量
                      ("Turnover", numpy.float64), # 成交额 //10000
                      ("TransTime", numpy.int32), # 成交时间 # HHMMSSmmm 精度：毫秒
                      ("LocalTime", numpy.int32), # 本地时间 # HHMMSSmmm 精度：毫秒
                      ("LocalIndex", numpy.uint32)]) # 本地序号

# 股票类：广播个股快照 # 字节：327
stock_ltb_market_s_size = 327
stock_ltb_market_s_type = numpy.dtype([
                      ("Code", "S9"), # 证券代码 # gbk
                      ("Name", "S24"), # 证券名称 # gbk 中文 //无
                      ("Type", "S6"), # 证券类型 # gbk //配置指定，否则就为空
                      ("Market", "S6"), # 证券市场 # gbk //SSE，SZE
                      ("Status", "S2"), # 证券状态 # gbk //"N"
                      ("Last", numpy.uint32), # 最新价 //10000
                      ("Open", numpy.uint32), # 开盘价 //10000
                      ("High", numpy.uint32), # 最高价 //10000
                      ("Low", numpy.uint32), # 最低价 //10000
                      ("Close", numpy.uint32), # 收盘价 //10000
                      ("PreClose", numpy.uint32), # 昨收价 //10000 //无
                      ("Volume", numpy.int64), # 成交量
                      ("Turnover", numpy.int64), # 成交额 //10000
                      ("AskPrice", numpy.uint32, (10,)), # 申卖价 //10000
                      ("AskVolume", numpy.int32, (10,)), # 申卖量
                      ("BidPrice", numpy.uint32, (10,)), # 申买价 //10000
                      ("BidVolume", numpy.int32, (10,)), # 申买量
                      ("HighLimit", numpy.uint32), # 涨停价 //10000 //无
                      ("LowLimit", numpy.uint32), # 跌停价 //10000 //无
                      ("OpenInterest", numpy.int64), # 持仓量
                      ("IOPV", numpy.int32), # 基金净值 //10000
                      ("TradeCount", numpy.int32), # 成交笔数
                      ("YieldToMaturity", numpy.uint32), # 到期收益率 //10000
                      ("AuctionPrice", numpy.uint32), # 动态参考价格 //10000
                      ("BidPriceLevel", numpy.int32), # 买价深度
                      ("OfferPriceLevel", numpy.int32), # 卖价深度
                      ("TotalBidVolume", numpy.int32), # 申买总量
                      ("TotalOfferVolume", numpy.int32), # 申卖总量
                      ("WeightedAvgBidPrice", numpy.uint32), # 申买加权均价 //10000
                      ("WeightedAvgOfferPrice", numpy.uint32), # 申卖加权均价 //10000
                      ("AltWeightedAvgBidPrice", numpy.uint32), # 债券申买加权均价 //10000
                      ("AltWeightedAvgOfferPrice", numpy.uint32), # 债券申卖加权均价 //10000
                      ("TradingPhase", (numpy.str_, 2)), # 交易阶段
                      ("OpenRestriction", (numpy.str_, 2)), # 开仓限制
                      ("QuoteTime", numpy.int32), # 行情时间 # HHMMSSmmm 精度：毫秒
                      ("LocalTime", numpy.int32), # 本地时间 # HHMMSSmmm 精度：毫秒
                      ("LocalIndex", numpy.uint32)]) # 本地序号
stock_ltb_market_s_type_src = numpy.dtype([
                      ("Code", "S9"), # 证券代码 # gbk
                      ("Name", "S24"), # 证券名称 # gbk 中文 //无
                      ("Type", "S6"), # 证券类型 # gbk //配置指定，否则就为空
                      ("Market", "S6"), # 证券市场 # gbk //SSE，SZE
                      ("Status", "S2"), # 证券状态 # gbk //"N"
                      ("Last", numpy.float64), # 最新价 //10000
                      ("Open", numpy.float64), # 开盘价 //10000
                      ("High", numpy.float64), # 最高价 //10000
                      ("Low", numpy.float64), # 最低价 //10000
                      ("Close", numpy.float64), # 收盘价 //10000
                      ("PreClose", numpy.float64), # 昨收价 //10000 //无
                      ("Volume", numpy.int64), # 成交量
                      ("Turnover", numpy.float64), # 成交额 //10000
                      ("AskPrice", numpy.float64, (10,)), # 申卖价 //10000
                      ("AskVolume", numpy.int32, (10,)), # 申卖量
                      ("BidPrice", numpy.float64, (10,)), # 申买价 //10000
                      ("BidVolume", numpy.int32, (10,)), # 申买量
                      ("HighLimit", numpy.float64), # 涨停价 //10000 //无
                      ("LowLimit", numpy.float64), # 跌停价 //10000 //无
                      ("OpenInterest", numpy.int64), # 持仓量
                      ("IOPV", numpy.float64), # 基金净值 //10000
                      ("TradeCount", numpy.int32), # 成交笔数
                      ("YieldToMaturity", numpy.float64), # 到期收益率 //10000
                      ("AuctionPrice", numpy.float64), # 动态参考价格 //10000
                      ("BidPriceLevel", numpy.int32), # 买价深度
                      ("OfferPriceLevel", numpy.int32), # 卖价深度
                      ("TotalBidVolume", numpy.int32), # 申买总量
                      ("TotalOfferVolume", numpy.int32), # 申卖总量
                      ("WeightedAvgBidPrice", numpy.float64), # 申买加权均价 //10000
                      ("WeightedAvgOfferPrice", numpy.float64), # 申卖加权均价 //10000
                      ("AltWeightedAvgBidPrice", numpy.float64), # 债券申买加权均价 //10000
                      ("AltWeightedAvgOfferPrice", numpy.float64), # 债券申卖加权均价 //10000
                      ("TradingPhase", (numpy.str_, 2)), # 交易阶段
                      ("OpenRestriction", (numpy.str_, 2)), # 开仓限制
                      ("QuoteTime", numpy.int32), # 行情时间 # HHMMSSmmm 精度：毫秒
                      ("LocalTime", numpy.int32), # 本地时间 # HHMMSSmmm 精度：毫秒
                      ("LocalIndex", numpy.uint32)]) # 本地序号

# 股票类：广播指数快照 # 字节：99
stock_ltb_market_i_size = 99
stock_ltb_market_i_type = numpy.dtype([
                      ("Code", "S9"), # 指数代码 # gbk
                      ("Name", "S24"), # 指数名称 # gbk 中文 //无
                      ("Type", "S6"), # 指数类型 # gbk //配置指定，否则就为空
                      ("Market", "S6"), # 指数市场 # gbk //SSE，SZE
                      ("Status", "S2"), # 指数状态 # gbk //"N"
                      ("Last", numpy.int32), # 最新指数 //10000
                      ("Open", numpy.int32), # 开盘指数 //10000
                      ("High", numpy.int32), # 最高指数 //10000
                      ("Low", numpy.int32), # 最低指数 //10000
                      ("Close", numpy.int32), # 收盘指数 //10000
                      ("PreClose", numpy.int32), # 昨收指数 //10000
                      ("Volume", numpy.int64), # 成交量
                      ("Turnover", numpy.int64), # 成交额 //10000
                      ("QuoteTime", numpy.int32), # 行情时间 # HHMMSSmmm 精度：毫秒
                      ("LocalTime", numpy.int32), # 本地时间 # HHMMSSmmm 精度：毫秒
                      ("LocalIndex", numpy.uint32)]) # 本地序号
stock_ltb_market_i_type_src = numpy.dtype([
                      ("Code", "S9"), # 指数代码 # gbk
                      ("Name", "S24"), # 指数名称 # gbk 中文 //无
                      ("Type", "S6"), # 指数类型 # gbk //配置指定，否则就为空
                      ("Market", "S6"), # 指数市场 # gbk //SSE，SZE
                      ("Status", "S2"), # 指数状态 # gbk //"N"
                      ("Last", numpy.float64), # 最新指数 //10000
                      ("Open", numpy.float64), # 开盘指数 //10000
                      ("High", numpy.float64), # 最高指数 //10000
                      ("Low", numpy.float64), # 最低指数 //10000
                      ("Close", numpy.float64), # 收盘指数 //10000
                      ("PreClose", numpy.float64), # 昨收指数 //10000
                      ("Volume", numpy.int64), # 成交量
                      ("Turnover", numpy.int64), # 成交额 //10000
                      ("QuoteTime", numpy.float64), # 行情时间 # HHMMSSmmm 精度：毫秒
                      ("LocalTime", numpy.float64), # 本地时间 # HHMMSSmmm 精度：毫秒
                      ("LocalIndex", numpy.uint32)]) # 本地序号

# 股票类：广播逐笔成交 # 字节：
stock_ltb_market_t_size = 93
stock_ltb_market_t_type = numpy.dtype([
                      ("Code", "S9"), # 证券代码 # gbk
                      ("Name", "S24"), # 证券名称 # gbk 中文
                      ("Type", "S6"), # 证券类型 # gbk
                      ("Market", "S6"), # 证券市场 # gbk
                      ("Index", numpy.int32), # 成交编号
                      ("Price", numpy.uint32), # 成交价 //10000
                      ("Volume", numpy.int32), # 成交量
                      ("Turnover", numpy.int64), # 成交额 //10000
                      ("TradeGroupID", numpy.int32), # 成交组
                      ("BuyIndex", numpy.int32), # 买方委托序号
                      ("SellIndex", numpy.int32), # 卖方委托序号
                      ("OrderKind", (numpy.str_, 2)), # 报单类型
                      ("FunctionCode", (numpy.str_, 2)), # 功能码
                      ("TransTime", numpy.int32), # 成交时间 # HHMMSSmmm 精度：毫秒
                      ("LocalTime", numpy.int32), # 本地时间 # HHMMSSmmm 精度：毫秒
                      ("LocalIndex", numpy.uint32)]) # 本地序号
stock_ltb_market_t_type_src = numpy.dtype([
                      ("Code", "S9"), # 证券代码 # gbk
                      ("Name", "S24"), # 证券名称 # gbk 中文
                      ("Type", "S6"), # 证券类型 # gbk
                      ("Market", "S6"), # 证券市场 # gbk
                      ("Index", numpy.int32), # 成交编号
                      ("Price", numpy.float64), # 成交价 //10000
                      ("Volume", numpy.int32), # 成交量
                      ("Turnover", numpy.float64), # 成交额 //10000
                      ("TradeGroupID", numpy.int32), # 成交组
                      ("BuyIndex", numpy.int32), # 买方委托序号
                      ("SellIndex", numpy.int32), # 卖方委托序号
                      ("OrderKind", (numpy.str_, 2)), # 报单类型
                      ("FunctionCode", (numpy.str_, 2)), # 功能码
                      ("TransTime", numpy.int32), # 成交时间 # HHMMSSmmm 精度：毫秒
                      ("LocalTime", numpy.int32), # 本地时间 # HHMMSSmmm 精度：毫秒
                      ("LocalIndex", numpy.uint32)]) # 本地序号

# 股票类：主推个股快照 # 字节：314
stock_ltp_market_s_size = stock_tdf_market_s_size # 相同
stock_ltp_market_s_type = stock_tdf_market_s_type # 相同
stock_ltp_market_s_type_src = stock_tdf_market_s_type_src # 相同

# 股票类：主推指数快照 # 字节：98
stock_ltp_market_i_size = stock_tdf_market_i_size # 相同
stock_ltp_market_i_type = stock_tdf_market_i_type # 相同
stock_ltp_market_i_type_src = stock_tdf_market_i_type_src # 相同

# 股票类：主推逐笔成交 # 字节：76
stock_ltp_market_t_size = stock_tdf_market_t_size # 相同
stock_ltp_market_t_type = stock_tdf_market_t_type # 相同
stock_ltp_market_t_type_src = stock_tdf_market_t_type_src # 相同

# 期货类：内盘市场快照 # 字节：208
future_np_market_size = 208
future_np_market_type = numpy.dtype([
                      ("Code", "S8"), # 合约代码 # gbk
                      ("Name", "S2"), # 合约名称 # gbk 中文 //无
                      ("Type", "S2"), # 合约类型 # gbk
                      ("Market", "S6"), # 合约市场 # gbk
                      ("Status", "S2"), # 合约状态 # gbk
                      ("Last", numpy.uint32), # 最新价 //10000
                      ("Open", numpy.uint32), # 开盘价 //10000
                      ("High", numpy.uint32), # 最高价 //10000
                      ("Low", numpy.uint32), # 最低价 //10000
                      ("Close", numpy.uint32), # 收盘价 //10000
                      ("PreClose", numpy.uint32), # 昨收价 //10000
                      ("Volume", numpy.int64), # 成交量
                      ("Turnover", numpy.int64), # 成交额 //10000
                      ("AskPrice", numpy.uint32, (5,)), # 申卖价 //10000
                      ("AskVolume", numpy.int32, (5,)), # 申卖量
                      ("BidPrice", numpy.uint32, (5,)), # 申买价 //10000
                      ("BidVolume", numpy.int32, (5,)), # 申买量
                      ("HighLimit", numpy.uint32), # 涨停价 //10000
                      ("LowLimit", numpy.uint32), # 跌停价 //10000
                      ("Settle", numpy.uint32), # 今日结算价 //10000
                      ("PreSettle", numpy.uint32), # 昨日结算价 //10000
                      ("Position", numpy.int32), # 今日持仓量
                      ("PrePosition", numpy.int32), # 昨日持仓量
                      ("Average", numpy.uint32), # 均价 //10000
                      ("UpDown", numpy.int32), # 涨跌 //10000 //无
                      ("UpDownRate", numpy.int32), # 涨跌幅度 //10000 //无
                      ("Swing", numpy.int32), # 振幅 //10000 //无
                      ("Delta", numpy.int32), # 今日虚实度 //10000
                      ("PreDelta", numpy.int32), # 昨日虚实度 //10000
                      ("QuoteDate", numpy.int32), # 行情日期 # YYYYMMDD
                      ("QuoteTime", numpy.int32), # 行情时间 # HHMMSSmmm 精度：0.5秒
                      ("LocalDate", numpy.int32), # 本地日期 # YYYYMMDD
                      ("LocalTime", numpy.int32), # 本地时间 # HHMMSSmmm 精度：毫秒
                      ("LocalIndex", numpy.uint32)]) # 本地序号
future_np_market_type_src = numpy.dtype([
                      ("Code", "S8"), # 合约代码 # gbk
                      ("Name", "S2"), # 合约名称 # gbk 中文 //无
                      ("Type", "S2"), # 合约类型 # gbk
                      ("Market", "S6"), # 合约市场 # gbk
                      ("Status", "S2"), # 合约状态 # gbk
                      ("Last", numpy.float64), # 最新价 //10000
                      ("Open", numpy.float64), # 开盘价 //10000
                      ("High", numpy.float64), # 最高价 //10000
                      ("Low", numpy.float64), # 最低价 //10000
                      ("Close", numpy.float64), # 收盘价 //10000
                      ("PreClose", numpy.float64), # 昨收价 //10000
                      ("Volume", numpy.int64), # 成交量
                      ("Turnover", numpy.float64), # 成交额 //10000
                      ("AskPrice", numpy.float64, (5,)), # 申卖价 //10000
                      ("AskVolume", numpy.int32, (5,)), # 申卖量
                      ("BidPrice", numpy.float64, (5,)), # 申买价 //10000
                      ("BidVolume", numpy.int32, (5,)), # 申买量
                      ("HighLimit", numpy.float64), # 涨停价 //10000
                      ("LowLimit", numpy.float64), # 跌停价 //10000
                      ("Settle", numpy.float64), # 今日结算价 //10000
                      ("PreSettle", numpy.float64), # 昨日结算价 //10000
                      ("Position", numpy.int32), # 今日持仓量
                      ("PrePosition", numpy.int32), # 昨日持仓量
                      ("Average", numpy.float64), # 均价 //10000
                      ("UpDown", numpy.float64), # 涨跌 //10000 //无
                      ("UpDownRate", numpy.float64), # 涨跌幅度 //10000 //无
                      ("Swing", numpy.float64), # 振幅 //10000 //无
                      ("Delta", numpy.float64), # 今日虚实度 //10000
                      ("PreDelta", numpy.float64), # 昨日虚实度 //10000
                      ("QuoteDate", numpy.int32), # 行情日期 # YYYYMMDD
                      ("QuoteTime", numpy.int32), # 行情时间 # HHMMSSmmm 精度：0.5秒
                      ("LocalDate", numpy.int32), # 本地日期 # YYYYMMDD
                      ("LocalTime", numpy.int32), # 本地时间 # HHMMSSmmm 精度：毫秒
                      ("LocalIndex", numpy.uint32)]) # 本地序号
