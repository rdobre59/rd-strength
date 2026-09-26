import streamlit as st
import pandas as pd
import os

st.title("Workout History")

# Muscle Group Classifications for Colors
CHEST_BACK = ["Bench Press", "Incline Dumbbell Press", "Lat Pulldown", "Barbell Row", "Pull-ups", "Incline Chest Press", "Wide Pulldown", "Low Row", "Low Fly"]
ARMS_SHOULDERS = ["Overhead Press", "Lateral Raises", "Bicep Curls", "Tricep Extensions", "Tricep Extensions Single", "Cuff Shoulder Fly", "Overhead Tricep Extension", "Incline Drag Curl", "Rear Delt Fly", "Hammer Curl", "Tricep Pushdowns", "Face Pulls"]
LEGS = ["Squats", "Leg Press", "Romanian Deadlifts", "Calf Raises", "Abductors", "Quad extension", "Sissy Squat Hack", "Calf Press", "Ham Curl", "Adductors", "Single Leg Hyperextension", "Leg Extensions", "Hamstring Curls"]

def get_row_color(row):
    ex = row['Exercise']
    if ex in CHEST_BACK:
        return ['background-color: #19334d'] * len(row) # Dark Blue
    elif ex in ARMS_SHOULDERS:
        return ['background-color: #4d3319'] * len(row) # Dark Orange
    elif ex in LEGS:
        return ['background-color: #194d33'] * len(row) # Dark Mint
    return [''] * len(row)

if os.path.isfile("workout_history.csv"):
    df = pd.read_csv("workout_history.csv")
    
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
            
            # Apply the colors to the history tables
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