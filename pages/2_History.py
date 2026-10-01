import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime
from zoneinfo import ZoneInfo

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

CHEST_BACK = ["Bench Press", "Incline Dumbbell Press", "Lat Pulldown", "Barbell Row", "Pull-ups", "Incline Chest Press", "Wide Pulldown", "Low Row", "Mid Fly"]
ARMS_SHOULDERS = ["Shoulder Press", "Lateral Raises", "Bicep Curls", "Tricep Extensions", "Tricep Extensions Sg", "Cuff Shoulder Fly", "OH Tricep Extension", "Incline Drag Curl", "Rear Delt Fly", "Hammer Curl", "Tricep Pushdowns", "Face Pulls"]
LEGS = ["Squats", "Leg Press", "Romanian Deadlifts", "Calf Raises", "Abductors", "Quad extension", "Sissy Squat Hack", "Calf Press", "Ham Curl", "Adductors", "Single Leg HX", "Leg Extensions", "Hamstring Curls"]

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
SHEET_URL = st.secrets["sheet_url"]

try:
    df = conn.read(spreadsheet=SHEET_URL, usecols=list(range(7)), ttl=0)
    df = df.dropna(how="all")
    
    if not df.empty:
        if "Time" not in df.columns:
            df["Time"] = ""
        else:
            df["Time"] = df["Time"].fillna("")
            
        df = df.sort_values(by=["Date", "Time"], ascending=[False, False])
        
        st.subheader("Past Workouts & Live Corrections")
        st.caption("Expand a session below to view, edit weights/reps, or save changes directly to the cloud.")
        
        unique_workouts = df[['Date', 'Time', 'Workout Name']].drop_duplicates()
        
        # We store the updated master dataframe across interactions if needed
        all_sessions_dfs = []
        
        for index, row in unique_workouts.iterrows():
            date_str = row['Date']
            time_str = row['Time']
            workout_str = row['Workout Name']
            
            time_display = f" ({time_str})" if time_str != "" else ""
            
            with st.expander(f"{workout_str}  •  {date_str}{time_display}"):
                # Isolate this specific session's rows
                session_mask = (df['Date'] == date_str) & (df['Time'] == time_str) & (df['Workout Name'] == workout_str)
                workout_data = df[session_mask].copy()
                
                # We want the data editor to show clean user-facing columns
                editable_data = workout_data.drop(columns=['Date', 'Workout Name', 'Time'])
                
                # Calculate dynamic height to stop vertical scrolling 
                # (approx 35px per row + header + buffer for 1 new row)
                dynamic_height = (len(editable_data) + 2) * 35 + 10
                
                edited_sub_df = st.data_editor(
                editable_data,
                use_container_width=False, 
                hide_index=True,
                height=dynamic_height,
                column_config={
                    "Exercise": st.column_config.TextColumn("Exercise", width=145),
                    "Weight (kg)": st.column_config.NumberColumn("W (kg)", width=65, format="%.1f"),
                    "Set": st.column_config.NumberColumn("Set", width=45, format="%d"),
                    "Reps": st.column_config.NumberColumn("Reps", width=55, format="%d")
                }
            )
                
                # Reattach the hidden metadata columns back to the edited rows
                edited_sub_df["Date"] = date_str
                edited_sub_df["Time"] = time_str
                edited_sub_df["Workout Name"] = workout_str
                
                all_sessions_dfs.append(edited_sub_df)
                
                if st.button("Save Changes to This Session", key=f"save_{date_str}_{time_str}_{workout_str}"):
                    with st.spinner("Updating Google Sheet..."):
                        # Rebuild the full master dataframe by replacing this session's old rows with the new ones
                        other_sessions_df = df[~session_mask]
                        final_master_df = pd.concat([other_sessions_df, edited_sub_df], ignore_index=True)
                        
                        conn.update(spreadsheet=SHEET_URL, data=final_master_df)
                    st.success("Session updated successfully in the cloud!")
                    st.rerun()
                    
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
            fig_prog = px.line(
            chart_data, 
            x="Date", 
            y="Weight (kg)", 
            markers=True, 
            text="Weight (kg)"
                            )
            fig_prog.update_traces(textposition="top center")
            fig_prog.update_xaxes(dtick=86400000, tickformat="%b %d, %Y")
            st.plotly_chart(fig_prog, use_container_width=True)
        else:
                st.info("No workout history found yet. Go log your first session!")
except Exception as e:
    st.info("No workout history found yet. Go log your first session!")