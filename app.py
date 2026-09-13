import streamlit as st
import pandas as pd

# ---------------- PAGE SETUP ----------------

st.set_page_config(
    page_title="Nassau Candy Profitability",
    page_icon="🍬",
    layout="wide"
)

# ---------------- LOAD DATA ----------------

df = pd.read_csv("Nassau_Candy_Cleaned.csv")

df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    errors="coerce"
)

# ---------------- TITLE ----------------

st.title("🍬 Nassau Candy Distributor")
st.header("Product Line Profitability & Margin Performance Analysis")

st.write(
    "Interactive analysis of product profitability, division performance, "
    "cost structure and profit concentration."
)

st.divider()

# ---------------- SIDEBAR ----------------

st.sidebar.header("🔎 Filters")

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    [min_date, max_date]
)

divisions = ["All"] + sorted(
    df["Division"].dropna().unique().tolist()
)

selected_division = st.sidebar.selectbox(
    "Division",
    divisions
)

margin_threshold = st.sidebar.slider(
    "Minimum Gross Margin (%)",
    0,
    100,
    20
)

product_search = st.sidebar.text_input(
    "Search Product"
)

# ---------------- FILTER DATA ----------------

filtered_df = df.copy()

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["Order Date"].dt.date >= date_range[0]) &
        (filtered_df["Order Date"].dt.date <= date_range[1])
    ]

if selected_division != "All":
    filtered_df = filtered_df[
        filtered_df["Division"] == selected_division
    ]

if product_search:
    filtered_df = filtered_df[
        filtered_df["Product Name"].str.contains(
            product_search,
            case=False,
            na=False
        )
    ]

# ---------------- KPI CALCULATIONS ----------------

total_sales = filtered_df["Sales"].sum()
total_cost = filtered_df["Cost"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_units = filtered_df["Units"].sum()

profit_margin = (
    total_profit / total_sales * 100
    if total_sales != 0 else 0
)

# ---------------- KPI DISPLAY ----------------

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Cost", f"${total_cost:,.2f}")
col3.metric("Gross Profit", f"${total_profit:,.2f}")
col4.metric("Gross Margin", f"{profit_margin:.2f}%")
col5.metric("Total Units", f"{total_units:,.0f}")

st.divider()

# =========================================================
# PRODUCT PROFITABILITY
# =========================================================

st.header("1. Product Profitability Overview")

product_analysis = filtered_df.groupby("Product Name").agg(
    Sales=("Sales", "sum"),
    Units=("Units", "sum"),
    Gross_Profit=("Gross Profit", "sum")
)

product_analysis["Gross Margin (%)"] = (
    product_analysis["Gross_Profit"] /
    product_analysis["Sales"] * 100
)

product_analysis["Profit per Unit"] = (
    product_analysis["Gross_Profit"] /
    product_analysis["Units"]
)

product_analysis = product_analysis.replace(
    [float("inf"), -float("inf")],
    0
).fillna(0)

leaderboard = product_analysis[
    product_analysis["Gross Margin (%)"] >= margin_threshold
].sort_values(
    "Gross Margin (%)",
    ascending=False
).head(10)

st.subheader("🏆 Product Margin Leaderboard")

st.dataframe(
    leaderboard.style.format({
        "Sales": "${:,.2f}",
        "Gross_Profit": "${:,.2f}",
        "Gross Margin (%)": "{:.2f}%",
        "Profit per Unit": "${:,.2f}"
    }),
    use_container_width=True
)

# ---------------- TOP PRODUCTS BY PROFIT ----------------

st.subheader("Top 10 Products by Gross Profit")

top_profit = (
    filtered_df.groupby("Product Name")["Gross Profit"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(top_profit)

# =========================================================
# DIVISION PERFORMANCE
# =========================================================

st.header("2. Division Performance Dashboard")

division_analysis = filtered_df.groupby("Division").agg(
    Sales=("Sales", "sum"),
    Cost=("Cost", "sum"),
    Gross_Profit=("Gross Profit", "sum"),
    Units=("Units", "sum")
)

division_analysis["Gross Margin (%)"] = (
    division_analysis["Gross_Profit"] /
    division_analysis["Sales"] * 100
)

division_analysis = division_analysis.replace(
    [float("inf"), -float("inf")],
    0
).fillna(0)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue vs Gross Profit")

    st.bar_chart(
        division_analysis[["Sales", "Gross_Profit"]]
    )

with col2:
    st.subheader("Gross Margin by Division")

    st.bar_chart(
        division_analysis["Gross Margin (%)"]
    )

st.subheader("Division Performance Table")

st.dataframe(
    division_analysis.style.format({
        "Sales": "${:,.2f}",
        "Cost": "${:,.2f}",
        "Gross_Profit": "${:,.2f}",
        "Gross Margin (%)": "{:.2f}%"
    }),
    use_container_width=True
)

# =========================================================
# COST VS MARGIN
# =========================================================

st.header("3. Cost vs Margin Diagnostics")

cost_margin = filtered_df.groupby("Product Name").agg(
    Sales=("Sales", "sum"),
    Cost=("Cost", "sum"),
    Gross_Profit=("Gross Profit", "sum")
)

cost_margin["Margin (%)"] = (
    cost_margin["Gross_Profit"] /
    cost_margin["Sales"] * 100
)

cost_margin = cost_margin.replace(
    [float("inf"), -float("inf")],
    0
).fillna(0)

# ---------------- COST VS SALES CHART ----------------

st.subheader("Cost vs Sales")

scatter_data = cost_margin[["Sales", "Cost"]].copy()

st.scatter_chart(
    scatter_data,
    x="Sales",
    y="Cost"
)

# ---------------- RISK PRODUCTS ----------------

st.subheader("⚠️ Margin Risk Products")

risk_products = cost_margin[
    cost_margin["Margin (%)"] < margin_threshold
].sort_values(
    "Margin (%)"
)

st.dataframe(
    risk_products.head(10).style.format({
        "Sales": "${:,.2f}",
        "Cost": "${:,.2f}",
        "Gross_Profit": "${:,.2f}",
        "Margin (%)": "{:.2f}%"
    }),
    use_container_width=True
)

# =========================================================
# HIGH SALES / LOW MARGIN
# =========================================================

st.subheader("High-Sales / Low-Margin Products")

if not cost_margin.empty:

    high_sales_low_margin = cost_margin[
        (cost_margin["Sales"] >= cost_margin["Sales"].median()) &
        (cost_margin["Margin (%)"] < cost_margin["Margin (%)"].median())
    ]

    st.dataframe(
        high_sales_low_margin.sort_values(
            "Sales",
            ascending=False
        ).head(10).style.format({
            "Sales": "${:,.2f}",
            "Cost": "${:,.2f}",
            "Gross_Profit": "${:,.2f}",
            "Margin (%)": "{:.2f}%"
        }),
        use_container_width=True
    )

# =========================================================
# PROFIT CONCENTRATION
# =========================================================

st.header("4. Profit Concentration Analysis")

pareto = (
    filtered_df.groupby("Product Name")["Gross Profit"]
    .sum()
    .sort_values(ascending=False)
)

if pareto.sum() != 0:

    cumulative_profit = (
        pareto.cumsum() /
        pareto.sum() * 100
    )

    st.subheader("Pareto Analysis — Cumulative Profit")

    st.line_chart(
        cumulative_profit
    )

    products_80 = (
        cumulative_profit <= 80
    ).sum()

    total_products = len(pareto)

    st.metric(
        "Products contributing up to 80% of profit",
        products_80
    )

    st.write(
        f"Total products analyzed: **{total_products}**"
    )

# =========================================================
# MONTHLY MARGIN
# =========================================================

st.header("5. Monthly Margin Performance")

monthly = filtered_df.groupby(
    filtered_df["Order Date"].dt.to_period("M")
).agg(
    Sales=("Sales", "sum"),
    Gross_Profit=("Gross Profit", "sum")
)

monthly["Profit Margin (%)"] = (
    monthly["Gross_Profit"] /
    monthly["Sales"] * 100
)

monthly = monthly.replace(
    [float("inf"), -float("inf")],
    0
).fillna(0)

st.line_chart(
    monthly["Profit Margin (%)"]
)

if not monthly.empty:

    st.write(
        "Highest Monthly Margin:",
        f"{monthly['Profit Margin (%)'].max():.2f}%"
    )

    st.write(
        "Lowest Monthly Margin:",
        f"{monthly['Profit Margin (%)'].min():.2f}%"
    )

    st.write(
        "Average Monthly Margin:",
        f"{monthly['Profit Margin (%)'].mean():.2f}%"
    )

# =========================================================
# PROJECT INSIGHTS
# =========================================================

st.header("6. Project Insights")

if not division_analysis.empty:

    most_profitable_division = (
        division_analysis["Gross_Profit"].idxmax()
    )

    st.write(
        "🏭 **Most Profitable Division:**",
        most_profitable_division
    )

if not top_profit.empty:

    st.write(
        "🍫 **Most Profitable Product:**",
        top_profit.index[0]
    )

if not product_analysis.empty:

    highest_margin_product = (
        product_analysis["Gross Margin (%)"].idxmax()
    )

    st.write(
        "📈 **Highest Margin Product:**",
        highest_margin_product
    )

st.write(
    "⚠️ **Margin Risk Products:**",
    len(risk_products)
)

# =========================================================
# METHODOLOGY
# =========================================================

st.header("7. Methodology")

st.write("""
**Gross Profit = Sales − Cost**

**Gross Margin (%) = Gross Profit ÷ Sales × 100**

**Profit per Unit = Gross Profit ÷ Units**

**Revenue Contribution (%) = Product Sales ÷ Total Sales × 100**

**Profit Contribution (%) = Product Gross Profit ÷ Total Gross Profit × 100**

The analysis uses Python, Pandas and Streamlit.
""")

st.divider()

st.caption(
    "Nassau Candy Distributor | Product Line Profitability & Margin Performance Analysis"
)
