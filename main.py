import json
import base64
import requests
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivy.utils import platform

# V2.1 DASHBOARD WITH STREAKS
KV_INTERFACE = """
<FitnessRoot>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.03, 0.03, 0.03, 1
        Rectangle:
            pos: self.pos
            size: self.size

    # HEADER
    BoxLayout:
        size_hint_y: 0.1
        padding: [15, 10]
        Label:
            text: "Good evening, Gopimadhav"
            font_size: '22sp'
            bold: True
            text_size: self.size
            halign: 'left'
            valign: 'middle'

    ScrollView:
        size_hint_y: 0.9
        BoxLayout:
            orientation: 'vertical'
            padding: 15
            spacing: 15
            size_hint_y: None
            height: self.minimum_height

            # HEALTH OVERVIEW CARD
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: 160
                padding: 15
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [15]
                Label:
                    text: "Health overview"
                    bold: True
                    font_size: '18sp'
                    text_size: self.size
                    halign: 'left'
                GridLayout:
                    cols: 2
                    Label:
                        text: "[color=00ff00]13612[/color] / 10000 steps"
                        markup: True
                        text_size: self.size
                        halign: 'left'
                    Label:
                        text: "[color=ffff00]10.88[/color] / 10.00 km"
                        markup: True
                        text_size: self.size
                        halign: 'left'
                    Label:
                        text: "[color=ff5555]810[/color] / 400 kcal"
                        markup: True
                        text_size: self.size
                        halign: 'left'
                    Label:
                        text: "Peak HR: 193 bpm"
                        color: 1, 0.3, 0.3, 1
                        text_size: self.size
                        halign: 'left'

            # GOALS CARD
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: 110
                padding: 15
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [15]
                Label:
                    text: "Weight Goal: 89kg -> 75kg"
                    bold: True
                    text_size: self.size
                    halign: 'left'
                Label:
                    text: "Predicted: August 1, 2026"
                    color: 0.5, 0.8, 1, 1
                    text_size: self.size
                    halign: 'left'
                Label:
                    text: "Trend: On Track (-0.5kg/week)"
                    color: 0, 1, 0, 1
                    text_size: self.size
                    halign: 'left'

            # STREAK CARD (NEW)
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: 100
                padding: 15
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [15]
                Label:
                    text: "Daily Streak 🔥"
                    bold: True
                    text_size: self.size
                    halign: 'left'
                GridLayout:
                    cols: 3
                    Label:
                        text: "[b]Week[/b]\\n[color=ffaa00]5 / 7[/color]"
                        markup: True
                        halign: 'center'
                    Label:
                        text: "[b]Month[/b]\\n[color=00ccff]22 / 30[/color]"
                        markup: True
                        halign: 'center'
                    Label:
                        text: "[b]Year[/b]\\n[color=cc66ff]145 Days[/color]"
                        markup: True
                        halign: 'center'

            # ON-DEMAND CAMERA (Hidden by default)
            BoxLayout:
                id: camera_container
                orientation: 'vertical'
                size_hint_y: None
                height: 0
                opacity: 0
                Camera:
                    id: camera
                    resolution: (640, 480)
                    play: False

            # DYNAMIC CAPTURE BUTTON (Hidden by default)
            Button:
                id: capture_btn
                text: "CAPTURE"
                size_hint_y: None
                height: 0
                opacity: 0
                background_color: 0, 0.8, 0.3, 1
                on_press: root.capture_and_analyze()

            # ACTION BUTTONS
            GridLayout:
                cols: 2
                spacing: 10
                size_hint_y: None
                height: 60
                Button:
                    text: "📷 Treadmill"
                    background_color: 0.2, 0.6, 1, 1
                    on_press: root.toggle_camera('treadmill')
                Button:
                    text: "🥗 Meal Planner"
                    background_color: 1, 0.6, 0.2, 1
                    on_press: root.toggle_camera('meal')

            # AI OUTPUT CONSOLE
            Label:
                id: advice_output
                text: "Select an option above."
                text_size: self.width, None
                halign: 'center'
                size_hint_y: None
                height: max(self.texture_size[1], 100)
                color: 0.8, 0.8, 0.8, 1
"""

class FitnessRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_mode = None

    def toggle_camera(self, mode):
        self.current_mode = mode
        camera_container = self.ids.camera_container
        capture_btn = self.ids.capture_btn
        camera = self.ids.camera

        # Expand the camera and button
        camera_container.height = 300
        camera_container.opacity = 1
        capture_btn.height = 60
        capture_btn.opacity = 1
        camera.play = True
        
        # Change button text based on context
        if mode == 'treadmill':
            capture_btn.text = "ANALYZE TREADMILL"
            self.ids.advice_output.text = "Point camera at treadmill display..."
        elif mode == 'meal':
            capture_btn.text = "ESTIMATE CALORIES"
            self.ids.advice_output.text = "Point camera at food or menu..."

    def capture_and_analyze(self):
        self.ids.advice_output.text = "[ PROCESSING: CONNECTING TO BRAIN... ]"
        
        # Take picture and immediately hide camera to save battery
        photo_path = "capture.png"
        self.ids.camera.export_to_png(photo_path)
        
        self.ids.camera.play = False
        self.ids.camera_container.height = 0
        self.ids.camera_container.opacity = 0
        self.ids.capture_btn.height = 0
        self.ids.capture_btn.opacity = 0
        
        Clock.schedule_once(lambda dt: threading.Thread(target=self.call_gemini_api, args=(photo_path, self.current_mode)).start(), 0.5)

    @mainthread
    def update_ui(self, message):
        self.ids.advice_output.text = message

    def call_gemini_api(self, path, mode):
        api_key = "AQ.Ab8RN6JDhwc4Jvn1kTrsJUN4cqTPY8Sx_-nVS0rOzSRyh_8eBg"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        # Determine the AI's personality/instructions based on the button clicked
        if mode == 'treadmill':
            prompt = "Analyze this treadmill display. Extract Distance, Time, and Speed. Provide one specific technical optimization to reach the 75kg goal faster."
        else:
            prompt = "Analyze this image of food or a menu. Identify the main items and provide a rough calorie estimation. Is this meal aligned with a weight loss goal from 89kg to 75kg?"

        try:
            with open(path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/png", "data": encoded_string}}
                    ]
                }]
            }
            headers = {'Content-Type': 'application/json'}

            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()
                advice = result['candidates'][0]['content']['parts'][0]['text']
                self.update_ui(advice)
            else:
                self.update_ui(f"API ERROR: {response.status_code}")

        except Exception as e:
            self.update_ui(f"CONNECTION ERROR: {str(e)}")

class PersonalOptimizerApp(App):
    def build(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.INTERNET])
            
        Builder.load_string(KV_INTERFACE)
        return FitnessRoot()

if __name__ == '__main__':
    PersonalOptimizerApp().run()
