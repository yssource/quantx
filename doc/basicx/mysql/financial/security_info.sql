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
-- Table structure for security_info
-- ----------------------------
DROP TABLE IF EXISTS `security_info`;
CREATE TABLE `security_info` (
  `id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号',
  `inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码',
  `company` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '公司代码',
  `market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，SH、SZ',
  `code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码',
  `name` varchar(32) DEFAULT '' COMMENT '证券名称',
  `category` int(8) DEFAULT '0' COMMENT '证券类别，详见说明',
  `sector` int(8) DEFAULT '0' COMMENT '上市板块，详见说明',
  `is_st` int(8) DEFAULT '0' COMMENT '是否ST股，0:否、1:是',
  `list_state` int(8) DEFAULT '0' COMMENT '上市状态，详见说明',
  `list_date` date COMMENT '上市日期',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_inners` (`inners`),
  UNIQUE KEY `idx_company` (`company`),
  UNIQUE KEY `idx_market_code` (`market`,`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
