import streamlit as st

def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --aiec-green: #16A34A;
            --aiec-green-soft: #EAF8EF;
            --aiec-border: #E4E8EF;
            --aiec-text: #172033;
            --aiec-muted: #6B7280;
            --aiec-bg: #F7F9FC;
        }

        .stApp {
            background: var(--aiec-bg);
        }

        #MainMenu, footer {
            visibility: hidden;
        }

        .block-container {
            max-width: 1500px;
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }

        /* Login */
        .login-shell {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .login-card {
            width: 100%;
            max-width: 520px;
            background: #fff;
            border: 1px solid var(--aiec-border);
            border-radius: 18px;
            box-shadow: 0 18px 55px rgba(20, 32, 54, .08);
            padding: 34px 38px 28px 38px;
        }

        .brand-row {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 24px;
        }

        .brand-badge {
            width: 50px;
            height: 50px;
            border-radius: 13px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 800;
            font-size: 23px;
            background: linear-gradient(135deg, #15A34A 0%, #078D68 45%, #2563EB 100%);
        }

        .brand-title {
            margin: 0;
            font-size: 27px;
            font-weight: 800;
            color: var(--aiec-text);
        }

        .brand-subtitle {
            margin: 0;
            color: var(--aiec-muted);
            font-size: 14px;
        }

        .login-title {
            text-align: center;
            font-size: 28px;
            font-weight: 800;
            color: var(--aiec-text);
            margin: 8px 0 4px 0;
        }

        .login-subtitle {
            text-align: center;
            color: var(--aiec-muted);
            margin-bottom: 24px;
        }

        .demo-hint {
            margin-top: 16px;
            padding: 12px 14px;
            border-radius: 10px;
            background: #F8FAFC;
            border: 1px solid var(--aiec-border);
            color: #4B5563;
            font-size: 13px;
        }

        /* Header */
        .app-header {
            background: #fff;
            border: 1px solid var(--aiec-border);
            border-radius: 14px;
            padding: 14px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 18px;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .mini-badge {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-weight: 800;
            background: linear-gradient(135deg, #15A34A, #2563EB);
        }

        .header-title {
            font-size: 21px;
            font-weight: 800;
            color: var(--aiec-text);
        }

        .header-subtitle {
            color: var(--aiec-muted);
            font-size: 13px;
            margin-left: 5px;
        }

        .user-chip {
            background: #F6F8FB;
            border: 1px solid var(--aiec-border);
            border-radius: 999px;
            padding: 7px 12px;
            color: #374151;
            font-size: 14px;
        }

        /* Cards */
        .aiec-card {
            background: #fff;
            border: 1px solid var(--aiec-border);
            border-radius: 14px;
            padding: 20px;
            box-shadow: 0 4px 18px rgba(20, 32, 54, .03);
        }

        .page-title {
            font-size: 30px;
            font-weight: 800;
            color: var(--aiec-text);
            margin-bottom: 4px;
        }

        .page-subtitle {
            color: var(--aiec-muted);
            margin-bottom: 20px;
        }

        .metric-label {
            color: var(--aiec-muted);
            font-size: 13px;
        }

        .metric-value {
            color: var(--aiec-text);
            font-weight: 800;
            font-size: 26px;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: #fff;
            border-right: 1px solid var(--aiec-border);
        }

        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.2rem;
        }

        div[data-testid="stSidebar"] button[kind="secondary"] {
            border-radius: 10px;
            border: 1px solid transparent;
            justify-content: flex-start;
        }

        div[data-testid="stSidebar"] button[kind="primary"] {
            border-radius: 10px;
            border: 1px solid #BCE8C9;
            background: var(--aiec-green-soft);
            color: #087A35;
            justify-content: flex-start;
        }

        section[data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            min-width: 280px !important;
            width: 280px !important;
            transform: none !important;
        }

        section[data-testid="stSidebar"] > div {
            width: 280px !important;
        }

        /* Uploader */
        div[data-testid="stFileUploader"] {
            background: #fff;
            border: 1px dashed #C9D1DD;
            border-radius: 14px;
            padding: 10px;
        }

        div[data-testid="stFileUploader"] section {
            min-height: 180px;
        }

        .kpi-card {
            background: white;
            border-radius: 14px;
            padding: 20px;
            min-height: 135px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 3px 12px rgba(0,0,0,0.05);
        }

        .kpi-label {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 12px;
        }

        .kpi-value {
            font-size: 29px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .kpi-footer {
            font-size: 12px;
            color: #6b7280;
        }

        .kpi-blue {
            border-top: 4px solid #3b82f6;
        }

        .kpi-blue .kpi-value {
            color: #2563eb;
        }

        .kpi-purple {
            border-top: 4px solid #8b5cf6;
        }

        .kpi-purple .kpi-value {
            color: #7c3aed;
        }

        .kpi-orange {
            border-top: 4px solid #f97316;
        }

        .kpi-orange .kpi-value {
            color: #ea580c;
        }

        .kpi-green {
            border-top: 4px solid #22c55e;
        }

        .kpi-green .kpi-value {
            color: #16a34a;
        }

        .format-chip {
            display: inline-block;
            margin: 5px 6px 0 0;
            padding: 8px 11px;
            border-radius: 9px;
            background: #F5F7FA;
            border: 1px solid var(--aiec-border);
            font-size: 13px;
            color: #4B5563;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
