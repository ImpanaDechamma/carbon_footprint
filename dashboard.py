import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Carbon Footprint Dashboard",
    page_icon="🌍",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df.columns = df.columns.str.strip()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

df = load_data()

# ---------------- TITLE ----------------
st.title("🌍 Carbon Footprint Dashboard")
st.markdown("### 🚀 Smart Monitoring")

# ---------------- SIDEBAR ----------------
st.sidebar.header("🔍 Filters")

server = st.sidebar.selectbox("Select Server", df["server_id"].unique())

# ONLY DATE FILTER
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["timestamp"].min(), df["timestamp"].max()]
)

# COMPARISON GRAPH TYPE
compare_chart = st.sidebar.selectbox(
    "Comparison Graph Type",
    ["Bar Chart", "Pie Chart"]
)

# ---------------- USER INPUT ----------------
st.sidebar.subheader("➕ Add Data")

energy_input = st.sidebar.number_input("Energy (kWh)", min_value=0.0)
date_input = st.sidebar.date_input("Date")
time_input = st.sidebar.time_input("Time")   # ✅ only here

# ---------------- FILTER DATA ----------------
filtered_df = df[df["server_id"] == server].copy()

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["timestamp"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["timestamp"] <= pd.to_datetime(date_range[1]))
    ]

# ---------------- CARBON ----------------
EMISSION_FACTOR = 0.82
filtered_df["carbon"] = filtered_df.get(
    "carbon_emission",
    filtered_df["energy_kwh"] * EMISSION_FACTOR
)

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(
        columns=["server_id", "timestamp", "energy_kwh", "carbon"]
    )

# ---------------- ADD USER DATA ----------------
if energy_input > 0:
    timestamp = pd.to_datetime(str(date_input) + " " + str(time_input))

    new_data = pd.DataFrame({
        "server_id": [server],
        "timestamp": [timestamp],
        "energy_kwh": [energy_input],
        "carbon": [energy_input * EMISSION_FACTOR]
    })

    filtered_df = pd.concat([filtered_df, new_data], ignore_index=True)
    st.session_state.history = pd.concat(
        [st.session_state.history, new_data],
        ignore_index=True
    )

# ---------------- METRICS ----------------
st.subheader("📊 Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Energy", round(filtered_df["energy_kwh"].sum(), 2))
col2.metric("Carbon", round(filtered_df["carbon"].sum(), 2))
col3.metric("Average", round(filtered_df["carbon"].mean(), 2))

st.divider()

# ---------------- SERVER GRAPH ----------------
st.subheader(f"📉 Server {server} Carbon Trend")

fig1 = px.line(filtered_df, x="timestamp", y="carbon", markers=True)
fig1.update_xaxes(tickformat="%Y-%m-%d %H:%M")

st.plotly_chart(fig1, use_container_width=True)

# ---------------- COMPARISON GRAPH ----------------
st.subheader("📊 Server Comparison")

df["carbon"] = df.get(
    "carbon_emission",
    df["energy_kwh"] * EMISSION_FACTOR
)

df_filtered = df[
    (df["timestamp"] >= pd.to_datetime(date_range[0])) &
    (df["timestamp"] <= pd.to_datetime(date_range[1]))
]

if not df_filtered.empty:
    compare_data = df_filtered.groupby("server_id")["carbon"].sum().reset_index()

    if compare_chart == "Bar Chart":
        fig2 = px.bar(compare_data, x="server_id", y="carbon", color="server_id")
    else:
        fig2 = px.pie(compare_data, names="server_id", values="carbon")

    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No data available")

# ---------------- PREDICTION TABLE ----------------
st.subheader("🔮 Prediction Table")

if filtered_df.empty or len(filtered_df) < 2:
    st.warning("Not enough data for prediction")
else:
    filtered_df = filtered_df.sort_values("timestamp")
    filtered_df["time_index"] = np.arange(len(filtered_df))

    X = filtered_df[["time_index"]]
    y = filtered_df["carbon"]

    model = LinearRegression()
    model.fit(X, y)

    future_index = pd.DataFrame({
        "time_index": np.arange(len(filtered_df), len(filtered_df) + 5)
    })

    preds = model.predict(future_index)

    future_dates = pd.date_range(
        start=filtered_df["timestamp"].max(),
        periods=6,
        freq="D"
    )[1:]

    future_df = pd.DataFrame({
        "timestamp": future_dates,
        "predicted_carbon": preds
    })

    st.dataframe(future_df)

# ---------------- HISTORY ----------------
st.subheader("🕒 Recent Inputs")

recent = st.session_state.history.tail(10)
st.dataframe(recent)

# ---------------- HISTORY BAR GRAPH ----------------
st.subheader("📊 Recent Input Trend")

if not recent.empty:
    fig3 = px.bar(
        recent,
        x="timestamp",
        y="carbon",
        color="server_id"
    )
    fig3.update_xaxes(tickformat="%Y-%m-%d %H:%M")

    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No history data")
