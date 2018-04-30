
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

import sys
import netifaces

from PyQt5 import QtGui, QtWidgets

import images
import define
import window

def CheckMacAddress(mac_address):
    #print(netifaces.gateways()["default"][netifaces.AF_INET][0])
    #print(netifaces.gateways()["default"][netifaces.AF_INET][1])
    
    result = False
    for routing_nic_name in netifaces.interfaces():
        #print(netifaces.ifaddresses(routing_nic_name))
        try:
            routing_nic_mac_address = netifaces.ifaddresses(routing_nic_name)[netifaces.AF_LINK][0]["addr"]
            if mac_address == routing_nic_mac_address:
                result = True
                break
            #routing_ip_address = netifaces.ifaddresses(routing_nic_name)[netifaces.AF_INET][0]["addr"]
            # On Windows, netmask maybe give a wrong result in "netifaces" module.
            #routing_ip_netmask = netifaces.ifaddresses(routing_nic_name)[netifaces.AF_INET][0]["netmask"]
            
            #print("")
            #display_format = "%-30s %-20s"
            #print(display_format % ("Routing NIC Name:", routing_nic_name))
            #print(display_format % ("Routing NIC MAC Address:", routing_nic_mac_address))
            #print(display_format % ("Routing IP Address:", routing_ip_address))
            #print(display_format % ("Routing IP Netmask:", routing_ip_netmask))
        except KeyError:
            pass
    return result

def QuantX():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(define.DEF_ICON_MAIN_WINDOW))
    
    #if CheckMacAddress("90:61:ae:cd:ae:0f") == False:
    #    return
    
    main_window = window.MainWindow()
    main_window.is_system_initialization = True
    main_window.ReadSettings() # 读取界面属性
    main_window.show()
    main_window.SystemStart() # 初始化各模块
    main_window.is_system_initialization = False
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    QuantX()
