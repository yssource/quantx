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
-- Table structure for ex_rights_data
-- ----------------------------
DROP TABLE IF EXISTS `ex_rights_data`;
CREATE TABLE `ex_rights_data` (
  `id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号',
  `inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码',
  `market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，SH、SZ',
  `code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码',
  `date` date NOT NULL COMMENT '除权除息日期',
  `muler` float(16,7) DEFAULT '0.0000000' COMMENT '乘数',
  `adder` float(16,7) DEFAULT '0.0000000' COMMENT '加数',
  `sg` float(16,7) DEFAULT '0.0000000' COMMENT '送股比率，每股，非百分比',
  `pg` float(16,7) DEFAULT '0.0000000' COMMENT '配股比率，每股，非百分比',
  `price` float(10,3) DEFAULT '0.000' COMMENT '配股价，元',
  `bonus` float(16,7) DEFAULT '0.0000000' COMMENT '现金红利，每股，元',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_market_code_date` (`market`,`code`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
