# RD STRENGTH 

> A streamlined, personal workout tracker built with Python and Streamlit, optimized as a Progressive Web App (PWA) for iOS.

## Overview
RD Strength is a lightweight fitness logging application designed to replace spreadsheet tracking. It provides a mobile-friendly interface for loading predefined workout templates, logging sets and repetitions on the fly, and visualizing strength progression over time. 

## Features
* **Dynamic Templates:** Instantly load customized Arnold and Push-Pull-Legs (PPL) splits.
* **Interactive Logging:** An editable, Excel-like data grid allows for rapid input of weight and reps for individual sets.
* **Automated Data Storage:** Workouts are saved locally to a `workout_history.csv` file with exact date and time stamps to prevent session overlapping.
* **Smart History Filtering:** Past workouts are grouped into collapsible accordions by date and session name for a clean UI.
* **Visual Progress Tracking:** Automatically plots the maximum weight lifted per exercise on a chronological line chart to ensure progressive overload.
* **Custom UI Theme:** Features a custom dark-mode aesthetic with automatic muscle-group color coordination (Blue for Chest/Back, Orange for Arms/Shoulders, Mint for Legs).

## Technology Stack
* **Language:** Python
* **Frontend/Framework:** Streamlit
* **Data Handling:** Pandas
* **Deployment:** Streamlit Community Cloud

## File Structure
* `Home.py`: The main logging interface and template loader.
* `pages/History.py`: The workout log viewer and progress visualization chart.
* `.streamlit/config.toml`: Custom theme configurations for the dark gray UI.
* `requirements.txt`: Cloud deployment dependencies.
* `workout_history.csv`: The local database file generated upon the first saved workout.
