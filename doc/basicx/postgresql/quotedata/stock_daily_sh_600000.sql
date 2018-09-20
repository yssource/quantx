/*
Navicat PGSQL Data Transfer

Source Server         : 10.0.7.53
Source Server Version : 90601
Source Host           : 10.0.7.53:5432
Source Database       : quotedata
Source Schema         : public

Target Server Type    : PGSQL
Target Server Version : 90601
File Encoding         : 65001

Date: 2017-02-09 17:01:19
*/


-- ----------------------------
-- Table structure for stock_daily_sh_600000
-- ----------------------------
DROP TABLE IF EXISTS "public"."stock_daily_sh_600000";
CREATE TABLE "public"."stock_daily_sh_600000" (
"id" serial NOT NULL,
"date" date NOT NULL,
"open" float4 DEFAULT 0.0,
"high" float4 DEFAULT 0.0,
"low" float4 DEFAULT 0.0,
"close" float4 DEFAULT 0.0,
"volume" int8 DEFAULT 0,
"turnover" int8 DEFAULT 0
)
WITH (OIDS=FALSE);
COMMENT ON COLUMN "public"."stock_daily_sh_600000"."id" IS '序号';
COMMENT ON COLUMN "public"."stock_daily_sh_600000"."date" IS '日期';
COMMENT ON COLUMN "public"."stock_daily_sh_600000"."open" IS '开盘价';
COMMENT ON COLUMN "public"."stock_daily_sh_600000"."high" IS '最高价';
COMMENT ON COLUMN "public"."stock_daily_sh_600000"."low" IS '最低价';
COMMENT ON COLUMN "public"."stock_daily_sh_600000"."close" IS '收盘价';
COMMENT ON COLUMN "public"."stock_daily_sh_600000"."volume" IS '成交量，股';
COMMENT ON COLUMN "public"."stock_daily_sh_600000"."turnover" IS '成交额，元';

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Indexes structure for table stock_daily_sh_600000
-- ----------------------------
CREATE UNIQUE INDEX "idx_date" ON "public"."stock_daily_sh_600000" USING btree ("date");

-- ----------------------------
-- Primary Key structure for table stock_daily_sh_600000
-- ----------------------------
ALTER TABLE "public"."stock_daily_sh_600000" ADD PRIMARY KEY ("id");
