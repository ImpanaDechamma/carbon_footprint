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
    df = pd.read_csv("carbon_footprint_final.csv")
    df.columns = df.columns.str.strip()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

df = load_data()

# ---------------- TITLE ----------------
st.title("🌍 Carbon Footprint Dashboard")
st.markdown("### 🚀 Smart Monitoring")

# ---------------- SESSION STORAGE ----------------
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(
        columns=["server_id", "timestamp", "energy_kwh", "carbon"]
    )

# ---------------- SIDEBAR ----------------
st.sidebar.header("🔍 Filters")

server = st.sidebar.selectbox("Select Server", df["server_id"].unique())

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["timestamp"].min(), df["timestamp"].max()]
)

compare_chart = st.sidebar.selectbox(
    "Comparison Graph Type",
    ["Bar Chart", "Pie Chart"]
)

# ---------------- USER INPUT ----------------
st.sidebar.subheader("➕ Enter Data")

energy_input = st.sidebar.number_input("Energy (kWh)", min_value=0.0)
date_input = st.sidebar.date_input("Date")
time_input = st.sidebar.time_input("Time")

EMISSION_FACTOR = 0.82

# ---------------- ADD USER DATA ----------------
if energy_input > 0:
    timestamp = pd.to_datetime(str(date_input) + " " + str(time_input))

    new_data = pd.DataFrame({
        "server_id": [server],
        "timestamp": [timestamp],
        "energy_kwh": [energy_input],
        "carbon": [energy_input * EMISSION_FACTOR]
    })

    # Store only in session (DO NOT mix directly)
    st.session_state.history = pd.concat(
        [st.session_state.history, new_data],
        ignore_index=True
    )

# ---------------- COMBINE DATA ----------------
combined_df = pd.concat([df, st.session_state.history], ignore_index=True)

# Ensure correct carbon calculation
combined_df["carbon"] = combined_df.get(
    "carbon_emission",
    combined_df["energy_kwh"] * EMISSION_FACTOR
)

# Sort data (VERY IMPORTANT FIX)
combined_df = combined_df.sort_values("timestamp")

# Apply filters
filtered_df = combined_df[combined_df["server_id"] == server]

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["timestamp"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["timestamp"] <= pd.to_datetime(date_range[1]))
    ]

# ---------------- METRICS ----------------
st.subheader("📊 Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Energy", round(filtered_df["energy_kwh"].sum(), 2))
col2.metric("Total Carbon", round(filtered_df["carbon"].sum(), 2))
col3.metric("Average Carbon", round(filtered_df["carbon"].mean(), 6))

st.divider()

# ---------------- HISTOGRAM ----------------
st.subheader(f"📊 Server {server} Carbon Distribution")

if not filtered_df.empty:
    fig1 = px.histogram(filtered_df, x="carbon", nbins=10)
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("No data available")

# # ---------------- TREND GRAPH (FIXED) ----------------
# st.subheader("📈 Carbon Trend Over Time")

# if not filtered_df.empty:
#     fig_trend = px.line(
#         filtered_df,
#         x="timestamp",
#         y="carbon",
#         markers=True,
#         title="Carbon Emission Trend"
#     )
#     st.plotly_chart(fig_trend, use_container_width=True)
# else:
#     st.warning("No data available")

# ---------------- COMPARISON GRAPH ----------------
st.subheader("📊 Server Comparison")

df_filtered = combined_df[
    (combined_df["timestamp"] >= pd.to_datetime(date_range[0])) &
    (combined_df["timestamp"] <= pd.to_datetime(date_range[1]))
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

# ---------------- PREDICTION ----------------
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

recent = st.session_state.history.sort_values("timestamp").tail(10)
st.dataframe(recent)

# ---------------- RECENT TREND ----------------
st.subheader("📈 Recent Input Trend")

if not recent.empty:
    fig3 = px.line(
        recent,
        x="timestamp",
        y="carbon",
        color="server_id",
        markers=True
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No history data")

# ---------------- ALERTS ----------------
st.subheader("⚠️ Smart Alerts")

if not recent.empty and len(recent) >= 3:
    recent = recent.sort_values("timestamp")

    last = recent["carbon"].iloc[-1]
    prev = recent["carbon"].iloc[-2]
    avg = recent["carbon"].mean()

    if last > avg * 1.3:
        st.error("🚨 Sudden spike in carbon emission detected!")

    elif (recent["carbon"].iloc[-1] >
          recent["carbon"].iloc[-2] >
          recent["carbon"].iloc[-3]):
        st.warning("⚠️ Carbon emission is continuously increasing!")

    elif last < avg * 0.7:
        st.success("✅ Emission reduced significantly!")

    else:
        st.info("ℹ️ System is stable.")
else:
    st.info("Not enough data for alerts")

# ---------------- SUGGESTIONS ----------------
st.subheader("💡 Suggestions")

if not recent.empty and len(recent) >= 2:
    last = recent["carbon"].iloc[-1]
    prev = recent["carbon"].iloc[-2]

    if last > prev:
        st.warning("🔺 Emissions increasing → optimize server usage")

    elif last < prev:
        st.success("🔻 Emissions decreasing → good optimization")

    else:
        st.info("➖ Emissions stable → monitor regularly")
else:
    st.info("Add more inputs for suggestions")