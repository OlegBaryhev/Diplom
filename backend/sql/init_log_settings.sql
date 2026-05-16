INSERT INTO log_settings (table_name, time_retention_minutes, count_retention_limit)
VALUES
    ('user', 30, 5),
    ('category', 30, 5),
    ('brand', 30, 5),
    ('order', 30, 5),
    ('product', 30, 5),
    ('recalculate_history', 30, 5)
ON CONFLICT (table_name) DO NOTHING;