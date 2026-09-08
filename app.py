import streamlit as st
import pandas as pd

# Load dataset
df = pd.read_csv("Nassau_Candy_Cleaned.csv")

# Title
st.title("Nassau Candy Distributor")
st.header("Product Line Profitability & Margin Performance Analysis")

# Overall calculations
total_sales = df["Sales"].sum()
total_cost = df["Cost"].sum()
total_profit = df["Gross Profit"].sum()
profit_margin = (total_profit / total_sales) * 100

# Key Performance Indicators
st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sales", round(total_sales, 2))
col2.metric("Total Cost", round(total_cost, 2))
col3.metric("Gross Profit", round(total_profit, 2))
col4.metric("Profit Margin", f"{profit_margin:.2f}%")

# Division Analysis
st.subheader("Division Analysis")

division_analysis = df.groupby("Division").agg({
    "Sales": "sum",
    "Cost": "sum",
    "Gross Profit": "sum",
    "Units": "sum"
})

division_analysis["Profit Margin"] = (
    division_analysis["Gross Profit"] /
    division_analysis["Sales"] * 100
)

st.write("Sales by Division")
st.bar_chart(division_analysis["Sales"])

st.write("Gross Profit by Division")
st.bar_chart(division_analysis["Gross Profit"])

st.write("Profit Margin by Division")
st.bar_chart(division_analysis["Profit Margin"])

# Product Analysis
st.subheader("Top 10 Products by Sales")

top_products = (
    df.groupby("Product Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(top_products)

st.subheader("Top 10 Products by Gross Profit")

top_profit_products = (
    df.groupby("Product Name")["Gross Profit"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(top_profit_products)

# Monthly Margin
st.subheader("Monthly Profit Margin")

df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

monthly = df.groupby(
    df["Order Date"].dt.to_period("M")
).agg({
    "Sales": "sum",
    "Gross Profit": "sum"
})

monthly["Profit Margin"] = (
    monthly["Gross Profit"] /
    monthly["Sales"] * 100
)

monthly.index = monthly.index.astype(str)

st.line_chart(monthly["Profit Margin"])

# Pareto Analysis
st.subheader("Pareto Analysis")

pareto = (
    df.groupby("Product Name")["Gross Profit"]
    .sum()
    .sort_values(ascending=False)
)

pareto_percentage = (pareto / pareto.sum()) * 100
pareto_cumulative = pareto_percentage.cumsum()

pareto_df = pd.DataFrame({
    "Gross Profit": pareto,
    "Cumulative Profit %": pareto_cumulative
})

st.line_chart(pareto_df["Cumulative Profit %"].head(20))

# Project Insights
st.subheader("Project Insights")

st.write("• Total Sales:", round(total_sales, 2))
st.write("• Total Cost:", round(total_cost, 2))
st.write("• Total Gross Profit:", round(total_profit, 2))
st.write("• Overall Profit Margin:", round(profit_margin, 2), "%")
st.write("• Most Profitable Division:", division_analysis["Gross Profit"].idxmax())
st.write("• Highest Sales Division:", division_analysis["Sales"].idxmax())
st.write("• Most Profitable Product:", top_profit_products.index[0])
st.write("• Highest Selling Product:", top_products.index[0])
