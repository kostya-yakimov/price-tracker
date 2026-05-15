import os
import requests
import psycopg2

# --- Подключение к PostgreSQL ---
conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host="db",
    port="5432"
)

cur = conn.cursor()

# --- Получение данных из API ---
response = requests.get("https://dummyjson.com/products")
products = response.json()["products"]

# --- Загрузка данных в БД ---
for product in products:
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
        product["price"]
    ))

conn.commit()

cur.close()
conn.close()

print(f"Loaded {len(products)} products")
