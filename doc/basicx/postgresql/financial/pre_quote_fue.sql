/*
Navicat PGSQL Data Transfer

Source Server         : 10.0.7.53
Source Server Version : 90601
Source Host           : 10.0.7.53:5432
Source Database       : financial
Source Schema         : public

Target Server Type    : PGSQL
Target Server Version : 90601
File Encoding         : 65001

Date: 2017-12-20 17:01:19
*/


-- ----------------------------
-- Table structure for pre_quote_fue
-- ----------------------------
DROP TABLE IF EXISTS "public"."pre_quote_fue";
CREATE TABLE "public"."pre_quote_fue" (
"id" serial NOT NULL,
"inners" int4 NOT NULL DEFAULT 0,
"market" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"code" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"open" float4 DEFAULT 0.0000,
"high" float4 DEFAULT 0.0000,
"low" float4 DEFAULT 0.0000,
"close" float4 DEFAULT 0.0000,
"settle" float4 DEFAULT 0.0000,
"pre_close" float4 DEFAULT 0.0000,
"pre_settle" float4 DEFAULT 0.0000,
"volume" int8 DEFAULT 0,
"turnover" float8 DEFAULT 0.00,
"open_interest" int8 DEFAULT 0,
"chg_open_interest" int8 DEFAULT 0,
"basis_value" float4 DEFAULT 0.0000,
"main_flag" int4 DEFAULT 0,
"quote_date" date,
"quote_time" timestamp
)
WITH (OIDS=FALSE);
COMMENT ON COLUMN "public"."pre_quote_fue"."id" IS '序号';
COMMENT ON COLUMN "public"."pre_quote_fue"."inners" IS '内部代码';
COMMENT ON COLUMN "public"."pre_quote_fue"."market" IS '合约市场，详见说明';
COMMENT ON COLUMN "public"."pre_quote_fue"."code" IS '合约代码';
COMMENT ON COLUMN "public"."pre_quote_fue"."open" IS '开盘价';
COMMENT ON COLUMN "public"."pre_quote_fue"."high" IS '最高价';
COMMENT ON COLUMN "public"."pre_quote_fue"."low" IS '最低价';
COMMENT ON COLUMN "public"."pre_quote_fue"."close" IS '收盘价';
COMMENT ON COLUMN "public"."pre_quote_fue"."settle" IS '结算价';
COMMENT ON COLUMN "public"."pre_quote_fue"."pre_close" IS '昨收价';
COMMENT ON COLUMN "public"."pre_quote_fue"."pre_settle" IS '昨结价';
COMMENT ON COLUMN "public"."pre_quote_fue"."volume" IS '成交量，手';
COMMENT ON COLUMN "public"."pre_quote_fue"."turnover" IS '成交额，元';
COMMENT ON COLUMN "public"."pre_quote_fue"."open_interest" IS '持仓量，手';
COMMENT ON COLUMN "public"."pre_quote_fue"."chg_open_interest" IS '持仓量变化，手';
COMMENT ON COLUMN "public"."pre_quote_fue"."basis_value" IS '基差';
COMMENT ON COLUMN "public"."pre_quote_fue"."main_flag" IS '主力标志';
COMMENT ON COLUMN "public"."pre_quote_fue"."quote_date" IS '行情日期，2015-12-31';
COMMENT ON COLUMN "public"."pre_quote_fue"."quote_time" IS '行情时间';

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Indexes structure for table pre_quote_fue
-- ----------------------------
CREATE UNIQUE INDEX "idx_market_code" ON "public"."pre_quote_fue" USING btree ("market","code");

-- ----------------------------
-- Primary Key structure for table pre_quote_fue
-- ----------------------------
ALTER TABLE "public"."pre_quote_fue" ADD PRIMARY KEY ("id");
