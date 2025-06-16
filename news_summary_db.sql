DROP DATABASE IF EXISTS news_summary_db;

CREATE DATABASE news_summary_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE news_summary_db;

CREATE TABLE summary_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_text TEXT,
    summary TEXT,
    source_lang VARCHAR(5),
    target_lang VARCHAR(5),
    summary_length INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    FULLTEXT(original_text, summary),
    FOREIGN KEY (user_id) REFERENCES users(id)
);


CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);