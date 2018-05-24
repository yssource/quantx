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
-- Table structure for ex_rights_data
-- ----------------------------
DROP TABLE IF EXISTS "public"."ex_rights_data";
CREATE TABLE "public"."ex_rights_data" (
"id" serial NOT NULL,
"inners" int4 NOT NULL DEFAULT 0,
"market" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"code" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"date" date NOT NULL,
"muler" float4 DEFAULT 0.0,
"adder" float4 DEFAULT 0.0,
"sg" float4 DEFAULT 0.0,
"pg" float4 DEFAULT 0.0,
"price" float4 DEFAULT 0.0,
"bonus" float4 DEFAULT 0.0
)
WITH (OIDS=FALSE)

;
COMMENT ON COLUMN "public"."ex_rights_data"."id" IS '序号';
COMMENT ON COLUMN "public"."ex_rights_data"."inners" IS '内部代码';
COMMENT ON COLUMN "public"."ex_rights_data"."market" IS '证券市场，SH、SZ';
COMMENT ON COLUMN "public"."ex_rights_data"."code" IS '证券代码';
COMMENT ON COLUMN "public"."ex_rights_data"."date" IS '除权除息日期';
COMMENT ON COLUMN "public"."ex_rights_data"."muler" IS '乘数';
COMMENT ON COLUMN "public"."ex_rights_data"."adder" IS '加数';
COMMENT ON COLUMN "public"."ex_rights_data"."sg" IS '送股比率，每股，非百分比';
COMMENT ON COLUMN "public"."ex_rights_data"."pg" IS '配股比率，每股，非百分比';
COMMENT ON COLUMN "public"."ex_rights_data"."price" IS '配股价，元';
COMMENT ON COLUMN "public"."ex_rights_data"."bonus" IS '现金红利，每股，元';

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Indexes structure for table ex_rights_data
-- ----------------------------
CREATE UNIQUE INDEX "idx_market_code_date" ON "public"."ex_rights_data" USING btree ("market","code","date");

-- ----------------------------
-- Primary Key structure for table ex_rights_data
-- ----------------------------
ALTER TABLE "public"."ex_rights_data" ADD PRIMARY KEY ("id");
