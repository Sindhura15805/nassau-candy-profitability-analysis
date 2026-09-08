import streamlit as st
import pandas as pd

# Load dataset
df = pd.read_csv("Nassau_Candy_Cleaned.csv")

# Convert date
df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

# Title
st.title("Nassau Candy Distributor")
st.header("Product Line Profitability & Margin Performance Analysis")

# ---------------- FILTERS ----------------

st.sidebar.header("Filters")

# Date filter
min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    [min_date, max_date]
)

# Division filter
divisions = ["All"] + sorted(df["Division"].dropna().unique().tolist())
selected_division = st.sidebar.selectbox(
    "Division",
    divisions
)

# Margin threshold
margin_threshold = st.sidebar.slider(
    "Minimum Margin (%)",
    0, 100, 20
)

# Product search
product_search = st.sidebar.text_input(
    "Search Product"
)

# Apply date filter
if len(date_range) == 2:
    df = df[
        (df["Order Date"].dt.date >= date_range[0]) &
        (df["Order Date"].dt.date <= date_range[1])
    ]

# Apply division filter
if selected_division != "All":
    df = df[df["Division"] == selected_division]

# Product search
if product_search:
    df = df[
        df["Product Name"].str.contains(
            product_search,
            case=False,
            na=False
        )
    ]

# ---------------- KPI ----------------

total_sales = df["Sales"].sum()
total_cost = df["Cost"].sum()
total_profit = df["Gross Profit"].sum()

if total_sales != 0:
    profit_margin = total_profit / total_sales * 100
else:
    profit_margin = 0

st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sales", round(total_sales, 2))
col2.metric("Total Cost", round(total_cost, 2))
col3.metric("Gross Profit", round(total_profit, 2))
col4.metric("Profit Margin", f"{profit_margin:.2f}%")

# ---------------- PRODUCT PROFITABILITY ----------------

st.subheader("Product Profitability Overview")

product_analysis = df.groupby("Product Name").agg({
    "Sales": "sum",
    "Units": "sum",
    "Gross Profit": "sum"
})

product_analysis["Gross Margin (%)"] = (
    product_analysis["Gross Profit"] /
    product_analysis["Sales"] * 100
)

product_analysis["Profit per Unit"] = (
    product_analysis["Gross Profit"] /
    product_analysis["Units"]
)

product_analysis = product_analysis.replace(
    [float("inf"), -float("inf")], 0
).fillna(0)

filtered_products = product_analysis[
    product_analysis["Gross Margin (%)"] >= margin_threshold
]

st.write("Product Margin Leaderboard")
st.dataframe(
    filtered_products.sort_values(
        "Gross Margin (%)",
        ascending=False
    ).head(10)
)

st.write("Top 10 Products by Gross Profit")

top_profit = (
    df.groupby("Product Name")["Gross Profit"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(top_profit)

# ---------------- DIVISION ----------------

st.subheader("Division Performance Dashboard")

division_analysis = df.groupby("Division").agg({
    "Sales": "sum",
    "Gross Profit": "sum"
})

division_analysis["Gross Margin (%)"] = (
    division_analysis["Gross Profit"] /
    division_analysis["Sales"] * 100
)

st.write("Revenue vs Profit")

st.bar_chart(
    division_analysis[["Sales", "Gross Profit"]]
)

st.write("Margin by Division")

st.bar_chart(
    division_analysis["Gross Margin (%)"]
)

# ---------------- COST VS MARGIN ----------------

st.subheader("Cost vs Margin Diagnostics")

cost_margin = df.groupby("Product Name").agg({
    "Sales": "sum",
    "Cost": "sum",
    "Gross Profit": "sum"
})

cost_margin["Margin (%)"] = (
    cost_margin["Gross Profit"] /
    cost_margin["Sales"] * 100
)

st.scatter_chart(
    cost_margin[["Sales", "Cost"]]
)

st.write("Margin Risk Products")

risk_products = cost_margin[
    cost_margin["Margin (%)"] < margin_threshold
]

st.dataframe(
    risk_products.sort_values(
        "Margin (%)"
    ).head(10)
)

# ---------------- PARETO ----------------

st.subheader("Profit Concentration Analysis")

pareto = (
    df.groupby("Product Name")["Gross Profit"]
    .sum()
    .sort_values(ascending=False)
)

cumulative_profit = (
    pareto.cumsum() / pareto.sum() * 100
)

st.line_chart(
    cumulative_profit.head(20)
)

products_80 = (cumulative_profit <= 80).sum()

st.write(
    "Products contributing to approximately 80% of profit:",
    products_80
)

# ---------------- INSIGHTS ----------------

st.subheader("Project Insights")

if not division_analysis.empty:
    st.write(
        "Most Profitable Division:",
        division_analysis["Gross Profit"].idxmax()
    )

if not top_profit.empty:
    st.write(
        "Most Profitable Product:",
        top_profit.index[0]
    )

st.write(
    "Number of Margin Risk Products:",
    len(risk_products)
)
