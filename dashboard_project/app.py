import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page configuration
st.set_page_config(
    page_title="Business Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Interactive Business Intelligence Dashboard")
st.markdown("Dynamic dashboard with KPI cards, filters and interactive charts")

# Load datasets
@st.cache_data
def load_data():
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))

churn_file = os.path.join(BASE_DIR, "customer_churn.csv")
checkout_file = os.path.join(BASE_DIR, "checkout_ab_test.csv")

churn = pd.read_csv(churn_file)
checkout = pd.read_csv(checkout_file)

    # Clean Total Charges column
    churn["TotalChargesINR"] = pd.to_numeric(
        churn["TotalChargesINR"],
        errors="coerce"
    ).fillna(0)

    return churn, checkout

churn, checkout = load_data()

# Sidebar filters
st.sidebar.header("🔎 Dashboard Filters")

# Region Filter
regions = ["All"] + sorted(churn["Region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", regions)

# Category Filter
categories = ["All"] + sorted(churn["SubscriptionType"].unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", categories)

# Apply filters
filtered_data = churn.copy()

if selected_region != "All":
    filtered_data = filtered_data[
        filtered_data["Region"] == selected_region
    ]

if selected_category != "All":
    filtered_data = filtered_data[
        filtered_data["SubscriptionType"] == selected_category
    ]

# KPI Calculations
total_revenue = filtered_data["TotalChargesINR"].sum()
active_users = len(filtered_data[filtered_data["Churn"] == "No"])
churn_percent = (
    filtered_data["Churn"].eq("Yes").mean() * 100
)

converted_orders = checkout[checkout["Converted"] == "Yes"]
avg_ticket_size = converted_orders["OrderValueINR"].mean()

# KPI Cards
st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Total Revenue",
    f"₹ {total_revenue:,.0f}"
)

col2.metric(
    "👥 Active Users",
    f"{active_users:,}"
)

col3.metric(
    "📉 Churn %",
    f"{churn_percent:.2f}%"
)

col4.metric(
    "🎟️ Avg Ticket Size",
    f"₹ {avg_ticket_size:,.2f}"
)

st.divider()

# Chart 1 - Customers by Region
st.subheader("📍 Customers by Region")

region_data = (
    filtered_data.groupby("Region")
    .size()
    .reset_index(name="Customers")
)

fig1 = px.bar(
    region_data,
    x="Region",
    y="Customers",
    title="Customer Distribution by Region"
)

st.plotly_chart(fig1, use_container_width=True)

# Two charts side by side
col1, col2 = st.columns(2)

# Chart 2 - Churn by Subscription Type
with col1:
    subscription_data = (
        filtered_data.groupby(
            ["SubscriptionType", "Churn"]
        ).size()
        .reset_index(name="Count")
    )

    fig2 = px.bar(
        subscription_data,
        x="SubscriptionType",
        y="Count",
        color="Churn",
        barmode="group",
        title="Churn by Subscription Type"
    )

    st.plotly_chart(fig2, use_container_width=True)

# Chart 3 - Revenue by Contract Type
with col2:
    contract_data = (
        filtered_data.groupby("ContractType")["TotalChargesINR"]
        .sum()
        .reset_index()
    )

    fig3 = px.pie(
        contract_data,
        names="ContractType",
        values="TotalChargesINR",
        title="Revenue by Contract Type"
    )

    st.plotly_chart(fig3, use_container_width=True)

# Chart 4 - Monthly Charges Distribution
st.subheader("💵 Monthly Charges Distribution")

fig4 = px.histogram(
    filtered_data,
    x="MonthlyChargesINR",
    nbins=30,
    title="Monthly Charges Distribution"
)

st.plotly_chart(fig4, use_container_width=True)

# Footer
st.success("Dashboard created successfully using Streamlit!")
