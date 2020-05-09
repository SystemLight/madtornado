/*
 Navicat SQLite Data Transfer

 Source Server         : madtornado
 Source Server Type    : SQLite
 Source Server Version : 3021000
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3021000
 File Encoding         : 65001

 Date: 27/11/2019 19:55:52
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for mad
-- ----------------------------
DROP TABLE IF EXISTS "mad";
CREATE TABLE "mad" (
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "name" TEXT,
  "site" TEXT,
  "github" TEXT,
  "contribution" integer
);

-- ----------------------------
-- Records of mad
-- ----------------------------
INSERT INTO "mad" VALUES (1, 'SystemLight', 'http://lisys.xyz', 'https://github.com/SystemLight', 100);

-- ----------------------------
-- Table structure for sqlite_sequence
-- ----------------------------
DROP TABLE IF EXISTS "sqlite_sequence";
CREATE TABLE "sqlite_sequence" (
  "name",
  "seq"
);

-- ----------------------------
-- Records of sqlite_sequence
-- ----------------------------
INSERT INTO "sqlite_sequence" VALUES ('mad', 1);

-- ----------------------------
-- Auto increment value for mad
-- ----------------------------
UPDATE "sqlite_sequence" SET seq = 1 WHERE name = 'mad';

PRAGMA foreign_keys = true;
