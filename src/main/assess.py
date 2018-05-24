
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

import os
import datetime

import xlrd
import numpy as np
import pandas as pd

import common
import evaluate

pd.set_option("max_colwidth", 200)
pd.set_option("display.width", 500)
#pd.set_option("display.max_row", 500)
#pd.set_option("display.max_columns", 100)

class DailyReportItem(object):
    def __init__(self, **kwargs):
        self.trade_date = kwargs.get("trade_date", datetime.datetime(1970, 1, 1))
        self.account_id = kwargs.get("account_id", "")
        self.net_unit = kwargs.get("net_unit", 0.0)
        self.net_cumulative = kwargs.get("net_cumulative", 0.0)
        self.refer_index = kwargs.get("refer_index", 0.0)

    def ToString(self):
        return "trade_date：%s, " % self.trade_date.strftime("%Y-%m-%d") + \
               "account_id：%s, " % self.account_id + \
               "net_unit：%f, " % self.net_unit + \
               "net_cumulative：%f, " % self.net_cumulative + \
               "refer_index：%f" % self.refer_index

class Assess():
    def __init__(self, **kwargs):
        self.log_text = ""
        self.log_cate = "Assess"
        self.sheet_daily_report = "daily_report"
        self.data_folder = kwargs.get("data_folder", "") # 数据文件夹
        self.save_folder = kwargs.get("save_folder", "") # 保存文件夹
        
        self.folder_assess = ""
        if self.data_folder != "":
            self.folder_assess = self.data_folder + "/assess"
            if not os.path.exists(self.folder_assess):
                os.makedirs(self.folder_assess)

    def __del__(self):
        pass

    def SendMessage(self, log_type, log_cate, log_info):
        print("%s %s %s <%s> - %s" % (common.GetDateShort(), common.GetTimeShort(), log_type, log_cate, log_info))

    def SaveDailyReport(self, data_file):
        daily_report_list = []
        xls_file = xlrd.open_workbook(data_file)
        try:
            xls_sheet = xls_file.sheet_by_name(self.sheet_daily_report)
        except:
            self.log_text = "每日报表文件 %s 表单异常！%s" % (data_file, self.sheet_daily_report)
            self.SendMessage("E", self.log_cate, self.log_text)
            return False
        xls_rows = xls_sheet.nrows
        xls_cols = xls_sheet.ncols
        if xls_rows < 2:
            self.log_text = "每日报表文件 %s 行数异常！%d" % (data_file, xls_rows)
            self.SendMessage("E", self.log_cate, self.log_text)
            return False
        if xls_cols < 5:
            self.log_text = "每日报表文件 %s 列数异常！%d" % (data_file, xls_cols)
            self.SendMessage("E", self.log_cate, self.log_text)
            return False
        for i in range(xls_rows):
            if i > 0:
                trade_date = common.TransDateIntToDate(int(xls_sheet.row(i)[0].value))
                account_id = xls_sheet.row(i)[1].value
                net_unit = xls_sheet.row(i)[2].value
                net_cumulative = xls_sheet.row(i)[3].value
                refer_index = xls_sheet.row(i)[4].value
                daily_report_item = DailyReportItem(trade_date = trade_date, account_id = account_id, net_unit = net_unit, net_cumulative = net_cumulative, refer_index = refer_index)
                daily_report_list.append(daily_report_item)
        #for item in daily_report_list:
        #    print(item.ToString())
        self.log_text = "导入每日报表数据 %d 行。%s" % (len(daily_report_list), data_file)
        self.SendMessage("I", self.log_cate, self.log_text)
        
        if len(daily_report_list) > 0:
            columns = ["trade_date", "account_id", "net_unit", "net_cumulative", "refer_index"]
            result = pd.DataFrame(columns = columns) # 空
            if self.folder_assess == "": # 缓存路径为空
                self.SendMessage("E", self.log_cate, "缓存数据 每日报表 时，本地数据缓存路径为空！")
            else:
                result = pd.DataFrame(data = [[item.trade_date, item.account_id, item.net_unit, item.net_cumulative, item.refer_index] for item in daily_report_list], columns = columns)
                save_path = "%s/%s" % (self.folder_assess, self.sheet_daily_report)
                result.to_pickle(save_path)
            #if not result.empty:
            #    print(result)
            self.log_text = "每日报表数据缓存 %d 条。%s" % (result.shape[0], save_path)
            self.SendMessage("I", self.log_cate, self.log_text)
        
        return True

    def GetDailyReport(self, account, date_s, date_e):
        save_path = ""
        date_date_s = common.TransDateIntToDate(date_s)
        date_date_e = common.TransDateIntToDate(date_e)
        columns = ["trade_date", "account_id", "net_unit", "net_cumulative", "refer_index"]
        result = pd.DataFrame(columns = columns) # 空
        if self.folder_assess == "": # 缓存路径为空
            self.SendMessage("E", self.log_cate, "直接缓存获取 每日报表 时，本地数据缓存路径为空！")
        else:
            save_path = "%s/%s" % (self.folder_assess, self.sheet_daily_report)
            if not os.path.exists(save_path): # 缓存文件不存在
                self.SendMessage("E", self.log_cate, "直接缓存获取 每日报表 时，本地数据缓存文件不存在！")
            else: # 读取缓存文件
                result = pd.read_pickle(save_path)
                self.SendMessage("I", self.log_cate, "本地缓存 获取 %d 条 每日报表 数据。" % result.shape[0])
                result = result.ix[(result.account_id == account), :] # 如果上传的数据只是单账户的则可以省略这步
                result = result.ix[(result.trade_date >= date_date_s) & (result.trade_date <= date_date_e), :]
                self.SendMessage("I", self.log_cate, "本地缓存 滤得 %d 条 每日报表 数据。" % result.shape[0])
        if result.empty:
            self.SendMessage("W", self.log_cate, "获取的 每日报表 为空！")
        return result

    def StrategyEvaluation(self, daily_report):
        daily_report = daily_report.sort_values(by = ["trade_date"], ascending = True).reset_index(drop = True) # 日期从早到晚排序
        if not daily_report.empty:
            self.evaluate = evaluate.Evaluate(daily_report = daily_report)
            average_daily_net_rise = self.evaluate.CalcAverageDailyNetRise() # 001
            max_period_return, min_period_return = self.evaluate.CalcMaxMinPeriodReturn() # 002
            go_up_probability = self.evaluate.CalcGoUpProbability() # 003
            max_days_keep_up, max_days_keep_down = self.evaluate.CalcMaxDaysKeepUpOrDown() # 004
            max_drawdown_value, max_drawdown_date, drawdown_start_date = self.evaluate.CalcMaxDrawdown() # 005
            annual_return_rate, index_annual_return_rate = self.evaluate.CalcAnnualReturnRate() # 006
            return_volatility = self.evaluate.CalcReturnVolatility() # 007
            sharpe_ratio = self.evaluate.CalcSharpeRatio(annual_return_rate, return_volatility) # 008
            beta_value = self.evaluate.CalcBetaValue() # 009
            alpha_value = self.evaluate.CalcAlphaValue(annual_return_rate, index_annual_return_rate, beta_value) # 010
            info_ratio = self.evaluate.CalcInfoRatio() # 011
            print("平均每日净值涨幅：%f" % average_daily_net_rise)
            print("单周期最大涨幅：%f," % max_period_return, "单周期最大跌幅：%f" % min_period_return)
            print("上涨概率：%f" % go_up_probability)
            print("最大连续上涨天数：%f," % max_days_keep_up, "最大连续下跌天数：%f" % max_days_keep_down)
            print("最大回撤：%f," % max_drawdown_value, "最大回撤日期：%s," % max_drawdown_date.strftime("%Y-%m-%d"), "回撤开始日期：%s" % drawdown_start_date.strftime("%Y-%m-%d"))
            print("年化收益率：%f," % annual_return_rate, "参照指数年化收益率：%f" % index_annual_return_rate)
            print("收益波动率：%f" % return_volatility)
            print("夏普比率：%f" % sharpe_ratio)
            print("贝塔值：%f" % beta_value)
            print("阿尔法值：%f" % alpha_value)
            print("信息比率：%f" % info_ratio)
            self.evaluate.MakeNetValueCompare(self.save_folder) # 012

if __name__ == "__main__":
    data_folder = "../data"
    save_folder = "../../doc"
    daily_report_file = "../../doc/daily_report.xlsx"
    assess = Assess(data_folder = data_folder, save_folder = save_folder)
    ret = assess.SaveDailyReport(daily_report_file)
    if ret == True:
        daily_report = assess.GetDailyReport("LHTZ_20170428001", 20170101, 20180228)
        if not daily_report.empty:
            assess.StrategyEvaluation(daily_report)
