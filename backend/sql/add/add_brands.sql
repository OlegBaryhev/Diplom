CREATE OR REPLACE FUNCTION insert_brands(
    p_count INT
)
RETURNS void AS $$
DECLARE
  i INT;
BEGIN
  FOR i IN 1..p_count LOOP
    INSERT INTO brands (name, description, created_at)
    VALUES (
      'Бренд_' || i,
      'Описание бренда ' || i,
      NOW()
    )
    ON CONFLICT (name) DO NOTHING;
  END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT insert_brands(10);
