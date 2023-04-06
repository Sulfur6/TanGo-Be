CREATE TABLE IF NOT EXISTS user (
    id int unsigned UNIQUE NOT NULL AUTO_INCREMENT COMMENT 'user id',
    name varchar(128) UNIQUE NOT NULL COMMENT 'user name',
    password varchar(128) NOT NULL COMMENT 'user password',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='user table';

CREATE TABLE IF NOT EXISTS network_node (
    id int unsigned UNIQUE NOT NULL AUTO_INCREMENT COMMENT 'network node id',
    name varchar(32) NOT NULL COMMENT 'name of the network node',
    cpu int NOT NULL COMMENT 'all cpu resource/cores',
    mem int NOT NULL COMMENT 'all mem resource/GB',
    disk int NOT NULL COMMENT 'all disk resource/GB',
    cpu_rem int NOT NULL COMMENT 'remain cpu resource/cores',
    mem_rem int NOT NULL COMMENT 'remain mem resource/GB',
    disk_rem int NOT NULL COMMENT 'remain disk resource/GB',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='network node table';

CREATE TABLE IF NOT EXISTS network_node_delay (
    id int unsigned UNIQUE NOT NULL AUTO_INCREMENT COMMENT 'delay info id',
    node_id int unsigned NOT NULL COMMENT 'network node id',
    geo_place_id int unsigned NOT NULL COMMENT 'geographic place id',
    delay int unsigned NOT NULL COMMENT 'node to geo place delay',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='record delay info';

CREATE TABLE IF NOT EXISTS task_set (
    id int unsigned UNIQUE NOT NULL AUTO_INCREMENT COMMENT 'task set id',
    name varchar(128) NOT NULL COMMENT 'task set name',
    task_count int unsigned NOT NULL COMMENT 'number of tasks task set contains',
    state tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0(incomplete) or 1(running) or 2(finish)',
    creator_id int unsigned NOT NULL DEFAULT '1' COMMENT 'creator id of the task set',
    ctime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'create time',
    mtime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'modify time',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='task set';

CREATE TABLE IF NOT EXISTS task (
    id int unsigned UNIQUE NOT NULL AUTO_INCREMENT COMMENT 'task id',
    task_set_id int unsigned NOT NULL COMMENT 'task set id the task belong to',
    node_id int unsigned COMMENT 'net node id the task assigned to',
    cpu_dem int unsigned NOT NULL COMMENT 'CPU resource required/core count',
    mem_dem int unsigned NOT NULL COMMENT 'memory resource required/GB',
    disk_dem int unsigned NOT NULL COMMENT 'disk resource required/GB',
    delay_constraint int unsigned COMMENT 'delay constraint to all the geo pot/ms',
    image_tag varchar(32) COMMENT 'image used in this task',
#     'ctime' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'create time',
#     'mtime' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'modify time',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='tasks';

CREATE TABLE IF NOT EXISTS inter_task_constraints (
    id int unsigned UNIQUE NOT NULL AUTO_INCREMENT COMMENT 'inter task constraint id',
    task_set_id int unsigned NOT NULL COMMENT 'task set id',
    a_task_id int unsigned NOT NULL COMMENT 'one of the task related to this constraint',
    z_task_id int unsigned NOT NULL COMMENT 'another one of the task related to this constraint',
    bandwidth int unsigned COMMENT 'inter task bandwidth constraint',
    delay int unsigned COMMENT 'inter task delay constraint',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='inter task constraints';
