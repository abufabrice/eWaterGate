import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

st.set_page_config(page_title="💧 RO Savings Calculator", page_icon="💧", layout="centered")

# --- Header Image and Title
st.markdown("""
    <div style='text-align: center;'>
        <img src='https://i.imgur.com/8fFJhB2.png' width='180'>
        <h1 style='color: #1f77b4;'>RO System Cost Savings Simulator</h1>
        <h4 style='color: #3399cc;'>Purify tap water and save money sustainably</h4>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- Custom Blue Styling
st.markdown("""
<style>
    .stSlider > div > div > div {
        background: #1f77b4;
    }
    .stNumberInput > div > input {
        border: 1px solid #1f77b4;
    }
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- User Inputs
st.header("1️⃣ Enter Your Household Characteristics")

V_daily = st.number_input("💧 Daily water consumption (liters)", min_value=1.0, value=5.0, step=0.5)
D = st.slider("📅 Number of days to simulate", 30, 365, 365)
C_bottled = st.number_input("🧴 Cost of bottled water per liter (XAF)", min_value=10.0, value=150.0)
C_system = st.number_input("🔧 One-time cost of RO system (XAF)", min_value=10000.0, value=75000.0)

st.subheader("🔁 Filter Cartridge Information")
cartridge_data = [
    {"name": "Sediment Filter", "cost": 5000, "capacity": 3000},
    {"name": "Carbon Filter", "cost": 7000, "capacity": 6000},
    {"name": "RO Membrane", "cost": 15000, "capacity": 12000}
]

cartridges = []
for cart in cartridge_data:
    cost = st.number_input(f"💸 {cart['name']} - Cost (XAF)", min_value=1000.0, value=float(cart['cost']))
    capacity = st.number_input(f"📦 {cart['name']} - Capacity (liters)", min_value=100.0, value=float(cart['capacity']))
    cartridges.append({"name": cart['name'], "cost": cost, "capacity": capacity})

# --- Calculation Logic
def calculate(V_daily, D, C_bottled, C_system, cartridges):
    V_total = V_daily * D
    C_bottled_total = V_total * C_bottled

    cart_rows = []
    total_cart_cost = 0
    for cart in cartridges:
        replacements = np.ceil(V_total / cart['capacity'])
        cost = replacements * cart['cost']
        total_cart_cost += cost
        cart_rows.append([cart['name'], int(replacements), cost])

    C_RO_total = C_system + total_cart_cost
    savings = C_bottled_total - C_RO_total

    return V_total, C_bottled_total, C_RO_total, savings, cart_rows

# --- Output Section
st.header("📊 2️⃣ Simulation Results")

if st.button("💧 Simulate Savings"):
    V_total, bottled_cost, ro_cost, savings, cart_rows = calculate(V_daily, D, C_bottled, C_system, cartridges)

    st.metric("💦 Total Volume Filtered (liters)", f"{V_total:.0f} L")
    st.metric("🧴 Cost of Bottled Water", f"{bottled_cost:,.0f} XAF")
    st.metric("🔧 Cost of RO System (incl. filters)", f"{ro_cost:,.0f} XAF")
    st.metric("✅ Net Savings", f"{savings:,.0f} XAF")

    st.subheader("🧾 Cartridge Replacement Breakdown")
    df = pd.DataFrame(cart_rows, columns=["Cartridge", "Replacements", "Total Cost (XAF)"])
    st.dataframe(df, use_container_width=True)

    # --- Sensitivity Chart
    st.subheader("📈 3️⃣ Sensitivity Analysis: Daily Water Usage vs. Savings")
    V_range = np.linspace(1, 20, 100)
    savings_curve = []
    for V in V_range:
        _, _, _, s, _ = calculate(V, D, C_bottled, C_system, cartridges)
        savings_curve.append(s)

    fig, ax = plt.subplots()
    ax.plot(V_range, savings_curve, label="Net Savings", color="#1f77b4")
    ax.set_xlabel("Daily Water Usage (L)")
    ax.set_ylabel("Savings (XAF)")
    ax.set_title("Sensitivity of Savings to Daily Usage")
    ax.grid(True)
    st.pyplot(fig)

    # --- Break-even Estimation
    st.subheader("📍 4️⃣ Estimated Break-even Point")
    if savings > 0:
        try:
            t = C_system / (V_daily * C_bottled - sum([cart['cost'] / cart['capacity'] for cart in cartridges]) * V_daily)
            st.success(f"Break-even point: {int(np.ceil(t))} days")
        except ZeroDivisionError:
            st.warning("Unable to compute break-even point (division by zero).")
    else:
        st.warning("No savings with current settings. Try adjusting usage or costs.")
