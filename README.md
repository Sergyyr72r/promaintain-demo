# 🏗️ promaintain Portal

**Digital Construction Project Management & Time Tracking System**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://promaintain-demo.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-Proprietary-red)

## 📖 About the Project

**promaintain Portal** is a centralized web application designed to replace scattered Excel files in construction project management. It streamlines time tracking for workers, provides real-time cost analysis for scaffolding projects, and offers powerful administration tools including "Smart Excel Import" and automated KPI dashboards.

The system is built to handle:
* **Time Tracking:** Workers log hours against specific scaffolds.
* **Project Planning:** Storing volume ($m^3$), weight ($to$), and cost ($€$) data.
* **Analytics:** Comparing planned vs. actual metrics.

---

## 🚀 Key Features

### 👷 For Workers (Mobile Optimized)
* **No-Password Login:** Simple selection from a predefined worker list.
* **Time Booking:** Intuitive form to log hours for specific project sites.
* **Scaffold Data Entry:** Ability to input planning data (Volume, Area, Weight) directly on-site.

### ⚙️ For Administrators
* **Master Dashboard:** A consolidated view matching the exact structure of internal Excel reports.
* **KPI & Analytics:**
    * Interactive **Bar Charts** (Hours per Worker).
    * **Donut Charts** (Hours per Scaffold) with smart grouping of small values into "Other".
    * Automatic calculation of metrics: `€/to`, `€/m³`, `kg/m³`.
* **Data Editing:** Inline correction of logs and scaffold data.
* **Excel Export:** Download formatted reports with styling (borders, headers) ready for accounting.

---

## 📥 Smart Excel Import System (New!)

The application features a robust **Transactional Import Engine** designed to migrate legacy data safely.

### How it works:
1.  **Project Detection:** The system automatically detects the project number from the **filename** (e.g., uploading `02-016_Data.xlsx` automatically assigns data to Project `02-016...` or creates it).
2.  **Two-Tab Processing:**
    * `Gerüste`: Creates or updates scaffold definitions (Weight, Cost, etc.).
    * `Stundenübersicht`: Imports time logs.
3.  **Duplicate Protection:**
    * **Scaffolds:** Uses `UPSERT` logic (Updates existing scaffolds, inserts new ones).
    * **Hours:** Checks for identical records (User + Date + Hours + Scaffold) to prevent double booking.
4.  **Transactional Safety:** The import is atomic. Either the whole file is processed successfully, or nothing changes (preventing corrupt data).

---

## 🔧 Database Management (Protected)

To prevent accidental data loss, critical database operations are protected:
* **Database Reset:** A "Hard Reset" button (DROP TABLE) is available to clear all data for a fresh start.
* **Security:** This feature is hidden behind a password protection (Default: `31337`).
* **Logs:** Detailed logs of the last import operation can be viewed for debugging.

---

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io) (Python)
* **Database:** SQLite3 (Local/Embedded)
* **Data Processing:** Pandas (DataFrames, Aggregation)
* **Visualization:** Plotly Express (Interactive Charts)
* **Excel Engine:** OpenPyXL (Reading & Formatting Exports)

---

## 📦 Installation & Local Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/promaintain-demo.git](https://github.com/YOUR_USERNAME/promaintain-demo.git)
    cd promaintain-demo
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App:**
    ```bash
    streamlit run app.py
    ```

---

## 📂 File Structure

* `app.py`: Main application logic (UI, DB interactions, plotting).
* `seed_db.py`: Script to generate dummy test data.
* `construction_log.db`: SQLite database file (created automatically).
* `requirements.txt`: List of python dependencies.

---

## 👤 Author

Developed by **Sergey Romanov** for **promaintain®** (2025).
