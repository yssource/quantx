
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

from PyQt5.QtWidgets import QDialog

import config
import logger

class RiskctrlPanel(QDialog):
    def __init__(self, parent):
        super(RiskctrlPanel, self).__init__(parent)
        self.parent = parent
        self.log_text = ""
        self.log_cate = "RiskctrlPanel"
        self.config = config.Config()
        self.logger = logger.Logger()
        
        self.InitUserInterface()

    def __del__(self):
        pass

    def InitUserInterface(self):
        pass
