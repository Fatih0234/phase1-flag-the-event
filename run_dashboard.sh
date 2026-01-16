#!/bin/bash
# Launch the Streamlit dashboard for error analysis

source .venv/bin/activate
streamlit run bikeclf/phase1/dashboard.py --server.port 8501 --server.address localhost
