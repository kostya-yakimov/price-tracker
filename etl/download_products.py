import os
import time
import random
import requests
import psycopg2

# --- Подключение к PostgreSQL ---
import time

while True:
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("DB_HOST", "db"),
            port="5432"
        )

        print("Connected to PostgreSQL")
        break

    except Exception as e:
        print("Waiting for PostgreSQL...")
        print(e)
        time.sleep(5)

cur = conn.cursor()

while True:
    print("Loading products...")

    # --- Получение данных ---
    response = requests.get("https://dummyjson.com/products")
    products = response.json()["products"]

    # --- Загрузка в БД ---
    for product in products:

        # Небольшое случайное изменение цены
        modified_price = round(
            product["price"] * random.uniform(0.95, 1.05),
            2
        )

        cur.execute("""
            INSERT INTO product_prices (
                product_id,
                title,
                category,
                price
            )
            VALUES (%s, %s, %s, %s)
        """, (
            product["id"],
            product["title"],
            product["category"],
            modified_price
        ))

    conn.commit()

    cur.execute("""
    DELETE FROM product_prices
    WHERE id IN (
        SELECT id
        FROM (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY product_id
                       ORDER BY loaded_at DESC
                   ) AS rn
            FROM product_prices
        ) t
        WHERE rn > 100
    )
    """)

    conn.commit()

    print(f"Loaded {len(products)} products")

    # --- Ждем 30 минут ---
    time.sleep(30)
