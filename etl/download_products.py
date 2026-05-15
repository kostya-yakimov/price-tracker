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
            host="db",
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

    print(f"Loaded {len(products)} products")

    # --- Ждем 30 минут ---
    time.sleep(1800)
