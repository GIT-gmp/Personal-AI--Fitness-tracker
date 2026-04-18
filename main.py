import json
import base64
import requests
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivy.utils import platform

# V3.0 PREMIUM DARK THEME DASHBOARD
KV_INTERFACE = """
<ActionBtn@ButtonBehavior+BoxLayout>:
    orientation: 'vertical'
    padding: [10, 10]
    canvas.before:
        Color:
            rgba: 0.15, 0.15, 0.15, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10]
    title_text: ''
    sub_text: ''
    Label:
        text: root.title_text
        bold: True
        font_size: '14sp'
        text_size: self.size
        halign: 'left'
        valign: 'bottom'
    Label:
        text: root.sub_text
        font_size: '11sp'
        color: 0.6, 0.6, 0.6, 1
        text_size: self.size
        halign: 'left'
        valign: 'top'

<FitnessRoot>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.02, 0.02, 0.02, 1
        Rectangle:
            pos: self.pos
            size: self.size

    # HEADER
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.12
        padding: [15, 20, 15, 5]
        Label:
            text: "Good evening, Gopimadhav"
            font_size: '22sp'
            bold: True
            text_size: self.size
            halign: 'left'
            valign: 'bottom'
        Label:
            text: "Last synced [color=cccccc]Just Now[/color]"
            markup: True
            font_size: '12sp'
            color: 0.5, 0.5, 0.5, 1
            text_size: self.size
            halign: 'left'
            valign: 'top'

    ScrollView:
        size_hint_y: 0.88
        BoxLayout:
            orientation: 'vertical'
            padding: [15, 10, 15, 20]
            spacing: 20
            size_hint_y: None
            height: self.minimum_height

            # CARD 1: WORKOUT INSIGHTS
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: 220
                padding: 15
                spacing: 10
                canvas.before:
                    Color:
                        rgba: 0.08, 0.08, 0.08, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [15]
                
                # Title
                Label:
                    text: "Workout Insights & Progress"
                    font_size: '16sp'
                    bold: True
                    size_hint_y: 0.2
                    text_size: self.size
                    halign: 'left'

                # Graph & Stats Area
                BoxLayout:
                    size_hint_y: 0.5
                    spacing: 10
                    # Simulated Graph Box
                    BoxLayout:
                        size_hint_x: 0.5
                        canvas.before:
                            Color:
                                rgba: 0.15, 0.25, 0.4, 0.5
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [5]
                            Color:
                                rgba: 0.3, 0.5, 1, 1
                            Line:
                                points: [self.x, self.y+10, self.x+20, self.y+30, self.x+40, self.y+20, self.x+60, self.y+60, self.x+80, self.y+40, self.x+100, self.y+70, self.x+120, self.y+30]
                                width: 1.5
                    # Stats Text
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_x: 0.5
                        Label:
                            text: "Walking: 5200 steps, 310 kcal\\nWalking: 4200 steps, 310 kcal\\nWalking: 3700 steps, 310 kcal"
                            font_size: '10sp'
                            color: 0.7, 0.7, 0.7, 1
                            text_size: self.size
                            halign: 'left'

                # Calories Bar
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: 0.3
                    Label:
                        text: "Calories burned"
                        font_size: '12sp'
                        text_size: self.size
                        halign: 'left'
                    BoxLayout:
                        size_hint_y: None
                        height: 8
                        canvas.before:
                            Color:
                                rgba: 0.2, 0.2, 0.2, 1
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [4]
                            Color:
                                rgba: 1, 0.3, 0.2, 1
                            RoundedRectangle:
                                pos: self.pos
                                size: (self.width * 0.8, self.height) # 80% fill
                                radius: [4]
                    BoxLayout:
                        Label:
                            text: "[color=ff5555]810[/color]/400"
                            markup: True
                            font_size: '12sp'
                            text_size: self.size
                            halign: 'left'
                        Label:
                            text: "400 goal"
                            font_size: '12sp'
                            color: 0.6, 0.6, 0.6, 1
                            text_size: self.size
                            halign: 'right'

            # CARD 2: FITNESS GOALS & MEAL PLAN
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: 380
                padding: 15
                spacing: 12
                canvas.before:
                    Color:
                        rgba: 0.08, 0.08, 0.08, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [15]

                Label:
                    text: "Fitness Goals & Meal Plan"
                    font_size: '16sp'
                    bold: True
                    size_hint_y: None
                    height: 25
                    text_size: self.size
                    halign: 'left'

                # Weight Goal Bar
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: 50
                    BoxLayout:
                        Label:
                            text: "Weight Goal"
                            font_size: '13sp'
                            text_size: self.size
                            halign: 'left'
                        Label:
                            text: "Target date: Dec. 23"
                            font_size: '11sp'
                            color: 0.6, 0.6, 0.6, 1
                            text_size: self.size
                            halign: 'right'
                    BoxLayout:
                        size_hint_y: None
                        height: 8
                        canvas.before:
                            Color:
                                rgba: 0.2, 0.2, 0.2, 1
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [4]
                            Color:
                                rgba: 0.5, 0.9, 0.3, 1
                            RoundedRectangle:
                                pos: self.pos
                                size: (self.width * 0.6, self.height) # 60% fill
                                radius: [4]
                    BoxLayout:
                        Label:
                            text: "80kg"
                            font_size: '11sp'
                            text_size: self.size
                            halign: 'left'
                        Label:
                            text: "70kg"
                            font_size: '11sp'
                            text_size: self.size
                            halign: 'right'

                Label:
                    text: "Goal Predictor: 10-12 weeks at current progress"
                    font_size: '11sp'
                    color: 0.6, 0.6, 0.6, 1
                    size_hint_y: None
                    height: 20
                    text_size: self.size
                    halign: 'left'

                # Log Progress Pictures
                Label:
                    text: "Log Progress Pictures"
                    font_size: '14sp'
                    bold: True
                    size_hint_y: None
                    height: 25
                    text_size: self.size
                    halign: 'left'
                GridLayout:
                    cols: 2
                    spacing: 10
                    size_hint_y: None
                    height: 50
                    ActionBtn:
                        title_text: "[ Gallery ]"
                        sub_text: "Upload picture"
                        on_press: root.ui_message("Gallery upload requires v3.1 update.")
                    ActionBtn:
                        title_text: "[ Camera ]"
                        sub_text: "Take a picture"
                        on_press: root.toggle_camera('treadmill')

                # Meal Plan & Logging
                Label:
                    text: "Meal Plan & Logging"
                    font_size: '14sp'
                    bold: True
                    size_hint_y: None
                    height: 25
                    text_size: self.size
                    halign: 'left'
                GridLayout:
                    cols: 2
                    spacing: 10
                    size_hint_y: None
                    height: 50
                    ActionBtn:
                        title_text: "[ Menu ]"
                        sub_text: "Upload menu picture"
                        on_press: root.ui_message("Menu upload requires v3.1 update.")
                    ActionBtn:
                        title_text: "[ Food Plate ]"
                        sub_text: "Take food picture"
                        on_press: root.toggle_camera('meal')

            # LIVE CAMERA COMPONENT
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
            Button:
                id: capture_btn
                text: "SNAP PHOTO"
                size_hint_y: None
                height: 0
                opacity: 0
                background_color: 0, 0.6, 1, 1
                on_press: root.capture_and_analyze()

            # AI OUTPUT CONSOLE
            Label:
                id: advice_output
                text: "System Ready."
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

    def ui_message(self, msg):
        self.ids.advice_output.text = msg

    def toggle_camera(self, mode):
        self.current_mode = mode
        camera_container = self.ids.camera_container
        capture_btn = self.ids.capture_btn
        camera = self.ids.camera

        camera_container.height = 300
        camera_container.opacity = 1
        capture_btn.height = 50
        capture_btn.opacity = 1
        camera.play = True
        
        if mode == 'treadmill':
            capture_btn.text = "ANALYZE PROGRESS"
            self.ids.advice_output.text = "Camera Active: Point at treadmill..."
        elif mode == 'meal':
            capture_btn.text = "ESTIMATE MEAL"
            self.ids.advice_output.text = "Camera Active: Point at food plate..."

    def capture_and_analyze(self):
        self.ids.advice_output.text = "[ PROCESSING: ANALYZING WITH AI... ]"
        
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

        if mode == 'treadmill':
            prompt = "Analyze this treadmill display. Extract Distance, Time, and Speed. Provide one specific optimization to reach the target weight."
        else:
            prompt = "Analyze this image of food. Identify the main items and provide a rough calorie estimation. Is this aligned with a weight loss goal?"

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
