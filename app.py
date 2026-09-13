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
    "This dashboard analyzes product profitability, gross margin, "
    "division performance, cost structure, profit concentration, "
    "and margin volatility."
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

    # Basic cleaning
    df = df[df["Sales"] > 0]
    df = df[df["Gross Profit"].notna()]

    # Handle missing Units
    df["Units"] = df["Units"].fillna(0)

    # Standardize text columns
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

st.sidebar.header("🔎 Filters")

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
divisions = sorted(df["Division"].dropna().unique())

selected_divisions = st.sidebar.multiselect(
    "Division",
    divisions,
    default=divisions
)

# Margin threshold
margin_threshold = st.sidebar.slider(
    "Margin Risk Threshold (%)",
    min_value=0,
    max_value=100,
    value=20,
    step=1
)

# Product search
product_search = st.sidebar.text_input(
    "Search Product"
)

# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()

# Date filtering
if len(date_range) == 2:

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    filtered_df = filtered_df[
        (filtered_df["Order Date"] >= start_date)
        &
        (filtered_df["Order Date"] <= end_date)
    ]

# Division filtering
if selected_divisions:
    filtered_df = filtered_df[
        filtered_df["Division"].isin(selected_divisions)
    ]

# Product search
if product_search:
    filtered_df = filtered_df[
        filtered_df["Product Name"]
        .str.contains(
            product_search,
            case=False,
            na=False
        )
    ]

# =========================================================
# PROJECT OVERVIEW
# =========================================================

st.header("📌 1. Project Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Records",
        f"{len(filtered_df):,}"
    )

with col2:
    st.metric(
        "Unique Products",
        f"{filtered_df['Product Name'].nunique():,}"
    )

with col3:
    st.metric(
        "Divisions",
        f"{filtered_df['Division'].nunique():,}"
    )

st.write(
    """
    **Objective:** Identify which product lines generate strong profit
    and margins, detect low-margin products, compare division performance,
    analyze cost structure, and identify profit concentration risks.
    """
)

# =========================================================
# DATASET OVERVIEW
# =========================================================

st.header("📁 2. Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Sales",
        f"${filtered_df['Sales'].sum():,.2f}"
    )

with col2:
    st.metric(
        "Cost",
        f"${filtered_df['Cost'].sum():,.2f}"
    )

with col3:
    st.metric(
        "Gross Profit",
        f"${filtered_df['Gross Profit'].sum():,.2f}"
    )

with col4:
    st.metric(
        "Units",
        f"{filtered_df['Units'].sum():,.0f}"
    )

st.write("### Dataset Preview")

st.dataframe(
    filtered_df.head(20),
    use_container_width=True
)

# =========================================================
# KPI CALCULATIONS
# =========================================================

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_units = filtered_df["Units"].sum()

if total_sales != 0:
    overall_margin = (
        total_profit / total_sales
    ) * 100
else:
    overall_margin = 0

if total_units != 0:
    overall_profit_per_unit = (
        total_profit / total_units
    )
else:
    overall_profit_per_unit = 0

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

product_df["Gross Margin (%)"] = (
    product_df["Gross Profit"]
    / product_df["Sales"]
    * 100
)

product_df["Profit per Unit"] = (
    product_df["Gross Profit"]
    / product_df["Units"].replace(0, pd.NA)
)

product_df["Revenue Contribution (%)"] = (
    product_df["Sales"]
    / product_df["Sales"].sum()
    * 100
)

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
# KPI DASHBOARD
# =========================================================

st.header("📊 3. KPI Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Gross Margin",
        f"{overall_margin:.2f}%"
    )

with col2:
    st.metric(
        "Profit per Unit",
        f"${overall_profit_per_unit:,.2f}"
    )

with col3:

    if len(product_df) > 0:

        top_revenue_product = product_df.loc[
            product_df["Revenue Contribution (%)"].idxmax()
        ]

        st.metric(
            "Top Revenue Contribution",
            f"{top_revenue_product['Revenue Contribution (%)']:.2f}%"
        )

    else:
        st.metric(
            "Top Revenue Contribution",
            "0%"
        )

with col4:

    if len(product_df) > 0:

        top_profit_product = product_df.loc[
            product_df["Profit Contribution (%)"].idxmax()
        ]

        st.metric(
            "Top Profit Contribution",
            f"{top_profit_product['Profit Contribution (%)']:.2f}%"
        )

    else:
        st.metric(
            "Top Profit Contribution",
            "0%"
        )

# =========================================================
# PRODUCT PROFITABILITY OVERVIEW
# =========================================================

st.header("🍫 4. Product Profitability Overview")

st.subheader("Product Margin Leaderboard")

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
    ].head(20),
    use_container_width=True
)

# ---------------------------------------------------------
# Top Profit Products
# ---------------------------------------------------------

st.subheader("Top Products by Gross Profit")

top_profit = (
    product_df
    .sort_values(
        "Gross Profit",
        ascending=False
    )
    .head(10)
    .set_index("Product Name")
)

st.bar_chart(
    top_profit["Gross Profit"]
)

# ---------------------------------------------------------
# Top Margin Products
# ---------------------------------------------------------

st.subheader("Top Products by Gross Margin")

top_margin = (
    product_df
    .sort_values(
        "Gross Margin (%)",
        ascending=False
    )
    .head(10)
    .set_index("Product Name")
)

st.bar_chart(
    top_margin["Gross Margin (%)"]
)

# =========================================================
# PRODUCT CLASSIFICATION
# =========================================================

st.subheader("Product Profitability Classification")

if len(product_df) > 0:

    sales_median = product_df["Sales"].median()
    margin_median = product_df["Gross Margin (%)"].median()

    def classify_product(row):

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
            classify_product,
            axis=1
        )
    )

    classification_counts = (
        product_df["Classification"]
        .value_counts()
    )

    st.bar_chart(
        classification_counts
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
# DIVISION PERFORMANCE
# =========================================================

st.header("🏢 5. Division Performance Dashboard")

division_df = (
    filtered_df
    .groupby("Division", as_index=False)
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

# ---------------------------------------------------------
# Revenue vs Profit
# ---------------------------------------------------------

st.subheader("Revenue vs Profit by Division")

division_chart = (
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
    division_chart
)

# ---------------------------------------------------------
# Margin by Division
# ---------------------------------------------------------

st.subheader("Average Gross Margin by Division")

margin_chart = (
    division_df
    .set_index("Division")
    ["Gross Margin (%)"]
)

st.bar_chart(
    margin_chart
)

# ---------------------------------------------------------
# Division Table
# ---------------------------------------------------------

st.subheader("Division Performance Table")

st.dataframe(
    division_df,
    use_container_width=True
)

# =========================================================
# COST VS MARGIN DIAGNOSTICS
# =========================================================

st.header("💸 6. Cost vs Margin Diagnostics")

st.subheader("Cost vs Sales")

scatter_data = filtered_df[
    [
        "Sales",
        "Cost"
    ]
].copy()

st.scatter_chart(
    scatter_data,
    x="Sales",
    y="Cost"
)

st.write(
    "Products where cost is high compared with sales may indicate "
    "cost-heavy or margin-poor product lines."
)

# ---------------------------------------------------------
# Margin Risk Products
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
    f"Number of products below the selected margin threshold: "
    f"**{len(risk_products)}**"
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
# High Sales / Low Margin
# ---------------------------------------------------------

st.subheader("High-Sales / Low-Margin Products")

if len(product_df) > 0:

    sales_median = product_df["Sales"].median()

    high_sales_low_margin = product_df[
        (product_df["Sales"] >= sales_median)
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
# PROFIT CONCENTRATION / PARETO
# =========================================================

st.header("📈 7. Profit Concentration Analysis")

# ---------------------------------------------------------
# Revenue Pareto
# ---------------------------------------------------------

st.subheader("Revenue Pareto Analysis")

revenue_pareto = (
    product_df
    .sort_values(
        "Sales",
        ascending=False
    )
    .copy()
)

revenue_pareto["Cumulative Revenue (%)"] = (
    revenue_pareto["Sales"].cumsum()
    / revenue_pareto["Sales"].sum()
    * 100
)

revenue_chart = (
    revenue_pareto[
        [
            "Product Name",
            "Cumulative Revenue (%)"
        ]
    ]
    .set_index("Product Name")
)

st.line_chart(
    revenue_chart
)

# Correctly identify products needed to reach 80%
if len(revenue_pareto) > 0:

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
    "Products contributing to 80% of Revenue",
    f"{revenue_80_products} "
    f"({revenue_80_percentage:.2f}% of products)"
)

# ---------------------------------------------------------
# Profit Pareto
# ---------------------------------------------------------

st.subheader("Profit Pareto Analysis")

profit_pareto = (
    product_df
    .sort_values(
        "Gross Profit",
        ascending=False
    )
    .copy()
)

if profit_pareto["Gross Profit"].sum() != 0:

    profit_pareto["Cumulative Profit (%)"] = (
        profit_pareto["Gross Profit"].cumsum()
        / profit_pareto["Gross Profit"].sum()
        * 100
    )

else:

    profit_pareto["Cumulative Profit (%)"] = 0

profit_chart = (
    profit_pareto[
        [
            "Product Name",
            "Cumulative Profit (%)"
        ]
    ]
    .set_index("Product Name")
)

st.line_chart(
    profit_chart
)

if len(profit_pareto) > 0:

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
    "Products contributing to 80% of Profit",
    f"{profit_80_products} "
    f"({profit_80_percentage:.2f}% of products)"
)

# ---------------------------------------------------------
# Region Concentration
# ---------------------------------------------------------

st.subheader("Revenue & Profit Concentration by Region")

if "Region" in filtered_df.columns:

    region_df = (
        filtered_df
        .groupby("Region", as_index=False)
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

    region_df["Profit Contribution (%)"] = (
        region_df["Gross Profit"]
        / region_df["Gross Profit"].sum()
        * 100
    )

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
# MARGIN VOLATILITY
# =========================================================

st.header("📅 8. Margin Volatility Analysis")

monthly_df = filtered_df.copy()

monthly_df["Month"] = (
    monthly_df["Order Date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_summary = (
    monthly_df
    .groupby("Month", as_index=False)
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

# ---------------------------------------------------------
# Monthly Sales & Profit
# ---------------------------------------------------------

st.subheader("Monthly Sales and Gross Profit")

monthly_chart = (
    monthly_summary
    .set_index("Month")
    [
        [
            "Sales",
            "Gross Profit"
        ]
    ]
)

st.line_chart(
    monthly_chart
)

# ---------------------------------------------------------
# Monthly Margin
# ---------------------------------------------------------

st.subheader("Monthly Gross Margin")

monthly_margin_chart = (
    monthly_summary
    .set_index("Month")
    ["Margin (%)"]
)

st.line_chart(
    monthly_margin_chart
)

# ---------------------------------------------------------
# Margin Volatility
# ---------------------------------------------------------

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
# FACTORY & PRODUCT SUPPLY INFORMATION
# =========================================================

st.header("🏭 9. Factory & Product Supply Information")

st.write(
    "The following information shows the factory locations and "
    "the relationship between product lines and their associated factories."
)

# ---------------------------------------------------------
# Factory Coordinates
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
# Product Factory Correlation
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
# SUMMARY & SUGGESTIONS
# =========================================================

st.header("💡 10. Summary & Suggestions")

if len(product_df) > 0:

    # Most profitable division
    best_division = division_df.loc[
        division_df["Gross Profit"].idxmax(),
        "Division"
    ]

    # Highest profit product
    best_profit_product = product_df.loc[
        product_df["Gross Profit"].idxmax(),
        "Product Name"
    ]

    # Highest margin product
    best_margin_product = product_df.loc[
        product_df["Gross Margin (%)"].idxmax(),
        "Product Name"
    ]

    # Number of risk products
    risk_count = len(
        product_df[
            product_df["Gross Margin (%)"]
            < margin_threshold
        ]
    )

    # Summary metrics
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

    # -----------------------------------------------------
    # Recommendations
    # -----------------------------------------------------

    st.subheader("Key Recommendations")

    st.write(
        """
        **1. Prioritize high-profit and high-margin products**  
        Focus inventory, marketing and sales efforts on products
        that generate strong profitability.

        **2. Review high-sales / low-margin products**  
        High revenue does not always mean high profitability.
        These products should be reviewed for pricing and sourcing.

        **3. Control product costs**  
        Cost-heavy products should be evaluated for supplier
        negotiation, sourcing changes or repricing.

        **4. Monitor profit concentration**  
        If a small number of products contribute most of the profit,
        the business may have dependency risk.

        **5. Monitor margin volatility**  
        Large changes in monthly margin may indicate changes in
        pricing, product mix or costs.

        **6. Review weak product lines**  
        Low-sales and low-profit products can be considered for
        product rationalization or discontinuation review.
        """
    )

# =========================================================
# METHODOLOGY
# =========================================================

st.header("📐 11. Methodology")

st.subheader("Data Cleaning & Validation")

st.write(
    """
    • Validated sales and cost values  
    • Removed zero-sales records  
    • Removed records with missing gross profit  
    • Handled missing unit values  
    • Standardized product and division labels
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

st.subheader("Analysis Areas")

st.write(
    """
    • Product-level profitability  
    • Division-level performance  
    • Revenue vs profit comparison  
    • Cost vs sales diagnostics  
    • Margin risk identification  
    • Profit concentration / Pareto analysis  
    • Regional and state concentration  
    • Margin volatility  
    • Factory and product relationship analysis
    """
)

st.success(
    "Dashboard analysis completed successfully."
)
