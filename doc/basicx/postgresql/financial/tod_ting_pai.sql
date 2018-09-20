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

Date: 2017-12-21 17:01:19
*/


-- ----------------------------
-- Table structure for tod_ting_pai
-- ----------------------------
DROP TABLE IF EXISTS "public"."tod_ting_pai";
CREATE TABLE "public"."tod_ting_pai" (
"id" serial NOT NULL,
"inners" int4 NOT NULL DEFAULT 0,
"market" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"code" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"name" varchar(32) COLLATE "default" DEFAULT ''::character varying,
"category" int4 DEFAULT 0,
"tp_date" timestamp,
"tp_time" varchar(30) COLLATE "default" DEFAULT ''::character varying,
"tp_reason" varchar(110) COLLATE "default" DEFAULT ''::character varying,
"tp_statement" int4 DEFAULT 0,
"tp_term" varchar(60) COLLATE "default" DEFAULT ''::character varying,
"fp_date" timestamp,
"fp_time" varchar(30) COLLATE "default" DEFAULT ''::character varying,
"fp_statement" varchar(110) COLLATE "default" DEFAULT ''::character varying,
"update_time" timestamp
)
WITH (OIDS=FALSE);
COMMENT ON COLUMN "public"."tod_ting_pai"."id" IS '序号';
COMMENT ON COLUMN "public"."tod_ting_pai"."inners" IS '内部代码';
COMMENT ON COLUMN "public"."tod_ting_pai"."market" IS '证券市场，SH、SZ';
COMMENT ON COLUMN "public"."tod_ting_pai"."code" IS '证券代码';
COMMENT ON COLUMN "public"."tod_ting_pai"."name" IS '证券名称';
COMMENT ON COLUMN "public"."tod_ting_pai"."category" IS '证券类别，详见说明';
COMMENT ON COLUMN "public"."tod_ting_pai"."tp_date" IS '停牌日期';
COMMENT ON COLUMN "public"."tod_ting_pai"."tp_time" IS '停牌时间';
COMMENT ON COLUMN "public"."tod_ting_pai"."tp_reason" IS '停牌原因';
COMMENT ON COLUMN "public"."tod_ting_pai"."tp_statement" IS '停牌事项说明，详见说明';
COMMENT ON COLUMN "public"."tod_ting_pai"."tp_term" IS '停牌期限';
COMMENT ON COLUMN "public"."tod_ting_pai"."fp_date" IS '复牌日期';
COMMENT ON COLUMN "public"."tod_ting_pai"."fp_time" IS '复牌时间';
COMMENT ON COLUMN "public"."tod_ting_pai"."fp_statement" IS '复牌事项说明';
COMMENT ON COLUMN "public"."tod_ting_pai"."update_time" IS '更新时间';

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Indexes structure for table tod_ting_pai
-- ----------------------------
CREATE UNIQUE INDEX "idx_market_code" ON "public"."tod_ting_pai" USING btree ("market","code");

-- ----------------------------
-- Primary Key structure for table tod_ting_pai
-- ----------------------------
ALTER TABLE "public"."tod_ting_pai" ADD PRIMARY KEY ("id");
