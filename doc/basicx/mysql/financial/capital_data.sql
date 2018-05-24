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
-- Table structure for capital_data
-- ----------------------------
DROP TABLE IF EXISTS `capital_data`;
CREATE TABLE `capital_data` (
  `id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号',
  `inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码',
  `market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，SH、SZ',
  `code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码',
  `name` varchar(32) DEFAULT '' COMMENT '证券名称',
  `end_date` date NOT NULL COMMENT '截止日期',
  `total_shares` bigint(64) DEFAULT '0' COMMENT '总股本，股',
  `circu_shares` bigint(64) DEFAULT '0' COMMENT '流通股本，股，A股',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_market_code_end_date` (`market`,`code`,`end_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
