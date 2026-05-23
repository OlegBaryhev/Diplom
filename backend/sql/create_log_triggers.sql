-- Функция-триггер для вставки в лог
CREATE OR REPLACE FUNCTION log_change()
RETURNS TRIGGER AS $$
DECLARE
    log_table_name TEXT;
    row_data JSONB;
BEGIN
    -- Сопоставление имени исходной таблицы с именем таблицы лога
    IF TG_TABLE_NAME = 'user' THEN
        log_table_name := 'user_log';
    ELSIF TG_TABLE_NAME = 'categories' THEN
        log_table_name := 'category_log';
    ELSIF TG_TABLE_NAME = 'brands' THEN
        log_table_name := 'brand_log';
    ELSIF TG_TABLE_NAME = 'orders' THEN
        log_table_name := 'order_log';
    ELSIF TG_TABLE_NAME = 'products' THEN
        log_table_name := 'product_log';
    ELSE
        RAISE EXCEPTION 'Unknown table: %', TG_TABLE_NAME;
    END IF;
    
    IF (TG_OP = 'DELETE') THEN
        row_data = to_jsonb(OLD);
    ELSE
        row_data = to_jsonb(NEW);
    END IF;
    
    EXECUTE format('INSERT INTO %I (operation, row_data) VALUES ($1, $2)', log_table_name)
    USING TG_OP, row_data;
    
    IF (TG_OP = 'DELETE') THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Удаляем старые триггеры, если есть
DROP TRIGGER IF EXISTS user_log_trigger ON "user";
DROP TRIGGER IF EXISTS category_log_trigger ON categories;
DROP TRIGGER IF EXISTS brand_log_trigger ON brands;
DROP TRIGGER IF EXISTS order_log_trigger ON orders;
DROP TRIGGER IF EXISTS product_log_trigger ON products;

-- Создаём триггеры
CREATE TRIGGER user_log_trigger
    AFTER INSERT OR UPDATE OR DELETE ON "user"
    FOR EACH ROW EXECUTE FUNCTION log_change();

CREATE TRIGGER category_log_trigger
    AFTER INSERT OR UPDATE OR DELETE ON categories
    FOR EACH ROW EXECUTE FUNCTION log_change();

CREATE TRIGGER brand_log_trigger
    AFTER INSERT OR UPDATE OR DELETE ON brands
    FOR EACH ROW EXECUTE FUNCTION log_change();

CREATE TRIGGER order_log_trigger
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION log_change();

CREATE TRIGGER product_log_trigger
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW EXECUTE FUNCTION log_change();