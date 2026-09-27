import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import streamlit.components.v1 as components

st.set_page_config(
    page_title="RD Strength", 
    page_icon="app-icon.png"
)

components.html(
    """
    <script>
        const doc = window.parent.document;
        let link = doc.querySelector("link[rel='apple-touch-icon']");
        if (!link) {
            link = doc.createElement('link');
            link.rel = 'apple-touch-icon';
            doc.head.appendChild(link);
        }
       
        link.href = 'https://raw.githubusercontent.com/rdobre59/rd-strength/main/app-icon.png';
    </script>
    """,
    height=0
)

st.markdown(
    """
    <div style="text-align: center; padding-bottom: 20px;">
        <h1 style="color: white; font-size: 3.2rem; font-weight: 800; margin-bottom: 5px; letter-spacing: 2px;">RD STRENGTH</h1>
        <div style="height: 5px; width: 120px; margin: 0 auto; background: linear-gradient(90deg, rgba(54, 162, 235, 1) 0%, rgba(255, 159, 64, 1) 50%, rgba(75, 192, 192, 1) 100%); border-radius: 5px;"></div>
    </div>
    """, 
    unsafe_allow_html=True
)



conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = st.secrets["sheet_url"]

try:
    # Read both the Bodyweight tab and the main Workout tab
    bw_df = conn.read(spreadsheet=SHEET_URL, worksheet="Bodyweight", usecols=[0, 1], ttl=0).dropna(how="all")
    workout_df = conn.read(spreadsheet=SHEET_URL, usecols=list(range(7)), ttl=0).dropna(how="all")
    
    st.subheader("Body Mass Tracking")
    
    with st.expander("Log Today's Weight", expanded=True):
        with st.form("bw_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                log_date = st.date_input("Date", date.today())
            with col2:
                weight_val = st.number_input("Weight (kg)", min_value=40.0, max_value=150.0, value=85.0, step=0.1, format="%.1f")
                
            submitted = st.form_submit_button("Save to Cloud")
            
            if submitted:
                new_entry = pd.DataFrame([{"Date": str(log_date), "Bodyweight (kg)": weight_val}])
                updated_bw = pd.concat([bw_df, new_entry], ignore_index=True)
                updated_bw = updated_bw.sort_values(by="Date")
                
                conn.update(spreadsheet=SHEET_URL, worksheet="Bodyweight", data=updated_bw)
                st.success("Bodyweight logged successfully!")
                st.rerun()

    st.divider()

    if not bw_df.empty:
        # Process and plot Bodyweight
        bw_df["Date"] = pd.to_datetime(bw_df["Date"])
        bw_chart_data = bw_df.set_index("Date")
        
        st.markdown("### Bodyweight Trend")
        fig_bw = px.line(
            bw_df, 
            x="Date", 
            y="Bodyweight (kg)", 
            markers=True, 
            text="Bodyweight (kg)"
        )
        fig_bw.update_traces(textposition="top center")
        fig_bw.update_xaxes(dtick=86400000, tickformat="%b %d, %Y")
        st.plotly_chart(fig_bw, use_container_width=True)
        current_weight = bw_chart_data.iloc[-1]["Bodyweight (kg)"]
        st.caption(f"**Latest recorded weight:** {current_weight} kg")
        
        # Process and plot Volume underneath if workout data exists
        if not workout_df.empty:
            workout_df["Date"] = pd.to_datetime(workout_df["Date"])
            workout_df["Weight (kg)"] = pd.to_numeric(workout_df["Weight (kg)"], errors='coerce').fillna(0)
            workout_df["Reps"] = pd.to_numeric(workout_df["Reps"], errors='coerce').fillna(0)
            
            # Calculate total volume per set
            workout_df["Volume (kg)"] = workout_df["Weight (kg)"] * workout_df["Reps"]
            
            # Group by Week (Monday start)
            weekly_volume = workout_df.groupby(pd.Grouper(key="Date", freq="W-MON"))["Volume (kg)"].sum().reset_index()
            weekly_volume = weekly_volume[weekly_volume["Volume (kg)"] > 0].set_index("Date")
            
            st.divider()
            st.markdown("### Correlated Weekly Volume")
            st.bar_chart(weekly_volume["Volume (kg)"])
            st.caption("Compare your weekly lifting workload against your body mass trend.")
            
    else:
        st.info("No bodyweight data logged yet. Add your first entry above.")

except Exception as e:
    st.error(f"Error loading data. Ensure the 'Bodyweight' tab is created. Details: {e}")