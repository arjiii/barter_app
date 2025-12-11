-- Bayanihan Exchange MySQL Schema (XAMPP)
-- Compatible with MySQL 8.x / MariaDB 10.4+

-- Create database (optional)
-- CREATE DATABASE IF NOT EXISTS bayanihan_exchange CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE bayanihan_exchange;

-- Users
CREATE TABLE IF NOT EXISTS users (
	id CHAR(36) PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	email VARCHAR(255) NOT NULL UNIQUE,
	password_hash VARCHAR(255) NOT NULL,
	is_verified TINYINT(1) DEFAULT 0,
	role ENUM('user','admin','moderator') DEFAULT 'user',
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	last_login_at DATETIME NULL,
	remember_token VARCHAR(255) NULL,
	email_verification_token VARCHAR(255) NULL,
	password_reset_token VARCHAR(255) NULL,
	password_reset_expires DATETIME NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sessions
CREATE TABLE IF NOT EXISTS user_sessions (
	id CHAR(36) PRIMARY KEY,
	user_id CHAR(36) NOT NULL,
	token VARCHAR(255) NOT NULL UNIQUE,
	expires_at DATETIME NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	ip_address VARCHAR(64) NULL,
	user_agent VARCHAR(255) NULL,
	CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Items
CREATE TABLE IF NOT EXISTS items (
	id CHAR(36) PRIMARY KEY,
	user_id CHAR(36) NOT NULL,
	title VARCHAR(255) NOT NULL,
	description TEXT NULL,
	category VARCHAR(100) NULL,
	`condition` VARCHAR(100) NULL,
	images JSON NULL,
	status ENUM('available','traded','removed','draft','pending') DEFAULT 'available',
	views INT DEFAULT 0,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT fk_items_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Categories
CREATE TABLE IF NOT EXISTS categories (
	id CHAR(36) PRIMARY KEY,
	name VARCHAR(100) NOT NULL UNIQUE,
	description VARCHAR(255) NULL,
	icon VARCHAR(64) NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Trades
CREATE TABLE IF NOT EXISTS trades (
	id CHAR(36) PRIMARY KEY,
	from_user_id CHAR(36) NOT NULL,
	to_user_id CHAR(36) NOT NULL,
	from_item_id CHAR(36) NOT NULL,
	to_item_id CHAR(36) NOT NULL,
	message TEXT NULL,
	status ENUM('pending','accepted','rejected','active','completed','cancelled') DEFAULT 'pending',
	expires_at DATETIME NULL,
	meeting_location VARCHAR(255) NULL,
	meeting_time DATETIME NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT fk_trades_from_user FOREIGN KEY (from_user_id) REFERENCES users(id) ON DELETE CASCADE,
	CONSTRAINT fk_trades_to_user FOREIGN KEY (to_user_id) REFERENCES users(id) ON DELETE CASCADE,
	CONSTRAINT fk_trades_from_item FOREIGN KEY (from_item_id) REFERENCES items(id) ON DELETE CASCADE,
	CONSTRAINT fk_trades_to_item FOREIGN KEY (to_item_id) REFERENCES items(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Messages
CREATE TABLE IF NOT EXISTS messages (
	id CHAR(36) PRIMARY KEY,
	trade_id CHAR(36) NOT NULL,
	sender_id CHAR(36) NOT NULL,
	receiver_id CHAR(36) NOT NULL,
	content TEXT NOT NULL,
	is_read TINYINT(1) DEFAULT 0,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT fk_messages_trade FOREIGN KEY (trade_id) REFERENCES trades(id) ON DELETE CASCADE,
	CONSTRAINT fk_messages_sender FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
	CONSTRAINT fk_messages_receiver FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ratings
CREATE TABLE IF NOT EXISTS user_ratings (
	id CHAR(36) PRIMARY KEY,
	from_user_id CHAR(36) NOT NULL,
	to_user_id CHAR(36) NOT NULL,
	trade_id CHAR(36) NOT NULL,
	rating TINYINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
	comment TEXT NULL,
	blockchain_tx_hash VARCHAR(255) NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT fk_ratings_from_user FOREIGN KEY (from_user_id) REFERENCES users(id) ON DELETE CASCADE,
	CONSTRAINT fk_ratings_to_user FOREIGN KEY (to_user_id) REFERENCES users(id) ON DELETE CASCADE,
	CONSTRAINT fk_ratings_trade FOREIGN KEY (trade_id) REFERENCES trades(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_verification_token ON users(email_verification_token);
CREATE INDEX idx_sessions_token ON user_sessions(token);
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_items_user_id ON items(user_id);
CREATE INDEX idx_items_status ON items(status);
CREATE INDEX idx_items_category ON items(category);
CREATE INDEX idx_trades_from_user ON trades(from_user_id);
CREATE INDEX idx_trades_to_user ON trades(to_user_id);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_messages_trade_id ON messages(trade_id);
CREATE INDEX idx_messages_sender ON messages(sender_id);
CREATE INDEX idx_messages_receiver ON messages(receiver_id);
CREATE INDEX idx_ratings_to_user ON user_ratings(to_user_id);


