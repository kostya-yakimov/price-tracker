import os
import streamlit as st
import pandas as pd
import psycopg2
import time

st.set_page_config(
    page_title="Product Price Tracker",
    layout="wide"
)

st.title("🛒 Product Price Tracker")

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host="db",
        port="5432"
    )

@st.cache_data(ttl=30)
def load_data():
    query = """
    SELECT
        title,
        category,
        price,
        loaded_at
    FROM product_prices
    ORDER BY loaded_at DESC
    LIMIT 5000
    """

    return pd.read_sql(query, conn)

df = load_data()

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

product_df = df[df["title"] == selected_product]

chart_df = (
    product_df[["loaded_at", "price"]]
    .sort_values("loaded_at")
    .set_index("loaded_at")
)

st.line_chart(chart_df)
