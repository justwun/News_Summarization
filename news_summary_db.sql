CREATE DATABASE news_summary_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE news_summary_db;

CREATE TABLE summary_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_text TEXT,
    summary TEXT,
    source_lang VARCHAR(5),
    target_lang VARCHAR(5),
    summary_length VARCHAR(20),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
