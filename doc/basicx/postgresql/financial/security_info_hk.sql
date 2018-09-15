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
-- Table structure for security_info_hk
-- ----------------------------
DROP TABLE IF EXISTS "public"."security_info_hk";
CREATE TABLE "public"."security_info_hk" (
"id" serial NOT NULL,
"inners" int4 NOT NULL DEFAULT 0,
"company" int4 NOT NULL DEFAULT 0,
"market" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"code" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"name" varchar(32) COLLATE "default" DEFAULT ''::character varying,
"category" int4 DEFAULT 0,
"sector" int4 DEFAULT 0,
"trade_unit" int4 DEFAULT 0,
"min_price_chg" float4 DEFAULT 0.0000,
"list_state" int4 DEFAULT 0,
"list_date" date
)
WITH (OIDS=FALSE)

;
COMMENT ON COLUMN "public"."security_info_hk"."id" IS '序号';
COMMENT ON COLUMN "public"."security_info_hk"."inners" IS '内部代码';
COMMENT ON COLUMN "public"."security_info_hk"."company" IS '公司代码';
COMMENT ON COLUMN "public"."security_info_hk"."market" IS '证券市场，SH、SZ';
COMMENT ON COLUMN "public"."security_info_hk"."code" IS '证券代码';
COMMENT ON COLUMN "public"."security_info_hk"."name" IS '证券名称';
COMMENT ON COLUMN "public"."security_info_hk"."category" IS '证券类别，详见说明';
COMMENT ON COLUMN "public"."security_info_hk"."sector" IS '上市板块，详见说明';
COMMENT ON COLUMN "public"."security_info_hk"."trade_unit" IS '买卖单位，股/手';
COMMENT ON COLUMN "public"."security_info_hk"."min_price_chg" IS '最小变动价格';
COMMENT ON COLUMN "public"."security_info_hk"."list_state" IS '上市状态，详见说明';
COMMENT ON COLUMN "public"."security_info_hk"."list_date" IS '上市日期';

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Indexes structure for table security_info_hk
-- ----------------------------
CREATE UNIQUE INDEX "idx_inners" ON "public"."security_info_hk" USING btree ("inners");
CREATE INDEX "idx_company" ON "public"."security_info_hk" USING btree ("company");
CREATE UNIQUE INDEX "idx_market_code" ON "public"."security_info_hk" USING btree ("market","code");

-- ----------------------------
-- Primary Key structure for table security_info_hk
-- ----------------------------
ALTER TABLE "public"."security_info_hk" ADD PRIMARY KEY ("id");
