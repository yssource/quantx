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
-- Table structure for pre_quote_stk_hk
-- ----------------------------
DROP TABLE IF EXISTS "public"."pre_quote_stk_hk";
CREATE TABLE "public"."pre_quote_stk_hk" (
"id" serial NOT NULL,
"inners" int4 NOT NULL DEFAULT 0,
"market" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"code" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"name" varchar(32) COLLATE "default" DEFAULT ''::character varying,
"category" int4 DEFAULT 0,
"open" float4 DEFAULT 0.0000,
"high" float4 DEFAULT 0.0000,
"low" float4 DEFAULT 0.0000,
"close" float4 DEFAULT 0.0000,
"pre_close" float4 DEFAULT 0.0000,
"volume" int8 DEFAULT 0,
"turnover" float8 DEFAULT 0.00,
"trade_count" int4 DEFAULT 0,
"quote_date" date,
"quote_time" timestamp
)
WITH (OIDS=FALSE)

;
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."id" IS '序号';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."inners" IS '内部代码';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."market" IS '证券市场，HK';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."code" IS '证券代码';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."name" IS '证券名称';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."category" IS '证券类别，详见说明';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."open" IS '开盘价';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."high" IS '最高价';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."low" IS '最低价';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."close" IS '收盘价';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."pre_close" IS '昨收价';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."volume" IS '成交量，股';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."turnover" IS '成交额，元';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."trade_count" IS '成交笔数';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."quote_date" IS '行情日期，2015-12-31';
COMMENT ON COLUMN "public"."pre_quote_stk_hk"."quote_time" IS '行情时间';

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Indexes structure for table pre_quote_stk_hk
-- ----------------------------
CREATE UNIQUE INDEX "idx_market_code" ON "public"."pre_quote_stk_hk" USING btree ("market","code");

-- ----------------------------
-- Primary Key structure for table pre_quote_stk_hk
-- ----------------------------
ALTER TABLE "public"."pre_quote_stk_hk" ADD PRIMARY KEY ("id");
