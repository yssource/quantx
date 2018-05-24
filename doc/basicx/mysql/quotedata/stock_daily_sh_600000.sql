/*
Navicat MySQL Data Transfer

Source Server         : 10.0.7.53
Source Server Version : 50717
Source Host           : 10.0.7.53:3306
Source Database       : quotedata

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001

Date: 2017-02-09 15:10:33
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for stock_daily_sh_600000
-- ----------------------------
DROP TABLE IF EXISTS `stock_daily_sh_600000`;
CREATE TABLE `stock_daily_sh_600000` (
  `id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号',
  `date` date NOT NULL COMMENT '日期',
  `open` float(10,3) DEFAULT '0.000' COMMENT '开盘价',
  `high` float(10,3) DEFAULT '0.000' COMMENT '最高价',
  `low` float(10,3) DEFAULT '0.000' COMMENT '最低价',
  `close` float(10,3) DEFAULT '0.000' COMMENT '收盘价',
  `volume` bigint(64) DEFAULT '0' COMMENT '成交量，股',
  `turnover` bigint(64) DEFAULT '0' COMMENT '成交额，元',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
