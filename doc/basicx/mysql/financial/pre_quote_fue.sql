/*
Navicat MySQL Data Transfer

Source Server         : 10.0.7.53
Source Server Version : 50717
Source Host           : 10.0.7.53:3306
Source Database       : financial

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001

Date: 2017-12-20 15:10:33
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for pre_quote_fue
-- ----------------------------
DROP TABLE IF EXISTS `pre_quote_fue`;
CREATE TABLE `pre_quote_fue` (
  `id` int(32) unsigned NOT NULL AUTO_INCREMENT COMMENT '序号',
  `inners` int(32) unsigned NOT NULL DEFAULT '0' COMMENT '内部代码',
  `market` varchar(32) NOT NULL DEFAULT '' COMMENT '合约市场，详见说明',
  `code` varchar(32) NOT NULL DEFAULT '' COMMENT '合约代码',
  `open` float(16,4) DEFAULT '0.0000' COMMENT '开盘价',
  `high` float(16,4) DEFAULT '0.0000' COMMENT '最高价',
  `low` float(16,4) DEFAULT '0.0000' COMMENT '最低价',
  `close` float(16,4) DEFAULT '0.0000' COMMENT '收盘价',
  `settle` float(16,4) DEFAULT '0.0000' COMMENT '结算价',
  `pre_close` float(16,4) DEFAULT '0.0000' COMMENT '昨收价',
  `pre_settle` float(16,4) DEFAULT '0.0000' COMMENT '昨结价',
  `volume` bigint(64) DEFAULT '0' COMMENT '成交量，手',
  `turnover` double(64,2) DEFAULT '0.00' COMMENT '成交额，元',
  `open_interest` bigint(64) DEFAULT '0' COMMENT '持仓量，手',
  `chg_open_interest` bigint(64) DEFAULT '0' COMMENT '持仓量变化，手',
  `basis_value` float(16,4) DEFAULT '0.0000' COMMENT '基差',
  `main_flag` int(8) DEFAULT '0' COMMENT '主力标志，1 是、0 否',
  `quote_date` date DEFAULT NULL COMMENT '行情日期，2015-12-31',
  `quote_time` datetime(6) DEFAULT NULL COMMENT '行情时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_market_code` (`market`,`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
