import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Nassau Candy Distributor",
    page_icon="🍫",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("🍫 Nassau Candy Distributor")
st.subheader("Product Line Profitability & Margin Performance Analysis")

st.markdown(
    """
    This Data Science project analyzes product profitability, gross margin,
    division performance, cost structure, profit concentration, regional
    performance, and margin volatility.
    """
)

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv("Nassau_Candy_Cleaned.csv")

# =========================================================
# DATA CLEANING & VALIDATION
# =========================================================

df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")

numeric_columns = ["Sales", "Units", "Gross Profit", "Cost"]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Remove invalid records
df = df.dropna(
    subset=["Order Date", "Sales", "Gross Profit", "Cost"]
)

# Remove zero / negative sales
df = df[df["Sales"] > 0]

# Handle missing units
df["Units"] = df["Units"].fillna(0)

# Standardize labels
df["Division"] = df["Division"].astype(str).str.strip()
df["Product Name"] = df["Product Name"].astype(str).str.strip()

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Dashboard Filters")

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

division_options = ["All"] + sorted(
    df["Division"].dropna().unique().tolist()
)

selected_division = st.sidebar.selectbox(
    "Division",
    division_options
)

margin_threshold = st.sidebar.slider(
    "Margin Threshold (%)",
    min_value=0,
    max_value=100,
    value=20,
    step=5
)

product_search = st.sidebar.text_input(
    "Product Search"
)

# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    filtered_df = filtered_df[
        (filtered_df["Order Date"] >= start_date)
        & (filtered_df["Order Date"] <= end_date)
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

df = filtered_df.copy()

# =========================================================
# CALCULATED FIELDS
# =========================================================

df["Gross Margin (%)"] = np.where(
    df["Sales"] != 0,
    (df["Gross Profit"] / df["Sales"]) * 100,
    0
)

df["Profit per Unit"] = np.where(
    df["Units"] > 0,
    df["Gross Profit"] / df["Units"],
    0
)

# =========================================================
# 1. PROJECT OVERVIEW
# =========================================================

st.markdown("---")
st.header("📌 1. Project Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Records", f"{len(df):,}")

with col2:
    st.metric("Products", df["Product Name"].nunique())

with col3:
    st.metric("Divisions", df["Division"].nunique())

st.markdown(
    """
    **Objective:** Analyze product-level and division-level profitability,
    identify margin risks, understand cost structure, measure profit
    concentration, and provide business recommendations.
    """
)

# =========================================================
# 2. DATASET OVERVIEW
# =========================================================

st.header("📁 2. Dataset Overview")

total_sales = df["Sales"].sum()
total_cost = df["Cost"].sum()
total_profit = df["Gross Profit"].sum()
total_units = df["Units"].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Sales", f"${total_sales:,.2f}")

with col2:
    st.metric("Total Cost", f"${total_cost:,.2f}")

with col3:
    st.metric("Gross Profit", f"${total_profit:,.2f}")

with col4:
    st.metric("Total Units", f"{total_units:,.0f}")

with st.expander("📄 Dataset Preview"):
    st.dataframe(
        df.head(10),
        use_container_width=True
    )

# =========================================================
# 3. KPI DASHBOARD
# =========================================================

st.header("📊 3. KPI Dashboard")

gross_margin = (
    total_profit / total_sales * 100
    if total_sales != 0 else 0
)

profit_per_unit = (
    total_profit / total_units
    if total_units != 0 else 0
)

# Product-level aggregation
product = df.groupby(
    ["Product Name", "Division"],
    as_index=False
).agg({
    "Sales": "sum",
    "Units": "sum",
    "Gross Profit": "sum",
    "Cost": "sum"
})

product["Gross Margin (%)"] = np.where(
    product["Sales"] != 0,
    product["Gross Profit"] / product["Sales"] * 100,
    0
)

product["Profit per Unit"] = np.where(
    product["Units"] > 0,
    product["Gross Profit"] / product["Units"],
    0
)

product["Revenue Contribution (%)"] = np.where(
    total_sales != 0,
    product["Sales"] / total_sales * 100,
    0
)

product["Profit Contribution (%)"] = np.where(
    total_profit != 0,
    product["Gross Profit"] / total_profit * 100,
    0
)

highest_revenue_contribution = (
    product["Revenue Contribution (%)"].max()
    if not product.empty else 0
)

highest_profit_contribution = (
    product["Profit Contribution (%)"].max()
    if not product.empty else 0
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Gross Margin",
        f"{gross_margin:.2f}%"
    )

with col2:
    st.metric(
        "Profit per Unit",
        f"${profit_per_unit:.2f}"
    )

with col3:
    st.metric(
        "Highest Product Revenue Contribution",
        f"{highest_revenue_contribution:.2f}%"
    )

with col4:
    st.metric(
        "Highest Product Profit Contribution",
        f"{highest_profit_contribution:.2f}%"
    )

# =========================================================
# 4. PRODUCT PROFITABILITY
# =========================================================

st.header("🍫 4. Product Profitability Overview")

st.subheader("Product-Level Margin Leaderboard")

leaderboard = product.sort_values(
    "Gross Profit",
    ascending=False
).copy()

leaderboard = leaderboard[
    [
        "Product Name",
        "Division",
        "Sales",
        "Cost",
        "Gross Profit",
        "Gross Margin (%)",
        "Profit per Unit",
        "Revenue Contribution (%)",
        "Profit Contribution (%)"
    ]
]

leaderboard.columns = [
    "Product",
    "Division",
    "Sales",
    "Cost",
    "Gross Profit",
    "Gross Margin (%)",
    "Profit per Unit",
    "Revenue Contribution (%)",
    "Profit Contribution (%)"
]

with st.expander("View Product Profitability Leaderboard"):
    st.dataframe(
        leaderboard.style.format({
            "Sales": "${:,.2f}",
            "Cost": "${:,.2f}",
            "Gross Profit": "${:,.2f}",
            "Gross Margin (%)": "{:.2f}%",
            "Profit per Unit": "${:.2f}",
            "Revenue Contribution (%)": "{:.2f}%",
            "Profit Contribution (%)": "{:.2f}%"
        }),
        use_container_width=True
    )

col1, col2 = st.columns(2)

with col1:

    top_profit = product.nlargest(
        10,
        "Gross Profit"
    ).sort_values(
        "Gross Profit"
    )

    fig = px.bar(
        top_profit,
        x="Gross Profit",
        y="Product Name",
        orientation="h",
        title="Top Products by Gross Profit"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    top_margin = product.nlargest(
        10,
        "Gross Margin (%)"
    ).sort_values(
        "Gross Margin (%)"
    )

    fig = px.bar(
        top_margin,
        x="Gross Margin (%)",
        y="Product Name",
        orientation="h",
        title="Top Products by Gross Margin"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================================
# 5. PRODUCT CLASSIFICATION
# =========================================================

st.header("📦 5. Product Profitability Classification")

median_sales = product["Sales"].median()
median_profit = product["Gross Profit"].median()

def classify_product(row):

    if row["Sales"] >= median_sales and row["Gross Profit"] >= median_profit:
        return "High Sales / High Profit"

    elif row["Sales"] >= median_sales and row["Gross Profit"] < median_profit:
        return "High Sales / Low Profit"

    elif row["Sales"] < median_sales and row["Gross Profit"] >= median_profit:
        return "Low Sales / High Profit"

    else:
        return "Low Sales / Low Profit"

product["Performance Category"] = product.apply(
    classify_product,
    axis=1
)

classification_counts = (
    product["Performance Category"]
    .value_counts()
    .reset_index()
)

classification_counts.columns = [
    "Category",
    "Products"
]

fig = px.bar(
    classification_counts,
    x="Category",
    y="Products",
    title="Product Performance Classification"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

with st.expander("View Classification Table"):
    st.dataframe(
        product[
            [
                "Product Name",
                "Division",
                "Sales",
                "Gross Profit",
                "Performance Category"
            ]
        ],
        use_container_width=True
    )

# =========================================================
# 6. DIVISION PERFORMANCE
# =========================================================

st.header("🏢 6. Division Performance Dashboard")

division = df.groupby(
    "Division",
    as_index=False
).agg({
    "Sales": "sum",
    "Gross Profit": "sum",
    "Cost": "sum",
    "Units": "sum"
})

division["Gross Margin (%)"] = np.where(
    division["Sales"] != 0,
    division["Gross Profit"] /
    division["Sales"] * 100,
    0
)

division["Profit per Unit"] = np.where(
    division["Units"] > 0,
    division["Gross Profit"] /
    division["Units"],
    0
)

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        division,
        x="Division",
        y=["Sales", "Gross Profit"],
        barmode="group",
        title="Revenue vs Profit by Division"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.bar(
        division,
        x="Division",
        y="Gross Margin (%)",
        title="Gross Margin by Division"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.subheader("Margin Distribution by Division")

division_margin = df[
    ["Division", "Gross Margin (%)"]
]

fig = px.box(
    division_margin,
    x="Division",
    y="Gross Margin (%)",
    title="Margin Distribution by Division"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

with st.expander("View Division Performance Table"):

    st.dataframe(
        division.style.format({
            "Sales": "${:,.2f}",
            "Gross Profit": "${:,.2f}",
            "Cost": "${:,.2f}",
            "Gross Margin (%)": "{:.2f}%",
            "Profit per Unit": "${:.2f}"
        }),
        use_container_width=True
    )

most_profitable_division = division.loc[
    division["Gross Profit"].idxmax(),
    "Division"
]

highest_margin_division = division.loc[
    division["Gross Margin (%)"].idxmax(),
    "Division"
]

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Most Profitable Division",
        most_profitable_division
    )

with col2:
    st.metric(
        "Highest Margin Division",
        highest_margin_division
    )

# =========================================================
# 7. COST STRUCTURE DIAGNOSTICS
# =========================================================

st.header("💸 7. Cost Structure Diagnostics")

fig = px.scatter(
    product,
    x="Sales",
    y="Cost",
    size="Gross Profit",
    hover_name="Product Name",
    title="Cost vs Sales"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.write(
    "Products with relatively high costs compared with their sales "
    "may require pricing, sourcing or cost-control review."
)

risk_products = product[
    product["Gross Margin (%)"] < margin_threshold
].copy()

st.subheader(
    f"Margin Risk Products Below {margin_threshold}%"
)

st.write(
    f"**{len(risk_products)} product(s)** are below "
    f"the selected margin threshold."
)

if not risk_products.empty:

    st.dataframe(
        risk_products[
            [
                "Product Name",
                "Division",
                "Sales",
                "Cost",
                "Gross Profit",
                "Gross Margin (%)"
            ]
        ],
        use_container_width=True
    )

high_sales_low_margin = product[
    (product["Sales"] >= median_sales)
    & (product["Gross Margin (%)"] < margin_threshold)
]

st.subheader("High-Sales / Low-Margin Products")

if high_sales_low_margin.empty:

    st.info(
        "No high-sales / low-margin products found "
        "under the selected margin threshold."
    )

else:

    st.dataframe(
        high_sales_low_margin[
            [
                "Product Name",
                "Division",
                "Sales",
                "Gross Profit",
                "Gross Margin (%)"
            ]
        ],
        use_container_width=True
    )

# =========================================================
# 8. PROFIT CONCENTRATION
# =========================================================

st.header("📈 8. Profit Concentration Analysis")

# Revenue Pareto

revenue_pareto = product.sort_values(
    "Sales",
    ascending=False
).copy()

revenue_pareto["Cumulative Revenue (%)"] = (
    revenue_pareto["Sales"].cumsum()
    / revenue_pareto["Sales"].sum()
    * 100
)

products_80_revenue = (
    revenue_pareto["Cumulative Revenue (%)"] <= 80
).sum()

if products_80_revenue == 0:
    products_80_revenue = 1

fig = px.bar(
    revenue_pareto,
    x="Product Name",
    y="Cumulative Revenue (%)",
    title="Revenue Pareto"
)

fig.add_hline(
    y=80,
    line_dash="dash"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.metric(
    "Products Needed for 80% Revenue",
    f"{products_80_revenue} "
    f"({products_80_revenue / len(product) * 100:.2f}%)"
)

# Profit Pareto

profit_pareto = product.sort_values(
    "Gross Profit",
    ascending=False
).copy()

profit_pareto["Cumulative Profit (%)"] = (
    profit_pareto["Gross Profit"].cumsum()
    / profit_pareto["Gross Profit"].sum()
    * 100
)

products_80_profit = (
    profit_pareto["Cumulative Profit (%)"] <= 80
).sum()

if products_80_profit == 0:
    products_80_profit = 1

fig = px.bar(
    profit_pareto,
    x="Product Name",
    y="Cumulative Profit (%)",
    title="Profit Pareto"
)

fig.add_hline(
    y=80,
    line_dash="dash"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.metric(
    "Products Needed for 80% Profit",
    f"{products_80_profit} "
    f"({products_80_profit / len(product) * 100:.2f}%)"
)

# =========================================================
# 9. REGIONAL & STATE PERFORMANCE
# =========================================================

st.header("🌎 9. Regional & State Performance")

region = df.groupby(
    "Region",
    as_index=False
).agg({
    "Sales": "sum",
    "Gross Profit": "sum"
})

fig = px.bar(
    region,
    x="Region",
    y=["Sales", "Gross Profit"],
    barmode="group",
    title="Revenue & Gross Profit by Region"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

state = df.groupby(
    "State/Province",
    as_index=False
).agg({
    "Sales": "sum",
    "Gross Profit": "sum"
})

top_states_revenue = state.nlargest(
    10,
    "Sales"
)

fig = px.bar(
    top_states_revenue.sort_values("Sales"),
    x="Sales",
    y="State/Province",
    orientation="h",
    title="Top States by Revenue"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

top_states_profit = state.nlargest(
    10,
    "Gross Profit"
)

fig = px.bar(
    top_states_profit.sort_values("Gross Profit"),
    x="Gross Profit",
    y="State/Province",
    orientation="h",
    title="Top States by Gross Profit"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# 10. MARGIN VOLATILITY
# =========================================================

st.header("📅 10. Margin Volatility Analysis")

monthly = df.set_index(
    "Order Date"
).resample("ME").agg({
    "Sales": "sum",
    "Gross Profit": "sum",
    "Cost": "sum"
}).reset_index()

monthly["Gross Margin (%)"] = np.where(
    monthly["Sales"] != 0,
    monthly["Gross Profit"] /
    monthly["Sales"] * 100,
    0
)

fig = px.line(
    monthly,
    x="Order Date",
    y=["Sales", "Gross Profit"],
    title="Monthly Sales & Gross Profit"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

fig = px.line(
    monthly,
    x="Order Date",
    y="Gross Margin (%)",
    title="Monthly Gross Margin"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

margin_volatility = monthly[
    "Gross Margin (%)"
].std()

st.metric(
    "Margin Volatility",
    f"{margin_volatility:.2f}%"
)

st.caption(
    "Margin volatility is measured using the standard deviation "
    "of monthly gross margin."
)

with st.expander("View Monthly Performance Table"):

    st.dataframe(
        monthly.style.format({
            "Sales": "${:,.2f}",
            "Gross Profit": "${:,.2f}",
            "Cost": "${:,.2f}",
            "Gross Margin (%)": "{:.2f}%"
        }),
        use_container_width=True
    )

# =========================================================
# 11. FACTORY & PRODUCT SUPPLY INFORMATION
# =========================================================

st.header("🏭 11. Factory & Product Supply Information")

factory_data = pd.DataFrame({
    "Factory": [
        "Lot's O' Nuts",
        "Wicked Choccy's",
        "Sugar Shack",
        "Secret Factory",
        "The Other Factory"
    ],
    "Latitude": [
        32.881893,
        32.076176,
        48.11914,
        41.446333,
        35.1175
    ],
    "Longitude": [
        -111.768036,
        -81.088371,
        -96.18115,
        -90.565487,
        -89.971107
    ]
})

st.subheader("Factory Locations")

st.map(
    factory_data.rename(
        columns={
            "Latitude": "lat",
            "Longitude": "lon"
        }
    )[["lat", "lon"]]
)

st.subheader("Factory Coordinates")

st.dataframe(
    factory_data,
    use_container_width=True
)

product_factory = pd.DataFrame({
    "Product": [
        "Wonka Bar - Nutty Crunch Surprise",
        "Wonka Bar - Fudge Mallows",
        "Wonka Bar -Scrumdiddlyumptious",
        "Wonka Bar - Milk Chocolate",
        "Wonka Bar - Triple Dazzle Caramel",
        "Laffy Taffy",
        "SweeTARTS",
        "Nerds",
        "Fun Dip",
        "Fizzy Lifting Drinks",
        "Everlasting Gobstopper",
        "Hair Toffee",
        "Lickable Wallpaper",
        "Wonka Gum",
        "Kazookles"
    ],
    "Factory": [
        "Lot's O' Nuts",
        "Lot's O' Nuts",
        "Lot's O' Nuts",
        "Wicked Choccy's",
        "Wicked Choccy's",
        "Sugar Shack",
        "Sugar Shack",
        "Sugar Shack",
        "Sugar Shack",
        "Sugar Shack",
        "Secret Factory",
        "The Other Factory",
        "Secret Factory",
        "Secret Factory",
        "The Other Factory"
    ]
})

st.subheader("Product–Factory Correlation")

st.dataframe(
    product_factory,
    use_container_width=True
)

# =========================================================
# 12. SUMMARY & RECOMMENDATIONS
# =========================================================

st.header("💡 12. Summary & Recommendations")

highest_profit_product = product.loc[
    product["Gross Profit"].idxmax(),
    "Product Name"
]

highest_margin_product = product.loc[
    product["Gross Margin (%)"].idxmax(),
    "Product Name"
]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Most Profitable Division",
        most_profitable_division
    )

with col2:
    st.metric(
        "Highest Profit Product",
        highest_profit_product
    )

with col3:
    st.metric(
        "Highest Margin Product",
        highest_margin_product
    )

with col4:
    st.metric(
        "Margin Risk Products",
        len(risk_products)
    )

st.subheader("Key Recommendations")

recommendations = [
    "Prioritize high-profit and high-margin products by focusing resources on products that provide strong profitability.",
    "Review high-sales / low-margin products because high revenue does not necessarily mean high profitability.",
    "Control product costs through supplier negotiation, sourcing improvements, or pricing adjustments.",
    "Monitor profit concentration because heavy dependence on a small number of products can create business risk.",
    "Monitor margin volatility and investigate significant monthly margin changes.",
    "Review low-sales and low-profit products for possible rationalization or discontinuation."
]

for i, recommendation in enumerate(
    recommendations,
    start=1
):
    st.markdown(
        f"**{i}. {recommendation}**"
    )

# =========================================================
# 13. METHODOLOGY
# =========================================================

st.header("📐 13. Methodology")

st.subheader("Data Cleaning & Validation")

st.markdown(
    """
    • Validate sales and cost values  
    • Remove zero-sales records  
    • Remove invalid records  
    • Handle missing unit values  
    • Standardize product labels  
    • Standardize division labels  
    • Convert order dates to the correct date format
    """
)

st.subheader("Key Formulas")

st.markdown(
    """
    **Gross Margin (%)**

    Gross Profit ÷ Sales × 100

    **Profit per Unit**

    Gross Profit ÷ Units

    **Revenue Contribution (%)**

    Product Sales ÷ Total Sales × 100

    **Profit Contribution (%)**

    Product Gross Profit ÷ Total Gross Profit × 100

    **Margin Volatility**

    Standard deviation of monthly gross margin
    """
)

st.subheader("Analysis Covered")

st.markdown(
    """
    ✔ Data Cleaning & Validation  
    ✔ Product Profitability  
    ✔ Gross Margin Analysis  
    ✔ Profit per Unit  
    ✔ Revenue Contribution  
    ✔ Profit Contribution  
    ✔ Product Classification  
    ✔ Division Performance  
    ✔ Margin Distribution by Division  
    ✔ Cost vs Sales Diagnostics  
    ✔ Margin Risk Identification  
    ✔ High-Sales / Low-Margin Analysis  
    ✔ Revenue Pareto Analysis  
    ✔ Profit Pareto Analysis  
    ✔ Regional & State Concentration  
    ✔ Margin Volatility  
    ✔ Factory & Product Relationship  
    ✔ Insights & Recommendations
    """
)

# =========================================================
# FINAL MESSAGE
# =========================================================

st.markdown("---")

st.success(
    "Nassau Candy Distributor Data Science Analysis Completed Successfully."
)
