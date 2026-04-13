import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ---------------- COUNTRY EMISSION FACTORS ----------------
COUNTRY_EMISSION_FACTORS = {
    "USA"          : 0.386,
    "EU (Average)" : 0.233,
    "India"        : 0.820,
    "China"        : 0.555,
    "Germany"      : 0.350,
    "UK"           : 0.233,
    "France"       : 0.052,
    "Australia"    : 0.790,
    "Canada"       : 0.130,
    "Brazil"       : 0.074,
    "Japan"        : 0.474,
    "South Korea"  : 0.415,
    "Russia"       : 0.322,
    "South Africa" : 0.928,
    "Custom"       : None,
}

COUNTRY_FLAGS = {
    "USA"          : "🇺🇸",
    "EU (Average)" : "🇪🇺",
    "India"        : "🇮🇳",
    "China"        : "🇨🇳",
    "Germany"      : "🇩🇪",
    "UK"           : "🇬🇧",
    "France"       : "🇫🇷",
    "Australia"    : "🇦🇺",
    "Canada"       : "🇨🇦",
    "Brazil"       : "🇧🇷",
    "Japan"        : "🇯🇵",
    "South Korea"  : "🇰🇷",
    "Russia"       : "🇷🇺",
    "South Africa" : "🇿🇦",
    "Custom"       : "⚙️",
}

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Carbon Footprint Dashboard",
    page_icon="🌍",
    layout="wide"
)

# ---------------- DARK THEME CSS ----------------
st.markdown("""
<style>
    .main {
        background: #020617;
        color: #e2e8f0;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1rem;
    }

    .hero-box {
        background: linear-gradient(135deg, #0f172a, #1d4ed8, #06b6d4);
        padding: 26px;
        border-radius: 20px;
        color: #e2e8f0;
        margin-bottom: 22px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
        border: 1px solid #1e293b;
    }

    .hero-title {
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .hero-subtitle {
        font-size: 16px;
        color: #cbd5e1;
    }

    .section-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 18px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.25);
    }

    div[data-testid="stMetric"] {
        background: #111827 !important;
        border: 1px solid #334155 !important;
        padding: 16px !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.25);
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
        font-weight: 800 !important;
    }

    div[data-testid="stMetricDelta"] {
        color: #22c55e !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] {
        background: #020617;
        border-right: 1px solid #1e293b;
    }

    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: #0f172a;
        color: #94a3b8;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 10px 16px;
    }

    .stTabs [aria-selected="true"] {
        background: #1d4ed8 !important;
        color: white !important;
    }

    .stButton button {
        background: linear-gradient(90deg, #2563eb, #0891b2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }

    .stDownloadButton button {
        background: linear-gradient(90deg, #2563eb, #0891b2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #1e293b;
        border-radius: 14px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("carbon_footprint_final.csv")
    df.columns = df.columns.str.strip()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

df = load_data()

# emission factor per server based on the dataset
SERVER_EMISSION_FACTORS = {
    "S1": 0.386,   # USA
    "S2": 0.233,   # EU
    "S3": 0.820,   # India
}

# ---------------- HERO ----------------
st.markdown("""
<div class="hero-box">
    <div class="hero-title">🌍 Carbon Footprint Dashboard</div>
    <div class="hero-subtitle">
        Smart monitoring, prediction, alerts, suggestions, and CSV-based analysis for server carbon emissions.
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- EMAIL REGISTRATION ----------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("📧 Alert Email Registration")
st.caption("Enter your email to receive an alert when carbon emissions are abnormal.")
email_col1, email_col2 = st.columns([3, 1])
with email_col1:
    user_email = st.text_input(
        "Your Email Address",
        placeholder="example@gmail.com",
        label_visibility="collapsed"
    )
with email_col2:
    register_clicked = st.button("✅ Register", use_container_width=True)
if register_clicked:
    if user_email and "@" in user_email and "." in user_email:
        st.session_state.alert_email = user_email
        st.success(f"Email **{user_email}** registered. You will receive alerts for abnormal emissions.")
    else:
        st.error("Please enter a valid email address.")
if "alert_email" in st.session_state and st.session_state.alert_email:
    st.info(f"📬 Alerts will be sent to: **{st.session_state.alert_email}**")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- SESSION STORAGE ----------------
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(
        columns=["server_id", "timestamp", "energy_kwh", "carbon"]
    )

# ---------------- SIDEBAR ----------------
st.sidebar.header("🔍 Filters")

server = st.sidebar.selectbox("Select Server", sorted(df["server_id"].dropna().unique()))

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["timestamp"].min().date(), df["timestamp"].max().date()]
)

compare_chart = st.sidebar.selectbox(
    "Comparison Graph Type",
    ["Bar Chart", "Pie Chart"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 Alert Threshold")
alert_threshold = st.sidebar.number_input(
    "Carbon Alert Threshold (kg CO₂)",
    min_value=0.0001,
    value=0.010,
    step=0.001,
    format="%.4f",
    help="An alert is triggered when the latest carbon reading exceeds this value."
)
st.sidebar.caption(f"Alert fires if carbon > **{alert_threshold} kg CO₂**")

# ---------------- USER INPUT ----------------
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Enter Data")

energy_input = st.sidebar.number_input("Energy (kWh)", min_value=0.0, step=0.1)
date_input = st.sidebar.date_input("Date")
time_input = st.sidebar.time_input("Time")

if st.sidebar.button("Add Data", use_container_width=True):
    if energy_input > 0:
        timestamp = pd.to_datetime(f"{date_input} {time_input}")
        emission_factor = SERVER_EMISSION_FACTORS.get(server, 0.82)
        carbon_value    = round(energy_input * emission_factor, 6)

        new_data = pd.DataFrame({
            "server_id" : [server],
            "timestamp" : [timestamp],
            "energy_kwh": [energy_input],
            "carbon"    : [carbon_value]
        })

        st.session_state.history = pd.concat(
            [st.session_state.history, new_data],
            ignore_index=True
        )
        st.sidebar.success(f"Added: {carbon_value} kg CO₂ ({server})")
    else:
        st.sidebar.warning("Enter energy greater than 0")

# ---------------- COMBINE DATA ----------------
combined_df = pd.concat([df, st.session_state.history], ignore_index=True)

if "carbon_emission" in combined_df.columns:
    combined_df["carbon"] = combined_df["carbon_emission"].fillna(
        combined_df.apply(
            lambda r: r["energy_kwh"] * SERVER_EMISSION_FACTORS.get(r["server_id"], 0.82),
            axis=1
        )
    )
else:
    combined_df["carbon"] = combined_df.apply(
        lambda r: r["energy_kwh"] * SERVER_EMISSION_FACTORS.get(r["server_id"], 0.82),
        axis=1
    )

combined_df["timestamp"] = pd.to_datetime(combined_df["timestamp"])
combined_df = combined_df.sort_values("timestamp")

# ---------------- FILTER DATA ----------------
filtered_df = combined_df[combined_df["server_id"] == server].copy()

if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    filtered_df = filtered_df[
        (filtered_df["timestamp"] >= start_date) &
        (filtered_df["timestamp"] <= end_date)
    ]

# ---------------- METRICS ----------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Energy", round(filtered_df["energy_kwh"].sum(), 2) if not filtered_df.empty else 0)
col2.metric("Total Carbon", round(filtered_df["carbon"].sum(), 2) if not filtered_df.empty else 0)
col3.metric("Average Carbon", round(filtered_df["carbon"].mean(), 6) if not filtered_df.empty else 0)
col4.metric("Peak Carbon", round(filtered_df["carbon"].max(), 6) if not filtered_df.empty else 0)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- HISTOGRAM ----------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader(f"📊 Server {server} Carbon Distribution")

if not filtered_df.empty:
    fig1 = px.histogram(
        filtered_df,
        x="carbon",
        nbins=10,
        title="Carbon Distribution",
        template="plotly_dark"
    )
    fig1.update_layout(
        height=400,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a"
    )
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("No data available")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- COMPARISON GRAPH ----------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("📊 Server Comparison")

df_filtered = combined_df.copy()
if len(date_range) == 2:
    df_filtered = df_filtered[
        (df_filtered["timestamp"] >= start_date) &
        (df_filtered["timestamp"] <= end_date)
    ]

if not df_filtered.empty:
    compare_data = df_filtered.groupby("server_id", as_index=False)["carbon"].sum()

    if compare_chart == "Bar Chart":
        fig2 = px.bar(
            compare_data,
            x="server_id",
            y="carbon",
            color="server_id",
            title="Server Comparison",
            template="plotly_dark"
        )
    else:
        fig2 = px.pie(
            compare_data,
            names="server_id",
            values="carbon",
            title="Server Comparison",
            template="plotly_dark",
            hole=0.35
        )

    fig2.update_layout(
        height=420,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a"
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No data available")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- PREDICTION ----------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("🔮 Predicted Carbon Emission (Random Forest)")
st.caption("Uses the trained Random Forest model to predict carbon emission based on current server, region and energy input.")

if not filtered_df.empty:
    pred_c1, pred_c2, pred_c3 = st.columns(3)

    with pred_c1:
        pred_energy = st.number_input(
            "🔋 Energy (kWh)",
            min_value=0.0001, value=0.01, step=0.001, format="%.4f",
            key="pred_energy"
        )
    with pred_c2:
        pred_power = st.number_input(
            "⚡ Power (Watts)",
            min_value=1.0, value=120.0, step=1.0,
            key="pred_power"
        )
    with pred_c3:
        pred_region = st.selectbox(
            "🌍 Region",
            ["USA", "EU", "India"],
            key="pred_region"
        )

    if st.button("🔮 Predict Carbon", use_container_width=True):
        try:
            import requests
            payload = {
                "server_id"      : server,
                "region"         : pred_region,
                "energy_kwh"     : pred_energy,
                "power_watts"    : pred_power,
                "emission_factor": {"USA": 0.386, "EU": 0.233, "India": 0.82}.get(pred_region, 0.386),
                "timestamp"      : pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            response = requests.post("http://127.0.0.1:5000/predict", json=payload, timeout=5)
            result   = response.json()

            if result.get("success"):
                predicted_val = result["predicted_carbon_emission"]
                actual_val    = round(pred_energy * payload["emission_factor"], 6)
                diff          = round(predicted_val - actual_val, 6)
                diff_pct      = round((diff / actual_val) * 100, 2) if actual_val != 0 else 0

                m1, m2, m3 = st.columns(3)
                m1.metric("🤖 Predicted Carbon",  f"{predicted_val} kg CO₂")
                m2.metric("🧮 Calculated Carbon", f"{actual_val} kg CO₂")
                m3.metric("📊 Difference",        f"{diff} kg CO₂", delta=f"{diff_pct}%")

                st.caption("🤖 **Predicted** = Random Forest model output based on power, time and server patterns")
                st.caption("🧮 **Calculated** = Direct formula: energy × emission factor")
            else:
                st.error(f"Prediction failed: {result.get('error')}")

        except requests.exceptions.ConnectionError:
            st.warning("⚠️ Flask API is not running. Start it with `python main.py` to use predictions.")
        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.warning("No data available for prediction.")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- HISTORY ----------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("🕒 Recent Inputs")

recent = st.session_state.history.sort_values("timestamp").tail(10)
st.dataframe(recent, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- RECENT TREND ----------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("📈 Recent Input Trend")

if not recent.empty:
    trend_df = recent.copy()
    trend_df["timestamp"] = pd.to_datetime(trend_df["timestamp"])

    trend_df = (
        trend_df.groupby(["server_id", "timestamp"], as_index=False)["carbon"]
        .mean()
        .sort_values(["server_id", "timestamp"])
    )

    fig3 = px.line(
        trend_df,
        x="timestamp",
        y="carbon",
        color="server_id",
        markers=True,
        title="Recent Input Trend",
        template="plotly_dark"
    )
    fig3.update_layout(
        height=430,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a"
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No history data")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ALERTS ----------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("⚠️ Smart Alerts")
st.caption(f"Current threshold: **{alert_threshold} kg CO₂** — change it in the sidebar.")

if not recent.empty and len(recent) >= 3:
    recent_alert = recent.sort_values("timestamp").copy()
    last         = recent_alert["carbon"].iloc[-1]
    avg          = recent_alert["carbon"].mean()
    alert_email  = st.session_state.get("alert_email", "")
    alert_type   = None

    # ── threshold breach (user-defined) ──────────────────────────────────────
    if last > alert_threshold:
        st.error(
            f"🚨 Carbon emission **{round(last, 6)} kg CO₂** exceeded your "
            f"threshold of **{alert_threshold} kg CO₂**!"
        )
        alert_type = "threshold"

    # ── spike: 30% above rolling average ─────────────────────────────────────
    elif last > avg * 1.3:
        st.error(
            f"🚨 Sudden spike detected! Current: **{round(last,6)} kg CO₂** "
            f"is 30%+ above average **{round(avg,6)} kg CO₂**."
        )
        alert_type = "spike"

    # ── rising trend: 3 consecutive increases ────────────────────────────────
    elif (
        recent_alert["carbon"].iloc[-1] >
        recent_alert["carbon"].iloc[-2] >
        recent_alert["carbon"].iloc[-3]
    ):
        st.warning(
            f"⚠️ Carbon emission is continuously increasing over the last 3 readings "
            f"(latest: **{round(last,6)} kg CO₂**)."
        )
        alert_type = "trend"

    # ── significant reduction ─────────────────────────────────────────────────
    elif last < avg * 0.7:
        st.success(
            f"✅ Emission reduced significantly! Current: **{round(last,6)} kg CO₂** "
            f"is 30%+ below average **{round(avg,6)} kg CO₂**."
        )

    # ── stable ────────────────────────────────────────────────────────────────
    else:
        st.info(
            f"ℹ️ System is stable. Current emission: **{round(last,6)} kg CO₂** "
            f"(threshold: {alert_threshold} kg CO₂)."
        )

    # ── send email if alert triggered ─────────────────────────────────────────
    if alert_type and alert_email:
        last_sent_key = f"last_alert_sent_{server}"
        last_sent     = st.session_state.get(last_sent_key)
        current_ts    = pd.Timestamp.now()
        if last_sent is None or (current_ts - last_sent).seconds > 600:
            try:
                from email_alert import send_alert_email
                send_alert_email(
                    recipient_email = alert_email,
                    server_id       = server,
                    current_carbon  = last,
                    avg_carbon      = avg,
                    alert_type      = alert_type
                )
                st.session_state[last_sent_key] = current_ts
                st.warning(f"📧 Alert email sent to **{alert_email}**")
            except Exception as e:
                st.error(f"Failed to send email: {e}")
else:
    st.info("Add at least 3 data entries using the sidebar to activate alerts.")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- SUGGESTIONS ----------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("💡 Actionable Suggestions")

if not recent.empty and len(recent) >= 2:
    recent_suggestion = recent.sort_values("timestamp").copy()
    last  = recent_suggestion["carbon"].iloc[-1]
    prev  = recent_suggestion["carbon"].iloc[-2]
    avg   = recent_suggestion["carbon"].mean()
    peak  = recent_suggestion["carbon"].max()
    change_pct = round(((last - prev) / prev) * 100, 2) if prev != 0 else 0

    if last > prev:
        st.warning(f"🔺 Carbon emissions increased by **{change_pct}%** compared to the previous reading ({round(prev,6)} → {round(last,6)} kg CO₂).")

        st.markdown("**Here is what you can do to bring emissions down:**")

        with st.expander("⚡ 1. Apply Power Capping", expanded=True):
            st.markdown("""
            Power capping limits the maximum power a server can draw, directly reducing energy consumption.
            - Use **IPMI or BIOS settings** to set a power cap (e.g., cap at 80% of TDP).
            - On Linux servers, use `rapl` (Running Average Power Limit) to enforce CPU power limits.
            - A 10% reduction in power draw typically results in a **10% reduction in carbon emission**.
            - Best applied during **off-peak hours** when full performance is not required.
            """)

        with st.expander("🌙 2. Schedule Workloads During Off-Peak Hours"):
            st.markdown("""
            Grid carbon intensity varies throughout the day — it is typically lower at night when renewable sources dominate.
            - Move **batch jobs, backups, and data processing** tasks to late night or early morning.
            - Use job schedulers like **cron, Apache Airflow, or Kubernetes CronJobs** to automate this.
            - This can reduce effective carbon emissions by **15–30%** without changing hardware.
            """)

        with st.expander("🖥️ 3. Consolidate Underutilised Servers"):
            st.markdown("""
            Idle or low-utilisation servers still consume 40–60% of their peak power.
            - Use **VM consolidation tools** (VMware vSphere, Proxmox) to migrate workloads to fewer active servers.
            - Power down or hibernate servers that are below **20% CPU utilisation** for extended periods.
            - Each server powered down saves approximately **200–500W** continuously.
            """)

        with st.expander("🌍 4. Migrate Workloads to Low-Emission Regions"):
            st.markdown("""
            The same workload produces vastly different carbon emissions depending on where it runs.
            - **France (0.052 kg CO₂/kWh)** — nuclear-heavy grid, one of the cleanest in the world.
            - **Brazil (0.074 kg CO₂/kWh)** — hydro-dominated, excellent for carbon-sensitive workloads.
            - **Canada (0.130 kg CO₂/kWh)** — mix of hydro and nuclear.
            - Migrating from India (0.82) to France (0.052) reduces carbon by up to **94%** for the same energy.
            """)

        with st.expander("🔧 5. Enable Dynamic Voltage and Frequency Scaling (DVFS)"):
            st.markdown("""
            DVFS reduces CPU voltage and clock speed during low-demand periods, cutting power consumption.
            - Enable **CPU governor settings** on Linux: set to `powersave` or `ondemand` mode.
            - Command: `cpupower frequency-set -g powersave`
            - Can reduce CPU power draw by **20–40%** during idle or light workloads.
            - Works best on servers with variable workloads throughout the day.
            """)

        with st.expander("♻️ 6. Switch to Renewable Energy Sources"):
            st.markdown("""
            Switching the data center's power supply to renewables directly reduces the emission factor.
            - Purchase **Renewable Energy Certificates (RECs)** to offset grid emissions.
            - Negotiate a **Power Purchase Agreement (PPA)** with a solar or wind energy provider.
            - Install **on-site solar panels** if the facility allows it.
            - This can bring the effective emission factor close to **0.0 kg CO₂/kWh**.
            """)

    elif last < prev:
        st.success(f"🔻 Carbon emissions decreased by **{abs(change_pct)}%** compared to the previous reading ({round(prev,6)} → {round(last,6)} kg CO₂). Good work!")

        st.markdown("**Keep the momentum going with these practices:**")

        with st.expander("✅ 1. Maintain Current Optimisation Settings", expanded=True):
            st.markdown("""
            The current reduction suggests your optimisation strategies are working.
            - Document what changed (power cap, workload schedule, server consolidation) so it can be repeated.
            - Set these configurations as **default baseline settings** for all servers.
            - Review settings every **30 days** to ensure they remain effective as workloads change.
            """)

        with st.expander("📉 2. Set a Carbon Reduction Target"):
            st.markdown(f"""
            Your current average emission is **{round(avg, 6)} kg CO₂** and peak is **{round(peak, 6)} kg CO₂**.
            - Set a target to reduce average emissions by a further **10–20%** over the next month.
            - Track progress using the prediction table above to see if you are on track.
            - Consider adopting the **Green Software Foundation's SCI (Software Carbon Intensity)** metric
              to measure carbon per unit of useful work done.
            """)

        with st.expander("🔍 3. Identify and Eliminate Remaining Waste"):
            st.markdown("""
            Even with reductions, there is usually further optimisation possible.
            - Run a **power audit** to identify which servers or services consume the most energy.
            - Look for **zombie processes** — background tasks consuming CPU with no useful output.
            - Check for **memory leaks** in applications that force servers to work harder than needed.
            - Use tools like **PowerTOP, Grafana, or Prometheus** to monitor per-process energy usage.
            """)

    else:
        st.info(f"➖ Carbon emissions are stable at **{round(last, 6)} kg CO₂**. No change from the previous reading.")

        st.markdown("**Stability is good, but here are proactive steps to reduce further:**")

        with st.expander("📊 1. Analyse Peak Emission Periods", expanded=True):
            st.markdown(f"""
            Your peak emission recorded is **{round(peak, 6)} kg CO₂** vs average of **{round(avg, 6)} kg CO₂**.
            - Investigate what workloads are running during peak emission periods.
            - If peak is significantly higher than average, those workloads are candidates for **rescheduling or capping**.
            - Use the historical trend chart above to identify recurring high-emission time windows.
            """)

        with st.expander("🌱 2. Explore Carbon Offsetting"):
            st.markdown("""
            While reducing emissions at source is ideal, carbon offsetting can neutralise unavoidable emissions.
            - Purchase **verified carbon offsets** through Gold Standard or Verra-certified projects.
            - Invest in **reforestation or direct air capture** projects proportional to your monthly emissions.
            - Calculate your monthly total from the Key Metrics section and offset accordingly.
            """)
else:
    st.info("Add at least 2 data entries using the sidebar to see detailed suggestions.")

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# COUNTRY CARBON CALCULATOR
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("🌍 Country-Based Carbon Emission Calculator")
st.caption("Select a country, enter energy consumed — carbon is calculated using that country's emission factor. You can also provide a custom factor.")

country_options  = [f"{COUNTRY_FLAGS[c]}  {c}" for c in COUNTRY_EMISSION_FACTORS]
selected_label   = st.selectbox("🗺️ Select Country", country_options)
selected_country = selected_label.split("  ", 1)[1].strip()

COUNTRY_TO_SERVER = {
    "USA": "S-USA", "EU (Average)": "S-EU", "India": "S-IND",
    "China": "S-CHN", "Germany": "S-DEU", "UK": "S-GBR",
    "France": "S-FRA", "Australia": "S-AUS", "Canada": "S-CAN",
    "Brazil": "S-BRA", "Japan": "S-JPN", "South Korea": "S-KOR",
    "Russia": "S-RUS", "South Africa": "S-ZAF", "Custom": "S-CUSTOM",
}
calc_server = COUNTRY_TO_SERVER.get(selected_country, "S-CUSTOM")
st.caption(f"🖥️ Server assigned: **{calc_server}**")

ef_col1, ef_col2 = st.columns([2, 2])
with ef_col1:
    default_ef = COUNTRY_EMISSION_FACTORS[selected_country]
    if default_ef is None:
        active_ef = st.number_input(
            "✏️ Enter Custom Emission Factor (kg CO₂/kWh)",
            min_value=0.001, value=0.500, step=0.001, format="%.3f"
        )
    else:
        active_ef = st.number_input(
            f"⚡ Emission Factor for {selected_country} (kg CO₂/kWh)",
            min_value=0.001, value=float(default_ef), step=0.001, format="%.3f",
            help="Pre-filled from IEA/EPA data. You can override this value."
        )
with ef_col2:
    energy_kwh_input = st.number_input(
        "🔋 Energy Consumed (kWh)",
        min_value=0.0001, value=0.01, step=0.001, format="%.4f",
        help="Enter the energy consumed directly in kWh"
    )

if st.button("⚡ Calculate Carbon Emission", use_container_width=True):
    carbon_emission_calc = round(energy_kwh_input * active_ef, 6)
    annual_carbon        = round(carbon_emission_calc * 8760, 4)
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("🌐 Country",         f"{COUNTRY_FLAGS.get(selected_country,'')} {selected_country}")
    r2.metric("⚡ Emission Factor", f"{active_ef} kg CO₂/kWh")
    r3.metric("🔋 Energy Used",     f"{energy_kwh_input} kWh")
    r4.metric("💨 Carbon Emitted",  f"{carbon_emission_calc} kg CO₂")
    st.info(f"📅 Estimated annual carbon at {energy_kwh_input} kWh per hour: **{annual_carbon} kg CO₂/year**")

    new_calc = pd.DataFrame({
        "server_id": [calc_server], "timestamp": [pd.Timestamp.now()],
        "energy_kwh": [energy_kwh_input], "carbon": [carbon_emission_calc],
        "country": [selected_country], "emission_factor": [active_ef]
    })
    if "country_calc_history" not in st.session_state:
        st.session_state.country_calc_history = pd.DataFrame()
    st.session_state.country_calc_history = pd.concat(
        [st.session_state.country_calc_history, new_calc], ignore_index=True
    )
    st.success("✅ Result saved to comparison table below.")

if "country_calc_history" in st.session_state and not st.session_state.country_calc_history.empty:
    hist = st.session_state.country_calc_history.copy()
    st.markdown("#### 📋 Calculation History")
    st.dataframe(
        hist[["server_id", "country", "emission_factor", "energy_kwh", "carbon", "timestamp"]]
        .sort_values("timestamp", ascending=False).reset_index(drop=True),
        use_container_width=True
    )
    country_summary = hist.groupby("country", as_index=False)["carbon"].sum().sort_values("carbon", ascending=False)
    fig_country = px.bar(
        country_summary, x="country", y="carbon", color="country",
        title="Total Carbon Emission by Country",
        labels={"carbon": "Carbon (kg CO₂)", "country": "Country"},
        template="plotly_dark"
    )
    fig_country.update_layout(height=400, paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", showlegend=False)
    st.plotly_chart(fig_country, use_container_width=True)

    ef_summary = hist.drop_duplicates("country")[["country", "emission_factor"]].sort_values("emission_factor", ascending=False)
    fig_ef = px.bar(
        ef_summary, x="country", y="emission_factor",
        color="emission_factor", color_continuous_scale="RdYlGn_r",
        title="Emission Factor Comparison (kg CO₂/kWh)",
        labels={"emission_factor": "kg CO₂/kWh"}, template="plotly_dark"
    )
    fig_ef.update_layout(height=380, paper_bgcolor="#0f172a", plot_bgcolor="#0f172a")
    st.plotly_chart(fig_ef, use_container_width=True)

    cleanest = country_summary.iloc[-1]["country"]
    st.success(f"💡 Recommendation: **{cleanest}** has the lowest carbon emission. Consider routing workloads there.")

    if st.button("🗑️ Clear Calculation History"):
        st.session_state.country_calc_history = pd.DataFrame()
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# CSV UPLOAD + ANALYSIS + GRAPH
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("📁 Upload CSV & Analyze")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        upload_df = pd.read_csv(uploaded_file)
        upload_df.columns = upload_df.columns.str.strip()

        st.success("CSV uploaded successfully!")

        st.write("### Preview of Uploaded Data")
        st.dataframe(upload_df.head(), use_container_width=True)

        st.write("### Dataset Info")
        info1, info2, info3 = st.columns(3)
        info1.metric("Rows", upload_df.shape[0])
        info2.metric("Columns", upload_df.shape[1])
        info3.metric("Missing Values", int(upload_df.isnull().sum().sum()))

        numeric_cols = upload_df.select_dtypes(include=np.number).columns.tolist()
        all_cols = upload_df.columns.tolist()

        if len(all_cols) >= 2:
            st.write("### Graph Generator")

            c1, c2, c3 = st.columns(3)

            with c1:
                graph_type = st.selectbox(
                    "Select Graph Type",
                    ["Line Chart", "Bar Chart", "Scatter Plot", "Histogram", "Box Plot"]
                )

            with c2:
                x_col = st.selectbox("Select X-axis", all_cols)

            y_col = None
            with c3:
                if graph_type in ["Line Chart", "Bar Chart", "Scatter Plot", "Box Plot"]:
                    y_options = [col for col in numeric_cols if col != x_col] if x_col in numeric_cols else numeric_cols
                    if y_options:
                        y_col = st.selectbox("Select Y-axis", y_options)
                    else:
                        st.warning("No suitable numeric column found for Y-axis.")

            if st.button("Generate Graph"):
                fig = None

                if graph_type == "Line Chart" and y_col:
                    fig = px.line(
                        upload_df,
                        x=x_col,
                        y=y_col,
                        title=f"{y_col} vs {x_col}",
                        template="plotly_dark"
                    )

                elif graph_type == "Bar Chart" and y_col:
                    fig = px.bar(
                        upload_df,
                        x=x_col,
                        y=y_col,
                        title=f"{y_col} vs {x_col}",
                        template="plotly_dark"
                    )

                elif graph_type == "Scatter Plot" and y_col:
                    fig = px.scatter(
                        upload_df,
                        x=x_col,
                        y=y_col,
                        title=f"{y_col} vs {x_col}",
                        template="plotly_dark"
                    )

                elif graph_type == "Histogram":
                    if x_col in upload_df.columns:
                        fig = px.histogram(
                            upload_df,
                            x=x_col,
                            title=f"Histogram of {x_col}",
                            template="plotly_dark"
                        )

                elif graph_type == "Box Plot" and y_col:
                    fig = px.box(
                        upload_df,
                        x=x_col,
                        y=y_col,
                        title=f"{y_col} by {x_col}",
                        template="plotly_dark"
                    )

                if fig is not None:
                    fig.update_layout(
                        height=500,
                        paper_bgcolor="#0f172a",
                        plot_bgcolor="#0f172a"
                    )
                    st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("Uploaded CSV must contain at least 2 columns.")

        st.write("### Statistical Summary")
        st.dataframe(upload_df.describe(include="all"), use_container_width=True)

    except Exception as e:
        st.error(f"Error reading file: {e}")

st.markdown('</div>', unsafe_allow_html=True)