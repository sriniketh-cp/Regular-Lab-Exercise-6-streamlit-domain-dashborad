import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Green AI Data Center Telemetry Analytics",
    page_icon="⚡",
    layout="wide"
)


st.sidebar.header("📁 Dataset Input")
uploaded_file = st.sidebar.file_uploader("Upload Telemetry CSV File", type=["csv"])

st.title("⚡ Green AI Data Center Telemetry Portal")
st.caption("Hyperscale digital twin dashboard for workload monitoring and carbon optimization.")

if uploaded_file is None:
    st.info("👈 Please upload your `green_ai_datacenter.csv` file using the sidebar to begin analysis.")
    st.stop()


@st.cache_data
def load_uploaded_data(file):
    df = pd.read_csv(file)
    # Strip whitespace and convert column names to lower case to ensure strict matching
    df.columns = df.columns.str.strip().str.lower()
    return df

df_raw = load_uploaded_data(uploaded_file)


st.sidebar.divider()
st.sidebar.header("🔍 Filter Telemetry Data")

server_types = df_raw["server_type"].dropna().unique().tolist()
selected_servers = st.sidebar.multiselect(
    "Select Server Architecture:",
    options=server_types,
    default=server_types
)

cooling_types = df_raw["cooling_type"].dropna().unique().tolist()
selected_cooling = st.sidebar.multiselect(
    "Select Cooling Technology:",
    options=cooling_types,
    default=cooling_types
)

efficiency_classes = ["All"] + list(df_raw["energy_efficiency_class"].dropna().unique())
selected_class = st.sidebar.selectbox(
    "Select Energy Efficiency Class:",
    options=efficiency_classes
)

min_cpu = float(df_raw["cpu_utilization"].min())
max_cpu = float(df_raw["cpu_utilization"].max())
cpu_range = st.sidebar.slider(
    "CPU Utilization Range (%):", 
    min_value=min_cpu, 
    max_value=max_cpu, 
    value=(min_cpu, max_cpu)
)

min_power = float(df_raw["power_consumption_kw"].min())
max_power = float(df_raw["power_consumption_kw"].max())
power_range = st.sidebar.slider(
    "Power Draw Range (kW):", 
    min_value=min_power, 
    max_value=max_power, 
    value=(min_power, max_power)
)

st.sidebar.divider()
st.sidebar.info("💡 **Tip:** Adjust sidebar controls to dynamically update all KPIs, tables, and charts.")


filtered_df = df_raw[
    (df_raw["server_type"].isin(selected_servers)) &
    (df_raw["cooling_type"].isin(selected_cooling)) &
    (df_raw["cpu_utilization"] >= cpu_range[0]) &
    (df_raw["cpu_utilization"] <= cpu_range[1]) &
    (df_raw["power_consumption_kw"] >= power_range[0]) &
    (df_raw["power_consumption_kw"] <= power_range[1])
]

if selected_class != "All":
    filtered_df = filtered_df[filtered_df["energy_efficiency_class"] == selected_class]


if filtered_df.empty:
    st.warning("⚠️ No telemetry records match your filter criteria. Please adjust sidebar values.")
else:
    tab_overview, tab_analysis, tab_viz, tab_insights = st.tabs([
        "📋 Dataset Overview", 
        "📊 Data Analysis", 
        "📈 Visualizations", 
        "💡 Strategic Insights"
    ])

   
    with tab_overview:
        with st.container():
            st.subheader("📌 Key Performance Indicators (KPIs)")
            
            kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
            
            total_records = len(filtered_df)
            total_power = filtered_df["power_consumption_kw"].sum()
            avg_cpu = filtered_df["cpu_utilization"].mean()
            avg_pue = filtered_df["pue"].mean()
            total_carbon = filtered_df["carbon_emission_kg"].sum()

            kpi1.metric("Total Observations", f"{total_records}")
            kpi2.metric("Total Power Draw", f"{total_power:.1f} kW")
            kpi3.metric("Avg CPU Load", f"{avg_cpu:.1f} %")
            kpi4.metric("Avg PUE Index", f"{avg_pue:.2f}")
            kpi5.metric("Total CO₂ Output", f"{total_carbon:.1f} kg")

        st.divider()

        with st.container():
            st.subheader("📂 Uploaded Telemetry Data Preview")
            st.dataframe(filtered_df.head(10), use_container_width=True)

        with st.expander("🔍 Click to view Dataset Schema & Summary Statistics"):
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                st.write("**Descriptive Statistics**")
                st.dataframe(filtered_df.describe(), use_container_width=True)
            with col_exp2:
                st.write("**Data Types & Non-Null Values**")
                info_df = pd.DataFrame({
                    "Column Name": filtered_df.columns,
                    "Data Type": [str(dtype) for dtype in filtered_df.dtypes],
                    "Non-Null Count": filtered_df.notnull().sum().values
                })
                st.dataframe(info_df, use_container_width=True)

 
    with tab_analysis:
        with st.container():
            st.subheader("📋 Categorical Aggregations & Group-By Operations")
            
            gb_col1, gb_col2 = st.columns(2)

            with gb_col1:
                st.write("**Server Architecture Performance**")
                server_gb = filtered_df.groupby("server_type").agg(
                    nodes_count=("server_type", "count"),
                    avg_power_kw=("power_consumption_kw", "mean"),
                    avg_cpu_pct=("cpu_utilization", "mean")
                ).reset_index()
                st.dataframe(server_gb, use_container_width=True)

            with gb_col2:
                st.write("**Cooling Technology Efficiency**")
                cooling_gb = filtered_df.groupby("cooling_type").agg(
                    nodes_count=("cooling_type", "count"),
                    avg_pue=("pue", "mean"),
                    total_carbon_kg=("carbon_emission_kg", "sum")
                ).reset_index()
                st.dataframe(cooling_gb, use_container_width=True)

        with st.expander("📊 Click to view Cross-Tabulation (Server Type vs Cooling Type)"):
            crosstab_df = pd.crosstab(
                filtered_df["server_type"], 
                filtered_df["cooling_type"], 
                margins=True, 
                margins_name="Total"
            )
            st.dataframe(crosstab_df, use_container_width=True)

  
    with tab_viz:
        st.subheader("📈 Interactive Telemetry Plots")
        
        with st.container():
            viz_col1, viz_col2 = st.columns(2)

            with viz_col1:
                st.markdown("##### A. Server Type Distribution (Bar Chart)")
                fig1, ax1 = plt.subplots(figsize=(6, 4))
                server_counts = filtered_df["server_type"].value_counts()
                ax1.bar(server_counts.index, server_counts.values, color="#2B5B84", edgecolor="black")
                ax1.set_title("Node Count by Server Architecture")
                ax1.set_xlabel("Server Type")
                ax1.set_ylabel("Count")
                ax1.grid(axis="y", linestyle="--", alpha=0.5)
                plt.xticks(rotation=15)
                st.pyplot(fig1)

            with viz_col2:
                st.markdown("##### B. Sequential Metric Trends (Line Chart)")
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                df_sorted = filtered_df.sort_index()
                ax2.plot(df_sorted.index, df_sorted["cpu_utilization"], marker="o", label="CPU Util (%)", color="green")
                ax2.plot(df_sorted.index, df_sorted["power_consumption_kw"], marker="s", label="Power Draw (kW)", color="red")
                ax2.set_title("CPU Load vs Power Draw")
                ax2.set_xlabel("Record Index")
                ax2.set_ylabel("Metrics")
                ax2.legend()
                ax2.grid(True, linestyle="--", alpha=0.5)
                st.pyplot(fig2)

        with st.container():
            st.markdown("##### C. Workload vs. Power Correlation (Scatter Plot)")
            fig3, ax3 = plt.subplots(figsize=(10, 4))
            scatter = ax3.scatter(
                filtered_df["cpu_utilization"], 
                filtered_df["power_consumption_kw"], 
                c=filtered_df["pue"], 
                cmap="YlOrRd", 
                s=filtered_df["carbon_emission_kg"] * 25, 
                edgecolor="black", 
                alpha=0.85
            )
            ax3.set_title("CPU Utilization vs. Power Consumption (Color = PUE, Size = Carbon Emission)")
            ax3.set_xlabel("CPU Utilization (%)")
            ax3.set_ylabel("Power Consumption (kW)")
            ax3.grid(True, linestyle="--", alpha=0.5)
            cbar = plt.colorbar(scatter, ax=ax3)
            cbar.set_label("PUE Index")
            st.pyplot(fig3)

        with st.expander("💡 Click to expand detailed chart interpretations"):
            st.markdown("""
            * **Bar Chart Interpretation**: Identifies dominant hardware profiles. A high concentration of GPU clusters highlights compute-heavy nodes requiring liquid immersion.
            * **Line Chart Interpretation**: Demonstrates load variations across server slots. Spikes indicate unthrottled background workloads.
            * **Scatter Plot Interpretation**: Shows strong linear correlation between CPU workload and power. Large red markers pinpoint low-efficiency nodes emitting disproportionate carbon.
            """)

   
    with tab_insights:
        st.subheader("💡 Sustainability & Infrastructure Recommendations")
        
        ins_col1, ins_col2 = st.columns(2)
        
        with ins_col1:
            st.info("""
            **Cooling Optimization**
            * Direct-to-Chip and Liquid Immersion systems demonstrate PUE values closer to **1.10**, outperforming legacy Air Cooling (**1.45+**).
            * **Action**: Transition high-density GPU clusters to liquid immersion to reduce annual data center PUE by ~0.2.
            """)
            
        with ins_col2:
            st.success("""
            **Carbon Footprint Reduction**
            * Workloads operating above 85% CPU utilization generate over **6.0 kg CO₂** per cycle when tied to inefficient power racks.
            * **Action**: Implement dynamic carbon-aware load balancing to migrate peak compute jobs to eco-friendly racks during off-peak hours.
            """)

        with st.expander("⚠️ View Flagged Critical Anomaly Nodes"):
            anomalies = filtered_df[(filtered_df["pue"] > 1.35) | (filtered_df["cpu_utilization"] > 90.0)]
            if anomalies.empty:
                st.write("No critical anomalies detected under current filter conditions.")
            else:
                st.dataframe(anomalies, use_container_width=True)