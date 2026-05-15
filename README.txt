# AI-Solutions IIS Log Analytics Dashboard
## CET333 Product Development | TSHEPHANG NTHABA

---

## HOW TO RUN IN VS CODE

### Step 1 — Open the project folder
Open the folder containing app.py in VS Code.

### Step 2 — Open a terminal in VS Code
Go to: Terminal → New Terminal

### Step 3 — Install dependencies
Run this command in the terminal:
    pip install -r requirements.txt

### Step 4 — Add the dataset
Make sure the file  ai_solutions_iis_logs.csv  is in the same folder as app.py.
(If it is missing, the app will automatically generate and save it on first run.)

### Step 5 — Run the app
    python app.py

### Step 6 — Open the dashboard
Open your browser and go to:
    http://127.0.0.1:8050

---

## LOGIN ACCOUNTS

| Username   | Password   |
|------------|------------|
| admin      | admin123   |
| analyst    | sales2026  |
| tshephang  | bida2026   |

---

## PROJECT STRUCTURE

    ai_solutions_app/
    ├── app.py                    ← Main application file
    ├── requirements.txt          ← Python dependencies
    ├── README.txt                ← This file
    └── ai_solutions_iis_logs.csv ← Dataset (auto-generated if missing)

---

## SECTIONS IN app.py

    Section 1  — Generate / Load Default Dataset
    Section 2  — App Config & Credentials
    Section 3  — Login Page Layout
    Section 4  — Dashboard: Header & Upload
    Section 5  — Dashboard: Filters
    Section 6  — Dashboard: KPI Cards
    Section 7  — Dashboard: Visualisations
    Section 8  — Dashboard: Log Table
    Section 9  — Dashboard: Download
    Section 10 — Assemble Dashboard & Root Layout
    Section 11 — Callbacks: Routing, Login, Logout
    Section 12 — Callbacks: File Upload & Dropdowns
    Section 13 — Callbacks: KPI Cards & All Charts
    Section 14 — Callback: Download CSV
    Section 15 — Run Server
