#!/bin/sh

uvicorn backend.app:app --host 0.0.0.0 --port 8000 &
streamlit run frontend/frontend.py --server.port 8501 --server.address 0.0.0.0
