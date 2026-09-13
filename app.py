import streamlit as st
import pandas as pd

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Nassau Candy Profitability Analysis",
    page_icon="🍬",
    layout="wide"
)

# =========================================================
# LOAD DATASET
# =========================================================

df = pd.read_csv("Nassau_Candy_Cleaned.csv")

df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    errors="coerce"
)

# =========================================================
# PROJECT TITLE
# =========================================================

st.title("🍬 Nassau Candy Distributor")

st.header(
    "Product Line Profitability & Margin Performance Analysis"
)

st.write(
    "An interactive data analytics dashboard for analyzing "
    "product profitability, sales performance, cost structure, "
    "gross margins, division performance and profit concentration."
)

st.divider()

# =========================================================
# PROJECT OVERVIEW
# =========================================================

st.header("📌 1. Analysis Overview")

st.write("""
### Project Objective

The objective of this project is to analyze the profitability 
and margin performance of Nassau Candy Distributor using 
transaction-level sales data.

The analysis focuses on:

- Product-level profitability
- Gross profit and gross margin
- Sales and cost performance
- Division-wise performance
- High-sales and low-margin products
- Margin risk products
- Profit concentration
- Monthly margin trends
- Business recommendations

### Business Questions

**1. Which products generate the highest profit?**

**2. Which products have the highest gross margins?**

**3. Which divisions perform best?**

**4. Which products have high sales but low margins?**

**5. How concentrated is the company's profit?**

**6. How does profitability change over time?**
""")

st.divider()

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Dashboard Filters")

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Order Date Range",
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
    min_value=0,
    max_value=100,
    value=20
)

product_search = st.sidebar.text_input(
    "🔍 Search Product"
)

# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df.copy()

if len(date_range) == 2:

    filtered_df = filtered_df[
        (filtered_df["Order Date"].dt.date >= date_range[0])
        &
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

# =========================================================
# DATASET OVERVIEW
# =========================================================

st.header("📁 2. Dataset Overview")

dataset_records = len(filtered_df)

dataset_columns = len(filtered_df.columns)

unique_products = filtered_df["Product Name"].nunique()

unique_divisions = filtered_df["Division"].nunique()

dataset_units = filtered_df["Units"].sum()

if not filtered_df.empty:

    dataset_start = filtered_df["Order Date"].min().strftime(
        "%d %b %Y"
    )

    dataset_end = filtered_df["Order Date"].max().strftime(
        "%d %b %Y"
    )

    dataset_period = f"{dataset_start} → {dataset_end}"

else:

    dataset_period = "No Data"

# Dataset KPI cards

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "Total Records",
    f"{dataset_records:,}"
)

col2.metric(
    "Columns",
    f"{dataset_columns}"
)

col3.metric(
    "Unique Products",
    f"{unique_products:,}"
)

col4.metric(
    "Divisions",
    f"{unique_divisions:,}"
)

col5.metric(
    "Total Units",
    f"{dataset_units:,.0f}"
)

col6.metric(
    "Data Period",
    dataset_period
)

st.write(
    "### Dataset Description"
)

st.write("""
The dataset contains transaction-level information related to
Nassau Candy Distributor. It includes sales, cost, units,
product, division and order-date information used to evaluate
product profitability and business performance.
""")

# =========================================================
# DATASET PREVIEW
# =========================================================

st.subheader("📋 Dataset Preview")

st.dataframe(
    filtered_df.head(20),
    use_container_width=True
)

# Download button

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Dataset",
    data=csv_data,
    file_name="Nassau_Candy_Filtered.csv",
    mime="text/csv"
)

st.divider()

# =========================================================
# BUSINESS KPIs
# =========================================================

st.header("💰 3. Key Performance Indicators")

total_sales = filtered_df["Sales"].sum()

total_cost = filtered_df["Cost"].sum()

total_profit = filtered_df["Gross Profit"].sum()

total_units = filtered_df["Units"].sum()

profit_margin = (
    total_profit / total_sales * 100
    if total_sales != 0
    else 0
)

average_order_value = (
    total_sales / dataset_records
    if dataset_records > 0
    else 0
)

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "Total Sales",
    f"${total_sales:,.2f}"
)

col2.metric(
    "Total Cost",
    f"${total_cost:,.2f}"
)

col3.metric(
    "Gross Profit",
    f"${total_profit:,.2f}"
)

col4.metric(
    "Gross Margin",
    f"{profit_margin:.2f}%"
)

col5.metric(
    "Total Units",
    f"{total_units:,.0f}"
)

col6.metric(
    "Average Order Value",
    f"${average_order_value:,.2f}"
)

st.divider()

# =========================================================
# PRODUCT PROFITABILITY
# =========================================================

st.header("🍫 4. Product Profitability Analysis")

product_analysis = filtered_df.groupby(
    "Product Name"
).agg(
    Sales=("Sales", "sum"),
    Units=("Units", "sum"),
    Gross_Profit=("Gross Profit", "sum")
)

product_analysis["Gross Margin (%)"] = (
    product_analysis["Gross_Profit"]
    / product_analysis["Sales"]
    * 100
)

product_analysis["Profit per Unit"] = (
    product_analysis["Gross_Profit"]
    / product_analysis["Units"]
)

product_analysis = product_analysis.replace(
    [float("inf"), -float("inf")],
    0
).fillna(0)

# ---------------------------------------------------------
# TOP PROFIT PRODUCTS
# ---------------------------------------------------------

st.subheader("🏆 Top 10 Products by Gross Profit")

top_profit = (
    product_analysis
    .sort_values(
        "Gross_Profit",
        ascending=False
    )
    .head(10)
)

st.bar_chart(
    top_profit["Gross_Profit"]
)

st.dataframe(
    top_profit.style.format({
        "Sales": "${:,.2f}",
        "Gross_Profit": "${:,.2f}",
        "Gross Margin (%)": "{:.2f}%",
        "Profit per Unit": "${:,.2f}"
    }),
    use_container_width=True
)

# ---------------------------------------------------------
# HIGHEST MARGIN PRODUCTS
# ---------------------------------------------------------

st.subheader("📈 Highest Margin Products")

highest_margin = (
    product_analysis[
        product_analysis["Gross Margin (%)"]
        >= margin_threshold
    ]
    .sort_values(
        "Gross Margin (%)",
        ascending=False
    )
    .head(10)
)

st.dataframe(
    highest_margin.style.format({
        "Sales": "${:,.2f}",
        "Gross_Profit": "${:,.2f}",
        "Gross Margin (%)": "{:.2f}%",
        "Profit per Unit": "${:,.2f}"
    }),
    use_container_width=True
)

st.divider()

# =========================================================
# DIVISION PERFORMANCE
# =========================================================

st.header("🏭 5. Division Performance Analysis")

division_analysis = filtered_df.groupby(
    "Division"
).agg(
    Sales=("Sales", "sum"),
    Cost=("Cost", "sum"),
    Gross_Profit=("Gross Profit", "sum"),
    Units=("Units", "sum")
)

division_analysis["Gross Margin (%)"] = (
    division_analysis["Gross_Profit"]
    / division_analysis["Sales"]
    * 100
)

division_analysis = division_analysis.replace(
    [float("inf"), -float("inf")],
    0
).fillna(0)

col1, col2 = st.columns(2)

with col1:

    st.subheader("Sales vs Gross Profit")

    st.bar_chart(
        division_analysis[
            ["Sales", "Gross_Profit"]
        ]
    )

with col2:

    st.subheader("Gross Margin by Division")

    st.bar_chart(
        division_analysis[
            "Gross Margin (%)"
        ]
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

st.divider()

# =========================================================
# COST AND MARGIN ANALYSIS
# =========================================================

st.header("💸 6. Cost vs Margin Diagnostics")

cost_margin = filtered_df.groupby(
    "Product Name"
).agg(
    Sales=("Sales", "sum"),
    Cost=("Cost", "sum"),
    Gross_Profit=("Gross Profit", "sum")
)

cost_margin["Margin (%)"] = (
    cost_margin["Gross_Profit"]
    / cost_margin["Sales"]
    * 100
)

cost_margin = cost_margin.replace(
    [float("inf"), -float("inf")],
    0
).fillna(0)

st.subheader("Cost vs Sales")

if not cost_margin.empty:

    st.scatter_chart(
        cost_margin,
        x="Sales",
        y="Cost"
    )

st.write(
    "This visualization helps identify products with "
    "high sales and high cost structures."
)

# =========================================================
# MARGIN RISK
# =========================================================

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

st.divider()

# =========================================================
# HIGH SALES LOW MARGIN
# =========================================================

st.header("🎯 7. High-Sales / Low-Margin Analysis")

if not cost_margin.empty:

    sales_median = cost_margin["Sales"].median()

    margin_median = cost_margin["Margin (%)"].median()

    high_sales_low_margin = cost_margin[
        (cost_margin["Sales"] >= sales_median)
        &
        (cost_margin["Margin (%)"] < margin_median)
    ].sort_values(
        "Sales",
        ascending=False
    )

    st.write("""
    These products generate relatively high sales but have
    below-median margins. They may require cost reduction,
    pricing optimization or supplier negotiation.
    """)

    st.dataframe(
        high_sales_low_margin.head(10).style.format({
            "Sales": "${:,.2f}",
            "Cost": "${:,.2f}",
            "Gross_Profit": "${:,.2f}",
            "Margin (%)": "{:.2f}%"
        }),
        use_container_width=True
    )

st.divider()

# =========================================================
# PROFIT CONCENTRATION
# =========================================================

st.header("📊 8. Profit Concentration Analysis")

pareto = (
    filtered_df
    .groupby("Product Name")["Gross Profit"]
    .sum()
    .sort_values(
        ascending=False
    )
)

if not pareto.empty and pareto.sum() != 0:

    cumulative_profit = (
        pareto.cumsum()
        / pareto.sum()
        * 100
    )

    st.subheader(
        "Pareto Analysis — Cumulative Profit"
    )

    st.line_chart(
        cumulative_profit
    )

    products_80 = (
        cumulative_profit <= 80
    ).sum()

    total_products = len(pareto)

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Products contributing up to 80% of profit",
            products_80
        )

    with col2:

        st.metric(
            "Total Products",
            total_products
        )

st.divider()

# =========================================================
# MONTHLY PERFORMANCE
# =========================================================

st.header("📅 9. Monthly Margin Performance")

monthly = filtered_df.groupby(
    filtered_df["Order Date"].dt.to_period("M")
).agg(
    Sales=("Sales", "sum"),
    Gross_Profit=("Gross Profit", "sum")
)

monthly["Profit Margin (%)"] = (
    monthly["Gross_Profit"]
    / monthly["Sales"]
    * 100
)

monthly = monthly.replace(
    [float("inf"), -float("inf")],
    0
).fillna(0)

if not monthly.empty:

    st.subheader(
        "Monthly Profit Margin Trend"
    )

    st.line_chart(
        monthly["Profit Margin (%)"]
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Highest Monthly Margin",
            f"{monthly['Profit Margin (%)'].max():.2f}%"
        )

    with col2:

        st.metric(
            "Lowest Monthly Margin",
            f"{monthly['Profit Margin (%)'].min():.2f}%"
        )

    with col3:

        st.metric(
            "Average Monthly Margin",
            f"{monthly['Profit Margin (%)'].mean():.2f}%"
        )

st.divider()

# =========================================================
# KEY PROJECT INSIGHTS
# =========================================================

st.header("💡 10. Key Project Insights")

if not division_analysis.empty:

    most_profitable_division = (
        division_analysis["Gross_Profit"]
        .idxmax()
    )

    best_division_profit = (
        division_analysis["Gross_Profit"]
        .max()
    )

    st.success(
        f"🏭 **Most Profitable Division:** "
        f"{most_profitable_division} "
        f"with gross profit of "
        f"${best_division_profit:,.2f}"
    )

if not top_profit.empty:

    best_product = top_profit.index[0]

    best_product_profit = top_profit.iloc[0]["Gross_Profit"]

    st.info(
        f"🍫 **Most Profitable Product:** "
        f"{best_product} "
        f"with gross profit of "
        f"${best_product_profit:,.2f}"
    )

if not product_analysis.empty:

    highest_margin_product = (
        product_analysis[
            "Gross Margin (%)"
        ].idxmax()
    )

    highest_margin_value = (
        product_analysis[
            "Gross Margin (%)"
        ].max()
    )

    st.success(
        f"📈 **Highest Margin Product:** "
        f"{highest_margin_product} "
        f"with a gross margin of "
        f"{highest_margin_value:.2f}%"
    )

st.warning(
    f"⚠️ **Margin Risk Products:** "
    f"{len(risk_products)} products are below "
    f"the selected {margin_threshold}% margin threshold."
)

# =========================================================
# RECOMMENDATIONS
# =========================================================

st.header("🎯 11. Business Recommendations")

st.write("""
### Recommended Actions

**1. Focus on high-profit products**

Increase inventory availability and marketing support
for products that consistently generate high gross profit.

**2. Improve low-margin products**

Review pricing, supplier costs and operating expenses
for products with weak margins.

**3. Monitor high-sales / low-margin products**

These products generate revenue but may not contribute
sufficiently to profitability.

**4. Optimize division performance**

Identify the strongest divisions and study their
successful product and pricing strategies.

**5. Monitor profit concentration**

Products responsible for a large share of profit should
receive appropriate inventory and business attention.

**6. Track monthly trends**

Regular monitoring of monthly margins can help identify
declining profitability early.
""")

st.divider()

# =========================================================
# METHODOLOGY
# =========================================================

st.header("📐 12. Methodology")

st.write("""
### Data Processing

1. Loaded the Nassau Candy transactional dataset.
2. Converted the Order Date column into date format.
3. Applied date, division and product filters.
4. Aggregated sales, cost, units and gross profit.
5. Calculated profitability and margin metrics.
6. Performed product and division-level analysis.
7. Identified margin-risk products.
8. Analyzed profit concentration.
9. Evaluated monthly profitability trends.
10. Generated business insights and recommendations.

### Key Formulas

**Gross Profit = Sales − Cost**

**Gross Margin (%) = Gross Profit ÷ Sales × 100**

**Profit per Unit = Gross Profit ÷ Units**

**Average Order Value = Total Sales ÷ Number of Records**

**Profit Contribution (%) = Product Gross Profit ÷ Total Gross Profit × 100**
""")

st.divider()

# =========================================================
# FOOTER
# =========================================================

st.caption(
    "Nassau Candy Distributor | "
    "Product Line Profitability & Margin Performance Analysis"
)

st.caption(
    "Developed using Python, Pandas and Streamlit"
)
