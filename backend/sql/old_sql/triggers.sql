CREATE OR REPLACE FUNCTION delete_category_if_no_products()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM products WHERE category_id = OLD.category_id
    ) THEN
        DELETE FROM categories WHERE id = OLD.category_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Триггер, срабатывающий после удаления продукта
CREATE TRIGGER trg_delete_category_after_product_delete
AFTER DELETE ON products
FOR EACH ROW
EXECUTE FUNCTION delete_category_if_no_products();

-- Триггер, срабатывающий после обновления category_id продукта (если меняется категория)
CREATE TRIGGER trg_delete_category_after_product_update
AFTER UPDATE OF category_id ON products
FOR EACH ROW
WHEN (OLD.category_id IS DISTINCT FROM NEW.category_id)
EXECUTE FUNCTION delete_category_if_no_products();

-- Удаление корзины при удалении пользователя
CREATE OR REPLACE FUNCTION delete_cart_items_after_user_delete()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM cart_items WHERE user_id = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_delete_cart_items_after_user_delete
AFTER DELETE ON "user"
FOR EACH ROW
EXECUTE FUNCTION delete_cart_items_after_user_delete();
