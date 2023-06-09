CREATE DATABASE pipeline;

USE pipeline;

CREATE TABLE assets (
  asset_id INT AUTO_INCREMENT PRIMARY KEY,
  asset_name VARCHAR(64),
  asset_path VARCHAR(254) UNIQUE,
  asset_type VARCHAR(64)
);

CREATE TABLE asset_production (
  id INT AUTO_INCREMENT PRIMARY KEY,
  asset_id INT,
  asset_version int DEFAULT 1,
  version_path VARCHAR(254) UNIQUE,
  FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
);

CREATE TABLE users (
  user_id int AUTO_INCREMENT PRIMARY KEY,
  nameFirst VARCHAR(64),
  nameLast VARCHAR(64),
  email VARCHAR(64),
  username VARCHAR(64) UNIQUE
);

CREATE TABLE changelog (
  chlog_id INT AUTO_INCREMENT PRIMARY KEY,
  chlog_timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
  asset_id INT,
  chlog_message TEXT NULL,
  user_id int,
  FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

GRANT ALL PRIVILEGES ON pipeline.* TO 'docker' WITH GRANT OPTION;
FLUSH PRIVILEGES;