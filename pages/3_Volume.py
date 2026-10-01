import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import streamlit.components.v1 as components

# This must be the absolute first Streamlit command
st.set_page_config(
    page_title="RD Strength", 
    page_icon="app-icon.png"
)

# Apple Touch Icon injection
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

st.subheader("Volume Analytics")

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = st.secrets["sheet_url"]

try:
    # Read the first 7 columns (A through G) which includes 'Workout Name'
    workout_df = conn.read(spreadsheet=SHEET_URL, usecols=list(range(7)), ttl=0).dropna(how="all")
    
    if not workout_df.empty and "Workout Name" in workout_df.columns:
        workout_df["Date"] = pd.to_datetime(workout_df["Date"])
        workout_df["Weight (kg)"] = pd.to_numeric(workout_df["Weight (kg)"], errors='coerce').fillna(0.0)
        workout_df["Reps"] = pd.to_numeric(workout_df["Reps"], errors='coerce').fillna(0.0)
        workout_df["Volume (kg)"] = workout_df["Weight (kg)"] * workout_df["Reps"]
        
        # Clean the column strings to prevent mismatches
        workout_df["Workout Name"] = workout_df["Workout Name"].astype(str).str.strip()

        st.divider()
        
        # 1. Filters
        exercise_list = ["All Exercises"] + list(workout_df["Exercise"].dropna().unique())
        selected_exercise = st.selectbox("Filter by Exercise", exercise_list)

        workout_list = ["All Workouts"] + list(workout_df["Workout Name"].dropna().unique())
        selected_workout = st.selectbox("Filter by Workout", workout_list)

        # Apply filters
        filtered_df = workout_df.copy()

        if selected_exercise != "All Exercises":
            filtered_df = filtered_df[filtered_df["Exercise"] == selected_exercise]

        if selected_workout != "All Workouts":
            filtered_df = filtered_df[filtered_df["Workout Name"] == selected_workout]

        st.divider()

        if not filtered_df.empty:
            # Define specific colors for your splits
            split_colors = {
                "Anterior": "#36a2eb",  # Blue
                "Posterior": "#ff6384", # Red
                "Push": "#36a2eb",      
                "Pull": "#ff6384",
                "Legs": "#4bc0c0"       # Mint Green
            }

            tab1, tab2, tab3 = st.tabs(["Daily", "Monthly", "Yearly"])
            
            with tab1:
                # Group by Date AND Workout Name
                daily_vol = filtered_df.groupby(["Date", "Workout Name"])["Volume (kg)"].sum().reset_index()
                daily_vol["Volume (kg)"] = daily_vol["Volume (kg)"].astype(float)
                daily_vol["Volume Label"] = daily_vol["Volume (kg)"].astype(str)
                
                fig_daily = px.bar(
                    daily_vol, 
                    x="Date", 
                    y="Volume (kg)", 
                    color="Workout Name", 
                    color_discrete_map=split_colors,
                    text="Volume Label"
                )
                fig_daily.update_traces(textposition="outside")
                fig_daily.update_xaxes(dtick="86400000", tickformat="%b %d, %Y")
                st.plotly_chart(fig_daily, use_container_width=True)
                
            with tab2:
                monthly_vol = filtered_df.groupby([pd.Grouper(key="Date", freq="ME"), "Workout Name"])["Volume (kg)"].sum().reset_index()
                monthly_vol["Volume (kg)"] = monthly_vol["Volume (kg)"].astype(float)
                monthly_vol["Volume Label"] = monthly_vol["Volume (kg)"].astype(str)
                
                fig_monthly = px.bar(
                    monthly_vol, 
                    x="Date", 
                    y="Volume (kg)", 
                    color="Workout Name",
                    color_discrete_map=split_colors, 
                    text="Volume Label"
                )
                fig_monthly.update_traces(textposition="outside")
                fig_monthly.update_xaxes(dtick="M1", tickformat="%b %Y")
                st.plotly_chart(fig_monthly, use_container_width=True)
                
            with tab3:
                yearly_vol = filtered_df.groupby([pd.Grouper(key="Date", freq="YE"), "Workout Name"])["Volume (kg)"].sum().reset_index()
                yearly_vol["Volume (kg)"] = yearly_vol["Volume (kg)"].astype(float)
                yearly_vol["Year"] = yearly_vol["Date"].dt.year.astype(str)
                yearly_vol["Volume Label"] = yearly_vol["Volume (kg)"].astype(str)
                
                fig_yearly = px.bar(
                    yearly_vol, 
                    x="Year", 
                    y="Volume (kg)", 
                    color="Workout Name",
                    color_discrete_map=split_colors, 
                    text="Volume Label"
                )
                fig_yearly.update_traces(textposition="outside")
                st.plotly_chart(fig_yearly, use_container_width=True)
        else:
            st.info("No volume data found for the selected filters.")
            
    else:
        st.error("Could not find the 'Workout Name' column or the sheet is empty.")

except Exception as e:
    st.error(f"Error loading data: {e}")