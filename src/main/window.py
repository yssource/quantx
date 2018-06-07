
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
import time

import qdarkstyle
from pubsub import pub
from PyQt5.QtGui import QColor, QFont, QIcon, QPalette
from PyQt5.QtCore import QByteArray, QSettings, QSize, Qt, QTimer, QVariant
from PyQt5.QtWidgets import QAction, QApplication, QDesktopWidget, QDockWidget, QLabel, QMainWindow, QMenu
from PyQt5.QtWidgets import QMessageBox, QSystemTrayIcon, QTabWidget, QToolBar, QWidget, QVBoxLayout

import about_dialog
import log_info_panel
import strategy_panel
import analysis_panel
import riskctrl_panel
import tip_info_dialog
import quote_center_bar
import trade_center_bar

import images
import define
import config
import fixcfg
import logger
import basicx
import trader
import strate

import basic_data_maker

import ultimate
import strategy_base # 只是为了打包时能被编译到
import analysis_base # 只是为了打包时能被编译到
import panel_trader_stk_ape # 只是为了打包时能被编译到
import panel_trader_fue_ctp # 只是为了打包时能被编译到

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.is_system_initialization = False # 主要用来避免菜单中主题选择项的重复勾选问题
        
        # 必须在任何需要参数配置信息的模块创建前导入
        self.config = config.Config()
        self.config.LoadConfig_Main(define.CFG_FILE_PATH_MAIN)
        self.config.LoadConfig_Anal(define.CFG_FILE_PATH_ANAL)
        self.config.LoadConfig_Risk(define.CFG_FILE_PATH_RISK)
        
        self.log_text = ""
        self.log_cate = "MainWindow"
        self.logger = logger.Logger() # 存储日志信息到本地数据库
        self.logger.SetMainWindow(self) # 必须
        if self.config.cfg_main.logger_server_need == 1:
            self.logger.StartServer(self.config.cfg_main.logger_server_port, self.config.cfg_main.logger_server_Flag)
        
        # 托管时覆盖配置文件中的假密码信息
        self.fixcfg = fixcfg.FixCfg()
        self.fixcfg.AssignValue()
        
        self.logger.SendMessage("S", 1, self.log_cate, "***********************************************************************************")
        self.logger.SendMessage("S", 1, self.log_cate, "                       " + define.APP_COMPANY)
        self.logger.SendMessage("S", 1, self.log_cate, "                  " + define.APP_COPYRIGHT)
        self.logger.SendMessage("S", 1, self.log_cate, "***********************************************************************************")
        self.logger.SendMessage("S", 1, self.log_cate, "系统：" + define.APP_TITLE_EN)
        self.logger.SendMessage("S", 1, self.log_cate, "版本：" + define.APP_VERSION)
        
        self.InitUserInterface() # 此后才会显示日志信息

    def __del__(self):
        pass

    def InitUserInterface(self):
        self.about_dialog = None
        self.is_user_exit = False
        self.is_main_window_visible = True
        self.is_tray_icon_loaded = False
        self.is_not_first_run = False
        self.current_main_tab_index = 0
        self.basic_data_maker = None
        
        self.setWindowTitle(define.APP_TITLE_EN + " " + define.APP_VERSION)
        self.resize(define.DEF_MAIN_WINDOW_W, define.DEF_MAIN_WINDOW_H)
        
        geometry = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        geometry.moveCenter(center)
        self.move(geometry.topLeft())
        
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea) # 默认顶部收缩
        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea) # 默认顶部收缩
        self.setCorner(Qt.BottomRightCorner, Qt.BottomDockWidgetArea) # 默认底部扩展
        self.setCorner(Qt.BottomLeftCorner, Qt.BottomDockWidgetArea) # 默认底部扩展
        self.setDockOptions(QMainWindow.AnimatedDocks | QMainWindow.AllowNestedDocks | QMainWindow.AllowTabbedDocks);
        #self.setTabPosition(Qt.TopDockWidgetArea, QTabWidget.North) # 使顶部的停靠窗口嵌套后标签页在上面
        
        self.CreateActions()
        self.CreateMenuBar()
        self.CreateToolBar()
        self.CreateStatusBar()
        self.CreateLogsDock()
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        self.main_tab_panel_1 = strategy_panel.StrategyPanel(self)
        self.main_tab_panel_2 = analysis_panel.AnalysisPanel(self)
        self.main_tab_panel_3 = riskctrl_panel.RiskctrlPanel(self)
        self.main_tab_widget = QTabWidget()
        self.main_tab_widget.setTabPosition(QTabWidget.North)
        self.main_tab_widget.addTab(self.main_tab_panel_1, define.DEF_TEXT_MAIN_TAB_NAME_1)
        self.main_tab_widget.addTab(self.main_tab_panel_2, define.DEF_TEXT_MAIN_TAB_NAME_2)
        self.main_tab_widget.addTab(self.main_tab_panel_3, define.DEF_TEXT_MAIN_TAB_NAME_3)
        self.main_tab_widget.setTabIcon(0, QIcon(define.DEF_ICON_MAIN_TAB_HIDE))
        self.main_tab_widget.setTabIcon(1, QIcon(define.DEF_ICON_MAIN_TAB_HIDE))
        self.main_tab_widget.setTabIcon(2, QIcon(define.DEF_ICON_MAIN_TAB_HIDE))
        self.main_tab_widget.setFont(QFont("SimSun", 9))
        self.main_tab_widget.setCurrentIndex(0)
        self.main_tab_widget.setTabIcon(0, QIcon(define.DEF_ICON_MAIN_TAB_SHOW))
        self.main_tab_widget.setMovable(True)
        self.main_tab_widget.setTabsClosable(False)
        self.main_tab_widget.setUsesScrollButtons(True)
        self.main_tab_widget.currentChanged.connect(self.OnClickMainTabBar)
        
        self.v_box = QVBoxLayout()
        self.v_box.setContentsMargins(5, 5, 5, 5)
        self.v_box.addWidget(self.main_tab_widget, 1)
        
        self.main_widget.setLayout(self.v_box)
        
        self.tip_info_dialog = tip_info_dialog.TipInfoDialog(self)
        
        self.action_show_tab_1.setChecked(True)
        self.action_show_tab_2.setChecked(True)
        self.action_show_tab_3.setChecked(True)
        self.action_show_skin_norm.setChecked(True) # True
        self.action_show_skin_dark.setChecked(False) # False
        self.action_save_layout.setChecked(False)

    def CreateActions(self):
        self.action_exit = QAction(QIcon(define.DEF_ICON_ACTION_EXIT), "退出(&Q)", self)
        self.action_exit.setShortcut("Ctrl+Q")
        self.action_exit.setStatusTip("退出当前系统")
        self.action_exit.triggered.connect(self.OnActionExit)
        
        self.action_about = QAction(QIcon(define.DEF_ICON_ACTION_ABOUT), "关于(&A)", self)
        self.action_about.setShortcut("Ctrl+A")
        self.action_about.setStatusTip("系统相关信息")
        self.action_about.triggered.connect(self.OnActionAbout)
        
        self.action_show = QAction(QIcon(define.DEF_ICON_ACTION_SHOW), "显示(&S)", self)
        self.action_show.setShortcut("Ctrl+S")
        self.action_show.setStatusTip("显示主界面")
        self.action_show.triggered.connect(self.OnShowMainWindow)
        
        self.action_hide = QAction(QIcon(define.DEF_ICON_ACTION_HIDE), "隐藏(&H)", self)
        self.action_hide.setShortcut("Ctrl+H")
        self.action_hide.setStatusTip("隐藏主界面")
        self.action_hide.triggered.connect(self.OnHideMainWindow)
        
        self.action_show_tab_1 = QAction(define.DEF_TEXT_MAIN_TAB_NAME_1, self)
        self.action_show_tab_1.setCheckable(True)
        self.action_show_tab_1.triggered.connect(self.OnShowTabWidget_1)
        
        self.action_show_tab_2 = QAction(define.DEF_TEXT_MAIN_TAB_NAME_2, self)
        self.action_show_tab_2.setCheckable(True)
        self.action_show_tab_2.triggered.connect(self.OnShowTabWidget_2)
        
        self.action_show_tab_3 = QAction(define.DEF_TEXT_MAIN_TAB_NAME_3, self)
        self.action_show_tab_3.setCheckable(True)
        self.action_show_tab_3.triggered.connect(self.OnShowTabWidget_3)
        
        self.action_show_skin_norm = QAction("系统默认", self)
        self.action_show_skin_norm.setCheckable(True)
        self.action_show_skin_norm.triggered.connect(self.OnShowSkinWidget_Norm)
        
        self.action_show_skin_dark = QAction("黑色炫酷", self)
        self.action_show_skin_dark.setCheckable(True)
        self.action_show_skin_dark.triggered.connect(self.OnShowSkinWidget_Dark)
        
        self.action_save_layout = QAction("保存布局", self)
        self.action_save_layout.setCheckable(True)
        self.action_save_layout.triggered.connect(self.OnActionSaveLayout)
        
        self.action_basic_data_maker = QAction(QIcon(define.DEF_ICON_ACTION_ABOUT), "基础数据(&B)", self)
        self.action_basic_data_maker.setShortcut("Ctrl+B")
        self.action_basic_data_maker.setStatusTip("基础数据生成工具")
        self.action_basic_data_maker.triggered.connect(self.OnActionBasicDataMaker)

    def CreateMenuBar(self):
        self.menu_file = self.menuBar().addMenu("文件(&F)")
        self.menu_file.addAction(self.action_exit)
        self.menu_tool = self.menuBar().addMenu("工具(&T)")
        self.menu_tool.addAction(self.action_basic_data_maker)
        self.menu_view = self.menuBar().addMenu("视图(&V)")
        self.menu_view_tooler = self.menu_view.addMenu(QIcon(define.DEF_ICON_MENU_VIEW_TOOLER), "工具条(&T)")
        self.menu_view_docker = self.menu_view.addMenu(QIcon(define.DEF_ICON_MENU_VIEW_DOCKER), "停靠栏(&D)")
        self.menu_view_tabser = self.menu_view.addMenu(QIcon(define.DEF_ICON_MENU_VIEW_TABSER), "标签页(&B)")
        self.menu_view_tabser.addAction(self.action_show_tab_1)
        self.menu_view_tabser.addAction(self.action_show_tab_2)
        self.menu_view_tabser.addAction(self.action_show_tab_3)
        self.menu_view_skiner = self.menu_view.addMenu(QIcon(define.DEF_ICON_MENU_VIEW_SKINER), "自定义(&S)")
        self.menu_view_skiner.addAction(self.action_show_skin_norm)
        self.menu_view_skiner.addAction(self.action_show_skin_dark)
        self.menu_view.addAction(self.action_save_layout)
        self.menu_help = self.menuBar().addMenu("帮助(&H)")
        self.menu_help.addAction(self.action_about)

    def CreateToolBar(self):
        self.tool_bar_system = QToolBar(self)
        self.tool_bar_system.setWindowTitle("系统工具栏")
        self.tool_bar_system.setObjectName("ToolBar_System") #
        self.tool_bar_system.setToolTip("系统工具栏")
        self.tool_bar_system.setIconSize(QSize(16, 16))
        self.tool_bar_system.addAction(self.action_about)
        self.addToolBar(Qt.TopToolBarArea, self.tool_bar_system)
        self.menu_view_tooler.addAction(self.tool_bar_system.toggleViewAction())
        
        self.tool_bar_quote = quote_center_bar.QuoteCenterBar(self)
        self.tool_bar_quote.setWindowTitle("行情工具栏")
        self.tool_bar_quote.setObjectName("ToolBar_Quote")
        self.tool_bar_quote.setToolTip("行情工具栏")
        self.tool_bar_quote.setIconSize(QSize(16, 16))
        self.tool_bar_quote.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.addToolBar(Qt.BottomToolBarArea, self.tool_bar_quote)
        self.menu_view_tooler.addAction(self.tool_bar_quote.toggleViewAction())
        
        self.addToolBarBreak(Qt.BottomToolBarArea)
        
        self.tool_bar_trade = trade_center_bar.TradeCenterBar(self)
        self.tool_bar_trade.setWindowTitle("交易工具栏")
        self.tool_bar_trade.setObjectName("ToolBar_Trade")
        self.tool_bar_trade.setToolTip("交易工具栏")
        self.tool_bar_trade.setIconSize(QSize(16, 16))
        self.tool_bar_trade.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.addToolBar(Qt.BottomToolBarArea, self.tool_bar_trade)
        self.menu_view_tooler.addAction(self.tool_bar_trade.toggleViewAction())

    def CreateStatusBar(self):
        self.status_label_a_1 = QLabel()
        self.status_label_a_1.setText(define.APP_TITLE_EN)
        self.status_label_a_1.setFont(QFont("SimSun", 10, QFont.Bold))
        paLogoText = QPalette()
        paLogoText.setColor(QPalette.WindowText, QColor(128, 0, 0))
        self.status_label_a_1.setPalette(paLogoText)
        
        self.status_label_a_2 = QLabel()
        self.status_label_a_2.setText("就绪")
        self.status_label_z_1 = QLabel()
        self.status_label_z_1.setText("    NULL    ")
        self.status_label_z_2 = QLabel()
        self.status_label_z_2.setText("    NULL    ")
        self.status_label_z_3 = QLabel()
        self.status_label_z_3.setText("    NULL    ")
        self.status_label_z_4 = QLabel()
        self.status_label_z_4.setText("    NULL    ")
        self.status_bar = self.statusBar()
        self.status_bar.addWidget(self.status_label_a_1)
        self.status_bar.addWidget(self.status_label_a_2)
        self.status_bar.addPermanentWidget(self.status_label_z_1)
        self.status_bar.addPermanentWidget(self.status_label_z_2)
        self.status_bar.addPermanentWidget(self.status_label_z_3)
        self.status_bar.addPermanentWidget(self.status_label_z_4)
        
        self.timer_show_date_time = QTimer()
        self.timer_show_date_time.timeout.connect(self.OnShowDateTime)
        self.timer_show_date_time.start(100)
        
        pub.subscribe(self.OnStatusBarInfo_1, "statusbar.info.show_1")
        pub.subscribe(self.OnStatusBarInfo_2, "statusbar.info.show_2")
        pub.subscribe(self.OnStatusBarInfo_3, "statusbar.info.show_3")

    def CreateTrayIcon(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.log_text = "本系统不支持托盘图标！"
            self.logger.SendMessage("W", 3, self.log_cate, self.log_text, "S")
            return
        
        QApplication.setQuitOnLastWindowClosed(False) # 点击主界面关闭按钮将不会结束程序，需要从托盘菜单退出
        
        self.tray_icon_menu = QMenu()
        self.tray_icon_menu.addAction(self.action_show)
        self.tray_icon_menu.addAction(self.action_hide)
        self.tray_icon_menu.addSeparator()
        self.tray_icon_menu.addAction(self.action_about)
        self.tray_icon_menu.addAction(self.action_exit)
        
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        
        self.tray_icon.setToolTip(define.TRAY_POP_START_TITLE)
        self.tray_icon.setIcon(QIcon(define.DEF_ICON_SYSTEM_TRAY))
        
        self.tray_icon.messageClicked.connect(self.OnTrayIconMsgClicked)
        self.tray_icon.activated.connect(self.OnTrayIconClicked)
        
        self.action_show.setEnabled(False)
        self.action_hide.setEnabled(True)
        
        self.tray_icon.show()
        
        self.is_tray_icon_loaded = True

    def CreateLogsDock(self):
        self.dock_logs_s = QDockWidget("系统日志", self)
        self.dock_logs_s.setObjectName("DockLogs_S") #
        self.dock_logs_s.setFont(QFont("SimSun", 9))
        self.dock_logs_s.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea | Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.log_info_panel_s = log_info_panel.LogInfoPanel(self)
        self.dock_logs_s.setWidget(self.log_info_panel_s)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_logs_s)
        self.menu_view_docker.addAction(self.dock_logs_s.toggleViewAction())
        
        self.dock_logs_t = QDockWidget("交易日志", self)
        self.dock_logs_t.setObjectName("DockLogs_T") #
        self.dock_logs_t.setFont(QFont("SimSun", 9))
        self.dock_logs_t.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea | Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.log_info_panel_t = log_info_panel.LogInfoPanel(self)
        self.dock_logs_t.setWidget(self.log_info_panel_t)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_logs_t)
        self.menu_view_docker.addAction(self.dock_logs_t.toggleViewAction())
        
        self.dock_logs_m = QDockWidget("监控日志", self)
        self.dock_logs_m.setObjectName("DockLogs_M") #
        self.dock_logs_m.setFont(QFont("SimSun", 9))
        self.dock_logs_m.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea | Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.log_info_panel_m = log_info_panel.LogInfoPanel(self)
        self.dock_logs_m.setWidget(self.log_info_panel_m)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_logs_m)
        self.menu_view_docker.addAction(self.dock_logs_m.toggleViewAction())
        
        self.dock_logs_a = QDockWidget("回测日志", self)
        self.dock_logs_a.setObjectName("DockLogs_A") #
        self.dock_logs_a.setFont(QFont("SimSun", 9))
        self.dock_logs_a.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea | Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.log_info_panel_a = log_info_panel.LogInfoPanel(self)
        self.dock_logs_a.setWidget(self.log_info_panel_a)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_logs_a)
        self.menu_view_docker.addAction(self.dock_logs_a.toggleViewAction())
        
        self.logger.SetLogInfoPanel_S(self.log_info_panel_s) # 必须
        self.logger.SetLogInfoPanel_T(self.log_info_panel_t) # 必须
        self.logger.SetLogInfoPanel_M(self.log_info_panel_m) # 必须
        self.logger.SetLogInfoPanel_A(self.log_info_panel_a) # 必须

    def TransStrToBool(self, value, default):
        value = value.lower()
        if value == "true":
            return True
        elif value == "false":
            return False
        else:
            return default

    # QDockWidget 和 QToolBar 都需设置对象名，这样才能 saveState() 和 restoreState() 状态、位置、大小等
    def ReadSettings(self):
        settings = QSettings("X-Lab-QuantX", define.APP_TITLE_EN) # 位于：HKEY_CURRENT_USER -> Software -> X-Lab-QuantX
        #settings = QSettings("./X-Lab-QuantX.ini", QSettings.IniFormat)
        
        self.is_not_first_run = self.TransStrToBool(settings.value("NotFirstRunFlag", ""), False)
        if self.is_not_first_run == False: # 首次运行，无保存值，为否，且菜单项“保存布局”为是
            self.WriteSettings() # 此时保存的是窗口初始化时的布局
        else: # 读取上次退出时保存的布局
            settings.beginGroup("MainWindow")
            self.restoreState(settings.value("MainWindowLayout", QVariant(QByteArray())))
            self.restoreGeometry(settings.value("MainWindowGeometry", QVariant(QByteArray())))
            self.main_widget.restoreGeometry(settings.value("MainWidgetGeometry", QVariant(QByteArray())))
            self.main_tab_widget.restoreGeometry(settings.value("MainTabWidgetGeometry", QVariant(QByteArray()))) # 貌似无法还原 Tab 页顺序
            self.current_main_tab_index = settings.value("MainTabWidgetCurrentTab", 0)
            self.action_show_tab_1.setChecked(self.TransStrToBool(settings.value("ActionShowTab_1", ""), True))
            self.action_show_tab_2.setChecked(self.TransStrToBool(settings.value("ActionShowTab_2", ""), True))
            self.action_show_tab_3.setChecked(self.TransStrToBool(settings.value("ActionShowTab_3", ""), True))
            self.action_show_skin_norm.setChecked(self.TransStrToBool(settings.value("ActionShowSkin_Norm", ""), True)) # True
            self.OnShowSkinWidget_Norm(self.TransStrToBool(settings.value("ActionShowSkin_Norm", ""), True)) # True
            self.action_show_skin_dark.setChecked(self.TransStrToBool(settings.value("ActionShowSkin_Dark", ""), False)) # False
            self.OnShowSkinWidget_Dark(self.TransStrToBool(settings.value("ActionShowSkin_Dark", ""), False)) # False
            self.action_save_layout.setChecked(self.TransStrToBool(settings.value("ActionSaveLayout", ""), False))
            # 目前不能还原退出时的标签页显示顺序，只能还原标签页是否显示
            self.OnShowTabWidget_1(self.TransStrToBool(settings.value("ActionShowTab_1", ""), True))
            self.OnShowTabWidget_2(self.TransStrToBool(settings.value("ActionShowTab_2", ""), True))
            self.OnShowTabWidget_3(self.TransStrToBool(settings.value("ActionShowTab_3", ""), True))
            # 放在 ShowTabWidget_1、ShowTabWidget_2、ShowTabWidget_3 之后，防止篡改当前标签页
            self.main_tab_widget.setCurrentIndex(self.current_main_tab_index) # 在变换了 Tab 页位置后将无意义
            self.main_tab_widget.setTabIcon(self.current_main_tab_index, QIcon(define.DEF_ICON_MAIN_TAB_SHOW))
            for i in range(self.main_tab_widget.count()):
                if i != self.current_main_tab_index:
                    self.main_tab_widget.setTabIcon(i, QIcon(define.DEF_ICON_MAIN_TAB_HIDE))
            settings.endGroup()
        
        self.log_text = "用户界面设置导入完成。"
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")

    # QDockWidget 和 QToolBar 都需设置对象名，这样才能 saveState() 和 restoreState() 状态、位置、大小等
    def WriteSettings(self):
        settings = QSettings("X-Lab-QuantX", define.APP_TITLE_EN) # 位于：HKEY_CURRENT_USER -> Software -> X-Lab-QuantX
        #settings = QSettings("./X-Lab-QuantX.ini", QSettings.IniFormat)
        
        if self.action_save_layout.isChecked() == True:
            settings.setValue("NotFirstRunFlag", True) # 始终为真
            settings.beginGroup("MainWindow")
            settings.setValue("MainWindowLayout", self.saveState())
            settings.setValue("MainWindowGeometry", self.saveGeometry())
            settings.setValue("MainWidgetGeometry", self.main_widget.saveGeometry())
            settings.setValue("MainTabWidgetGeometry", self.main_tab_widget.saveGeometry()) # 貌似无法保存 Tab 页顺序
            settings.setValue("MainTabWidgetCurrentTab", self.main_tab_widget.currentIndex()) # 在变换了 Tab 页位置后将无意义
            settings.setValue("ActionShowTab_1", self.action_show_tab_1.isChecked())
            settings.setValue("ActionShowTab_2", self.action_show_tab_2.isChecked())
            settings.setValue("ActionShowTab_3", self.action_show_tab_3.isChecked())
            settings.setValue("ActionShowSkin_Norm", self.action_show_skin_norm.isChecked())
            settings.setValue("ActionShowSkin_Dark", self.action_show_skin_dark.isChecked())
            settings.setValue("ActionSaveLayout", self.action_save_layout.isChecked())
            settings.endGroup()
        else:
            settings.setValue("NotFirstRunFlag", True) # 始终为真
            settings.beginGroup("MainWindow")
            settings.setValue("MainWindowLayout", QByteArray())
            settings.setValue("MainWindowGeometry", QByteArray())
            settings.setValue("MainWidgetGeometry", QByteArray())
            settings.setValue("MainTabWidgetGeometry", QByteArray())
            settings.setValue("MainTabWidgetCurrentTab", 0)
            settings.setValue("ActionShowTab_1", True)
            settings.setValue("ActionShowTab_2", True)
            settings.setValue("ActionShowTab_3", True)
            settings.setValue("ActionShowSkin_Norm", True)
            settings.setValue("ActionShowSkin_Dark", False)
            settings.setValue("ActionSaveLayout", self.action_save_layout.isChecked()) # 只有这个保存现值，其他均保存原值
            settings.endGroup()
        
        self.log_text = "用户界面设置导出完成。"
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")

    def RemoveSettings(self, str_key):
        settings = QSettings("X-Lab-QuantX", define.APP_TITLE_EN)
        #settings = QSettings("./X-Lab-QuantX.ini", QSettings.IniFormat)
        settings.remove(str_key)

    def SystemStart(self):
        self.log_text = "开始系统初始化 ..."
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        
        self.basicx = basicx.BasicX()
        if self.config.cfg_main.data_db_need == 0:
            self.basicx.InitBasicData(folder = self.config.cfg_main.data_folder) # 不使用数据库
        if self.config.cfg_main.data_db_need == 1:
            self.basicx.InitBasicData(host = self.config.cfg_main.data_db_host, port = self.config.cfg_main.data_db_port, 
                                      user = self.config.cfg_main.data_db_user, passwd = self.config.cfg_main.data_db_pass, 
                                      folder = self.config.cfg_main.data_folder)
        
        self.trader = trader.Trader()
        self.trader.start()
        
        self.strate = strate.Strate()
        self.strate.LoadStrategy()
        self.main_tab_panel_1.OnReloadStrategy()
        self.strate.start()
        
        self.log_text = "系统初始化完成。"
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        
        self.CreateTrayIcon()
        
        self.log_text = "加载系统托盘图标完成。"
        self.logger.SendMessage("I", 1, self.log_cate, self.log_text, "S")
        
        self.OnShowTrayIconMsg(define.APP_TITLE_EN + " " + define.APP_VERSION)

    def SystemStop(self):
        if self.trader.started == True:
            self.trader.stop()
        if self.strate.started == True:
            self.strate.stop()
        if self.logger.started == True:
            self.logger.StopServer()
        pub.unsubAll()

    def closeEvent(self, event):
        if self.is_user_exit == False:
            #QMessageBox.information(self, "提示", "程序将继续运行，如需退出，请点击托盘图标。", QMessageBox.Ok)
            self.OnHideMainWindow()
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def OnShowDateTime(self):
        time_now = time.localtime(time.time())
        str_date_time = time.strftime("%Y-%m-%d %A %H:%M:%S", time_now)
        self.status_label_z_4.setText(str_date_time)

    def OnStatusBarInfo_1(self, msg):
        self.status_label_z_1.setText(msg)

    def OnStatusBarInfo_2(self, msg):
        self.status_label_z_2.setText(msg)

    def OnStatusBarInfo_3(self, msg):
        self.status_label_z_3.setText(msg)

    def OnActionExit(self):
        reply = QMessageBox.question(self, "询问", "确认退出当前系统？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.is_user_exit = True
            self.SystemStop()
            self.WriteSettings() # 保存界面属性
            self.timer_show_date_time.stop()
            del self.timer_show_date_time
            QApplication.setQuitOnLastWindowClosed(True)
            self.tray_icon.hide()
            self.close()
            self.log_text = "用户 退出 当前系统！"
            self.logger.SendMessage("E", 4, self.log_cate, self.log_text, "S")

    def OnActionAbout(self):
        if self.about_dialog == None:
            self.about_dialog = about_dialog.AboutDialog(self)
        self.about_dialog.show()

    def OnTrayIconClicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            pass
        elif reason == QSystemTrayIcon.DoubleClick:
            if self.is_main_window_visible == True:
                self.OnHideMainWindow()
            else:
                self.OnShowMainWindow()
        elif reason == QSystemTrayIcon.MiddleClick:
            self.OnTrayIconMsgClicked()

    def OnShowMainWindow(self):
        self.show()
        self.is_main_window_visible = True
        self.action_show.setEnabled(False)
        self.action_hide.setEnabled(True)

    def OnHideMainWindow(self):
        self.hide()
        self.is_main_window_visible = False
        self.action_show.setEnabled(True)
        self.action_hide.setEnabled(False)

    def OnTrayIconMsgClicked(self):
        QMessageBox.information(self, "提示", "小兔子乖乖，把门儿开开。", QMessageBox.Ok)

    def OnShowTrayIconMsg(self, msg, type = "info", time = 5000):
        if self.is_tray_icon_loaded == True:
            if type == "info":
                self.tray_icon.showMessage(define.TRAY_POP_TITLE_INFO, msg, QSystemTrayIcon.Information, time)
            elif type == "warn":
                self.tray_icon.showMessage(define.TRAY_POP_TITLE_WARN, msg, QSystemTrayIcon.Warning, time)
            elif type == "error":
                self.tray_icon.showMessage(define.TRAY_POP_TITLE_ERROR, msg, QSystemTrayIcon.Critical, time)

    def OnShowSkinWidget_Norm(self, show):
        if show == True:
            self.action_show_skin_dark.setChecked(False)
            QApplication.instance().setStyleSheet("")
            self.logger.ChangeInfoMsgColor() #
        else:
            if self.is_system_initialization == False: # 避免初始化过程中 action_show_skin_norm 被触发
                self.action_show_skin_norm.setChecked(True)
                self.action_show_skin_dark.setChecked(False)

    def OnShowSkinWidget_Dark(self, show):
        if show == True:
            self.action_show_skin_norm.setChecked(False)
            QApplication.instance().setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
            self.logger.ChangeInfoMsgColor() #
        else:
            if self.is_system_initialization == False: # 避免初始化过程中 action_show_skin_norm 被触发
                self.action_show_skin_norm.setChecked(False)
                self.action_show_skin_dark.setChecked(True)

    def OnActionSaveLayout(self, save):
        if save == True:
            self.logger.SendMessage("I", 1, self.log_cate, "用户 启用 窗口布局保存。", "S")
            QMessageBox.information(self, "提示", "在系统退出时将 保存 窗口布局。", QMessageBox.Ok)
        else:
            self.logger.SendMessage("I", 1, self.log_cate, "用户 取消 窗口布局保存。", "S")
            QMessageBox.information(self, "提示", "在系统退出时将 忽略 窗口布局。", QMessageBox.Ok)

    def OnShowTabWidget_1(self, show):
        if show == True:
            index = self.main_tab_widget.addTab(self.main_tab_panel_1, define.DEF_TEXT_MAIN_TAB_NAME_1)
            self.main_tab_widget.setTabIcon(index, QIcon(define.DEF_ICON_MAIN_TAB_SHOW))
            self.main_tab_widget.setCurrentIndex(index) # 显示为当前的
            for i in range(self.main_tab_widget.count()):
                if i != index:
                    self.main_tab_widget.setTabIcon(i, QIcon(define.DEF_ICON_MAIN_TAB_HIDE))
        else:
            for i in range(self.main_tab_widget.count()):
                if define.DEF_TEXT_MAIN_TAB_NAME_1 == self.main_tab_widget.tabText(i).__str__(): # .__str__()
                    self.main_tab_widget.removeTab(i)
                    break
            index = self.main_tab_widget.currentIndex()
            self.main_tab_widget.setTabIcon(index, QIcon(define.DEF_ICON_MAIN_TAB_SHOW))

    def OnShowTabWidget_2(self, show):
        if show == True:
            index = self.main_tab_widget.addTab(self.main_tab_panel_2, define.DEF_TEXT_MAIN_TAB_NAME_2)
            self.main_tab_widget.setTabIcon(index, QIcon(define.DEF_ICON_MAIN_TAB_SHOW))
            self.main_tab_widget.setCurrentIndex(index) # 显示为当前的
            for i in range(self.main_tab_widget.count()):
                if i != index:
                    self.main_tab_widget.setTabIcon(i, QIcon(define.DEF_ICON_MAIN_TAB_HIDE))
        else:
            for i in range(self.main_tab_widget.count()):
                if define.DEF_TEXT_MAIN_TAB_NAME_2 == self.main_tab_widget.tabText(i).__str__(): # .__str__()
                    self.main_tab_widget.removeTab(i)
                    break
            index = self.main_tab_widget.currentIndex()
            self.main_tab_widget.setTabIcon(index, QIcon(define.DEF_ICON_MAIN_TAB_SHOW))

    def OnShowTabWidget_3(self, show):
        if show == True:
            index = self.main_tab_widget.addTab(self.main_tab_panel_3, define.DEF_TEXT_MAIN_TAB_NAME_3)
            self.main_tab_widget.setTabIcon(index, QIcon(define.DEF_ICON_MAIN_TAB_SHOW))
            self.main_tab_widget.setCurrentIndex(index) # 显示为当前的
            for i in range(self.main_tab_widget.count()):
                if i != index:
                    self.main_tab_widget.setTabIcon(i, QIcon(define.DEF_ICON_MAIN_TAB_HIDE))
        else:
            for i in range(self.main_tab_widget.count()):
                if define.DEF_TEXT_MAIN_TAB_NAME_3 == self.main_tab_widget.tabText(i).__str__(): # .__str__()
                    self.main_tab_widget.removeTab(i)
                    break
            index = self.main_tab_widget.currentIndex()
            self.main_tab_widget.setTabIcon(index, QIcon(define.DEF_ICON_MAIN_TAB_SHOW))

    def OnClickMainTabBar(self, index): # 左键单击和双击都会响应
        self.main_tab_widget.setTabIcon(index, QIcon(define.DEF_ICON_MAIN_TAB_SHOW))
        for i in range(self.main_tab_widget.count()):
            if i != index:
                self.main_tab_widget.setTabIcon(i, QIcon(define.DEF_ICON_MAIN_TAB_HIDE))

    def OnActionBasicDataMaker(self):
        if self.basic_data_maker == None:
            self.basic_data_maker = basic_data_maker.BasicDataMaker(folder = self.config.cfg_main.data_folder)
            self.basic_data_maker.SetMsSQL(host = self.config.cfg_main.jysj_db_host, port = self.config.cfg_main.jysj_db_port, 
                                           user = self.config.cfg_main.jysj_db_user, password = self.config.cfg_main.jysj_db_pass, 
                                           database = self.config.cfg_main.jysj_db_name_jydb, charset = self.config.cfg_main.jysj_db_charset)
            if self.config.cfg_main.data_db_need == 1: # 否则不保存数据到数据库
                self.basic_data_maker.SetMySQL(host = self.config.cfg_main.data_db_host, port = self.config.cfg_main.data_db_port, 
                                               user = self.config.cfg_main.data_db_user, passwd = self.config.cfg_main.data_db_pass, 
                                               db = self.config.cfg_main.data_db_name_financial, charset = self.config.cfg_main.data_db_charset)
        self.basic_data_maker.show()
