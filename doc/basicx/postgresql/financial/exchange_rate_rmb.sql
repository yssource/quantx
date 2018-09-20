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

Date: 2017-02-09 17:01:19
*/


-- ----------------------------
-- Table structure for exchange_rate
-- ----------------------------
DROP TABLE IF EXISTS "public"."exchange_rate";
CREATE TABLE "public"."exchange_rate" (
"id" serial NOT NULL,
"base_money" varchar(8) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"price" float4 NOT NULL DEFAULT 0.0000,
"exchange_money" varchar(8) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"quote_type" int8 DEFAULT 0,
"end_date" date NOT NULL
)
WITH (OIDS=FALSE);
COMMENT ON COLUMN "public"."exchange_rate"."id" IS '序号';
COMMENT ON COLUMN "public"."exchange_rate"."base_money" IS '基础货币，RMB';
COMMENT ON COLUMN "public"."exchange_rate"."price" IS '汇率价格，人民币元 / 100外币';
COMMENT ON COLUMN "public"."exchange_rate"."exchange_money" IS '汇兑货币，USD、HKD';
COMMENT ON COLUMN "public"."exchange_rate"."quote_type" IS '标价方式，1 直接、2 间接';
COMMENT ON COLUMN "public"."exchange_rate"."end_date" IS '截止日期';

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Indexes structure for table exchange_rate
-- ----------------------------
CREATE UNIQUE INDEX "idx_base_money_exchange_money_end_date" ON "public"."exchange_rate" USING btree ("base_money","exchange_money","end_date");

-- ----------------------------
-- Primary Key structure for table exchange_rate
-- ----------------------------
ALTER TABLE "public"."exchange_rate" ADD PRIMARY KEY ("id");
