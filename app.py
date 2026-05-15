# =============================================================
#  AI-Solutions  |  IIS Web Server Log Analytics Dashboard
#  CET333 Product Development  |  ROSE MAITUMELO SEREMANE
#  Business Intelligence and Data Analytics
# =============================================================
#  HOW TO RUN IN VS CODE
#  1. Open Anaconda Prompt
#  2. pip install dash==2.14.2 dash-bootstrap-components==1.5.0 plotly==5.18.0 pandas openpyxl
#  3. cd to this folder
#  4. python app.py
#  5. Open http://127.0.0.1:8050
# =============================================================

import pandas as pd
import numpy as np
import random
import os
import base64
import io
from datetime import datetime, timedelta

import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc

# =============================================================
#  SECTION 1 — GENERATE / LOAD DATASET
# =============================================================

random.seed(42)
np.random.seed(42)

COUNTRIES = [
    {"name": "United Kingdom",  "continent": "Europe",        "ip": "128.1"},
    {"name": "Germany",         "continent": "Europe",        "ip": "130.83"},
    {"name": "France",          "continent": "Europe",        "ip": "194.199"},
    {"name": "Netherlands",     "continent": "Europe",        "ip": "145.220"},
    {"name": "Italy",           "continent": "Europe",        "ip": "151.21"},
    {"name": "United States",   "continent": "North America", "ip": "155.55"},
    {"name": "Canada",          "continent": "North America", "ip": "142.112"},
    {"name": "Mexico",          "continent": "North America", "ip": "187.141"},
    {"name": "South Africa",    "continent": "Africa",        "ip": "196.25"},
    {"name": "Nigeria",         "continent": "Africa",        "ip": "41.206"},
    {"name": "Kenya",           "continent": "Africa",        "ip": "197.232"},
    {"name": "Botswana",        "continent": "Africa",        "ip": "196.43"},
    {"name": "Egypt",           "continent": "Africa",        "ip": "197.47"},
    {"name": "India",           "continent": "Asia",          "ip": "157.20"},
    {"name": "China",           "continent": "Asia",          "ip": "58.14"},
    {"name": "Japan",           "continent": "Asia",          "ip": "60.32"},
    {"name": "UAE",             "continent": "Asia",          "ip": "94.200"},
    {"name": "Australia",       "continent": "Oceania",       "ip": "203.0"},
    {"name": "New Zealand",     "continent": "Oceania",       "ip": "210.48"},
]

PAGES = [
    {"url": "/index.html",           "type": "home",      "weight": 20},
    {"url": "/about.php",            "type": "home",      "weight": 8},
    {"url": "/images/events.jpg",    "type": "asset",     "weight": 15},
    {"url": "/event.php",            "type": "event",     "weight": 10},
    {"url": "/scheduledemo.php",     "type": "demo",      "weight": 7},
    {"url": "/prototype.php",        "type": "prototype", "weight": 7},
    {"url": "/virtualassistant.php", "type": "va",        "weight": 8},
    {"url": "/jobs.php",             "type": "jobs",      "weight": 6},
    {"url": "/contact.php",          "type": "home",      "weight": 5},
    {"url": "/pricing.php",          "type": "home",      "weight": 4},
    {"url": "/solutions.php",        "type": "home",      "weight": 6},
    {"url": "/blog.php",             "type": "home",      "weight": 4},
]

JOB_TYPES = [
    "Data Analyst", "ML Engineer", "Software Developer",
    "BI Consultant", "DevOps Engineer", "Product Manager",
    "UI/UX Designer", "AI Researcher",
]

PAGE_PROBS = [p["weight"] / sum(x["weight"] for x in PAGES) for p in PAGES]


def generate_logs():
    records = []
    start = datetime(2026, 1, 1)
    for day in range(90):
        log_date = start + timedelta(days=day)
        for _ in range(random.randint(40, 140)):
            country = random.choice(COUNTRIES)
            page    = random.choices(PAGES, weights=PAGE_PROBS, k=1)[0]
            status  = random.choices(
                [200, 304, 404, 500],
                weights=[0.65, 0.25, 0.07, 0.03], k=1)[0]
            ip = f"{country['ip']}.{random.randint(0,255)}.{random.randint(1,254)}"
            t  = (f"{random.randint(0,23):02d}:"
                  f"{random.randint(0,59):02d}:"
                  f"{random.randint(0,59):02d}")
            records.append({
                "date":         log_date.strftime("%Y-%m-%d"),
                "time":         t,
                "ip_address":   ip,
                "method":       "GET",
                "url_stem":     page["url"],
                "status_code":  status,
                "country":      country["name"],
                "continent":    country["continent"],
                "request_type": page["type"],
                "job_type":     random.choice(JOB_TYPES) if page["type"] == "jobs" else "",
            })
    return pd.DataFrame(records)


def load_default():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "ai_solutions_iis_logs.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"[OK] Loaded {len(df):,} rows")
    else:
        df = generate_logs()
        df.to_csv(path, index=False)
        print(f"[OK] Generated & saved {len(df):,} rows")
    df["date"]  = pd.to_datetime(df["date"])
    df["week"]  = df["date"].dt.to_period("W").astype(str)
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["job_type"]     = df["job_type"].fillna("")
    df["request_type"] = df["request_type"].fillna("home")
    df["status_code"]  = df["status_code"].astype(int)
    return df


DF_DEFAULT = load_default()

# =============================================================
#  SECTION 2 — APP CONFIG / THEME
# =============================================================

USERS = {
    "admin":     "admin123",
    "rose":      "bida2026",
    "analyst":   "sales2026",
}

# ── Tech / Professional Dark Navy Palette ────────────────────
NAV_DEEP   = "#0A0E1A"   # deepest navy         (page bg / header)
NAV_DARK   = "#0F1629"   # dark navy            (sidebar / panels)
NAV_MID    = "#141E35"   # mid navy             (card bg)
NAV_SURF   = "#1A2540"   # surface navy         (raised cards)
NAV_BORDER = "#243050"   # border               (dividers)
BLUE_PRI   = "#2563EB"   # electric blue        (primary accent)
BLUE_LIGHT = "#3B82F6"   # lighter blue         (hover)
CYAN_ACC   = "#06B6D4"   # cyan                 (secondary accent)
CYAN_LIGHT = "#22D3EE"   # light cyan           (highlights)
VIOLET     = "#7C3AED"   # violet               (tertiary)
EMERALD    = "#10B981"   # emerald              (success / positive)
AMBER      = "#F59E0B"   # amber                (warning / 304)
RED_ERR    = "#EF4444"   # red                  (error / 500)
ORANGE_404 = "#F97316"   # orange               (404)
TXT_PRI    = "#F0F4FF"   # primary text         (white-ish)
TXT_SEC    = "#94A3B8"   # secondary text       (slate)
TXT_MUTED  = "#475569"   # muted text

WHITE      = "#FFFFFF"

# Google Fonts — Inter (UI) + JetBrains Mono (data/code)
FONT_IMPORT = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
"""

CHART_COLORS = [BLUE_PRI, CYAN_ACC, VIOLET, EMERALD, AMBER,
                BLUE_LIGHT, CYAN_LIGHT, "#A78BFA", "#34D399", "#FCD34D"]

CARD = {
    "background":   NAV_SURF,
    "border":       f"1px solid {NAV_BORDER}",
    "borderRadius": "10px",
    "padding":      "18px 20px",
    "marginBottom": "18px",
    "boxShadow":    "0 2px 12px rgba(0,0,0,0.35)",
}

PERIOD_OPTIONS = [
    {"label": "Daily",   "value": "date"},
    {"label": "Weekly",  "value": "week"},
    {"label": "Monthly", "value": "month"},
]

CHART_OPTIONS = [
    {"label": "All Charts",                       "value": "all"},
    {"label": "Requests Over Time (Line)",        "value": "time"},
    {"label": "HTTP Status Codes (Doughnut)",     "value": "status"},
    {"label": "Sales Metrics by Continent (Bar)", "value": "geo"},
    {"label": "Job Types Requested (Pie)",        "value": "jobs_pie"},
    {"label": "Top 10 Countries (Bar)",           "value": "country"},
    {"label": "Demo vs Prototype (Scatter)",      "value": "scatter"},
]

REQUEST_TYPE_OPTIONS = [
    {"label": "All Types",         "value": "all"},
    {"label": "Demo",              "value": "demo"},
    {"label": "Prototype",         "value": "prototype"},
    {"label": "Virtual Assistant", "value": "va"},
    {"label": "Jobs",              "value": "jobs"},
    {"label": "Event",             "value": "event"},
    {"label": "Home / Info",       "value": "home"},
    {"label": "Asset",             "value": "asset"},
]

STATUS_OPTIONS = [
    {"label": "All Status Codes",   "value": "all"},
    {"label": "200 — OK",           "value": "200"},
    {"label": "304 — Not Modified", "value": "304"},
    {"label": "404 — Not Found",    "value": "404"},
    {"label": "500 — Server Error", "value": "500"},
]


def dropdown_options(df):
    regions   = [{"label": "All Regions",   "value": "all"}] + [
        {"label": c, "value": c} for c in sorted(df["continent"].dropna().unique())]
    countries = [{"label": "All Countries", "value": "all"}] + [
        {"label": c, "value": c} for c in sorted(df["country"].dropna().unique())]
    job_opts  = [{"label": "All Job Types", "value": "all"}] + [
        {"label": j, "value": j} for j in sorted(
            df[df["job_type"] != ""]["job_type"].dropna().unique())]
    return regions, countries, job_opts


# ── Dropdown / Input styles (dark theme) ────────────────────
DD_STYLE = {
    "fontSize": "13px",
    "fontFamily": "'Inter', sans-serif",
}

# Inject global CSS via a custom index_string
CUSTOM_CSS = f"""
{FONT_IMPORT}

body, html {{
    background-color: {NAV_DEEP} !important;
    font-family: 'Inter', sans-serif !important;
    color: {TXT_PRI} !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {NAV_DARK}; }}
::-webkit-scrollbar-thumb {{ background: {NAV_BORDER}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {BLUE_PRI}; }}

/* Dropdown overrides */
.Select-control, .Select-menu-outer {{
    background-color: {NAV_DARK} !important;
    border-color: {NAV_BORDER} !important;
    color: {TXT_PRI} !important;
    font-family: 'Inter', sans-serif !important;
}}
.Select-value-label, .Select-placeholder {{
    color: {TXT_PRI} !important;
}}
.VirtualizedSelectOption {{
    background-color: {NAV_DARK} !important;
    color: {TXT_PRI} !important;
}}
.VirtualizedSelectFocusedOption {{
    background-color: {NAV_SURF} !important;
}}

/* DataTable filter row inputs */
.dash-filter input {{
    background-color: {NAV_DARK} !important;
    color: {TXT_PRI} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    border: 1px solid {NAV_BORDER} !important;
}}

/* Plotly chart backgrounds — keep transparent */
.js-plotly-plot .plotly .bg {{
    fill: transparent !important;
}}

/* Bootstrap overrides */
.btn {{ font-family: 'Inter', sans-serif !important; }}
.card {{ background: {NAV_SURF} !important; }}
.text-muted {{ color: {TXT_SEC} !important; }}
.fw-bold {{ font-weight: 600 !important; }}
label {{ color: {TXT_SEC} !important; font-size: 12px !important; }}
"""

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    title="AI-Solutions IIS Analytics",
)
server = app.server

app.index_string = f"""
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>{CUSTOM_CSS}</style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
"""

# =============================================================
#  SECTION 3 — LOGIN PAGE
# =============================================================

login_layout = dbc.Container(fluid=True,
    style={"background": NAV_DEEP, "minHeight": "100vh"},
    children=[
        dbc.Row(justify="center", align="center",
                style={"minHeight": "100vh"},
                children=[
            dbc.Col(md=4, children=[
                html.Div([
                    html.Div([
                        html.H4("AI-Solutions",
                                className="text-white mb-1",
                                style={"fontWeight": "700",
                                       "letterSpacing": "1px",
                                       "fontFamily": "'Inter', sans-serif"}),
                        html.P("IIS Log Analytics System",
                               className="mb-0",
                               style={"color": TXT_SEC,
                                      "fontSize": "13px",
                                      "fontFamily": "'Inter', sans-serif"}),
                    ], style={
                        "background":    f"linear-gradient(135deg, {NAV_DARK}, {NAV_SURF})",
                        "borderBottom":  f"2px solid {BLUE_PRI}",
                        "padding":       "26px 28px",
                        "borderRadius":  "12px 12px 0 0",
                        "textAlign":     "center",
                    }),
                    html.Div([
                        html.P("Sign in to your account",
                               className="text-muted mb-4",
                               style={"fontSize": "14px",
                                      "textAlign": "center",
                                      "fontFamily": "'Inter', sans-serif"}),
                        dbc.Label("Username", className="fw-bold small",
                                  style={"color": TXT_SEC,
                                         "fontFamily": "'Inter', sans-serif"}),
                        dbc.Input(id="username", type="text",
                                  placeholder="Enter username",
                                  className="mb-3",
                                  style={"borderColor":      NAV_BORDER,
                                         "backgroundColor":  NAV_DARK,
                                         "color":            TXT_PRI,
                                         "fontFamily":       "'Inter', sans-serif"}),
                        dbc.Label("Password", className="fw-bold small",
                                  style={"color": TXT_SEC,
                                         "fontFamily": "'Inter', sans-serif"}),
                        dbc.Input(id="password", type="password",
                                  placeholder="Enter password",
                                  className="mb-3",
                                  style={"borderColor":      NAV_BORDER,
                                         "backgroundColor":  NAV_DARK,
                                         "color":            TXT_PRI,
                                         "fontFamily":       "'Inter', sans-serif"}),
                        html.Div(id="login-error",
                                 className="text-danger mb-3",
                                 style={"fontSize": "13px",
                                        "minHeight": "20px",
                                        "fontFamily": "'Inter', sans-serif"}),
                        dbc.Button("Login", id="login-btn",
                                   className="w-100 mb-4",
                                   n_clicks=0,
                                   style={
                                       "background": f"linear-gradient(135deg, {BLUE_PRI}, {CYAN_ACC})",
                                       "border":     "none",
                                       "fontWeight": "600",
                                       "fontFamily": "'Inter', sans-serif",
                                   }),
                    ], style={"padding": "28px 32px",
                              "backgroundColor": NAV_SURF}),
                ], style={
                    "border":        f"1px solid {NAV_BORDER}",
                    "borderRadius":  "12px",
                    "boxShadow":     f"0 8px 32px rgba(0,0,0,0.5)",
                    "background":    NAV_SURF,
                }),
            ]),
        ]),
    ]
)


# =============================================================
#  SECTION 4 — DASHBOARD LAYOUT
# =============================================================

r_opts, c_opts, j_opts = dropdown_options(DF_DEFAULT)

# Helper: section header with accent line
def section_header(title, badge=None):
    return html.Div([
        html.Div([
            html.Div(style={
                "width":           "3px",
                "height":          "18px",
                "background":      f"linear-gradient({BLUE_PRI}, {CYAN_ACC})",
                "borderRadius":    "2px",
                "marginRight":     "10px",
                "flexShrink":      "0",
            }),
            html.Span(title, style={
                "color":       TXT_PRI,
                "fontWeight":  "600",
                "fontSize":    "13px",
                "letterSpacing": "0.5px",
                "fontFamily":  "'Inter', sans-serif",
            }),
            html.Span(badge, style={
                "background":   f"rgba(37,99,235,0.2)",
                "color":        CYAN_LIGHT,
                "fontSize":     "10px",
                "padding":      "2px 8px",
                "borderRadius": "20px",
                "marginLeft":   "10px",
                "fontFamily":   "'JetBrains Mono', monospace",
                "border":       f"1px solid rgba(6,182,212,0.3)",
            }) if badge else html.Span(),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "14px"}),
    ])


dashboard_layout = html.Div(
    style={"background": NAV_DEEP, "minHeight": "100vh", "fontFamily": "'Inter', sans-serif"},
    children=[

    # ── Top Header Bar ───────────────────────────────────────
    html.Div([
        html.Div([
            # Left: brand
            html.Div([
                html.Div([
                    html.Span("◈ ", style={"color": CYAN_ACC, "fontFamily": "monospace"}),
                    html.Span("AI-SOLUTIONS", style={
                        "fontWeight":    "700",
                        "fontSize":      "16px",
                        "letterSpacing": "3px",
                        "color":         TXT_PRI,
                        "fontFamily":    "'Inter', sans-serif",
                    }),
                ]),
                html.Div("IIS LOG ANALYTICS DASHBOARD", style={
                    "fontSize":    "10px",
                    "color":       TXT_MUTED,
                    "letterSpacing": "2px",
                    "fontFamily":  "'JetBrains Mono', monospace",
                    "marginTop":   "2px",
                }),
            ]),
            # Right: user + logout
            html.Div([
                html.Span("●", style={"color": EMERALD, "fontSize": "8px", "marginRight": "6px"}),
                html.Span(id="welcome-msg", style={
                    "fontSize":   "12px",
                    "color":      TXT_SEC,
                    "fontFamily": "'JetBrains Mono', monospace",
                    "marginRight": "16px",
                }),
                html.Button("LOGOUT", id="logout-btn",
                            n_clicks=0,
                            style={
                                "background":    "transparent",
                                "border":        f"1px solid {NAV_BORDER}",
                                "color":         TXT_SEC,
                                "fontSize":      "10px",
                                "letterSpacing": "1.5px",
                                "padding":       "5px 14px",
                                "borderRadius":  "4px",
                                "cursor":        "pointer",
                                "fontFamily":    "'Inter', sans-serif",
                            }),
            ], style={"display": "flex", "alignItems": "center"}),
        ], style={
            "maxWidth":      "1400px",
            "margin":        "0 auto",
            "display":       "flex",
            "justifyContent": "space-between",
            "alignItems":    "center",
            "padding":       "0 24px",
            "height":        "56px",
        }),
        # bottom accent line
        html.Div(style={
            "height":     "1px",
            "background": f"linear-gradient(90deg, {BLUE_PRI}, {CYAN_ACC}, transparent)",
        }),
    ], style={
        "background": NAV_DARK,
        "borderBottom": f"1px solid {NAV_BORDER}",
        "position":   "sticky",
        "top":        "0",
        "zIndex":     "1000",
    }),

    # ── Page body ───────────────────────────────────────────
    html.Div(style={"maxWidth": "1400px", "margin": "0 auto", "padding": "20px 24px"},
    children=[

        dbc.Row(className="g-3", children=[

            # ══════════════════════════════════════════════
            #  LEFT SIDEBAR — Upload + Filters
            # ══════════════════════════════════════════════
            dbc.Col(md=3,
                    style={"position": "sticky", "top": "72px",
                           "alignSelf": "flex-start", "height": "fit-content"},
                    children=[

                # ── Upload ──────────────────────────────
                html.Div([
                    section_header("Data Source", "LIVE"),
                    html.P("Upload .csv / .xlsx to replace default dataset",
                           style={"color": TXT_SEC, "fontSize": "12px",
                                  "marginBottom": "12px"}),
                    dcc.Upload(
                        id="upload-data",
                        children=html.Button(
                            "⬆  BROWSE FILE",
                            style={
                                "background":    "transparent",
                                "border":        f"1px solid {BLUE_PRI}",
                                "color":         BLUE_LIGHT,
                                "fontSize":      "11px",
                                "letterSpacing": "1.5px",
                                "padding":       "7px 18px",
                                "borderRadius":  "4px",
                                "cursor":        "pointer",
                                "fontFamily":    "'Inter', sans-serif",
                                "fontWeight":    "500",
                                "width":         "100%",
                            }),
                        multiple=False,
                    ),
                    html.Div(id="upload-status",
                             style={"fontSize": "11px", "color": EMERALD,
                                    "fontFamily": "'JetBrains Mono', monospace",
                                    "marginTop": "8px"}),
                ], style=CARD),

                # ── Filters ─────────────────────────────
                html.Div([
                    section_header("Filters"),

                    html.Label("TIME PERIOD"),
                    dcc.Dropdown(id="period-dd",
                                 options=PERIOD_OPTIONS,
                                 value="month",
                                 clearable=False,
                                 style={**DD_STYLE, "marginBottom": "12px"}),

                    html.Label("CONTINENT"),
                    dcc.Dropdown(id="continent-dd",
                                 options=r_opts,
                                 value="all",
                                 clearable=False,
                                 style={**DD_STYLE, "marginBottom": "12px"}),

                    html.Label("COUNTRY"),
                    dcc.Dropdown(id="country-dd",
                                 options=c_opts,
                                 value="all",
                                 clearable=False,
                                 style={**DD_STYLE, "marginBottom": "12px"}),

                    html.Label("REQUEST TYPE"),
                    dcc.Dropdown(id="reqtype-dd",
                                 options=REQUEST_TYPE_OPTIONS,
                                 value="all",
                                 clearable=False,
                                 style={**DD_STYLE, "marginBottom": "12px"}),

                    html.Label("JOB TYPE"),
                    dcc.Dropdown(id="jobtype-dd",
                                 options=j_opts,
                                 value="all",
                                 clearable=False,
                                 style={**DD_STYLE, "marginBottom": "12px"}),

                    html.Label("HTTP STATUS"),
                    dcc.Dropdown(id="status-dd",
                                 options=STATUS_OPTIONS,
                                 value="all",
                                 clearable=False,
                                 style={**DD_STYLE, "marginBottom": "16px"}),

                    html.Button("↺  RESET FILTERS", id="reset-btn",
                                n_clicks=0,
                                style={
                                    "background":    "transparent",
                                    "border":        f"1px solid {NAV_BORDER}",
                                    "color":         TXT_SEC,
                                    "fontSize":      "10px",
                                    "letterSpacing": "1.5px",
                                    "padding":       "6px 14px",
                                    "borderRadius":  "4px",
                                    "cursor":        "pointer",
                                    "fontFamily":    "'Inter', sans-serif",
                                    "width":         "100%",
                                    "marginBottom":  "10px",
                                }),

                    html.Div(id="filter-summary",
                             style={
                                 "fontSize":   "10px",
                                 "color":      TXT_MUTED,
                                 "fontFamily": "'JetBrains Mono', monospace",
                                 "lineHeight": "1.5",
                             }),
                ], style=CARD),

            ]),

            # ══════════════════════════════════════════════
            #  RIGHT MAIN CONTENT
            # ══════════════════════════════════════════════
            dbc.Col(md=9, children=[

                # ── KPI Cards ───────────────────────────
                html.Div([
                    section_header("Key Performance Indicators"),
                    dbc.Row(id="kpi-row", className="g-3"),
                ], style=CARD),

                # ── Charts ──────────────────────────────
                html.Div([
                    dbc.Row([
                        dbc.Col(
                            section_header("Visualisations"),
                            className="d-flex align-items-center"
                        ),
                        dbc.Col([
                            html.Label("SHOW CHART", style={"marginRight": "8px",
                                                             "fontSize": "10px",
                                                             "letterSpacing": "1px"}),
                            dcc.Dropdown(id="chart-select",
                                         options=CHART_OPTIONS,
                                         value="all",
                                         clearable=False,
                                         style={**DD_STYLE, "minWidth": "240px"}),
                        ], className="d-flex align-items-center justify-content-end",
                           style={"gap": "8px"}),
                    ], align="center", className="mb-3"),
                    html.Div(id="charts-container"),
                ], style=CARD),

                # ── Log Table ───────────────────────────
                html.Div([
                    dbc.Row([
                        dbc.Col(section_header("IIS Web Server Log"),
                                className="d-flex align-items-center"),
                        dbc.Col(html.P(id="log-count",
                                       style={
                                           "fontSize":    "11px",
                                           "color":       TXT_MUTED,
                                           "fontFamily":  "'JetBrains Mono', monospace",
                                           "textAlign":   "right",
                                           "marginBottom": "0",
                                       })),
                    ], align="center", className="mb-3"),

                    dash_table.DataTable(
                        id="log-table",
                        columns=[
                            {"name": "Date",       "id": "date",         "type": "text"},
                            {"name": "Time",       "id": "time",         "type": "text"},
                            {"name": "IP Address", "id": "ip_address",   "type": "text"},
                            {"name": "Method",     "id": "method",       "type": "text"},
                            {"name": "URL",        "id": "url_stem",     "type": "text"},
                            {"name": "Status",     "id": "status_code",  "type": "numeric"},
                            {"name": "Country",    "id": "country",      "type": "text"},
                            {"name": "Continent",  "id": "continent",    "type": "text"},
                            {"name": "Type",       "id": "request_type", "type": "text"},
                            {"name": "Job Type",   "id": "job_type",     "type": "text"},
                        ],
                        data=[],
                        page_size=15,
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        page_action="native",
                        style_table={"overflowX": "auto"},

                        style_header={
                            "backgroundColor": NAV_DARK,
                            "color":           CYAN_LIGHT,
                            "fontWeight":      "600",
                            "fontSize":        "11px",
                            "letterSpacing":   "1px",
                            "border":          f"1px solid {NAV_BORDER}",
                            "textAlign":       "center",
                            "fontFamily":      "Inter, sans-serif",
                            "padding":         "10px 8px",
                        },
                        style_cell={
                            "fontSize":        "12px",
                            "padding":         "8px 10px",
                            "fontFamily":      "'JetBrains Mono', monospace",
                            "border":          f"1px solid {NAV_BORDER}",
                            "textAlign":       "left",
                            "minWidth":        "100px",
                            "maxWidth":        "200px",
                            "whiteSpace":      "normal",
                            "backgroundColor": NAV_SURF,
                            "color":           TXT_PRI,
                        },
                        style_filter={
                            "backgroundColor": NAV_DARK,
                            "border":          f"1px solid {NAV_BORDER}",
                            "color":           TXT_PRI,
                            "fontSize":        "11px",
                            "fontFamily":      "'JetBrains Mono', monospace",
                        },
                        style_data_conditional=[
                            {
                                "if": {"filter_query": "{status_code} = 200"},
                                "backgroundColor": "rgba(16,185,129,0.08)",
                                "color":           "#6EE7B7",
                            },
                            {
                                "if": {"filter_query": "{status_code} = 304"},
                                "backgroundColor": "rgba(37,99,235,0.08)",
                                "color":           "#93C5FD",
                            },
                            {
                                "if": {"filter_query": "{status_code} = 404"},
                                "backgroundColor": "rgba(245,158,11,0.08)",
                                "color":           "#FCD34D",
                            },
                            {
                                "if": {"filter_query": "{status_code} = 500"},
                                "backgroundColor": "rgba(239,68,68,0.08)",
                                "color":           "#FCA5A5",
                            },
                            {
                                "if": {"row_index": "odd"},
                                "backgroundColor": NAV_MID,
                            },
                        ],
                    ),
                ], style=CARD),

                # ── Export ──────────────────────────────
                html.Div([
                    dbc.Row([
                        dbc.Col(section_header("Export Data"),
                                className="d-flex align-items-center"),
                        dbc.Col([
                            html.Button("⬇  DOWNLOAD FILTERED CSV",
                                        id="download-btn",
                                        n_clicks=0,
                                        style={
                                            "background":    BLUE_PRI,
                                            "border":        "none",
                                            "color":         WHITE,
                                            "fontSize":      "11px",
                                            "letterSpacing": "1.5px",
                                            "padding":       "9px 20px",
                                            "borderRadius":  "4px",
                                            "cursor":        "pointer",
                                            "fontFamily":    "'Inter', sans-serif",
                                            "fontWeight":    "600",
                                        }),
                            dcc.Download(id="download-csv"),
                        ], className="text-end"),
                    ], align="center"),
                ], style={**CARD, "marginBottom": "40px"}),

            ]),  # end right col

        ]),  # end main row

    ]),  # end page body
])  # end dashboard_layout


# =============================================================
#  SECTION 5 — ROOT LAYOUT
# =============================================================

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="session-store", storage_type="session", data={}),
    dcc.Store(id="data-store",    storage_type="session", data=None),
    html.Div(id="page-content"),
])


# =============================================================
#  SECTION 6 — AUTH CALLBACKS
# =============================================================

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    State("session-store", "data"),
)
def route(pathname, session):
    try:
        if session and session.get("user"):
            return dashboard_layout
    except Exception:
        pass
    return login_layout


@app.callback(
    Output("session-store", "data"),
    Output("url",           "pathname"),
    Output("login-error",   "children"),
    Input("login-btn",      "n_clicks"),
    State("username",       "value"),
    State("password",       "value"),
    prevent_initial_call=True,
)
def login(n, username, password):
    if not n:
        return dash.no_update, dash.no_update, ""
    if not username or not password:
        return dash.no_update, dash.no_update, "⚠  Please enter username and password."
    if USERS.get(username) == password:
        return {"user": username}, "/dashboard", ""
    return dash.no_update, dash.no_update, "⚠  Invalid username or password."


@app.callback(
    Output("session-store", "data",     allow_duplicate=True),
    Output("url",           "pathname", allow_duplicate=True),
    Input("logout-btn",     "n_clicks"),
    prevent_initial_call=True,
)
def logout(n):
    if not n:
        return dash.no_update, dash.no_update
    return {}, "/"


@app.callback(
    Output("welcome-msg", "children"),
    Input("session-store", "data"),
)
def welcome(session):
    try:
        if session and session.get("user"):
            return f"session: {session['user']}"
    except Exception:
        pass
    return ""


# =============================================================
#  SECTION 7 — UPLOAD & DROPDOWN CALLBACKS
# =============================================================

@app.callback(
    Output("data-store",    "data"),
    Output("upload-status", "children"),
    Output("continent-dd",  "options"),
    Output("country-dd",    "options"),
    Output("jobtype-dd",    "options"),
    Input("upload-data",    "contents"),
    State("upload-data",    "filename"),
    prevent_initial_call=True,
)
def handle_upload(contents, filename):
    if not contents:
        return dash.no_update, "", dash.no_update, dash.no_update, dash.no_update
    try:
        _, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        if filename.endswith(".csv"):
            udf = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif filename.endswith((".xlsx", ".xls")):
            udf = pd.read_excel(io.BytesIO(decoded))
        else:
            return (dash.no_update,
                    f"⚠  Unsupported file — upload .csv or .xlsx only.",
                    dash.no_update, dash.no_update, dash.no_update)

        if "date" in udf.columns:
            udf["date"]  = pd.to_datetime(udf["date"], errors="coerce")
            udf["week"]  = udf["date"].dt.to_period("W").astype(str)
            udf["month"] = udf["date"].dt.to_period("M").astype(str)
        for col in ["job_type", "request_type"]:
            if col not in udf.columns:
                udf[col] = ""
        udf["job_type"]     = udf["job_type"].fillna("")
        udf["request_type"] = udf["request_type"].fillna("home")
        if "status_code" in udf.columns:
            udf["status_code"] = udf["status_code"].astype(int)

        r, c, j = dropdown_options(udf)
        msg = f"✓  {filename}  ({len(udf):,} rows loaded)"
        return udf.to_json(date_format="iso", orient="split"), msg, r, c, j

    except Exception as e:
        return (dash.no_update,
                f"⚠  Error: {str(e)}",
                dash.no_update, dash.no_update, dash.no_update)


@app.callback(
    Output("continent-dd", "options", allow_duplicate=True),
    Output("country-dd",   "options", allow_duplicate=True),
    Output("jobtype-dd",   "options", allow_duplicate=True),
    Input("page-content",  "children"),
    State("data-store",    "data"),
    prevent_initial_call=True,
)
def init_dropdowns(_, stored):
    d = (pd.read_json(io.StringIO(stored), orient="split")
         if stored else DF_DEFAULT)
    return dropdown_options(d)


@app.callback(
    Output("continent-dd", "value"),
    Output("country-dd",   "value"),
    Output("period-dd",    "value"),
    Output("reqtype-dd",   "value"),
    Output("jobtype-dd",   "value"),
    Output("status-dd",    "value"),
    Input("reset-btn",     "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    return "all", "all", "month", "all", "all", "all"


# =============================================================
#  SECTION 8 — CHART THEME HELPER
# =============================================================

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=TXT_SEC, size=11),
    margin=dict(t=42, b=30, l=10, r=10),
    title_font=dict(color=TXT_PRI, size=13, family="Inter, sans-serif"),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color=TXT_SEC, size=11),
    ),
    xaxis=dict(gridcolor=NAV_BORDER, zerolinecolor=NAV_BORDER,
               tickfont=dict(color=TXT_SEC)),
    yaxis=dict(gridcolor=NAV_BORDER, zerolinecolor=NAV_BORDER,
               tickfont=dict(color=TXT_SEC)),
)


def apply_theme(fig):
    fig.update_layout(**CHART_LAYOUT)
    return fig


# =============================================================
#  SECTION 9 — MAIN DASHBOARD CALLBACK
# =============================================================

@app.callback(
    Output("kpi-row",          "children"),
    Output("charts-container", "children"),
    Output("log-table",        "data"),
    Output("log-count",        "children"),
    Output("filter-summary",   "children"),
    Input("period-dd",         "value"),
    Input("continent-dd",      "value"),
    Input("country-dd",        "value"),
    Input("reqtype-dd",        "value"),
    Input("jobtype-dd",        "value"),
    Input("status-dd",         "value"),
    Input("chart-select",      "value"),
    Input("page-content",      "children"),
    State("data-store",        "data"),
)
def update_dashboard(period, continent, country, req_type,
                     job_type, http_status, chart_select,
                     _page, stored):

    # ── load dataset ─────────────────────────────────────
    try:
        if stored:
            d = pd.read_json(io.StringIO(stored), orient="split")
            d["date"] = pd.to_datetime(d["date"])
            if "week"  not in d.columns:
                d["week"]  = d["date"].dt.to_period("W").astype(str)
            if "month" not in d.columns:
                d["month"] = d["date"].dt.to_period("M").astype(str)
            d["status_code"] = d["status_code"].astype(int)
        else:
            d = DF_DEFAULT.copy()
    except Exception:
        d = DF_DEFAULT.copy()

    # ── apply filters ────────────────────────────────────
    total_before = len(d)
    active_filters = []

    if continent and continent != "all":
        d = d[d["continent"] == continent]
        active_filters.append(f"continent:{continent}")
    if country and country != "all":
        d = d[d["country"] == country]
        active_filters.append(f"country:{country}")
    if req_type and req_type != "all":
        d = d[d["request_type"] == req_type]
        active_filters.append(f"type:{req_type}")
    if job_type and job_type != "all":
        d = d[d["job_type"] == job_type]
        active_filters.append(f"job:{job_type}")
    # FIX: http_status values are strings from dropdown ("200","304"…)
    # compare to int column safely
    if http_status and http_status != "all":
        d = d[d["status_code"] == int(http_status)]
        active_filters.append(f"status:{http_status}")

    if active_filters:
        filter_txt = "active → " + "  |  ".join(active_filters) + f"  ({len(d):,} / {total_before:,} rows)"
    else:
        filter_txt = f"no active filters  ·  showing all {len(d):,} rows"

    # empty guard
    if d.empty:
        kpis   = [dbc.Col(html.P("No data for selected filters.",
                                  style={"color": TXT_MUTED}))]
        charts = html.P("No data.", style={"color": TXT_MUTED, "padding": "12px"})
        return kpis, charts, [], "0 rows", filter_txt

    # ── KPI cards ────────────────────────────────────────
    def kpi(title, value, icon, accent):
        return dbc.Col(
            html.Div([
                html.Div([
                    html.Div(icon, style={
                        "fontSize": "18px",
                        "marginBottom": "6px",
                    }),
                    html.Div(title, style={
                        "fontSize":    "10px",
                        "color":       TXT_MUTED,
                        "letterSpacing": "1.2px",
                        "fontFamily":  "'JetBrains Mono', monospace",
                        "marginBottom": "4px",
                    }),
                    html.Div(str(value), style={
                        "fontSize":    "26px",
                        "fontWeight":  "700",
                        "color":       TXT_PRI,
                        "lineHeight":  "1",
                        "fontFamily":  "'Inter', sans-serif",
                    }),
                ]),
                html.Div(style={
                    "position":   "absolute",
                    "bottom":     "0",
                    "left":       "0",
                    "right":      "0",
                    "height":     "2px",
                    "background": accent,
                    "borderRadius": "0 0 8px 8px",
                }),
            ], style={
                "background":   NAV_MID,
                "border":       f"1px solid {NAV_BORDER}",
                "borderRadius": "8px",
                "padding":      "16px 18px 18px",
                "position":     "relative",
                "minHeight":    "100px",
            }),
            md=2,
        )

    kpis = [
        kpi("TOTAL REQUESTS",     f"{len(d):,}",                              "📊", BLUE_PRI),
        kpi("DEMO REQUESTS",      (d["request_type"]=="demo").sum(),           "🎯", CYAN_ACC),
        kpi("PROTOTYPE REQUESTS", (d["request_type"]=="prototype").sum(),      "🔧", VIOLET),
        kpi("VA ENGAGEMENTS",     (d["request_type"]=="va").sum(),             "🤖", EMERALD),
        kpi("JOBS PLACED",        (d["request_type"]=="jobs").sum(),           "💼", AMBER),
        kpi("COUNTRIES",          d["country"].nunique(),                      "🌍", RED_ERR),
    ]

   # ── charts ───────────────────────────────────────────
    period = period or "month"
    pl = {"date": "Date", "week": "Week", "month": "Month"}.get(period, "Month")

    # ── Chart 1: Requests Over Time (line) ──────────────
    t_df = d.groupby(period).size().reset_index(name="requests")
    t_df.columns = [pl, "requests"]
    fig_time = px.line(t_df, x=pl, y="requests", markers=True,
                       title="Requests Over Time",
                       labels={"requests": "Requests"},
                       color_discrete_sequence=[BLUE_PRI])
    fig_time.update_traces(
        line_color=BLUE_PRI,
        marker=dict(size=6, color=CYAN_ACC, line=dict(color=BLUE_PRI, width=1)),
        fill="tozeroy",
        fillcolor="rgba(37,99,235,0.06)"
    )
    apply_theme(fig_time)
    fig_time.update_xaxes(showgrid=False)

    # ── Chart 2: HTTP Status Codes (doughnut) ───────────
    s_df = d["status_code"].value_counts().reset_index()
    s_df.columns = ["status", "count"]
    fig_status = px.pie(s_df, names="status", values="count", hole=0.52,
                        title="HTTP Status Codes",
                        color_discrete_sequence=[EMERALD, BLUE_PRI, AMBER, RED_ERR])
    fig_status.update_traces(
        textposition="inside",
        textinfo="percent+label",
        marker=dict(line=dict(color=NAV_DARK, width=2)),
        textfont=dict(family="JetBrains Mono, monospace", size=11),
    )
    apply_theme(fig_status)
    fig_status.update_layout(showlegend=True, margin=dict(t=42, b=10, l=10, r=10))

    # ── Chart 3: Sales Metrics by Continent (grouped bar) ─
    sales = ["demo", "prototype", "va", "jobs"]
    g_df  = (d[d["request_type"].isin(sales)]
             .groupby(["continent", "request_type"])
             .size().reset_index(name="count"))
    fig_geo = px.bar(g_df, x="continent", y="count",
                     color="request_type", barmode="group",
                     title="Sales Metrics by Continent",
                     color_discrete_map={
                         "demo":      BLUE_PRI,
                         "prototype": CYAN_ACC,
                         "va":        VIOLET,
                         "jobs":      EMERALD,
                     },
                     labels={"count": "Requests", "continent": "Continent",
                              "request_type": "Type"})
    apply_theme(fig_geo)
    fig_geo.update_xaxes(showgrid=False)

    # ── Chart 4: Top 10 Countries (horizontal bar) ──────
    c_df = d["country"].value_counts().head(10).reset_index()
    c_df.columns = ["country", "requests"]
    fig_country = px.bar(c_df.sort_values("requests"),
                         x="requests", y="country", orientation="h",
                         color="requests",
                         color_continuous_scale=[NAV_BORDER, BLUE_PRI, CYAN_ACC],
                         title="Top 10 Countries by Traffic",
                         labels={"requests": "Requests", "country": "Country"})
    apply_theme(fig_country)
    fig_country.update_layout(coloraxis_showscale=False)
    fig_country.update_yaxes(showgrid=False)

    # ── Chart 5 & 6: still available via selector ───────
    jdata = d[d["request_type"] == "jobs"]["job_type"]
    jdata = jdata[jdata != ""]
    if jdata.empty:
        fig_job = go.Figure()
        fig_job.update_layout(title="Job Types — no data")
    else:
        j_df = jdata.value_counts().reset_index()
        j_df.columns = ["job_type", "count"]
        fig_job = px.pie(j_df, names="job_type", values="count",
                         hole=0.42, title="Job Types Requested",
                         color_discrete_sequence=CHART_COLORS)
        fig_job.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color=NAV_DARK, width=2)),
            textfont=dict(family="JetBrains Mono, monospace", size=11),
        )
    apply_theme(fig_job)
    fig_job.update_layout(margin=dict(t=42, b=10, l=10, r=10))

    sc_df = (d[d["request_type"].isin(["demo", "prototype"])]
             .groupby(["country", "continent", "request_type"])
             .size().unstack(fill_value=0).reset_index())
    sc_df.columns.name = None
    for col in ["demo", "prototype"]:
        if col not in sc_df.columns:
            sc_df[col] = 0
    fig_scat = px.scatter(sc_df, x="demo", y="prototype",
                          color="continent", hover_name="country",
                          size="demo", title="Demo vs Prototype by Country",
                          color_discrete_sequence=CHART_COLORS,
                          labels={"demo": "Demo Requests",
                                  "prototype": "Prototype Requests"})
    apply_theme(fig_scat)

    # ── chart card wrapper ────────────────────────────────
    def chart_card(fig, span=6):
        fig.update_layout(
            margin=dict(t=36, b=24, l=10, r=10),
            height=280,          # fixed height keeps all 4 on one screen
        )
        return dbc.Col(
            html.Div(
                dcc.Graph(figure=fig,
                          config={"displayModeBar": False},
                          style={"height": "280px"}),
                style={
                    "background":   NAV_MID,
                    "border":       f"1px solid {NAV_BORDER}",
                    "borderRadius": "8px",
                    "overflow":     "hidden",
                }
            ),
            md=span,
        )

    # ── 2 × 2 grid: all 4 charts visible on one screen ──
    sel = chart_select or "all"
    if sel == "all":
        charts = html.Div([
            dbc.Row([
                chart_card(fig_time,    8),   # wide — line chart
                chart_card(fig_status,  4),   # narrow — doughnut
            ], className="mb-3 g-3"),
            dbc.Row([
                chart_card(fig_geo,     6),   # grouped bar
                chart_card(fig_country, 6),   # horizontal bar
            ], className="g-3"),
        ])
    elif sel == "time":
        charts = dbc.Row([chart_card(fig_time,    12)], className="g-3")
    elif sel == "status":
        charts = dbc.Row([chart_card(fig_status,   8)], className="g-3")
    elif sel == "geo":
        charts = dbc.Row([chart_card(fig_geo,     12)], className="g-3")
    elif sel == "jobs_pie":
        charts = dbc.Row([chart_card(fig_job,      8)], className="g-3")
    elif sel == "country":
        charts = dbc.Row([chart_card(fig_country, 12)], className="g-3")
    elif sel == "scatter":
        charts = dbc.Row([chart_card(fig_scat,    12)], className="g-3")
    else:
        charts = html.P("Select a chart from the dropdown above.",
                        style={"color": TXT_MUTED, "padding": "12px"})
    # ── log table ─────────────────────────────────────────
    cols  = ["date","time","ip_address","method","url_stem",
             "status_code","country","continent","request_type","job_type"]
    avail = [c for c in cols if c in d.columns]
    shown = min(500, len(d))
    table = (d[avail].tail(shown)
             .assign(date=d["date"].dt.strftime("%Y-%m-%d"))
             .to_dict("records"))
    log_cnt = f"{len(table):,} of {len(d):,} rows  ·  most recent first"

    return kpis, charts, table, log_cnt, filter_txt


# =============================================================
#  SECTION 10 — DOWNLOAD CALLBACK  (FIXED)
# =============================================================

@app.callback(
    Output("download-csv", "data"),
    Input("download-btn",  "n_clicks"),
    State("continent-dd",  "value"),
    State("country-dd",    "value"),
    State("reqtype-dd",    "value"),
    State("jobtype-dd",    "value"),
    State("status-dd",     "value"),
    State("data-store",    "data"),
    prevent_initial_call=True,
)
def download_csv(n, continent, country, req_type,
                 job_type, http_status, stored):
    if not n:
        return dash.no_update
    try:
        if stored:
            d = pd.read_json(io.StringIO(stored), orient="split")
            d["date"] = pd.to_datetime(d["date"])
        else:
            d = DF_DEFAULT.copy()

        # Ensure status_code is int for safe comparison
        d["status_code"] = d["status_code"].astype(int)

        if continent   and continent   != "all":
            d = d[d["continent"]    == continent]
        if country     and country     != "all":
            d = d[d["country"]      == country]
        if req_type    and req_type    != "all":
            d = d[d["request_type"] == req_type]
        if job_type    and job_type    != "all":
            d = d[d["job_type"]     == job_type]
        # FIX: http_status is a string value from dropdown ("200","304" etc.)
        # Cast to int before comparing against the int status_code column
        if http_status and http_status != "all":
            d = d[d["status_code"] == int(http_status)]

        # Format date for export
        d = d.copy()
        d["date"] = d["date"].dt.strftime("%Y-%m-%d")

        # Drop internal columns not needed in export
        export_cols = ["date","time","ip_address","method","url_stem",
                       "status_code","country","continent","request_type","job_type"]
        export_cols = [c for c in export_cols if c in d.columns]

        return dcc.send_data_frame(
            d[export_cols].to_csv,
            "ai_solutions_filtered_logs.csv",
            index=False
        )
    except Exception as e:
        print(f"[Download error] {e}")
        return dash.no_update


# =============================================================
#  SECTION 11 — RUN
# =============================================================

if __name__ == "__main__":
    print("\n" + "=" * 56)
    print("  AI-Solutions — IIS Log Analytics Dashboard")
    print("  CET333 Product Development | ROSE MAITUMELO SEREMANE")
    print("=" * 56)
    print("  Open:  http://127.0.0.1:8050")
    print("  Stop:  Ctrl + C")
    print("=" * 56 + "\n")
    app.run(debug=False, port=8050, use_reloader=False)