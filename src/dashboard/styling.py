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
            background: linear-gradient(135deg, #f8fafc 0%, #eef6ff 100%);
            border: 1px solid #dbeafe;
            border-radius: 18px;
            padding: 22px 26px;
            margin-bottom: 26px;
        }

        .status-title {
            font-size: 22px;
            font-weight: 750;
            color: #111827;
            margin-bottom: 6px;
        }

        .status-subtitle {
            color: #64748b;
            font-size: 15px;
            margin-bottom: 14px;
        }

        .status-chip {
            display: inline-block;
            padding: 8px 14px;
            margin: 4px 6px 4px 0;
            border-radius: 999px;
            background-color: #dcfce7;
            color: #166534;
            border: 1px solid #86efac;
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
        </style>
        """,
        unsafe_allow_html=True,
    )