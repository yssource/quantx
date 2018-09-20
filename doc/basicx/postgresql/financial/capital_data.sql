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
-- Table structure for capital_data
-- ----------------------------
DROP TABLE IF EXISTS "public"."capital_data";
CREATE TABLE "public"."capital_data" (
"id" serial NOT NULL,
"inners" int4 NOT NULL DEFAULT 0,
"market" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"code" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"name" varchar(32) COLLATE "default" DEFAULT ''::character varying,
"end_date" date NOT NULL,
"total_shares" int8 DEFAULT 0,
"circu_shares" int8 DEFAULT 0
)
WITH (OIDS=FALSE);
COMMENT ON COLUMN "public"."capital_data"."id" IS '序号';
COMMENT ON COLUMN "public"."capital_data"."inners" IS '内部代码';
COMMENT ON COLUMN "public"."capital_data"."market" IS '证券市场，SH、SZ';
COMMENT ON COLUMN "public"."capital_data"."code" IS '证券代码';
COMMENT ON COLUMN "public"."capital_data"."name" IS '证券名称';
COMMENT ON COLUMN "public"."capital_data"."end_date" IS '截止日期';
COMMENT ON COLUMN "public"."capital_data"."total_shares" IS '总股本，股';
COMMENT ON COLUMN "public"."capital_data"."circu_shares" IS '流通股本，股，A股';

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Indexes structure for table capital_data
-- ----------------------------
CREATE UNIQUE INDEX "idx_market_code_end_date" ON "public"."capital_data" USING btree ("market","code","end_date");

-- ----------------------------
-- Primary Key structure for table capital_data
-- ----------------------------
ALTER TABLE "public"."capital_data" ADD PRIMARY KEY ("id");
