/*
 Navicat MySQL Data Transfer

 Source Server         : Tango
 Source Server Type    : MySQL
 Source Server Version : 50741 (5.7.41)
 Source Host           : localhost:3306
 Source Schema         : tango

 Target Server Type    : MySQL
 Target Server Version : 50741 (5.7.41)
 File Encoding         : 65001

 Date: 09/04/2023 16:29:17
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for inter_task_constraints
-- ----------------------------
DROP TABLE IF EXISTS `inter_task_constraints`;
CREATE TABLE `inter_task_constraints` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'inter task constraint id',
  `task_set_id` int(10) unsigned NOT NULL COMMENT 'task set id',
  `a_task_id` int(10) unsigned NOT NULL COMMENT 'one of the task related to this constraint',
  `z_task_id` int(10) unsigned NOT NULL COMMENT 'another one of the task related to this constraint',
  `bandwidth` int(10) unsigned DEFAULT NULL COMMENT 'inter task bandwidth constraint',
  `delay` int(10) unsigned DEFAULT NULL COMMENT 'inter task delay constraint',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='inter task constraints';

-- ----------------------------
-- Table structure for network_node
-- ----------------------------
DROP TABLE IF EXISTS `network_node`;
CREATE TABLE `network_node` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'network node id',
  `name` varchar(32) NOT NULL COMMENT 'name of the network node',
  `cpu` int(11) NOT NULL COMMENT 'all cpu resource/cores',
  `mem` int(11) NOT NULL COMMENT 'all mem resource/GB',
  `disk` int(11) NOT NULL COMMENT 'all disk resource/GB',
  `cpu_rem` int(11) NOT NULL COMMENT 'remain cpu resource/cores',
  `mem_rem` int(11) NOT NULL COMMENT 'remain mem resource/GB',
  `disk_rem` int(11) NOT NULL COMMENT 'remain disk resource/GB',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COMMENT='network node table';

-- ----------------------------
-- Table structure for network_node_delay
-- ----------------------------
DROP TABLE IF EXISTS `network_node_delay`;
CREATE TABLE `network_node_delay` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'delay info id',
  `node_id` int(10) unsigned NOT NULL COMMENT 'network node id',
  `geo_place_id` int(10) unsigned NOT NULL COMMENT 'geographic place id',
  `delay` int(10) unsigned NOT NULL COMMENT 'node to geo place delay',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `node foreign key` (`node_id`),
  CONSTRAINT `node foreign key` FOREIGN KEY (`node_id`) REFERENCES `network_node` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COMMENT='record delay info';

-- ----------------------------
-- Table structure for task
-- ----------------------------
DROP TABLE IF EXISTS `task`;
CREATE TABLE `task` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'task id',
  `task_set_id` int(10) unsigned NOT NULL COMMENT 'task set id the task belong to',
  `node_id` int(10) unsigned DEFAULT NULL COMMENT 'net node id the task assigned to',
  `cpu_dem` int(10) unsigned NOT NULL COMMENT 'CPU resource required/core count',
  `mem_dem` int(10) unsigned NOT NULL COMMENT 'memory resource required/GB',
  `disk_dem` int(10) unsigned NOT NULL COMMENT 'disk resource required/GB',
  `delay_constraint` int(10) unsigned DEFAULT NULL COMMENT 'delay constraint to all the geo pot/ms',
  `image_tag` varchar(32) DEFAULT NULL COMMENT 'image used in this task',
  `task_id` int(10) NOT NULL COMMENT 'Task id inside a task set',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `task_set_related` (`task_set_id`),
  CONSTRAINT `task_set_related` FOREIGN KEY (`task_set_id`) REFERENCES `task_set` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COMMENT='tasks';

-- ----------------------------
-- Table structure for task_set
-- ----------------------------
DROP TABLE IF EXISTS `task_set`;
CREATE TABLE `task_set` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'task set id',
  `name` varchar(128) NOT NULL COMMENT 'task set name',
  `task_count` int(10) unsigned NOT NULL COMMENT 'number of tasks task set contains',
  `state` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '0(incomplete) or 1(running) or 2(finish)',
  `creator_id` int(10) unsigned NOT NULL DEFAULT '1' COMMENT 'creator id of the task set',
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'create time',
  `mtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'modify time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COMMENT='task set';

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'user id',
  `name` varchar(128) NOT NULL COMMENT 'user name',
  `password` varchar(128) NOT NULL COMMENT 'user password',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COMMENT='user table';

SET FOREIGN_KEY_CHECKS = 1;
