/*
Navicat MySQL Data Transfer

Source Server         : 10.0.7.53
Source Server Version : 50717
Source Host           : 10.0.7.53:3306
Source Database       : financial

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001

Date: 2017-12-21 15:10:33
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for tod_ting_pai
-- ----------------------------
DROP TABLE IF EXISTS `tod_ting_pai`;
CREATE TABLE `tod_ting_pai` (
  `id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号',
  `inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码',
  `market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，SH、SZ',
  `code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码',
  `name` varchar(32) DEFAULT '' COMMENT '证券名称',
  `category` int(8) DEFAULT '0' COMMENT '证券类别，详见说明',
  `tp_date` datetime(6) DEFAULT NULL COMMENT '停牌日期',
  `tp_time` varchar(30) DEFAULT '' COMMENT '停牌时间',
  `tp_reason` varchar(110) DEFAULT '' COMMENT '停牌原因',
  `tp_statement` int(8) DEFAULT '0' COMMENT '停牌事项说明，详见说明',
  `tp_term` varchar(60) DEFAULT '' COMMENT '停牌期限',
  `fp_date` datetime(6) DEFAULT NULL COMMENT '复牌日期',
  `fp_time` varchar(30) DEFAULT '' COMMENT '复牌时间',
  `fp_statement` varchar(110) DEFAULT '' COMMENT '复牌事项说明',
  `update_time` datetime(6) DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_market_code` (`market`,`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
