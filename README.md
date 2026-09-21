# Expert Diet Planner

A simple, AI-powered diet planning application using Streamlit and Google GenAI (Gemini).

## Installation

1. Make sure you have [Python](https://www.python.org/downloads/) installed (version 3.10 or newer is recommended).
2. Open your terminal or command prompt in this folder.
3. Install the required dependencies by running:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

Run the following command in your terminal:
```bash
streamlit run diet_planner.py
```
This will automatically open the application in your default web browser (or you can navigate to `http://localhost:8501`).

## Setup

- The application uses Google's Gemini AI. You will need a **FREE API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey).
- You can either enter the key directly in the app's UI, or set it as an environment variable (`GOOGLE_API_KEY`) on your system.
- If you just want to test the UI without an API key, check the **"Run in Demo Mode"** box in the app.

## Files Included
- `diet_planner.py`: The main application code.
- `requirements.txt`: The list of Python libraries needed to run the app.
- `run_app.bat`: A quick-start Windows script to install dependencies and run the app.
