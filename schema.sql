CREATE DATABASE IF NOT EXISTS age_wise_video;
USE age_wise_video;

CREATE TABLE IF NOT EXISTS admin (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100),
    password VARCHAR(100)
);

INSERT INTO admin(username, password)
VALUES ('admin', 'admin');

CREATE TABLE IF NOT EXISTS register (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    mobile VARCHAR(20),
    email VARCHAR(100),
    uname VARCHAR(100),
    pass VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS upload_video (
    id INT PRIMARY KEY,
    age VARCHAR(20),
    filename VARCHAR(255)
);
