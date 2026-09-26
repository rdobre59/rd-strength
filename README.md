# RD STRENGTH 

> A streamlined, personal workout tracker built with Python and Streamlit, optimized as a Progressive Web App (PWA) for iOS.
> 
## Overview
RD Strength is a lightweight fitness logging application designed to replace spreadsheet tracking. It provides a mobile-friendly interface for loading predefined workout templates, logging sets and repetitions on the fly, and visualizing strength progression over time. 

**Data is saved directly to a private Google Sheet**, ensuring your workout history is permanently stored, fully accessible, and safe from cloud server resets.

## Features
* **Dynamic Templates:** Instantly load customized Arnold and Push-Pull-Legs (PPL) splits. The code is fully open so you can easily swap in your own custom routines.
* **Interactive Logging:** An editable, Excel-like data grid allows for rapid input of weight and reps for individual sets.
* **Cloud Database (Google Sheets):** Workouts are saved in real-time to a private Google Sheet you control, ensuring persistent and secure data storage.
* **Smart History Filtering:** Past workouts are grouped into collapsible accordions by date and session name for a clean UI.
* **Visual Progress Tracking:** Automatically plots the maximum weight lifted per exercise on a chronological line chart to ensure progressive overload.
* **Custom UI Theme:** Features a custom dark-mode aesthetic with automatic muscle-group color coordination (Blue for Chest/Back, Orange for Arms/Shoulders, Mint for Legs).

## Technology Stack
* **Language:** Python
* **Frontend/Framework:** Streamlit
* **Data Handling:** Pandas
* **Database/Storage:** Google Sheets API (`st-gsheets-connection`)
* **Deployment:** Streamlit Community Cloud

---

## How to Deploy Your Own Instance

If you want to use this app for your own workouts, you will need to host your own version so your data remains entirely private. Follow these steps:

### Phase 1: Fork the Code
1. Log in to [GitHub](https://github.com/) and click the **Fork** button at the top right of this repository to create your own copy.

### Phase 2: Set Up Your Google Sheet
1. Create a new, blank [Google Sheet](https://sheets.google.com).
2. In the very first row, type these exact 7 column headers in order:
   `Exercise` | `Set` | `Weight (kg)` | `Reps` | `Date` | `Time` | `Workout Name`
3. Copy the URL of your Google Sheet and keep it handy—you will need it for the deployment secrets.

### Phase 3: Get Google Cloud Credentials
To allow the app to securely write to your Google Sheet behind the scenes, you need a Service Account.
1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2. Search for the **Google Sheets API** and click **Enable**.
3. Go to **Credentials** (on the left menu) > **Create Credentials** > **Service Account**. Name it and click **Done**.
4. Click the pencil icon next to your new Service Account, go to the **Keys** tab, and click **Add Key** > **Create new key** > **JSON**. The file will download to your computer.
5. Open the JSON file. Find the `"client_email"` address and copy it.
6. Go to your Google Sheet, click **Share**, paste that email address, set it to **Editor**, and click Send.

### Phase 4: Deploy to Streamlit Cloud
1. Go to [Streamlit Community Cloud](https://share.streamlit.io/) and log in with your GitHub account.
2. Click **New app** and select your forked repository. Set the **Main file path** to `1_Home.py`.
3. Before clicking Deploy, click **Advanced settings...** 
4. In the **Secrets** box, configure your secure connection. Paste your actual Google Sheet URL at the top, and carefully map the corresponding values from your downloaded JSON file into the fields below:
   ```toml
   sheet_url = "[https://docs.google.com/spreadsheets/d/YOUR_REAL_URL_HERE/edit](https://docs.google.com/spreadsheets/d/YOUR_REAL_URL_HERE/edit)"

   [connections.gsheets]
   type = "service_account"
   project_id = "PASTE_FROM_JSON"
   private_key_id = "PASTE_FROM_JSON"
   private_key = "PASTE_FROM_JSON"
   client_email = "PASTE_FROM_JSON"
   client_id = "PASTE_FROM_JSON"
   auth_uri = "[https://accounts.google.com/o/oauth2/auth](https://accounts.google.com/o/oauth2/auth)"
   token_uri = "[https://oauth2.googleapis.com/token](https://oauth2.googleapis.com/token)"
   auth_provider_x509_cert_url = "[https://www.googleapis.com/oauth2/v1/certs](https://www.googleapis.com/oauth2/v1/certs)"
   client_x509_cert_url = "PASTE_FROM_JSON"
   universe_domain = "googleapis.com"
(Note: Ensure your private_key includes the -----BEGIN PRIVATE KEY----- and -----END PRIVATE KEY----- blocks exactly as they appear in the JSON).

5. Click Save and then click Deploy!

 ### Phase 5: Install on iOS (Progressive Web App)
Open the Safari app on your iPhone and navigate to your newly deployed Streamlit app URL.

Tap the Share button at the bottom center of the screen (the square with an arrow pointing up).

Scroll down and tap Add to Home Screen.

Name it "RD Strength" and tap Add. The app will now launch in full-screen mode like a native iOS application.
