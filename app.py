import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================
# PAGE SETUP
# =========================
st.set_page_config(
    page_title="Nassau Candy Analysis",
    page_icon="🍫",
    layout="wide"
)

st.title("🍫 Nassau Candy Distributor")
st.subheader("Product Line Profitability & Margin Performance Analysis")

# =========================
# LOAD & CLEAN DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("Nassau_Candy_Cleaned.csv")

    for col in ["Order Date", "Ship Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["Sales", "Units", "Gross Profit", "Cost"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Sales", "Gross Profit", "Cost"])
    df = df[df["Sales"] > 0]
    df["Units"] = df["Units"].fillna(0)

    for col in ["Division", "Product Name", "State", "Region"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


df = load_data()

if df.empty:
    st.error("No valid data found.")
    st.stop()

# Calculated fields
df["Gross Margin (%)"] = np.where(
    df["Sales"] > 0,
    df["Gross Profit"] / df["Sales"] * 100,
    0
)

df["Profit per Unit"] = np.where(
    df["Units"] > 0,
    df["Gross Profit"] / df["Units"],
    0
)

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("🔎 Filters")

filtered = df.copy()

if "Order Date" in df.columns:
    min_date = df["Order Date"].min().date()
    max_date = df["Order Date"].max().date()

    dates = st.sidebar.date_input(
        "Order Date",
        (min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(dates, tuple) and len(dates) == 2:
        start = pd.Timestamp(dates[0])
        end = pd.Timestamp(dates[1]) + pd.Timedelta(days=1)

        filtered = filtered[
            (filtered["Order Date"] >= start) &
            (filtered["Order Date"] < end)
        ]

if "Division" in df.columns:
    divisions = sorted(df["Division"].dropna().unique())

    selected = st.sidebar.multiselect(
        "Division",
        divisions,
        default=divisions
    )

    filtered = filtered[
        filtered["Division"].isin(selected)
    ]

margin = st.sidebar.slider(
    "Minimum Margin (%)",
    0, 100, 0
)

filtered = filtered[
    filtered["Gross Margin (%)"] >= margin
]

if "Product Name" in df.columns:
    search = st.sidebar.text_input("Search Product")

    if search:
        filtered = filtered[
            filtered["Product Name"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# =========================
# KPI DASHBOARD
# =========================
st.header("📊 KPI Dashboard")

sales = filtered["Sales"].sum()
cost = filtered["Cost"].sum()
profit = filtered["Gross Profit"].sum()
units = filtered["Units"].sum()
margin_value = profit / sales * 100 if sales else 0

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Sales", f"${sales:,.0f}")
c2.metric("Total Cost", f"${cost:,.0f}")
c3.metric("Gross Profit", f"${profit:,.0f}")
c4.metric("Units Sold", f"{units:,.0f}")
c5.metric("Gross Margin", f"{margin_value:.2f}%")

# =========================
# PRODUCT ANALYSIS
# =========================
st.header("🍬 Product Profitability")

product = filtered.groupby(
    ["Product Name", "Division"],
    as_index=False
).agg({
    "Sales": "sum",
    "Units": "sum",
    "Gross Profit": "sum",
    "Cost": "sum"
})

product["Gross Margin (%)"] = (
    product["Gross Profit"] /
    product["Sales"] * 100
)

product["Profit per Unit"] = np.where(
    product["Units"] > 0,
    product["Gross Profit"] / product["Units"],
    0
)

product["Revenue Contribution (%)"] = (
    product["Sales"] / product["Sales"].sum() * 100
)

product["Profit Contribution (%)"] = (
    product["Gross Profit"] /
    product["Gross Profit"].sum() * 100
)

col1, col2 = st.columns(2)

with col1:
    top_sales = product.nlargest(10, "Sales")

    fig = px.bar(
        top_sales,
        x="Sales",
        y="Product Name",
        color="Division",
        orientation="h",
        title="Top Products by Sales"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    top_profit = product.nlargest(10, "Gross Profit")

    fig = px.bar(
        top_profit,
        x="Gross Profit",
        y="Product Name",
        color="Division",
        orientation="h",
        title="Top Products by Profit"
    )

    st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    product.sort_values(
        "Gross Profit",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)

# =========================
# PROFITABILITY CLASSIFICATION
# =========================
st.header("🎯 Profitability Classification")

median_sales = product["Sales"].median()
median_profit = product["Gross Profit"].median()

product["Classification"] = np.select(
    [
        (product["Sales"] >= median_sales) &
        (product["Gross Profit"] >= median_profit),

        (product["Sales"] >= median_sales) &
        (product["Gross Profit"] < median_profit),

        (product["Sales"] < median_sales) &
        (product["Gross Profit"] >= median_profit)
    ],
    [
        "High Sales / High Profit",
        "High Sales / Low Profit",
        "Low Sales / High Profit"
    ],
    default="Low Sales / Low Profit"
)

classification = (
    product["Classification"]
    .value_counts()
    .reset_index()
)

classification.columns = ["Classification", "Products"]

fig = px.bar(
    classification,
    x="Classification",
    y="Products",
    title="Product Profitability Categories"
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# DIVISION & COST ANALYSIS
# =========================
st.header("🏢 Division & Cost Analysis")

division = filtered.groupby(
    "Division",
    as_index=False
).agg({
    "Sales": "sum",
    "Cost": "sum",
    "Gross Profit": "sum",
    "Units": "sum"
})

division["Gross Margin (%)"] = (
    division["Gross Profit"] /
    division["Sales"] * 100
)

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        division,
        x="Division",
        y=["Sales", "Gross Profit"],
        barmode="group",
        title="Sales vs Profit by Division"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        division,
        x="Division",
        y="Cost",
        title="Cost by Division"
    )

    st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    division.sort_values(
        "Gross Profit",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)

# =========================
# PARETO ANALYSIS
# =========================
st.header("📈 Revenue & Profit Concentration")

pareto = product.sort_values(
    "Sales",
    ascending=False
).copy()

pareto["Cumulative Revenue (%)"] = (
    pareto["Sales"].cumsum() /
    pareto["Sales"].sum() * 100
)

fig = px.line(
    pareto,
    x="Product Name",
    y="Cumulative Revenue (%)",
    markers=True,
    title="Cumulative Revenue Contribution"
)

fig.add_hline(y=80, line_dash="dash")

st.plotly_chart(fig, use_container_width=True)

profit_pareto = product.sort_values(
    "Gross Profit",
    ascending=False
).copy()

profit_pareto["Cumulative Profit (%)"] = (
    profit_pareto["Gross Profit"].cumsum() /
    profit_pareto["Gross Profit"].sum() * 100
)

fig = px.line(
    profit_pareto,
    x="Product Name",
    y="Cumulative Profit (%)",
    markers=True,
    title="Cumulative Profit Contribution"
)

fig.add_hline(y=80, line_dash="dash")

st.plotly_chart(fig, use_container_width=True)

# =========================
# REGIONAL ANALYSIS
# =========================
st.header("🌎 Regional / State Performance")

location_col = (
    "State"
    if "State" in filtered.columns
    else "Region"
    if "Region" in filtered.columns
    else None
)

if location_col:

    location = filtered.groupby(
        location_col,
        as_index=False
    ).agg({
        "Sales": "sum",
        "Gross Profit": "sum",
        "Units": "sum"
    })

    location["Gross Margin (%)"] = (
        location["Gross Profit"] /
        location["Sales"] * 100
    )

    top_location = location.nlargest(
        15,
        "Sales"
    )

    fig = px.bar(
        top_location,
        x="Sales",
        y=location_col,
        orientation="h",
        title=f"Top {location_col}s by Sales"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        location.sort_values(
            "Gross Profit",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No State or Region column found.")

# =========================
# MARGIN RISK & VOLATILITY
# =========================
st.header("⚠️ Margin Risk & Volatility")

risk_limit = st.slider(
    "Risk Threshold (%)",
    0, 50, 20
)

risk = product[
    product["Gross Margin (%)"] < risk_limit
].sort_values("Gross Margin (%)")

if risk.empty:
    st.success("No products are below the selected margin threshold.")
else:
    st.warning(
        f"{len(risk)} product(s) require margin attention."
    )

    st.dataframe(
        risk[
            [
                "Product Name",
                "Division",
                "Sales",
                "Gross Profit",
                "Gross Margin (%)",
                "Profit per Unit"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

if "Order Date" in filtered.columns:

    monthly = (
        filtered.dropna(subset=["Order Date"])
        .set_index("Order Date")
        .resample("ME")
        .agg({
            "Sales": "sum",
            "Gross Profit": "sum"
        })
        .reset_index()
    )

    monthly["Gross Margin (%)"] = (
        monthly["Gross Profit"] /
        monthly["Sales"] * 100
    )

    fig = px.line(
        monthly,
        x="Order Date",
        y="Gross Margin (%)",
        markers=True,
        title="Monthly Gross Margin Trend"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# FACTORY INFORMATION
# =========================
st.header("🏭 Factory Information")

factory = pd.DataFrame({
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

st.dataframe(
    factory,
    use_container_width=True,
    hide_index=True
)

# =========================
# SUMMARY
# =========================
st.header("💡 Summary & Recommendations")

best_product = product.loc[
    product["Gross Profit"].idxmax()
]

best_margin = product.loc[
    product["Gross Margin (%)"].idxmax()
]

best_division = division.loc[
    division["Gross Profit"].idxmax()
]

st.write(
    f"**Most profitable product:** "
    f"{best_product['Product Name']} "
    f"(${best_product['Gross Profit']:,.2f} profit)"
)

st.write(
    f"**Highest-margin product:** "
    f"{best_margin['Product Name']} "
    f"({best_margin['Gross Margin (%)']:.2f}% margin)"
)

st.write(
    f"**Best division:** "
    f"{best_division['Division']} "
    f"(${best_division['Gross Profit']:,.2f} profit)"
)

st.write(
    "• Focus on high-profit products and divisions."
)

st.write(
    "• Review high-sales products with low margins."
)

st.write(
    "• Monitor products below the margin-risk threshold."
)

st.write(
    "• Use regional performance to identify strong and weak markets."
)

st.write(
    "• Monitor monthly margins to identify changes in profitability."
)

st.divider()

st.caption(
    "Nassau Candy Distributor | Data Science Project"
)
