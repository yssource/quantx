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
-- Table structure for industry_data
-- ----------------------------
DROP TABLE IF EXISTS `industry_data`;
CREATE TABLE `industry_data` (
  `id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号',
  `standard` int(32) NOT NULL DEFAULT '0' COMMENT '行业划分标准',
  `industry` int(32) NOT NULL DEFAULT '0' COMMENT '所属行业',
  `industry_code_1` varchar(32) DEFAULT '' COMMENT '一级行业代码',
  `industry_name_1` varchar(100) DEFAULT '' COMMENT '一级行业名称',
  `industry_code_2` varchar(32) DEFAULT '' COMMENT '二级行业代码',
  `industry_name_2` varchar(100) DEFAULT '' COMMENT '二级行业名称',
  `industry_code_3` varchar(32) DEFAULT '' COMMENT '三级行业代码',
  `industry_name_3` varchar(100) DEFAULT '' COMMENT '三级行业名称',
  `industry_code_4` varchar(32) DEFAULT '' COMMENT '四级行业代码',
  `industry_name_4` varchar(100) DEFAULT '' COMMENT '四级行业名称',
  `inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码',
  `market` varchar(32) NOT NULL DEFAULT '' COMMENT '证券市场，SH、SZ',
  `code` varchar(32) NOT NULL DEFAULT '' COMMENT '证券代码',
  `name` varchar(32) DEFAULT '' COMMENT '证券名称',
  `info_date` date NOT NULL COMMENT '信息日期',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_standard_industry_market_code_info_date` (`standard`,`industry`,`market`,`code`,`info_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
