import streamlit as st
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI
import pandas as pd

# Streamlit UI
st.set_page_config(page_title="Rankine Cycle Simulator", layout="centered")
st.title("♨️ Rankine Cycle Thermodynamic Simulator")

st.sidebar.header("Enter Cycle Parameters")

P_boiler = st.sidebar.slider("Boiler Pressure [MPa]", 1.0, 25.0, 8.0, step=0.5) * 1e6
P_condenser = st.sidebar.slider("Condenser Pressure [kPa]", 5.0, 50.0, 10.0, step=1.0) * 1e3
T_boiler = st.sidebar.slider("Boiler Temperature [°C]", 300, 600, 500, step=10) + 273.15
fluid = "Water"

# Simulation
if st.sidebar.button("Run Simulation 🚀"):
    try:
        # State points
        h1 = PropsSI('H', 'P', P_boiler, 'T', T_boiler, fluid)
        s1 = PropsSI('S', 'P', P_boiler, 'T', T_boiler, fluid)

        h2 = PropsSI('H', 'P', P_condenser, 'S', s1, fluid)
        T2 = PropsSI('T', 'P', P_condenser, 'H', h2, fluid)
        s2 = PropsSI('S', 'P', P_condenser, 'H', h2, fluid)

        h3 = PropsSI('H', 'P', P_condenser, 'Q', 0, fluid)
        s3 = PropsSI('S', 'P', P_condenser, 'Q', 0, fluid)
        T3 = PropsSI('T', 'P', P_condenser, 'Q', 0, fluid)

        h4 = PropsSI('H', 'P', P_boiler, 'S', s3, fluid)
        T4 = PropsSI('T', 'P', P_boiler, 'H', h4, fluid)
        s4 = PropsSI('S', 'P', P_boiler, 'H', h4, fluid)

        # Work & Efficiency
        W_turbine = h1 - h2
        W_pump = h4 - h3
        Qin = h1 - h4
        efficiency = (W_turbine - W_pump) / Qin * 100

        # Display results
        data = {
            "State": ["1-Turbine Inlet", "2-Turbine Exit", "3-Pump Inlet", "4-Pump Exit"],
            "Pressure (MPa)": [P_boiler/1e6, P_condenser/1e6, P_condenser/1e6, P_boiler/1e6],
            "Temperature (°C)": [T_boiler-273.15, T2-273.15, T3-273.15, T4-273.15],
            "Enthalpy (kJ/kg)": [h1/1000, h2/1000, h3/1000, h4/1000],
            "Entropy (kJ/kg·K)": [s1/1000, s2/1000, s3/1000, s4/1000]
        }
        df = pd.DataFrame(data)

        st.subheader("Cycle State Data")
        st.dataframe(df.style.format(precision=3), use_container_width=True)

        st.success(f"🌡️ Thermal Efficiency: **{efficiency:.2f}%**")

        # T-s Diagram
        T_vals = [T_boiler, T2, T3, T4, T_boiler]
        s_vals = [s1, s2, s3, s4, s1]
        fig1, ax1 = plt.subplots()
        ax1.plot([s/1000 for s in s_vals], [T-273.15 for T in T_vals], marker='o')
        for i, txt in enumerate(data["State"]):
            ax1.annotate(txt, (s_vals[i]/1000, T_vals[i]-273.15))
        ax1.set_title("T-s Diagram (Rankine Cycle)")
        ax1.set_xlabel("Entropy (kJ/kg·K)")
        ax1.set_ylabel("Temperature (°C)")
        ax1.grid(True)
        st.pyplot(fig1)

        # h-s Diagram
        h_vals = [h1, h2, h3, h4, h1]
        fig2, ax2 = plt.subplots()
        ax2.plot([s/1000 for s in s_vals], [h/1000 for h in h_vals], marker='o')
        for i, txt in enumerate(data["State"]):
            ax2.annotate(txt, (s_vals[i]/1000, h_vals[i]/1000))
        ax2.set_title("h-s Diagram (Rankine Cycle)")
        ax2.set_xlabel("Entropy (kJ/kg·K)")
        ax2.set_ylabel("Enthalpy (kJ/kg)")
        ax2.grid(True)
        st.pyplot(fig2)

    except Exception as e:
        st.error(f"❌ Error during simulation: {e}")
else:
    st.info("👈 Set values and click 'Run Simulation' to begin.")
