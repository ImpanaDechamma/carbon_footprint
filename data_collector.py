"""
Simulates live server telemetry for servers across multiple countries
and writes readings to MongoDB every 5 minutes.
    python data_collector.py
"""
import time
import random
from datetime import datetime
from utils import calculate_energy, calculate_carbon, get_emission_factor
from db import ensure_timeseries, insert_reading

# One server per country — extend or reduce as needed
SERVERS = {
    "S-USA"  : "USA",
    "S-EU"   : "EU (Average)",
    "S-IND"  : "India",
    "S-CHN"  : "China",
    "S-DEU"  : "Germany",
    "S-GBR"  : "UK",
    "S-FRA"  : "France",
    "S-AUS"  : "Australia",
    "S-CAN"  : "Canada",
    "S-BRA"  : "Brazil",
    "S-JPN"  : "Japan",
    "S-KOR"  : "South Korea",
    "S-RUS"  : "Russia",
    "S-ZAF"  : "South Africa",
}

# Emission factors aligned with dashboard COUNTRY_EMISSION_FACTORS
EMISSION_FACTORS = {
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
}

INTERVAL_SECONDS = 300          # 5 minutes
TIME_DIFF_HOURS  = INTERVAL_SECONDS / 3600


def collect_and_store():
    ts = datetime.utcnow()
    for server_id, country in SERVERS.items():
        power_watts     = round(random.uniform(75, 180), 1)
        energy_kwh      = calculate_energy(power_watts, TIME_DIFF_HOURS)
        emission_factor = EMISSION_FACTORS.get(country, 0.5)
        carbon_emission = round(energy_kwh * emission_factor, 6)

        insert_reading(
            server_id       = server_id,
            region          = country,
            power_watts     = power_watts,
            time_diff_hours = round(TIME_DIFF_HOURS, 6),
            energy_kwh      = energy_kwh,
            emission_factor = emission_factor,
            carbon_emission = carbon_emission,
            timestamp       = ts
        )
        print(f"[{ts}] {server_id:8s} ({country:15s}) | "
              f"{power_watts:6.1f}W | {energy_kwh:.6f} kWh | "
              f"{carbon_emission:.6f} kg CO2")


if __name__ == "__main__":
    ensure_timeseries()
    print("▶ Data collector started — writing every 5 minutes...\n")
    while True:
        collect_and_store()
        print("-" * 70)
        time.sleep(INTERVAL_SECONDS)
