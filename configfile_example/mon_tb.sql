
DROP TABLE IF EXISTS `mon_autoinc_status`;
CREATE TABLE `mon_autoinc_status` (
  `id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `COLUMN_NAME` varchar(64) NOT NULL DEFAULT '',
  `DATA_TYPE` varchar(64) NOT NULL DEFAULT '',
  `COLUMN_TYPE` longtext NOT NULL,
  `IS_UNSIGNED` int(1) NOT NULL DEFAULT '0',
  `IS_INT` int(1) NOT NULL DEFAULT '0',
  `MAX_VALUE` bigint(21) unsigned DEFAULT NULL,
  `AUTO_INCREMENT` bigint(21) unsigned DEFAULT NULL,
  `INDEX_NAME` varchar(64) NOT NULL DEFAULT '',
  `SEQ_IN_INDEX` bigint(2) NOT NULL DEFAULT '0',
  `DBTAG` varchar(40) DEFAULT NULL,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_dbtag` (`DBTAG`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `mon_autoinc_status_his`;
CREATE TABLE `mon_autoinc_status_his` (
  `id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `COLUMN_NAME` varchar(64) NOT NULL DEFAULT '',
  `DATA_TYPE` varchar(64) NOT NULL DEFAULT '',
  `COLUMN_TYPE` longtext NOT NULL,
  `IS_UNSIGNED` int(1) NOT NULL DEFAULT '0',
  `IS_INT` int(1) NOT NULL DEFAULT '0',
  `MAX_VALUE` bigint(21) unsigned DEFAULT NULL,
  `AUTO_INCREMENT` bigint(21) unsigned DEFAULT NULL,
  `INDEX_NAME` varchar(64) NOT NULL DEFAULT '',
  `SEQ_IN_INDEX` bigint(2) NOT NULL DEFAULT '0',
  `DBTAG` varchar(40) DEFAULT NULL,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_dbtag` (`DBTAG`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `mon_autoinc_status_tmp`;
CREATE TABLE `mon_autoinc_status_tmp` (
  `id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `COLUMN_NAME` varchar(64) NOT NULL DEFAULT '',
  `DATA_TYPE` varchar(64) NOT NULL DEFAULT '',
  `COLUMN_TYPE` longtext NOT NULL,
  `IS_UNSIGNED` int(1) NOT NULL DEFAULT '0',
  `IS_INT` int(1) NOT NULL DEFAULT '0',
  `MAX_VALUE` bigint(21) unsigned DEFAULT NULL,
  `AUTO_INCREMENT` bigint(21) unsigned DEFAULT NULL,
  `INDEX_NAME` varchar(64) NOT NULL DEFAULT '',
  `SEQ_IN_INDEX` bigint(2) NOT NULL DEFAULT '0',
  `DBTAG` varchar(40) DEFAULT NULL,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_dbtag` (`DBTAG`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `mon_tbsize`;
CREATE TABLE `mon_tbsize` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `DATA(M)` decimal(24,2) DEFAULT NULL,
  `INDEX(M)` decimal(24,2) DEFAULT NULL,
  `TOTAL(M)` decimal(25,2) DEFAULT NULL,
  `DBTAG` varchar(40) DEFAULT NULL,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_total` (`TOTAL(M)`),
  KEY `idx_data` (`DATA(M)`),
  KEY `idx_dbtag_tbname` (`DBTAG`,`TABLE_NAME`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `mon_tbsize_his`;
CREATE TABLE `mon_tbsize_his` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `DATA(M)` decimal(24,2) DEFAULT NULL,
  `INDEX(M)` decimal(24,2) DEFAULT NULL,
  `TOTAL(M)` decimal(25,2) DEFAULT NULL,
  `DBTAG` varchar(40) DEFAULT NULL,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_dbtag_tbname` (`DBTAG`,`TABLE_NAME`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `mon_tbsize_last`;
CREATE TABLE `mon_tbsize_last` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `DATA(M)` decimal(24,2) DEFAULT NULL,
  `INDEX(M)` decimal(24,2) DEFAULT NULL,
  `TOTAL(M)` decimal(25,2) DEFAULT NULL,
  `DBTAG` varchar(40) DEFAULT NULL,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_data` (`DATA(M)`),
  KEY `idx_total` (`TOTAL(M)`),
  KEY `idx_dbtag_tbname` (`DBTAG`,`TABLE_NAME`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `mon_tbsize_tmp`;
CREATE TABLE `mon_tbsize_tmp` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `DATA(M)` decimal(24,2) DEFAULT NULL,
  `INDEX(M)` decimal(24,2) DEFAULT NULL,
  `TOTAL(M)` decimal(25,2) DEFAULT NULL,
  `DBTAG` varchar(40) DEFAULT NULL,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_data` (`DATA(M)`),
  KEY `idx_total` (`TOTAL(M)`),
  KEY `idx_dbtag_tbname` (`DBTAG`,`TABLE_NAME`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `mon_dbsize_his`;
CREATE TABLE `mon_dbsize_his` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `DBTAG` varchar(40) DEFAULT NULL,
  `DATA(M)` decimal(24,2) DEFAULT NULL,
  `INDEX(M)` decimal(24,2) DEFAULT NULL,
  `TOTAL(M)` decimal(25,2) DEFAULT NULL,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_dbtag` (`DBTAG`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
