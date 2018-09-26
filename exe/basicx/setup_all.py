
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

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

path = "../../src/main" # 不用斜杠结尾

file_dict = \
    {
    "basicx" : ["%s/port/basicx.py" % path],
    "dbm_mongo" : ["%s/dbm_mongo.py" % path],
    "dbm_mysql" : ["%s/dbm_mysql.py" % path]
    }

for file_name, file_path in file_dict.items():
    print("模块 %s 开始编译：\r\n" % file_name)
    setup(cmdclass = {"build_ext": build_ext}, ext_modules = [Extension(file_name, file_path)])
    print("\r\n模块 %s 编译完成。\r\n" % file_name)

print("项目编译完成，共计 %d 个。\r\n" % len(file_dict.keys()))
