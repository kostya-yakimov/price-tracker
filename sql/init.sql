CREATE TABLE IF NOT EXISTS product_prices (
    id SERIAL PRIMARY KEY,
    product_id INT,
    title TEXT,
    category TEXT,
    price NUMERIC,
    loaded_at TIMESTAMP DEFAULT NOW()
);
