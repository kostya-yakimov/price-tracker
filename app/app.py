import os
import streamlit as st
import pandas as pd
import psycopg2

st.set_page_config(
    page_title="Product Price Tracker",
    layout="wide"
)

st.title("🛒 Product Price Tracker")

# --- Подключение к БД ---
conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host="db",
    port="5432"
)

# --- Загрузка данных ---
query = """
SELECT
    title,
    category,
    price,
    loaded_at
FROM product_prices
ORDER BY loaded_at DESC
"""

df = pd.read_sql(query, conn)

# =========================
# Последние данные
# =========================
st.header("Latest Products")

latest_df = (
    df.sort_values("loaded_at")
      .groupby("title")
      .tail(1)
)

st.dataframe(latest_df, use_container_width=True)

# =========================
# Средние цены по категориям
# =========================
st.header("Average Price by Category")

avg_category = (
    latest_df.groupby("category")["price"]
    .mean()
    .reset_index()
)

st.bar_chart(
    avg_category.set_index("category")
)

# =========================
# История цен
# =========================
st.header("Price History")

product_list = sorted(df["title"].unique())

selected_product = st.selectbox(
    "Select product",
    product_list
)

product_df = df[df["title"] == selected_product].copy()

# Преобразуем дату
product_df["loaded_at"] = pd.to_datetime(product_df["loaded_at"])

# Сортировка
product_df = product_df.sort_values("loaded_at")

# График Altair
chart = alt.Chart(product_df).mark_line(point=True).encode(
    x=alt.X(
        "loaded_at:T",
        title="Time"
    ),
    y=alt.Y(
        "price:Q",
        title="Price"
    ),
    tooltip=["loaded_at:T", "price:Q"]
).properties(
    width=900,
    height=400
)

st.altair_chart(chart, use_container_width=True)

conn.close()
