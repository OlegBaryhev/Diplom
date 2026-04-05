CREATE TYPE sort_by_enum AS ENUM ('price_asc', 'price_desc', 'name_asc', 'name_desc');

-- Процедура для пересчёта относительной цены
CREATE OR REPLACE PROCEDURE recalculate_relative_current_price(
    p_name VARCHAR,
    p_description VARCHAR,
    p_recalculated_by VARCHAR,
    p_type VARCHAR,
    p_value NUMERIC,
    p_search VARCHAR DEFAULT NULL,
    p_min_price INT DEFAULT NULL,
    p_max_price INT DEFAULT NULL,
    p_category_id INT DEFAULT NULL,
    p_brand_id INT DEFAULT NULL,
    p_sort_by sort_by_enum DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_clause TEXT := '';
BEGIN
    -- Формируем условие сортировки
    IF p_sort_by = 'price_asc' THEN
        v_order_clause := 'ORDER BY price ASC';
    ELSIF p_sort_by = 'price_desc' THEN
        v_order_clause := 'ORDER BY price DESC';
    ELSIF p_sort_by = 'name_asc' THEN
        v_order_clause := 'ORDER BY name ASC';
    ELSIF p_sort_by = 'name_desc' THEN
        v_order_clause := 'ORDER BY name DESC';
    END IF;

    EXECUTE format(
        'WITH filtered AS (
            SELECT id, price FROM products WHERE
                ($1 IS NULL OR name ILIKE %% || $1 || %%) AND
                ($2 IS NULL OR price >= $2) AND
                ($3 IS NULL OR price <= $3) AND
                ($4 IS NULL OR category_id = $4) AND
                ($5 IS NULL OR brand_id = $5)
            %s
        )
        UPDATE products p
        SET price = CASE
            WHEN $6 = ''rubles'' THEN GREATEST(0, ROUND(p.price + $7))
            ELSE GREATEST(0, ROUND(p.price * (1 + $7/100.0)))
            END
        FROM filtered f WHERE p.id = f.id',
        v_order_clause
    )
    USING p_search, p_min_price, p_max_price, p_category_id, p_brand_id, p_type, p_value;

    INSERT INTO recalculate_history(name, description, recalculated_by, parameters)
    VALUES (p_name, p_description, p_recalculated_by,
            json_build_object(
                'type', p_type,
                'value', p_value,
                'search', p_search,
                'min_price', p_min_price,
                'max_price', p_max_price,
                'category_id', p_category_id,
                'brand_id', p_brand_id,
                'sort_by', p_sort_by
            ));
END;
$$;

-- Процедура для фиксированной установки цены
CREATE OR REPLACE PROCEDURE recalculate_fixed_value(
    p_name VARCHAR,
    p_description VARCHAR,
    p_recalculated_by VARCHAR,
    p_value INT,
    p_search VARCHAR DEFAULT NULL,
    p_min_price INT DEFAULT NULL,
    p_max_price INT DEFAULT NULL,
    p_category_id INT DEFAULT NULL,
    p_brand_id INT DEFAULT NULL,
    p_sort_by sort_by_enum DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_clause TEXT := '';
BEGIN
    IF p_sort_by = 'price_asc' THEN
        v_order_clause := 'ORDER BY price ASC';
    ELSIF p_sort_by = 'price_desc' THEN
        v_order_clause := 'ORDER BY price DESC';
    ELSIF p_sort_by = 'name_asc' THEN
        v_order_clause := 'ORDER BY name ASC';
    ELSIF p_sort_by = 'name_desc' THEN
        v_order_clause := 'ORDER BY name DESC';
    END IF;

    EXECUTE format(
        'WITH filtered AS (
            SELECT id FROM products WHERE
                ($1 IS NULL OR name ILIKE %% || $1 || %%) AND
                ($2 IS NULL OR price >= $2) AND
                ($3 IS NULL OR price <= $3) AND
                ($4 IS NULL OR category_id = $4) AND
                ($5 IS NULL OR brand_id = $5)
            %s
        )
        UPDATE products p SET price = GREATEST(0, $6) FROM filtered f WHERE p.id = f.id',
        v_order_clause
    )
    USING p_search, p_min_price, p_max_price, p_category_id, p_brand_id, p_value;

    INSERT INTO recalculate_history(name, description, recalculated_by, parameters)
    VALUES (p_name, p_description, p_recalculated_by,
            json_build_object(
                'value', p_value,
                'search', p_search,
                'min_price', p_min_price,
                'max_price', p_max_price,
                'category_id', p_category_id,
                'brand_id', p_brand_id,
                'sort_by', p_sort_by
            ));
END;
$$;

-- Процедура для среднего относительного пересчета с учётом аналогов и смещения
CREATE OR REPLACE PROCEDURE recalculate_average_relative_price(
    p_name VARCHAR,
    p_description VARCHAR,
    p_recalculated_by VARCHAR,
    p_type VARCHAR,
    p_value NUMERIC,
    p_offset BOOLEAN DEFAULT FALSE,
    p_search VARCHAR DEFAULT NULL,
    p_min_price INT DEFAULT NULL,
    p_max_price INT DEFAULT NULL,
    p_category_id INT DEFAULT NULL,
    p_brand_id INT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    products_cursor CURSOR FOR
        SELECT id, price FROM products
        WHERE
            (p_search IS NULL OR name ILIKE '%' || p_search || '%') AND
            (p_min_price IS NULL OR price >= p_min_price) AND
            (p_max_price IS NULL OR price <= p_max_price) AND
            (p_category_id IS NULL OR category_id = p_category_id) AND
            (p_brand_id IS NULL OR brand_id = p_brand_id);

    analogs_cursor CURSOR FOR
        SELECT price FROM analogs
        WHERE
            (p_search IS NULL OR name ILIKE '%' || p_search || '%') AND
            (p_min_price IS NULL OR price >= p_min_price) AND
            (p_max_price IS NULL OR price <= p_max_price) AND
            (p_category_id IS NULL OR category_id = p_category_id) AND
            (p_brand_id IS NULL OR brand_id = p_brand_id);

    avg_analogs_price NUMERIC := 0;
    avg_products_price NUMERIC := 0;
    avg_total_price NUMERIC := 0;

    p_count INT := 0;
    a_count INT := 0;

    rec RECORD;
BEGIN
    -- Вычисляем среднюю цену аналогов
    SELECT AVG(price) INTO avg_analogs_price FROM analogs
    WHERE
        (p_search IS NULL OR name ILIKE '%' || p_search || '%') AND
        (p_min_price IS NULL OR price >= p_min_price) AND
        (p_max_price IS NULL OR price <= p_max_price) AND
        (p_category_id IS NULL OR category_id = p_category_id) AND
        (p_brand_id IS NULL OR brand_id = p_brand_id);

    -- Вычисляем среднюю цену продуктов
    SELECT AVG(price) INTO avg_products_price FROM products
    WHERE
        (p_search IS NULL OR name ILIKE '%' || p_search || '%') AND
        (p_min_price IS NULL OR price >= p_min_price) AND
        (p_max_price IS NULL OR price <= p_max_price) AND
        (p_category_id IS NULL OR category_id = p_category_id) AND
        (p_brand_id IS NULL OR brand_id = p_brand_id);

    avg_total_price := (COALESCE(avg_analogs_price,0) + COALESCE(avg_products_price,0)) / 2;

    -- Обновляем цены продуктов по формуле
    FOR rec IN products_cursor LOOP
        DECLARE
            val NUMERIC;
            new_price INT;
        BEGIN
            IF p_type = 'rubles' THEN
                val := p_value;
            ELSE
                val := avg_total_price * (p_value / 100.0);
            END IF;

            IF p_offset THEN
                new_price := GREATEST(0, ROUND(avg_total_price + (rec.price - avg_total_price) + val));
            ELSE
                new_price := GREATEST(0, ROUND(rec.price + val));
            END IF;

            UPDATE products SET price = new_price WHERE id = rec.id;
        END;
    END LOOP;

    INSERT INTO recalculate_history(name, description, recalculated_by, parameters)
    VALUES (p_name, p_description, p_recalculated_by,
            json_build_object(
                'type', p_type,
                'value', p_value,
                'offset', p_offset,
                'search', p_search,
                'min_price', p_min_price,
                'max_price', p_max_price,
                'category_id', p_category_id,
                'brand_id', p_brand_id
            ));
END;
$$;