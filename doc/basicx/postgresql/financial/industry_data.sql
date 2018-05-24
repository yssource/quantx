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
-- Table structure for industry_data
-- ----------------------------
DROP TABLE IF EXISTS "public"."industry_data";
CREATE TABLE "public"."industry_data" (
"id" serial NOT NULL,
"standard" int4 NOT NULL DEFAULT 0,
"industry" int4 NOT NULL DEFAULT 0,
"industry_code_1" varchar(32) COLLATE "default" DEFAULT ''::character varying,
"industry_name_1" varchar(100) COLLATE "default" DEFAULT ''::character varying,
"industry_code_2" varchar(32) COLLATE "default" DEFAULT ''::character varying,
"industry_name_2" varchar(100) COLLATE "default" DEFAULT ''::character varying,
"industry_code_3" varchar(32) COLLATE "default" DEFAULT ''::character varying,
"industry_name_3" varchar(100) COLLATE "default" DEFAULT ''::character varying,
"industry_code_4" varchar(32) COLLATE "default" DEFAULT ''::character varying,
"industry_name_4" varchar(100) COLLATE "default" DEFAULT ''::character varying,
"inners" int4 NOT NULL DEFAULT 0,
"market" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"code" varchar(32) COLLATE "default" NOT NULL DEFAULT ''::character varying,
"name" varchar(32) COLLATE "default" DEFAULT ''::character varying,
"info_date" date NOT NULL
)
WITH (OIDS=FALSE)

;
COMMENT ON COLUMN "public"."industry_data"."id" IS '序号';
COMMENT ON COLUMN "public"."industry_data"."standard" IS '行业划分标准';
COMMENT ON COLUMN "public"."industry_data"."industry" IS '所属行业';
COMMENT ON COLUMN "public"."industry_data"."industry_code_1" IS '一级行业代码';
COMMENT ON COLUMN "public"."industry_data"."industry_name_1" IS '一级行业名称';
COMMENT ON COLUMN "public"."industry_data"."industry_code_2" IS '二级行业代码';
COMMENT ON COLUMN "public"."industry_data"."industry_name_2" IS '二级行业名称';
COMMENT ON COLUMN "public"."industry_data"."industry_code_3" IS '三级行业代码';
COMMENT ON COLUMN "public"."industry_data"."industry_name_3" IS '三级行业名称';
COMMENT ON COLUMN "public"."industry_data"."industry_code_4" IS '四级行业代码';
COMMENT ON COLUMN "public"."industry_data"."industry_name_4" IS '四级行业名称';
COMMENT ON COLUMN "public"."industry_data"."inners" IS '内部代码';
COMMENT ON COLUMN "public"."industry_data"."market" IS '证券市场，SH、SZ';
COMMENT ON COLUMN "public"."industry_data"."code" IS '证券代码';
COMMENT ON COLUMN "public"."industry_data"."name" IS '证券名称';
COMMENT ON COLUMN "public"."industry_data"."info_date" IS '信息日期';

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Indexes structure for table industry_data
-- ----------------------------
CREATE UNIQUE INDEX "idx_standard_industry_market_code_info_date" ON "public"."industry_data" USING btree ("standard","industry","market","code","info_date");

-- ----------------------------
-- Primary Key structure for table industry_data
-- ----------------------------
ALTER TABLE "public"."industry_data" ADD PRIMARY KEY ("id");
