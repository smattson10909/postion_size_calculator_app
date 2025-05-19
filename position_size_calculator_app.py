import streamlit as st
import math
from decimal import Decimal
from PIL import Image

# Contract dictionary: symbol -> (tick_size, tick_value)
contracts = {
    "NQ (E-mini Nasdaq 100)": (0.25, 5.00),
    "ES (E-mini S&P 500)": (0.25, 12.50),
    "YM (E-mini Dow)": (1.0, 5.00),
    "RTY (E-mini Russell 2000)": (0.10, 5.00),
    "CL (Crude Oil)": (0.01, 10.00),
    "NG (Natural Gas)": (0.001, 10.00),
    "HO (Heating Oil)": (0.0001, 4.20),
    "RB (RBOB Gasoline)": (0.0001, 4.20),
    "GC (Gold)": (0.10, 10.00),
    "SI (Silver)": (0.005, 25.00),
    "PA (Palladium)": (0.10, 5.00),
    "HG (Copper)": (0.0005, 12.50),
    "PL (Platinum)": (0.10, 5.00),
    "ZB (30-Year T-Bond)": (0.015625, 31.25),
    "ZN (10-Year T-Note)": (0.015625, 15.625),
    "ZF (5-Year T-Note)": (0.0078125, 7.8125),
    "ZT (2-Year T-Note)": (0.0078125, 7.8125),
    "6A (Australian Dollar)": (0.0001, 10.00),
    "6B (British Pound)": (0.0001, 6.25),
    "6C (Canadian Dollar)": (0.0001, 10.00),
    "6J (Japanese Yen)": (0.000001, 12.50),
    "6E (Euro)": (0.00005, 6.25),
    "6S (Swiss Franc)": (0.0001, 12.50),
    "6N (New Zealand Dollar)": (0.0001, 10.00),
    "CC (Cocoa)": (1.0, 10.00),
    "KC (Coffee)": (0.05, 18.75),
    "CT (Cotton)": (0.01, 500.00),
    "OJ (Orange Juice)": (0.0005, 7.50),
    "LBR (Lumber)": (0.10, 11.00),
    "SB (Sugar)": (0.0001, 11.20),
    "LE (Live Cattle)": (0.025, 400.00),
    "HE (Lean Hogs)": (0.025, 400.00),
    "ZC (Corn)": (0.25, 12.50),
    "ZO (Oats)": (0.25, 12.50),
    "ZW (Wheat)": (0.25, 12.50),
    "ZS (Soybeans)": (0.25, 12.50),
    "ZM (Soybean Meal)": (0.1, 10.00),
    "ZL (Soybean Oil)": (0.01, 6.00),
    "BTC (Bitcoin Futures)": (5.0, 25.00),
    "ETH (Ethereum Futures)": (0.10, 5.00)
}

logo = Image.open("crowded_market_report_logo.jpeg")
st.image(logo, width=250) 

st.title("Futures Position Size Calculator")

# Select contract
selected_contract = st.selectbox("Select Futures Contract", list(contracts.keys()))
tick_size, tick_value = contracts[selected_contract]
st.write(f"**Tick Size**: {tick_size} | **Tick Value**: ${tick_value}")

# Get decimal precision
tick_decimal_places = abs(Decimal(str(tick_size)).as_tuple().exponent)
decimal_format = f"%.{tick_decimal_places}f"

# Helper to round to nearest tick
def round_to_tick(value, tick):
    return round(round(value / tick) * tick, 10)

# Keys
entry_key = "entry_price_input"
stop_key = "stop_price_input"

# Set default values if not yet in session
if entry_key not in st.session_state:
    st.session_state[entry_key] = 0.0
if stop_key not in st.session_state:
    st.session_state[stop_key] = 0.0

# Round both values to the nearest tick
corrected_entry = round_to_tick(st.session_state[entry_key], tick_size)
corrected_stop = round_to_tick(st.session_state[stop_key], tick_size)

# If either one changed, update state and rerun
if corrected_entry != st.session_state[entry_key] or corrected_stop != st.session_state[stop_key]:
    st.session_state[entry_key] = corrected_entry
    st.session_state[stop_key] = corrected_stop
    st.rerun()

# Now render widgets using ONLY session keys (no value=)
entry_price = st.number_input("Entry Price", step=tick_size, format=decimal_format, key=entry_key)
stop_price = st.number_input("Stop Price", step=tick_size, format=decimal_format, key=stop_key)

# Use the corrected inputs for calculation
rounded_entry = round_to_tick(st.session_state[entry_key], tick_size)
rounded_stop = round_to_tick(st.session_state[stop_key], tick_size)

# Remaining inputs
aum = st.number_input("Account Size (AUM in $)", value=0.0, step=100.0)
risk_percent = st.number_input("Risk per Trade (%)", min_value=0.0, max_value=100.0, value=1.0, step=0.1)

if st.button("🔄 Reset Entry Prices"):
    st.session_state.clear()
    st.rerun()

# Calculation trigger
if st.button("Calculate Position Size"):
    if rounded_entry == 0 or rounded_stop == 0 or aum == 0 or risk_percent == 0:
        st.warning("Please fill in all inputs to calculate.")
    else:
        risk_per_trade = (risk_percent / 100) * aum
        stop_distance_ticks = abs(rounded_entry - rounded_stop) / tick_size
        raw_position_size = risk_per_trade / (tick_value * stop_distance_ticks)
        rounded_position_size = math.floor(raw_position_size)

        if rounded_position_size < 1:
            st.error("🚫 Your stop is too wide relative to your risk amount. No position can be taken with this setup. Consider trading micros if they are available.")

        st.success("✅ Position Size Calculated!")
        st.write(f"**Risk per Trade**: ${risk_per_trade:.2f}")
        st.write(f"**Stop Distance**: {stop_distance_ticks:.2f} ticks")
        st.write(f"**Calculated Position Size**: {raw_position_size:.2f} contracts")
        st.write(f"**Recommended Position Size**: {rounded_position_size} contracts (rounded down)")
