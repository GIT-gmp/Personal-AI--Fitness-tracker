# Personal Optimizer

A mobile-first fitness and health tracking application built with Kivy (Python).

## Purpose
Helps users reach weight loss goals (89kg -> 75kg) by integrating AI-powered analysis for treadmill workouts and meal planning via Google Gemini AI.

## Tech Stack
- **Language**: Python 3.12
- **UI Framework**: Kivy 2.3.1
- **AI Integration**: Google Gemini 1.5 Flash (via REST API with `requests`)
- **Image Processing**: Pillow

## Features
- Dashboard with health metrics (steps, distance, calories, heart rate)
- Weight goal tracking with streak counters
- Treadmill display AI analysis (via camera capture)
- Meal/food calorie estimation (via camera capture)

## Project Structure
- `main.py` - Entry point with all UI (KV language string) and application logic
- `requirements.txt` - Python dependencies
- `buildozer.spec` - Android build configuration

## Running the App
The app runs as a desktop GUI application using VNC. The workflow command is:
```
python main.py
```

## Notes
- The `Camera` widget is instantiated dynamically (not in the KV layout) to allow the app to run in environments without a physical camera
- The Gemini API key is embedded in the source; move to an environment variable for production
- Originally designed for Android (buildozer), but runs on desktop via Kivy's SDL2 backend
