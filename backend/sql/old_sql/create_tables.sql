CREATE TYPE userrole AS ENUM ('superuser', 'moderator', 'guest');
CREATE TYPE orderstatus AS ENUM ('pending', 'ready', 'completed', 'cancelled');

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    name VARCHAR,
    surname VARCHAR,
    role userrole NOT NULL DEFAULT 'guest',
    is_active INTEGER DEFAULT 1,
    avatar_url VARCHAR
);

CREATE TABLE recalculate_history (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    recalculated_by VARCHAR NOT NULL,
    recalculated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    parameters JSON NOT NULL
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR
);

CREATE TABLE brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    price INTEGER NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    brand_id INTEGER NOT NULL REFERENCES brands(id) ON DELETE CASCADE
);

CREATE TABLE analogs (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    price INTEGER NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    brand_id INTEGER NOT NULL REFERENCES brands(id) ON DELETE CASCADE
);

CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    CONSTRAINT user_product_unique UNIQUE (user_id, product_id)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    status orderstatus DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT now(),
    pickup_code VARCHAR NOT NULL UNIQUE
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL
);