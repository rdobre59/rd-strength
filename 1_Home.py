import streamlit as st
import pandas as pd
import datetime
import json
from streamlit_gsheets import GSheetsConnection
import plotly.express as px

st.set_page_config(
    page_title="RD Strength", 
    page_icon="app_icon.png"
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

# Custom HTML Logo
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

# Pull the secure URL from Streamlit Secrets
SHEET_URL = st.secrets["sheet_url"]
# --------------------------------

TEMPLATES = {
    "Anterior": [("Tricep Extensions Single", 2), ("Cuff Shoulder Fly", 2), ("Low Fly", 2), ("Incline Chest Press", 2), ("Overhead Tricep Extension", 2), ("Abductors", 2), ("Quad extension", 2), ("Sissy Squat Hack", 2)],
    "Posterior": [("Calf Press", 2), ("Wide Pulldown", 2), ("Incline Drag Curl", 2), ("Rear Delt Fly", 2), ("Hammer Curl", 2), ("Low Row", 2), ("Ham Curl", 2), ("Adductors", 2), ("Single Leg Hyperextension", 2)],
    "Arnold: Chest & Back": [("Bench Press", 2), ("Incline Dumbbell Press", 2), ("Lat Pulldown", 2), ("Barbell Row", 2), ("Pull-ups", 2)],
    "Arnold: Shoulders & Arms": [("Overhead Press", 2), ("Lateral Raises", 2), ("Bicep Curls", 2), ("Tricep Extensions", 2)],
    "Arnold: Legs": [("Squats", 2), ("Leg Press", 2), ("Romanian Deadlifts", 2), ("Calf Raises", 2)],
    "PPL: Push": [("Overhead Press", 2), ("Incline Bench Press", 2), ("Lateral Raises", 2), ("Tricep Pushdowns", 2)],
    "PPL: Pull": [("Pull-ups", 2), ("Barbell Row", 2), ("Face Pulls", 2), ("Bicep Curls", 2)],
    "PPL: Legs": [("Squats", 2), ("Leg Extensions", 2), ("Hamstring Curls", 2), ("Calf Raises", 2)],
    "Custom...": []
}

workout_type = st.selectbox("Workout Split", list(TEMPLATES.keys()))

if workout_type == "Custom...":
    workout_name = st.text_input("Enter custom workout name:")
else:
    workout_name = workout_type

if 'workout_log' not in st.session_state:
    st.session_state.workout_log = []

if st.button(f"Load {workout_type} Template"):
    st.session_state.workout_log = []
    for ex, num_sets in TEMPLATES[workout_type]:
        for set_num in range(1, num_sets + 1):
            st.session_state.workout_log.append({
                "Exercise": ex,
                "Set": set_num,
                "Weight (kg)": 0.0,
                "Reps": 0
            })

st.divider()
st.subheader(f"Current Log: {workout_name}")

if len(st.session_state.workout_log) > 0:
    df = pd.DataFrame(st.session_state.workout_log)
    
    edited_df = st.data_editor(
        df, 
        use_container_width=True,
        num_rows="dynamic", 
        hide_index=True,
        column_config={
            "Weight (kg)": st.column_config.NumberColumn("Weight (kg)", format="%.1f")
        }
    )
    
    if st.button("Finish & Save Workout"):
        final_log = edited_df.to_dict('records')
        today = datetime.date.today().strftime("%Y-%m-%d")
        now_time = datetime.datetime.now().strftime("%H:%M:%S") 
        
        for row in final_log:
            row["Date"] = today
            row["Time"] = now_time
            row["Workout Name"] = workout_name

        save_df = pd.DataFrame(final_log)
        
        # Read from Google Sheets, append new data, and update
        with st.spinner("Saving to Google Sheets..."):
            try:
                # ttl=0 forces it to fetch the absolute latest data, ignoring cache
                existing_df = conn.read(spreadsheet=SHEET_URL, usecols=list(range(7)), ttl=0)
                existing_df = existing_df.dropna(how="all") 
                updated_df = pd.concat([existing_df, save_df], ignore_index=True)
            except Exception:
                updated_df = save_df
                
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            
        st.success("Workout permanently saved to the cloud!")
        st.session_state.workout_log = [] 
else:
    st.info("Click the 'Load Template' button to pull up your exercises.")