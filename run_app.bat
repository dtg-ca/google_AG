@echo off
echo Installing requirements...
pip install -r requirements.txt
echo.
echo Starting Expert Diet Planner...
streamlit run diet_planner.py
pause
