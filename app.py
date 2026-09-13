import streamlit as st
import pandas as pd

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

st.write(
    """
    This Data Science project analyzes product profitability,
    gross margin, division performance, cost structure,
    profit concentration, and margin volatility.
    """
)

st.divider()

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    df = pd.read_csv("Nassau_Candy_Cleaned.csv")

    # Convert date
    df["Order Date"] = pd.to_datetime(
        df["Order Date"],
        errors="coerce"
    )

    # Basic validation
    df = df[df["Sales"] > 0]
    df = df[df["Gross Profit"].notna()]

    # Handle missing units
    df["Units"] = df["Units"].fillna(0)

    # Standardize text
    df["Product Name"] = (
        df["Product Name"]
        .astype(str)
        .str.strip()
    )

    df["Division"] = (
        df["Division"]
        .astype(str)
        .str.strip()
    )

    return df


df = load_data()

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Dashboard Filters")

# Date filter
min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Division filter
division_list = sorted(
    df["Division"].dropna().unique()
)

selected_divisions = st.sidebar.multiselect(
    "Division",
    division_list,
    default=division_list
)

# Margin threshold
margin_threshold = st.sidebar.slider(
    "Margin Risk Threshold (%)",
    0,
    100,
    20,
    1
)

# Product search
product_search = st.sidebar.text_input(
    "Search Product"
)

# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()

if len(date_range) == 2:

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    filtered_df = filtered_df[
        (filtered_df["Order Date"] >= start_date)
        &
        (filtered_df["Order Date"] <= end_date)
    ]

if selected_divisions:

    filtered_df = filtered_df[
        filtered_df["Division"].isin(
            selected_divisions
        )
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
# 1. PROJECT OVERVIEW
# =========================================================

st.header("📌 1. Project Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Records",
        f"{len(filtered_df):,}"
    )

with col2:
    st.metric(
        "Products",
        f"{filtered_df['Product Name'].nunique():,}"
    )

with col3:
    st.metric(
        "Divisions",
        f"{filtered_df['Division'].nunique():,}"
    )

st.write(
    """
    **Objective:** Analyze product-level and division-level
    profitability, identify margin risks, understand cost
    structure, measure profit concentration, and provide
    business recommendations.
    """
)

# =========================================================
# 2. DATASET OVERVIEW
# =========================================================

st.header("📁 2. Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Sales",
        f"${filtered_df['Sales'].sum():,.2f}"
    )

with col2:
    st.metric(
        "Total Cost",
        f"${filtered_df['Cost'].sum():,.2f}"
    )

with col3:
    st.metric(
        "Gross Profit",
        f"${filtered_df['Gross Profit'].sum():,.2f}"
    )

with col4:
    st.metric(
        "Total Units",
        f"{filtered_df['Units'].sum():,.0f}"
    )

st.subheader("Dataset Preview")

st.dataframe(
    filtered_df.head(20),
    use_container_width=True
)

# =========================================================
# PRODUCT LEVEL METRICS
# =========================================================

product_df = (
    filtered_df
    .groupby(
        ["Product Name", "Division"],
        as_index=False
    )
    .agg({
        "Sales": "sum",
        "Cost": "sum",
        "Gross Profit": "sum",
        "Units": "sum"
    })
)

# Gross Margin
product_df["Gross Margin (%)"] = (
    product_df["Gross Profit"]
    / product_df["Sales"]
    * 100
)

# Profit per Unit
product_df["Profit per Unit"] = (
    product_df["Gross Profit"]
    / product_df["Units"].replace(0, pd.NA)
)

# Revenue Contribution
product_df["Revenue Contribution (%)"] = (
    product_df["Sales"]
    / product_df["Sales"].sum()
    * 100
)

# Profit Contribution
if product_df["Gross Profit"].sum() != 0:

    product_df["Profit Contribution (%)"] = (
        product_df["Gross Profit"]
        / product_df["Gross Profit"].sum()
        * 100
    )

else:

    product_df["Profit Contribution (%)"] = 0

product_df = product_df.fillna(0)

# =========================================================
# 3. KPI DASHBOARD
# =========================================================

st.header("📊 3. KPI Dashboard")

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_units = filtered_df["Units"].sum()

if total_sales > 0:
    gross_margin = (
        total_profit / total_sales
    ) * 100
else:
    gross_margin = 0

if total_units > 0:
    profit_per_unit = (
        total_profit / total_units
    )
else:
    profit_per_unit = 0

if len(product_df) > 0:

    top_revenue = product_df.loc[
        product_df["Revenue Contribution (%)"].idxmax()
    ]

    top_profit = product_df.loc[
        product_df["Profit Contribution (%)"].idxmax()
    ]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Gross Margin",
        f"{gross_margin:.2f}%"
    )

with col2:
    st.metric(
        "Profit per Unit",
        f"${profit_per_unit:,.2f}"
    )

with col3:

    if len(product_df) > 0:
        st.metric(
            "Top Revenue Contribution",
            f"{top_revenue['Revenue Contribution (%)']:.2f}%"
        )
    else:
        st.metric(
            "Top Revenue Contribution",
            "0%"
        )

with col4:

    if len(product_df) > 0:
        st.metric(
            "Top Profit Contribution",
            f"{top_profit['Profit Contribution (%)']:.2f}%"
        )
    else:
        st.metric(
            "Top Profit Contribution",
            "0%"
        )

# =========================================================
# 4. PRODUCT PROFITABILITY OVERVIEW
# =========================================================

st.header("🍫 4. Product Profitability Overview")

st.subheader("Product-Level Margin Leaderboard")

leaderboard = product_df.sort_values(
    "Gross Margin (%)",
    ascending=False
)

st.dataframe(
    leaderboard[
        [
            "Product Name",
            "Division",
            "Sales",
            "Gross Profit",
            "Gross Margin (%)",
            "Profit per Unit",
            "Revenue Contribution (%)",
            "Profit Contribution (%)"
        ]
    ],
    use_container_width=True
)

# ---------------------------------------------------------
# Profit Contribution
# ---------------------------------------------------------

st.subheader("Top Products by Gross Profit")

top_profit_products = (
    product_df
    .sort_values(
        "Gross Profit",
        ascending=False
    )
    .head(10)
    .set_index("Product Name")
)

st.bar_chart(
    top_profit_products["Gross Profit"]
)

# ---------------------------------------------------------
# Margin Leaderboard
# ---------------------------------------------------------

st.subheader("Top Products by Gross Margin")

top_margin_products = (
    product_df
    .sort_values(
        "Gross Margin (%)",
        ascending=False
    )
    .head(10)
    .set_index("Product Name")
)

st.bar_chart(
    top_margin_products["Gross Margin (%)"]
)

# =========================================================
# 5. PRODUCT CLASSIFICATION
# =========================================================

st.header("📦 5. Product Profitability Classification")

if len(product_df) > 0:

    sales_median = product_df["Sales"].median()
    margin_median = product_df["Gross Margin (%)"].median()

    def classify(row):

        high_sales = row["Sales"] >= sales_median
        high_margin = row["Gross Margin (%)"] >= margin_median

        if high_sales and high_margin:
            return "High Sales / High Margin"

        elif high_sales and not high_margin:
            return "High Sales / Low Margin"

        elif not high_sales and high_margin:
            return "Low Sales / High Margin"

        else:
            return "Low Sales / Low Margin"

    product_df["Classification"] = (
        product_df.apply(
            classify,
            axis=1
        )
    )

    classification_count = (
        product_df["Classification"]
        .value_counts()
    )

    st.bar_chart(
        classification_count
    )

    st.dataframe(
        product_df[
            [
                "Product Name",
                "Division",
                "Sales",
                "Gross Profit",
                "Gross Margin (%)",
                "Classification"
            ]
        ],
        use_container_width=True
    )

# =========================================================
# 6. DIVISION PERFORMANCE
# =========================================================

st.header("🏢 6. Division Performance Dashboard")

division_df = (
    filtered_df
    .groupby(
        "Division",
        as_index=False
    )
    .agg({
        "Sales": "sum",
        "Cost": "sum",
        "Gross Profit": "sum",
        "Units": "sum"
    })
)

division_df["Gross Margin (%)"] = (
    division_df["Gross Profit"]
    / division_df["Sales"]
    * 100
)

# Revenue vs Profit
st.subheader("Revenue vs Profit by Division")

division_revenue_profit = (
    division_df
    .set_index("Division")
    [
        [
            "Sales",
            "Gross Profit"
        ]
    ]
)

st.bar_chart(
    division_revenue_profit
)

# Average margin
st.subheader("Gross Margin by Division")

division_margin = (
    division_df
    .set_index("Division")
    ["Gross Margin (%)"]
)

st.bar_chart(
    division_margin
)

# ---------------------------------------------------------
# Margin Distribution by Division
# ---------------------------------------------------------

st.subheader("Margin Distribution by Division")

margin_distribution = (
    filtered_df
    .merge(
        product_df[
            [
                "Product Name",
                "Division",
                "Gross Margin (%)"
            ]
        ],
        on=["Product Name", "Division"],
        how="left"
    )
)

distribution_table = (
    margin_distribution
    .groupby("Division")["Gross Margin (%)"]
    .agg(
        Minimum="min",
        Q1=lambda x: x.quantile(0.25),
        Median="median",
        Q3=lambda x: x.quantile(0.75),
        Maximum="max",
        Average="mean"
    )
    .reset_index()
)

st.dataframe(
    distribution_table,
    use_container_width=True
)

st.write(
    "The table shows the minimum, first quartile, median, "
    "third quartile, maximum and average margin for each division."
)

st.subheader("Division Performance Table")

st.dataframe(
    division_df,
    use_container_width=True
)

# =========================================================
# 7. COST STRUCTURE DIAGNOSTICS
# =========================================================

st.header("💸 7. Cost Structure Diagnostics")

st.subheader("Cost vs Sales")

cost_sales_data = filtered_df[
    [
        "Sales",
        "Cost"
    ]
].copy()

st.scatter_chart(
    cost_sales_data,
    x="Sales",
    y="Cost"
)

st.write(
    """
    Products with relatively high costs compared with their sales
    may require pricing, sourcing or cost-control review.
    """
)

# ---------------------------------------------------------
# Margin Risk
# ---------------------------------------------------------

st.subheader(
    f"Margin Risk Products Below {margin_threshold}%"
)

risk_products = product_df[
    product_df["Gross Margin (%)"]
    < margin_threshold
].sort_values(
    "Gross Margin (%)"
)

st.write(
    f"**{len(risk_products)} products** are below the selected "
    f"margin threshold."
)

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

# ---------------------------------------------------------
# High Sales Low Margin
# ---------------------------------------------------------

st.subheader("High-Sales / Low-Margin Products")

if len(product_df) > 0:

    high_sales_low_margin = product_df[
        (
            product_df["Sales"]
            >= product_df["Sales"].median()
        )
        &
        (
            product_df["Gross Margin (%)"]
            < margin_threshold
        )
    ].sort_values(
        "Sales",
        ascending=False
    )

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
# 8. PROFIT CONCENTRATION / PARETO
# =========================================================

st.header("📈 8. Profit Concentration Analysis")

# ---------------------------------------------------------
# Revenue Pareto
# ---------------------------------------------------------

st.subheader("Revenue Pareto")

revenue_pareto = (
    product_df
    .sort_values(
        "Sales",
        ascending=False
    )
    .copy()
)

if len(revenue_pareto) > 0:

    revenue_pareto["Cumulative Revenue (%)"] = (
        revenue_pareto["Sales"].cumsum()
        / revenue_pareto["Sales"].sum()
        * 100
    )

    st.line_chart(
        revenue_pareto.set_index(
            "Product Name"
        )[
            "Cumulative Revenue (%)"
        ]
    )

    revenue_80_products = (
        revenue_pareto[
            "Cumulative Revenue (%)"
        ] < 80
    ).sum() + 1

    revenue_80_products = min(
        revenue_80_products,
        len(revenue_pareto)
    )

    revenue_80_percentage = (
        revenue_80_products
        / len(revenue_pareto)
        * 100
    )

else:

    revenue_80_products = 0
    revenue_80_percentage = 0

st.metric(
    "Products Needed for 80% Revenue",
    f"{revenue_80_products} "
    f"({revenue_80_percentage:.2f}%)"
)

# ---------------------------------------------------------
# Profit Pareto
# ---------------------------------------------------------

st.subheader("Profit Pareto")

profit_pareto = (
    product_df
    .sort_values(
        "Gross Profit",
        ascending=False
    )
    .copy()
)

if len(profit_pareto) > 0:

    total_pareto_profit = (
        profit_pareto["Gross Profit"].sum()
    )

    if total_pareto_profit != 0:

        profit_pareto["Cumulative Profit (%)"] = (
            profit_pareto["Gross Profit"].cumsum()
            / total_pareto_profit
            * 100
        )

    else:

        profit_pareto["Cumulative Profit (%)"] = 0

    st.line_chart(
        profit_pareto.set_index(
            "Product Name"
        )[
            "Cumulative Profit (%)"
        ]
    )

    profit_80_products = (
        profit_pareto[
            "Cumulative Profit (%)"
        ] < 80
    ).sum() + 1

    profit_80_products = min(
        profit_80_products,
        len(profit_pareto)
    )

    profit_80_percentage = (
        profit_80_products
        / len(profit_pareto)
        * 100
    )

else:

    profit_80_products = 0
    profit_80_percentage = 0

st.metric(
    "Products Needed for 80% Profit",
    f"{profit_80_products} "
    f"({profit_80_percentage:.2f}%)"
)

# ---------------------------------------------------------
# Regional Concentration
# ---------------------------------------------------------

st.subheader("Revenue & Profit by Region")

if "Region" in filtered_df.columns:

    region_df = (
        filtered_df
        .groupby(
            "Region",
            as_index=False
        )
        .agg({
            "Sales": "sum",
            "Gross Profit": "sum"
        })
    )

    region_df["Revenue Contribution (%)"] = (
        region_df["Sales"]
        / region_df["Sales"].sum()
        * 100
    )

    if region_df["Gross Profit"].sum() != 0:

        region_df["Profit Contribution (%)"] = (
            region_df["Gross Profit"]
            / region_df["Gross Profit"].sum()
            * 100
        )

    else:

        region_df["Profit Contribution (%)"] = 0

    st.dataframe(
        region_df.sort_values(
            "Sales",
            ascending=False
        ),
        use_container_width=True
    )

# ---------------------------------------------------------
# State Concentration
# ---------------------------------------------------------

st.subheader("Top States by Revenue")

if "State/Province" in filtered_df.columns:

    state_df = (
        filtered_df
        .groupby(
            "State/Province",
            as_index=False
        )
        .agg({
            "Sales": "sum",
            "Gross Profit": "sum"
        })
        .sort_values(
            "Sales",
            ascending=False
        )
        .head(10)
    )

    state_df["Revenue Contribution (%)"] = (
        state_df["Sales"]
        / filtered_df["Sales"].sum()
        * 100
    )

    st.dataframe(
        state_df,
        use_container_width=True
    )

# =========================================================
# 9. MARGIN VOLATILITY
# =========================================================

st.header("📅 9. Margin Volatility Analysis")

monthly_df = filtered_df.copy()

monthly_df["Month"] = (
    monthly_df["Order Date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_summary = (
    monthly_df
    .groupby(
        "Month",
        as_index=False
    )
    .agg({
        "Sales": "sum",
        "Gross Profit": "sum"
    })
)

monthly_summary["Margin (%)"] = (
    monthly_summary["Gross Profit"]
    / monthly_summary["Sales"]
    * 100
)

st.subheader("Monthly Sales & Gross Profit")

st.line_chart(
    monthly_summary.set_index("Month")[
        [
            "Sales",
            "Gross Profit"
        ]
    ]
)

st.subheader("Monthly Gross Margin")

st.line_chart(
    monthly_summary.set_index("Month")[
        "Margin (%)"
    ]
)

if len(monthly_summary) > 1:

    margin_volatility = (
        monthly_summary["Margin (%)"]
        .std()
    )

else:

    margin_volatility = 0

st.metric(
    "Margin Volatility",
    f"{margin_volatility:.2f}%"
)

st.write(
    "Margin volatility is measured using the standard deviation "
    "of monthly gross margin."
)

# =========================================================
# 10. FACTORY & PRODUCT SUPPLY INFORMATION
# =========================================================

st.header("🏭 10. Factory & Product Supply Information")

st.write(
    """
    The project brief provides factory coordinates and the
    relationship between product lines and their associated factories.
    """
)

# ---------------------------------------------------------
# Factory Data
# ---------------------------------------------------------

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
        48.119140,
        41.446333,
        35.117500
    ],

    "Longitude": [
        -111.768036,
        -81.088371,
        -96.181150,
        -90.565487,
        -89.971107
    ]
})

st.subheader("Factory Locations")

map_data = factory_data.rename(
    columns={
        "Latitude": "lat",
        "Longitude": "lon"
    }
)

st.map(map_data)

st.subheader("Factory Coordinates")

st.dataframe(
    factory_data,
    use_container_width=True
)

# ---------------------------------------------------------
# Product Factory Relationship
# ---------------------------------------------------------

st.subheader("Product–Factory Correlation")

product_factory = pd.DataFrame({

    "Division": [
        "Chocolate",
        "Chocolate",
        "Chocolate",
        "Chocolate",
        "Chocolate",
        "Sugar",
        "Sugar",
        "Sugar",
        "Sugar",
        "Other",
        "Sugar",
        "Sugar",
        "Other",
        "Other",
        "Other"
    ],

    "Product": [
        "Wonka Bar - Nutty Crunch Surprise",
        "Wonka Bar - Fudge Mallows",
        "Wonka Bar - Scrumdiddlyumptious",
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

st.dataframe(
    product_factory,
    use_container_width=True
)

# =========================================================
# 11. SUMMARY & RECOMMENDATIONS
# =========================================================

st.header("💡 11. Summary & Recommendations")

if len(product_df) > 0:

    best_division = division_df.loc[
        division_df["Gross Profit"].idxmax(),
        "Division"
    ]

    best_profit_product = product_df.loc[
        product_df["Gross Profit"].idxmax(),
        "Product Name"
    ]

    best_margin_product = product_df.loc[
        product_df["Gross Margin (%)"].idxmax(),
        "Product Name"
    ]

    risk_count = len(
        product_df[
            product_df["Gross Margin (%)"]
            < margin_threshold
        ]
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Most Profitable Division",
            best_division
        )

        st.metric(
            "Highest Profit Product",
            best_profit_product
        )

    with col2:

        st.metric(
            "Highest Margin Product",
            best_margin_product
        )

        st.metric(
            "Margin Risk Products",
            risk_count
        )

    st.subheader("Key Recommendations")

    st.write(
        """
        **1. Prioritize high-profit and high-margin products**  
        Focus resources on products that provide strong profitability.

        **2. Review high-sales / low-margin products**  
        High revenue does not necessarily mean high profitability.
        Pricing and sourcing should be reviewed.

        **3. Control product costs**  
        Cost-heavy products should be considered for supplier
        negotiation or repricing.

        **4. Monitor profit concentration**  
        Heavy dependence on a small number of products can create
        business risk.

        **5. Monitor margin volatility**  
        Significant monthly margin changes should be investigated.

        **6. Review weak products**  
        Low-sales and low-profit products may require rationalization
        or discontinuation review.
        """
    )

# =========================================================
# 12. METHODOLOGY
# =========================================================

st.header("📐 12. Methodology")

st.subheader("Data Cleaning & Validation")

st.write(
    """
    • Validate sales and cost values  
    • Remove zero-sales records  
    • Remove invalid profit records  
    • Handle missing unit values  
    • Standardize product labels  
    • Standardize division labels  
    • Convert order dates to the correct date format
    """
)

st.subheader("Key Formulas")

st.write(
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

st.write(
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

st.success(
    "Nassau Candy Distributor Data Science Analysis Completed Successfully."
)
