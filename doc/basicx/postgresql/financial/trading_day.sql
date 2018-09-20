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

Date: 2017-09-04 17:01:19
*/


-- ----------------------------
-- Table structure for trading_day
-- ----------------------------
DROP TABLE IF EXISTS "public"."trading_day";
CREATE TABLE "public"."trading_day" (
"id" serial NOT NULL,
"natural_date" date NOT NULL,
"market" int4 NOT NULL DEFAULT 0,
"trading_day" int4 DEFAULT 0,
"week_end" int4 DEFAULT 0,
"month_end" int4 DEFAULT 0,
"quarter_end" int4 DEFAULT 0,
"year_end" int4 DEFAULT 0
)
WITH (OIDS=FALSE);
COMMENT ON COLUMN "public"."trading_day"."id" IS '序号';
COMMENT ON COLUMN "public"."trading_day"."natural_date" IS '日期';
COMMENT ON COLUMN "public"."trading_day"."market" IS '证券市场，72、83、89';
COMMENT ON COLUMN "public"."trading_day"."trading_day" IS '是否交易';
COMMENT ON COLUMN "public"."trading_day"."week_end" IS '是否周末';
COMMENT ON COLUMN "public"."trading_day"."month_end" IS '是否月末';
COMMENT ON COLUMN "public"."trading_day"."quarter_end" IS '是否季末';
COMMENT ON COLUMN "public"."trading_day"."year_end" IS '是否年末';

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Indexes structure for table trading_day
-- ----------------------------
CREATE UNIQUE INDEX "idx_natural_date_market" ON "public"."trading_day" USING btree ("natural_date","market");

-- ----------------------------
-- Primary Key structure for table trading_day
-- ----------------------------
ALTER TABLE "public"."trading_day" ADD PRIMARY KEY ("id");
