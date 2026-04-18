import json
import base64
import requests
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivy.utils import platform

KV_INTERFACE = """
<FitnessRoot>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.05, 0.05, 0.05, 1
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: "PERSONAL OPTIMIZER v1.1"
        size_hint_y: 0.1
        color: 0, 1, 0, 1
        font_size: '20sp'
        bold: True

    Camera:
        id: camera
        resolution: (640, 480)
        play: True
        size_hint_y: 0.5

    Button:
        text: "ANALYZE WORKOUT"
        size_hint_y: 0.15
        background_color: 0, 0.7, 0.3, 1
        on_press: root.capture_and_analyze()

    ScrollView:
        size_hint_y: 0.25
        padding: [15, 15]
        Label:
            id: advice_output
            text: "System Ready.\\nWaiting for Treadmill Data..."
            text_size: self.width, None
            halign: 'center'
            size_hint_y: None
            height: self.texture_size[1]
            color: 0.9, 0.9, 0.9, 1
"""

class FitnessRoot(BoxLayout):
    def capture_and_analyze(self):
        self.ids.advice_output.text = "[ PROCESSING: CONNECTING TO BRAIN... ]"
        photo_path = "workout_capture.png"
        self.ids.camera.export_to_png(photo_path)
        
        # Run API call in a background thread so the app doesn't freeze
        Clock.schedule_once(lambda dt: threading.Thread(target=self.call_gemini_api, args=(photo_path,)).start(), 1.0)

    @mainthread
    def update_ui(self, message):
        # Update the text on the main screen safely
        self.ids.advice_output.text = message

    def call_gemini_api(self, path):
        api_key = "AQ.Ab8RN6JDhwc4Jvn1kTrsJUN4cqTPY8Sx_-nVS0rOzSRyh_8eBg"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        try:
            # Convert image to Base64
            with open(path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            # Build the lightweight REST payload
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "Analyze this treadmill display. Extract Distance, Time, and Speed. User Profile: 89kg, 169cm. Goal: 75kg. Current Routine: 3km run + 1.2km walk (15% incline). Provide one specific technical optimization for tomorrow's session."},
                        {"inline_data": {"mime_type": "image/png", "data": encoded_string}}
                    ]
                }]
            }
            headers = {'Content-Type': 'application/json'}

            # Send the request
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()
                advice = result['candidates'][0]['content']['parts'][0]['text']
                self.update_ui(advice)
            else:
                self.update_ui(f"API ERROR: {response.status_code}\\n{response.text}")

        except Exception as e:
            self.update_ui(f"CONNECTION ERROR: {str(e)}")

class PersonalOptimizerApp(App):
    def build(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            # Ask for permissions right as the app boots
            request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.INTERNET])
            
        Builder.load_string(KV_INTERFACE)
        return FitnessRoot()

if __name__ == '__main__':
    PersonalOptimizerApp().run()
