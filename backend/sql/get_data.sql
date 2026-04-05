-- Реализация функции поиска для категорий(Аналогично ручке /search)
CREATE OR REPLACE FUNCTION search_categories(
    p_search VARCHAR DEFAULT NULL,
    p_sort_by VARCHAR DEFAULT NULL
) RETURNS TABLE (
    id INT,
    name VARCHAR,
    description VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.description
    FROM categories c
    WHERE
        (p_search IS NULL OR c.name ILIKE '%' || p_search || '%')
    ORDER BY
        CASE WHEN p_sort_by = 'name_asc' THEN c.name END ASC,
        CASE WHEN p_sort_by = 'name_desc' THEN c.name END DESC,
        c.id ASC;
END;
$$ LANGUAGE plpgsql STABLE;


-- Вызов функции
SELECT * FROM search_categories('Какая-то очень полезная вещь', 'name_asc');

-- Пустое значение
SELECT * FROM search_categories(NULL, NULL);

