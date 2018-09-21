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
-- Table structure for component_hsggt
-- ----------------------------
DROP TABLE IF EXISTS "public"."component_hsggt";
CREATE TABLE "public"."component_hsggt" (
"id" serial NOT NULL,
"inners" int4 NOT NULL DEFAULT 0,
"market" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"code" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"name" varchar(32) COLLATE "default" DEFAULT ''::character varying,
"category" int4 DEFAULT 0,
"comp_type" int4 DEFAULT 0,
"update_time" timestamp
)
WITH (OIDS=FALSE);
COMMENT ON COLUMN "public"."component_hsggt"."id" IS '序号';
COMMENT ON COLUMN "public"."component_hsggt"."inners" IS '内部代码';
COMMENT ON COLUMN "public"."component_hsggt"."market" IS '证券市场，SH、SZ、HK';
COMMENT ON COLUMN "public"."component_hsggt"."code" IS '证券代码';
COMMENT ON COLUMN "public"."component_hsggt"."name" IS '证券名称';
COMMENT ON COLUMN "public"."component_hsggt"."category" IS '证券类别，详见说明';
COMMENT ON COLUMN "public"."component_hsggt"."comp_type" IS '成分类别，详见说明';
COMMENT ON COLUMN "public"."component_hsggt"."update_time" IS '更新时间';

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Indexes structure for table component_hsggt
-- ----------------------------
CREATE UNIQUE INDEX "idx_market_code" ON "public"."component_hsggt" USING btree ("market","code");

-- ----------------------------
-- Primary Key structure for table component_hsggt
-- ----------------------------
ALTER TABLE "public"."component_hsggt" ADD PRIMARY KEY ("id");
