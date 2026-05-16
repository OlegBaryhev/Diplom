CREATE OR REPLACE FUNCTION insert_categories(
    p_count INT
)
RETURNS void AS $$
DECLARE
  i INT;
BEGIN
  FOR i IN 1..p_count LOOP
    INSERT INTO categories (name, description)
    VALUES (
      'Категория_' || i,
      'Описание ' || i
    )
    ON CONFLICT (name) DO NOTHING;
  END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT insert_categories(10);
