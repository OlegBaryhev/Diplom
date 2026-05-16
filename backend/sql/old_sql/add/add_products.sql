CREATE OR REPLACE FUNCTION insert_products_with_random_categories_and_brands_and_price(
    p_count INT,
    p_min_price INT,
    p_max_price INT
)
RETURNS void AS $$
DECLARE
  category_ids INT[];
  brand_ids INT[];
  i INT;
  cat_count INT;
  brand_count INT;
  random_price INT;
BEGIN
  SELECT array_agg(id) INTO category_ids FROM categories;
  cat_count := array_length(category_ids, 1);

  SELECT array_agg(id) INTO brand_ids FROM brands;
  brand_count := array_length(brand_ids, 1);

  IF cat_count IS NULL OR cat_count = 0 THEN
    RAISE EXCEPTION 'В таблице не найдено ни одной категории';
  END IF;

  IF brand_count IS NULL OR brand_count = 0 THEN
    RAISE EXCEPTION 'В таблице не найдено ни одного бренда';
  END IF;

  IF p_min_price > p_max_price THEN
    RAISE EXCEPTION 'Минимальная цена не может быть больше максимальной';
  END IF;

  FOR i IN 1..p_count LOOP
    random_price := floor(random() * (p_max_price - p_min_price + 1))::int + p_min_price;
    INSERT INTO products (name, description, price, category_id, brand_id)
    VALUES (
      'Продукт_' || i,
      'Описание продукта ' || i,
      random_price,
      category_ids[(floor(random() * cat_count + 1))::int],
      brand_ids[(floor(random() * brand_count + 1))::int]
    );
  END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT insert_products_with_random_categories_and_brands_and_price(10, 50000, 1500000);
