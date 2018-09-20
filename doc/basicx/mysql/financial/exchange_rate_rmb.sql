/*
Navicat MySQL Data Transfer

Source Server         : 10.0.7.53
Source Server Version : 50717
Source Host           : 10.0.7.53:3306
Source Database       : financial

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001

Date: 2017-02-09 15:10:33
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for exchange_rate
-- ----------------------------
DROP TABLE IF EXISTS `exchange_rate`;
CREATE TABLE `exchange_rate` (
  `id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号',
  `base_money` varchar(8) NOT NULL DEFAULT '' COMMENT '基础货币，RMB',
  `price` float(16,4) NOT NULL DEFAULT '0.0000' COMMENT '汇率价格，人民币元 / 100外币',
  `exchange_money` varchar(8) NOT NULL DEFAULT '' COMMENT '汇兑货币，USD、HKD',
  `quote_type` int(8) DEFAULT '0' COMMENT '标价方式，1 直接、2 间接',
  `end_date` date NOT NULL COMMENT '截止日期',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_base_money_exchange_money_end_date` (`base_money`,`exchange_money`,`end_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
