
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

import config
import common

class FixCfg(common.Singleton):
    def __init__(self):
        self.config = config.Config()

    def AssignValue(self):
        # 顶点APE股票
        if self.config.cfg_main.user_username_ape == "0":
            self.config.cfg_main.user_username_ape = "username"
            self.config.cfg_main.user_password_ape = "password"
            self.config.cfg_main.user_gdh_sh_ape = "0123456789"
            self.config.cfg_main.user_gdh_sz_ape = "0123456789"
            self.config.cfg_main.user_asset_account_ape = "asset_account"
        # 顶点VIP股票
        if self.config.cfg_main.user_username_vip == "0":
            self.config.cfg_main.user_username_vip = "username"
            self.config.cfg_main.user_password_vip = "password"
            self.config.cfg_main.user_gdh_sh_vip = "0123456789"
            self.config.cfg_main.user_gdh_sz_vip = "0123456789"
            self.config.cfg_main.user_asset_account_vip = "asset_account"
        # 上期CTP期货
        if self.config.cfg_main.user_username_ctp == "0":
            self.config.cfg_main.user_username_ctp = "12345678"
            self.config.cfg_main.user_password_ctp = "123456"
            self.config.cfg_main.user_asset_account_ctp = "asset_account"
