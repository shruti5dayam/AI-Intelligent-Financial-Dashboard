"""
Dashboard styling utilities.

Responsibilities:
- Apply custom dashboard CSS
- Create a more product-like Streamlit UI
"""

from __future__ import annotations

import streamlit as st


def apply_dashboard_styles() -> None:
    """
    Apply custom CSS styles to the Streamlit dashboard.

    Returns
    -------
    None
        Renders CSS into the Streamlit app.
    """

    st.markdown(
        """
        <style>
        .main-title {
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 4px;
        }

        .main-subtitle {
            font-size: 17px;
            color: #8b949e;
            margin-bottom: 28px;
        }

        .status-panel {
            background: linear-gradient(135deg, #111827 0%, #1e293b 55%, #0f172a 100%);
            border: 1px solid rgba(148, 163, 184, 0.35);
            border-radius: 18px;
            padding: 22px 26px;
            margin-bottom: 26px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.25);
        }

        .status-title {
            font-size: 22px;
            font-weight: 750;
            color: #f8fafc;
            margin-bottom: 6px;
        }
        

        .status-subtitle {
            color: #cbd5e1;
            font-size: 15px;
            margin-bottom: 14px;
        }

        .status-chip {
            display: inline-block;
            padding: 8px 14px;
            margin: 4px 6px 4px 0;
            border-radius: 999px;
            background-color: rgba(34, 197, 94, 0.14);
            color: #86efac;
            border: 1px solid rgba(134, 239, 172, 0.55);
            font-size: 14px;
            font-weight: 600;
        }

        .kpi-card {
            border-radius: 20px;
            padding: 24px 20px;
            min-height: 130px;
            color: white;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
        }

        .kpi-label {
            font-size: 14px;
            opacity: 0.92;
            margin-bottom: 10px;
        }

        .kpi-value {
            font-size: 34px;
            font-weight: 800;
            line-height: 1.15;
        }

        .kpi-note {
            font-size: 13px;
            opacity: 0.85;
            margin-top: 10px;
        }
        .kpi-card-wrapper {
            position: relative;
        }

        .kpi-tooltip {
            visibility: hidden;
            opacity: 0;
            position: absolute;
            left: 16px;
            top: 105%;
            min-width: 260px;
            max-width: 420px;
            background: #020617;
            color: #f8fafc;
            border: 1px solid rgba(148, 163, 184, 0.45);
            border-radius: 14px;
            padding: 12px 14px;
            font-size: 13px;
            line-height: 1.5;
            z-index: 9999;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
        }

        .kpi-card-wrapper:hover .kpi-tooltip {
            visibility: visible;
            opacity: 1;
        }

        .gradient-blue {
            background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
        }

        .gradient-pink {
            background: linear-gradient(135deg, #d946ef 0%, #f43f5e 100%);
        }

        .gradient-green {
            background: linear-gradient(135deg, #22c55e 0%, #2dd4bf 100%);
        }

        .gradient-purple {
            background: linear-gradient(135deg, #6366f1 0%, #9333ea 100%);
        }

        .gradient-orange {
            background: linear-gradient(135deg, #f97316 0%, #facc15 100%);
        }

        .section-title {
            font-size: 26px;
            font-weight: 800;
            margin: 26px 0 14px 0;
        }

                .status-chip-warning {
            background-color: #fef3c7;
            color: #92400e;
            border: 1px solid #fcd34d;
        }

        .status-chip-error {
            background-color: #fee2e2;
            color: #991b1b;
            border: 1px solid #fca5a5;
        }

        .dashboard-nav-container {
            background: rgba(15, 23, 42, 0.92);
            border: 1px solid rgba(148, 163, 184, 0.35);
            border-radius: 18px;
            padding: 16px 20px;
            margin: 18px 0 20px 0;
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.22);
        }

        .dashboard-nav-title {
            font-size: 15px;
            font-weight: 700;
            color: #e5e7eb;
            margin-bottom: 8px;
        }

        .content-panel {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 22px 24px;
            margin: 18px 0 24px 0;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
        }

        .content-panel-title {
            font-size: 22px;
            font-weight: 800;
            color: #111827;
            margin-bottom: 6px;
        }

        .content-panel-subtitle {
            font-size: 14px;
            color: #64748b;
            margin-bottom: 16px;
        }

        .debug-panel {
            background: #f8fafc;
            border: 1px dashed #94a3b8;
            border-radius: 16px;
            padding: 18px 20px;
            margin: 16px 0;
        }

        .small-helper-text {
            font-size: 13px;
            color: #64748b;
            margin-top: 6px;
        }

        div[data-testid="stRadio"] > div {
            gap: 12px;
        }

        div[data-testid="stRadio"] label {
            background: rgba(15, 23, 42, 0.92) !important;
            border: 1px solid rgba(148, 163, 184, 0.45) !important;
            border-radius: 999px !important;
            padding: 8px 16px !important;
            min-width: fit-content;
            color: #e5e7eb !important;
        }

        div[data-testid="stRadio"] label p {
            color: #e5e7eb !important;
            font-weight: 600;
        }
        
        </style>
        """,
        unsafe_allow_html=True,
    )