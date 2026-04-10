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

def calculate_carbon(energy_kwh, region="India"):
    """Return carbon emission in kg CO2 given energy in kWh and region."""
    factor = EMISSION_FACTORS.get(region, 0.5)
    return round(energy_kwh * factor, 6)

def calculate_energy(power_watts, time_diff_hours=0.083333):
    """Convert power (W) and time (hours) to energy (kWh)."""
    return round((power_watts * time_diff_hours) / 1000, 6)

def get_emission_factor(region):
    """Return emission factor for a given region/country."""
    return EMISSION_FACTORS.get(region, 0.5)
