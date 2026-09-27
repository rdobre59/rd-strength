import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection




st.set_page_config(
    page_title="RD Strength", 
    page_icon="app_icon.png"
)


# Keep the consistent custom header
st.markdown(
    """
    <div style="text-align: center; padding-bottom: 20px;">
        <h1 style="color: white; font-size: 3.2rem; font-weight: 800; margin-bottom: 5px; letter-spacing: 2px;">RD STRENGTH</h1>
        <div style="height: 5px; width: 120px; margin: 0 auto; background: linear-gradient(90deg, rgba(54, 162, 235, 1) 0%, rgba(255, 159, 64, 1) 50%, rgba(75, 192, 192, 1) 100%); border-radius: 5px;"></div>
    </div>
    """, 
    unsafe_allow_html=True
)

# --- GOOGLE SHEETS CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = st.secrets["sheet_url"]

try:
    # Pull data from the cloud
    df = conn.read(spreadsheet=SHEET_URL, usecols=list(range(7)), ttl=0)
    df = df.dropna(how="all")
    
    if not df.empty:
        st.subheader("Volume Analytics")
        st.caption("Total Volume = Weight (kg) × Reps")
        
        # 1. Clean and convert data types
        df["Weight (kg)"] = pd.to_numeric(df["Weight (kg)"], errors='coerce').fillna(0)
        df["Reps"] = pd.to_numeric(df["Reps"], errors='coerce').fillna(0)
        
        # 2. Calculate the actual volume per set
        df["Volume (kg)"] = df["Weight (kg)"] * df["Reps"]
        
        # 3. Parse the Date string into datetime objects for grouping
        df["Date"] = pd.to_datetime(df["Date"])
        df["Year"] = df["Date"].dt.strftime('%Y')
        df["Month"] = df["Date"].dt.strftime('%Y-%m')
        df["Day"] = df["Date"].dt.strftime('%Y-%m-%d')
        
        # Optional Filter: See total overall volume or isolate a specific lift
        exercises = ["Total (All Exercises)"] + list(df["Exercise"].unique())
        selected_ex = st.selectbox("Filter by Exercise:", exercises)
        
        if selected_ex != "Total (All Exercises)":
            df = df[df["Exercise"] == selected_ex]
            
        st.divider()

        # Create tabs for clean mobile navigation
        tab_day, tab_month, tab_year = st.tabs(["Daily", "Monthly", "Yearly"])
        
        with tab_day:
            daily_vol = df.groupby("Day")["Volume (kg)"].sum().reset_index()
            if not daily_vol.empty:
                st.bar_chart(daily_vol.set_index("Day"), y="Volume (kg)")
            else:
                st.info("No data for this selection.")
                
        with tab_month:
            monthly_vol = df.groupby("Month")["Volume (kg)"].sum().reset_index()
            if not monthly_vol.empty:
                st.bar_chart(monthly_vol.set_index("Month"), y="Volume (kg)")
            else:
                st.info("No data for this selection.")
                
        with tab_year:
            yearly_vol = df.groupby("Year")["Volume (kg)"].sum().reset_index()
            if not yearly_vol.empty:
                st.bar_chart(yearly_vol.set_index("Year"), y="Volume (kg)")
            else:
                st.info("No data for this selection.")
                
    else:
        st.info("No workout history found yet. Go log your first session!")
except Exception as e:
    st.info("Unable to load workout history. Ensure your Google Sheet is connected properly.")