
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

import configobj
import configparser

import common

class CfgMain(object):
    def __init__(self):
        self.quote_stock_ltb_need = 0
        self.quote_stock_ltb_flag = "flag"
        self.quote_stock_ltb_addr = "127.0.0.1"
        self.quote_stock_ltb_port = 9999
        self.quote_stock_ltb_show = "show"
        self.quote_stock_ltb_tips = "tips"
        
        self.quote_stock_ltp_need = 0
        self.quote_stock_ltp_flag = "flag"
        self.quote_stock_ltp_addr = "127.0.0.1"
        self.quote_stock_ltp_port = 9999
        self.quote_stock_ltp_show = "show"
        self.quote_stock_ltp_tips = "tips"
        
        self.quote_stock_tdf_need = 0
        self.quote_stock_tdf_flag = "flag"
        self.quote_stock_tdf_addr = "127.0.0.1"
        self.quote_stock_tdf_port = 9999
        self.quote_stock_tdf_show = "show"
        self.quote_stock_tdf_tips = "tips"
        
        self.quote_future_np_need = 0
        self.quote_future_np_flag = "flag"
        self.quote_future_np_addr = "127.0.0.1"
        self.quote_future_np_port = 9999
        self.quote_future_np_show = "show"
        self.quote_future_np_tips = "tips"
        
        self.trade_stock_ape_need = 0
        self.trade_stock_ape_save = 0
        self.trade_stock_ape_flag = "flag"
        self.trade_stock_ape_addr = "127.0.0.1"
        self.trade_stock_ape_port = 9999
        self.trade_stock_ape_show = "show"
        self.trade_stock_ape_tips = "tips"
        
        self.trade_future_np_ctp_need = 0
        self.trade_future_np_ctp_save = 0
        self.trade_future_np_ctp_flag = "flag"
        self.trade_future_np_ctp_addr = "127.0.0.1"
        self.trade_future_np_ctp_port = 9999
        self.trade_future_np_ctp_show = "show"
        self.trade_future_np_ctp_tips = "tips"
        
        self.logger_server_need = 0
        self.logger_server_port = 9999
        self.logger_server_flag = "flag"
        
        self.data_folder = "../data"
        self.data_db_need = 0
        self.data_db_host = "0.0.0.0"
        self.data_db_port = 9999
        self.data_db_user = "username"
        self.data_db_pass = "password"
        
        self.anal_folder = "../anal"
        
        self.stra_folder = "../stra"
        self.stra_auto_load = 0
        self.stra_debug_info = 0
        
        #华宝股票
        self.user_username_ape = "username"
        self.user_password_ape = "password"
        self.user_gdh_sh_ape = "0123456789"
        self.user_gdh_sz_ape = "0123456789"
        self.user_asset_account_ape = "asset_account"
        
        #上期期货
        self.user_username_ctp = "username"
        self.user_password_ctp = "password"
        self.user_asset_account_ctp = "asset_account"

    def LoadConfig(self, file_path):
        config = configparser.ConfigParser()
        config.read(file_path, encoding = "utf-8") # BOM：utf-8-sig
        
        self.quote_stock_ltb_need = int(config.get("nets", "quote_stock_ltb_need"))
        self.quote_stock_ltb_flag = config.get("nets", "quote_stock_ltb_flag")
        self.quote_stock_ltb_addr = config.get("nets", "quote_stock_ltb_addr")
        self.quote_stock_ltb_port = int(config.get("nets", "quote_stock_ltb_port"))
        self.quote_stock_ltb_show = config.get("nets", "quote_stock_ltb_show")
        self.quote_stock_ltb_tips = config.get("nets", "quote_stock_ltb_tips") # 配置文件格式必须为 UTF8 否则会报异常
        
        self.quote_stock_ltp_need = int(config.get("nets", "quote_stock_ltp_need"))
        self.quote_stock_ltp_flag = config.get("nets", "quote_stock_ltp_flag")
        self.quote_stock_ltp_addr = config.get("nets", "quote_stock_ltp_addr")
        self.quote_stock_ltp_port = int(config.get("nets", "quote_stock_ltp_port"))
        self.quote_stock_ltp_show = config.get("nets", "quote_stock_ltp_show")
        self.quote_stock_ltp_tips = config.get("nets", "quote_stock_ltp_tips") # 配置文件格式必须为 UTF8 否则会报异常
        
        self.quote_stock_tdf_need = int(config.get("nets", "quote_stock_tdf_need"))
        self.quote_stock_tdf_flag = config.get("nets", "quote_stock_tdf_flag")
        self.quote_stock_tdf_addr = config.get("nets", "quote_stock_tdf_addr")
        self.quote_stock_tdf_port = int(config.get("nets", "quote_stock_tdf_port"))
        self.quote_stock_tdf_show = config.get("nets", "quote_stock_tdf_show")
        self.quote_stock_tdf_tips = config.get("nets", "quote_stock_tdf_tips") # 配置文件格式必须为 UTF8 否则会报异常
        
        self.quote_future_np_need = int(config.get("nets", "quote_future_np_need"))
        self.quote_future_np_flag = config.get("nets", "quote_future_np_flag")
        self.quote_future_np_addr = config.get("nets", "quote_future_np_addr")
        self.quote_future_np_port = int(config.get("nets", "quote_future_np_port"))
        self.quote_future_np_show = config.get("nets", "quote_future_np_show")
        self.quote_future_np_tips = config.get("nets", "quote_future_np_tips") # 配置文件格式必须为 UTF8 否则会报异常
        
        self.trade_stock_ape_need = int(config.get("nets", "trade_stock_ape_need"))
        self.trade_stock_ape_save = int(config.get("nets", "trade_stock_ape_save"))
        self.trade_stock_ape_flag = config.get("nets", "trade_stock_ape_flag")
        self.trade_stock_ape_addr = config.get("nets", "trade_stock_ape_addr")
        self.trade_stock_ape_port = int(config.get("nets", "trade_stock_ape_port"))
        self.trade_stock_ape_show = config.get("nets", "trade_stock_ape_show")
        self.trade_stock_ape_tips = config.get("nets", "trade_stock_ape_tips") # 配置文件格式必须为 UTF8 否则会报异常
        
        self.trade_future_np_ctp_need = int(config.get("nets", "trade_future_np_ctp_need"))
        self.trade_future_np_ctp_save = int(config.get("nets", "trade_future_np_ctp_save"))
        self.trade_future_np_ctp_flag = config.get("nets", "trade_future_np_ctp_flag")
        self.trade_future_np_ctp_addr = config.get("nets", "trade_future_np_ctp_addr")
        self.trade_future_np_ctp_port = int(config.get("nets", "trade_future_np_ctp_port"))
        self.trade_future_np_ctp_show = config.get("nets", "trade_future_np_ctp_show")
        self.trade_future_np_ctp_tips = config.get("nets", "trade_future_np_ctp_tips") # 配置文件格式必须为 UTF8 否则会报异常
        
        self.logger_server_need = int(config.get("nets", "logger_server_need"))
        self.logger_server_port = int(config.get("nets", "logger_server_port"))
        self.logger_server_Flag = config.get("nets", "logger_server_Flag")
        
        self.data_folder = config.get("data", "data_folder")
        self.data_db_need = int(config.get("data", "data_db_need"))
        self.data_db_host = config.get("data", "data_db_host")
        self.data_db_port = int(config.get("data", "data_db_port"))
        self.data_db_user = config.get("data", "data_db_user")
        self.data_db_pass = config.get("data", "data_db_pass")
        
        self.anal_folder = config.get("anal", "anal_folder")
        
        self.stra_folder = config.get("stra", "stra_folder")
        self.stra_auto_load = int(config.get("stra", "stra_auto_load"))
        self.stra_debug_info = int(config.get("stra", "stra_debug_info"))
        
        # 顶点股票
        self.user_username_ape = config.get("user", "user_username_ape")
        self.user_password_ape = config.get("user", "user_password_ape")
        self.user_gdh_sh_ape = config.get("user", "user_gdh_sh_ape")
        self.user_gdh_sz_ape = config.get("user", "user_gdh_sz_ape")
        self.user_asset_account_ape = config.get("user", "user_asset_account_ape")
        
        # 上期期货
        self.user_username_ctp = config.get("user", "user_username_ctp")
        self.user_password_ctp = config.get("user", "user_password_ctp")
        self.user_asset_account_ctp = config.get("user", "user_asset_account_ctp")

class CfgAnal(object):
    def __init__(self):
        self.filter_security_check_all = 1
        self.filter_security_category_a = 1
        self.filter_security_category_etf = 0
        self.filter_security_category_level = 0
        self.filter_security_category_open = 0
        self.filter_security_sector_main = 1
        self.filter_security_sector_small = 1
        self.filter_security_sector_start = 1
        self.filter_security_sector_unknow = 0
        self.filter_security_list_state_1 = 1
        self.filter_security_list_state_2 = 0
        self.filter_security_list_state_3 = 0
        self.filter_security_list_state_4 = 0
        self.filter_security_list_state_5 = 0
        self.filter_security_list_state_6 = 0
        self.filter_security_list_state_7 = 0
        self.filter_security_st_non = 0
        self.filter_security_st_use = 0
        self.filter_security_data_daily = 0
        self.filter_security_data_kline_1_m = 0
        
        self.date_get_quote_data_s = 20180101
        self.date_get_quote_data_e = 0
        
        self.ignore_user_tips = 1
        self.ignore_local_file_loss = 1
        self.ignore_ex_rights_data_loss = 1
        self.ignore_local_data_imperfect = 1
        
        self.date_analysis_test_s = 20180101
        self.date_analysis_test_e = 0

    def LoadConfig(self, filePath):
        config = configobj.ConfigObj(filePath)
        
        self.filter_security_check_all = int(config["filter"]["filter_security_check_all"])
        self.filter_security_category_a = int(config["filter"]["filter_security_category_a"])
        self.filter_security_category_etf = int(config["filter"]["filter_security_category_etf"])
        self.filter_security_category_level = int(config["filter"]["filter_security_category_level"])
        self.filter_security_category_open = int(config["filter"]["filter_security_category_open"])
        self.filter_security_sector_main = int(config["filter"]["filter_security_sector_main"])
        self.filter_security_sector_small = int(config["filter"]["filter_security_sector_small"])
        self.filter_security_sector_start = int(config["filter"]["filter_security_sector_start"])
        self.filter_security_sector_unknow = int(config["filter"]["filter_security_sector_unknow"])
        self.filter_security_list_state_1 = int(config["filter"]["filter_security_list_state_1"])
        self.filter_security_list_state_2 = int(config["filter"]["filter_security_list_state_2"])
        self.filter_security_list_state_3 = int(config["filter"]["filter_security_list_state_3"])
        self.filter_security_list_state_4 = int(config["filter"]["filter_security_list_state_4"])
        self.filter_security_list_state_5 = int(config["filter"]["filter_security_list_state_5"])
        self.filter_security_list_state_6 = int(config["filter"]["filter_security_list_state_6"])
        self.filter_security_list_state_7 = int(config["filter"]["filter_security_list_state_7"])
        self.filter_security_st_non = int(config["filter"]["filter_security_st_non"])
        self.filter_security_st_use = int(config["filter"]["filter_security_st_use"])
        self.filter_security_data_daily = int(config["filter"]["filter_security_data_daily"])
        self.filter_security_data_kline_1_m = int(config["filter"]["filter_security_data_kline_1_m"])
        
        self.date_get_quote_data_s = config["quote"]["date_get_quote_data_s"]
        self.date_get_quote_data_e = config["quote"]["date_get_quote_data_e"]
        
        self.ignore_user_tips = int(config["ignore"]["ignore_user_tips"])
        self.ignore_local_file_loss = int(config["ignore"]["ignore_local_file_loss"])
        self.ignore_ex_rights_data_loss = int(config["ignore"]["ignore_ex_rights_data_loss"])
        self.ignore_local_data_imperfect = int(config["ignore"]["ignore_local_data_imperfect"])
        
        self.date_analysis_test_s = config["analysis"]["date_analysis_test_s"]
        self.date_analysis_test_e = config["analysis"]["date_analysis_test_e"]

    def SaveConfig(self, cfgAnal, filePath):
        config = configobj.ConfigObj(filePath)
        
        config["filter"]["filter_security_check_all"] = int(self.filter_security_check_all)
        config["filter"]["filter_security_category_a"] = int(self.filter_security_category_a)
        config["filter"]["filter_security_category_etf"] = int(self.filter_security_category_etf)
        config["filter"]["filter_security_category_level"] = int(self.filter_security_category_level)
        config["filter"]["filter_security_category_open"] = int(self.filter_security_category_open)
        config["filter"]["filter_security_sector_main"] = int(self.filter_security_sector_main)
        config["filter"]["filter_security_sector_small"] = int(self.filter_security_sector_small)
        config["filter"]["filter_security_sector_start"] = int(self.filter_security_sector_start)
        config["filter"]["filter_security_sector_unknow"] = int(self.filter_security_sector_unknow)
        config["filter"]["filter_security_list_state_1"] = int(self.filter_security_list_state_1)
        config["filter"]["filter_security_list_state_2"] = int(self.filter_security_list_state_2)
        config["filter"]["filter_security_list_state_3"] = int(self.filter_security_list_state_3)
        config["filter"]["filter_security_list_state_4"] = int(self.filter_security_list_state_4)
        config["filter"]["filter_security_list_state_5"] = int(self.filter_security_list_state_5)
        config["filter"]["filter_security_list_state_6"] = int(self.filter_security_list_state_6)
        config["filter"]["filter_security_list_state_7"] = int(self.filter_security_list_state_7)
        config["filter"]["filter_security_st_non"] = int(self.filter_security_st_non)
        config["filter"]["filter_security_st_use"] = int(self.filter_security_st_use)
        config["filter"]["filter_security_data_daily"] = int(self.filter_security_data_daily)
        config["filter"]["filter_security_data_kline_1_m"] = int(self.filter_security_data_kline_1_m)
        
        config["quote"]["date_get_quote_data_s"] = self.date_get_quote_data_s
        config["quote"]["date_get_quote_data_e"] = self.date_get_quote_data_e
        
        config["ignore"]["ignore_user_tips"] = int(self.ignore_user_tips)
        config["ignore"]["ignore_local_file_loss"] = int(self.ignore_local_file_loss)
        config["ignore"]["ignore_ex_rights_data_loss"] = int(self.ignore_ex_rights_data_loss)
        config["ignore"]["ignore_local_data_imperfect"] = int(self.ignore_local_data_imperfect)
        
        config["analysis"]["date_analysis_test_s"] = self.date_analysis_test_s
        config["analysis"]["date_analysis_test_e"] = self.date_analysis_test_e
        
        config.write() # 配置文件格式必须为 UTF8 否则会报异常

class Config(common.Singleton):
    def __init__(self):
        self.cfg_main = CfgMain()
        self.cfg_anal = CfgAnal()

    def LoadConfig_Main(self, file_path):
        self.cfg_main.LoadConfig(file_path)

    def LoadConfig_Anal(self, file_path):
        self.cfg_anal.LoadConfig(file_path)

    def SaveConfig_Main(self, cfg_main, file_path):
        pass

    def SaveConfig_Anal(self, cfg_anal, file_path):
        self.cfg_anal.SaveConfig(cfg_anal, file_path)
