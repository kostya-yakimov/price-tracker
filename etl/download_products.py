import os
import time
import random
import requests
import psycopg2
from psycopg2 import OperationalError

# --- Подключение к PostgreSQL с авторестартом ---
def get_connection():
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
            return conn
        except OperationalError as e:
            print("Waiting for PostgreSQL...")
            print(e)
            time.sleep(5)

conn = get_connection()

while True:
    print("Loading products...")
    try:
        # --- Получение данных ---
        response = requests.get("https://dummyjson.com/products", timeout=10)
        response.raise_for_status()
        products = response.json()["products"]
        
        # --- Использование контекстного менеджера для курсора ---
        with conn.cursor() as cur:
            # --- Загрузка в БД ---
            for product in products:
                modified_price = round(product["price"] * random.uniform(0.95, 1.05), 2)
                
                # Используем ON CONFLICT, если product_id уникален, либо просто копим историю
                cur.execute("""
                    INSERT INTO product_prices (product_id, title, category, price)
                    VALUES (%s, %s, %s, %s)
                """, (
                    product["id"],
                    product["title"],
                    product["category"],
                    modified_price
                ))
            
            # --- Очистка старых записей (ротация) ---
            cur.execute("""
                DELETE FROM product_prices 
                WHERE id IN (
                    SELECT id FROM (
                        SELECT id, ROW_NUMBER() OVER (
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

    except requests.RequestException as req_err:
        print(f"API Error: {req_err}")
    except psycopg2.Error as db_err:
        print(f"Database Error: {db_err}")
        conn.rollback()
        # Если база упала, переподключаемся
        conn = get_connection()

    # --- Ждем 15 минут ---
    print("Sleeping for 15 minutes...")
    time.sleep(900)
