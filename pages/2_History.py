import streamlit as st
import pandas as pd
import json
from streamlit_gsheets import GSheetsConnection

st.markdown(
    """
    <div style="text-align: center; padding-bottom: 20px;">
        <h1 style="color: white; font-size: 3.2rem; font-weight: 800; margin-bottom: 5px; letter-spacing: 2px;">RD STRENGTH</h1>
        <div style="height: 5px; width: 120px; margin: 0 auto; background: linear-gradient(90deg, rgba(54, 162, 235, 1) 0%, rgba(255, 159, 64, 1) 50%, rgba(75, 192, 192, 1) 100%); border-radius: 5px;"></div>
    </div>
    """, 
    unsafe_allow_html=True
)

CHEST_BACK = ["Bench Press", "Incline Dumbbell Press", "Lat Pulldown", "Barbell Row", "Pull-ups", "Incline Chest Press", "Wide Pulldown", "Low Row"]
ARMS_SHOULDERS = ["Overhead Press", "Lateral Raises", "Bicep Curls", "Tricep Extensions", "Tricep Extensions Single", "Cuff Shoulder Fly", "Low Fly", "Overhead Tricep Extension", "Incline Drag Curl", "Rear Delt Fly", "Hammer Curl", "Tricep Pushdowns", "Face Pulls"]
LEGS = ["Squats", "Leg Press", "Romanian Deadlifts", "Calf Raises", "Abductors", "Quad extension", "Sissy Squat Hack", "Calf Press", "Ham Curl", "Adductors", "Single Leg Hyperextension", "Leg Extensions", "Hamstring Curls"]

def get_row_color(row):
    ex = row['Exercise']
    if ex in CHEST_BACK:
        return ['background-color: #19334d'] * len(row)
    elif ex in ARMS_SHOULDERS:
        return ['background-color: #4d3319'] * len(row)
    elif ex in LEGS:
        return ['background-color: #194d33'] * len(row)
    return [''] * len(row)

# --- GOOGLE SHEETS CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Pull the secure URL from Streamlit Secrets
SHEET_URL = st.secrets["sheet_url"]
# --------------------------------

try:
    df = conn.read(spreadsheet=SHEET_URL, usecols=list(range(7)), ttl=0)
    df = df.dropna(how="all")
    
    if not df.empty:
        if "Time" not in df.columns:
            df["Time"] = ""
        else:
            df["Time"] = df["Time"].fillna("")
            
        df = df.sort_values(by=["Date", "Time"], ascending=[False, False])
        
        st.subheader("Past Workouts")
        
        unique_workouts = df[['Date', 'Time', 'Workout Name']].drop_duplicates()
        
        for index, row in unique_workouts.iterrows():
            date_str = row['Date']
            time_str = row['Time']
            workout_str = row['Workout Name']
            
            time_display = f" ({time_str})" if time_str != "" else ""
            
            with st.expander(f"{workout_str}  •  {date_str}{time_display}"):
                workout_data = df[(df['Date'] == date_str) & (df['Time'] == time_str) & (df['Workout Name'] == workout_str)]
                display_data = workout_data.drop(columns=['Date', 'Workout Name', 'Time'])
                
                styled_display = display_data.style.apply(get_row_color, axis=1).format({"Weight (kg)": "{:.1f}"})
                st.dataframe(styled_display, use_container_width=True, hide_index=True)
                
        total_workouts = df["Date"].nunique()
        st.caption(f"Total workout days logged: {total_workouts}")
        
        st.divider()

        st.subheader("Progress Tracker")
        
        unique_exercises = df["Exercise"].unique()
        selected_exercise = st.selectbox("Select an exercise to graph:", unique_exercises)
        
        exercise_data = df[df["Exercise"] == selected_exercise]
        chart_data = exercise_data.groupby("Date")["Weight (kg)"].max().reset_index()
        chart_data = chart_data.sort_values(by="Date", ascending=True)
        
        if not chart_data.empty:
            st.line_chart(chart_data, x="Date", y="Weight (kg)")
    else:
        st.info("No workout history found yet. Go log your first session!")
except Exception as e:
    st.info("No workout history found yet. Go log your first session!")