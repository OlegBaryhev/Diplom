CREATE OR REPLACE PROCEDURE add_admin_user(
    p_email VARCHAR,
    p_hashed_password VARCHAR,
    p_name VARCHAR DEFAULT NULL,
    p_surname VARCHAR DEFAULT NULL,
    p_avatar_url VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO "user" (email, hashed_password, name, surname, role, is_active, avatar_url)
    VALUES (p_email, p_hashed_password, p_name, p_surname, 'superuser', 1, p_avatar_url);
END;
$$;