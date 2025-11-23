MySQL (XAMPP) setup for Bayanihan Exchange

This folder contains a MySQL schema compatible with XAMPP (MySQL/MariaDB).

Steps

1. Start XAMPP and ensure MySQL is running.
2. Open phpMyAdmin (http://localhost/phpmyadmin).
3. Create a database named `bayanihan_exchange` (utf8mb4, unicode collation).
4. Import `Backend/mysql/schema.sql`:
   - Select the `bayanihan_exchange` DB
   - Go to Import → Choose file → `Backend/mysql/schema.sql` → Go

The schema creates these tables: `users`, `user_sessions`, `items`, `categories`, `trades`, `messages`, `user_ratings` plus indexes and FKs.

IDs and JSON columns

- IDs use `CHAR(36)` intended for UUIDs. Generate UUIDs in your app.
- `items.images` uses `JSON`. On MariaDB < 10.4 or MySQL < 5.7, change to `TEXT`.

Mapping from current frontend

- SQLite `TEXT` IDs (hex blobs) are replaced with UUID `CHAR(36)`.
- `images` stored as JSON array. If you prefer TEXT, change column to `TEXT` and store JSON string.
- Timestamps default to `CURRENT_TIMESTAMP` and auto-update on `updated_at`.

Optional seed

You can insert sample rows via phpMyAdmin or adapt your seeding script to write into MySQL using your backend.


