/*
Navicat MySQL Data Transfer

Source Server         : 10.0.7.53
Source Server Version : 50717
Source Host           : 10.0.7.53:3306
Source Database       : financial

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001

Date: 2017-09-04 15:10:33
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for trading_day
-- ----------------------------
DROP TABLE IF EXISTS `trading_day`;
CREATE TABLE `trading_day` (
  `id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号',
  `natural_date` date NOT NULL COMMENT '日期',
  `market` int(4) unsigned NOT NULL DEFAULT '0' COMMENT '证券市场，72、83、89',
  `trading_day` int(1) DEFAULT '0' COMMENT '是否交易',
  `week_end` int(1) DEFAULT '0' COMMENT '是否周末',
  `month_end` int(1) DEFAULT '0' COMMENT '是否月末',
  `quarter_end` int(1) DEFAULT '0' COMMENT '是否季末',
  `year_end` int(1) DEFAULT '0' COMMENT '是否年末',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_natural_date_market` (`natural_date`,`market`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
