import json
import base64
import requests
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivy.animation import Animation
from kivy.utils import platform
from plyer import filechooser

# V4.0 REACT NATIVE INSPIRED UI
KV_INTERFACE = """
#:import get_color kivy.utils.get_color_from_hex

<ProgressRing>:
    canvas:
        # Background Track
        Color:
            rgba: get_color('#334155')
        Line:
            circle: (self.center_x, self.center_y, (self.width/2) - root.radius_offset)
            width: root.thickness
        # Animated Foreground
        Color:
            rgba: root.ring_color
        Line:
            circle: (self.center_x, self.center_y, (self.width/2) - root.radius_offset, 0, root.angle)
            width: root.thickness
            cap: 'round'

<RNCard@BoxLayout>:
    orientation: 'vertical'
    padding: 16
    canvas.before:
        Color:
            rgba: get_color('#1E293B')
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [16]

<ActionBtn@ButtonBehavior+BoxLayout>:
    bg_color: get_color('#22C55E')
    text: "Button"
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]
    Label:
        text: root.text
        bold: True
        color: 0, 0, 0, 1

<FitnessRoot>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: get_color('#0F172A')
        Rectangle:
            pos: self.pos
            size: self.size

    ScrollView:
        size_hint_y: 0.9
        BoxLayout:
            orientation: 'vertical'
            padding: 16
            spacing: 16
            size_hint_y: None
            height: self.minimum_height

            Label:
                text: "Good Evening 👋"
                font_size: '24sp'
                bold: True
                size_hint_y: None
                height: 40
                text_size: self.size
                halign: 'left'
                valign: 'middle'

            # 🔹 ANIMATED DAILY ACTIVITY RINGS
            RNCard:
                size_hint_y: None
                height: 220
                Label:
                    text: "Daily Activity"
                    color: get_color('#94A3B8')
                    size_hint_y: 0.15
                    text_size: self.size
                    halign: 'left'
                FloatLayout:
                    ProgressRing:
                        id: ring_1
                        ring_color: get_color('#22C55E')
                        radius_offset: 0
                        thickness: 8
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        size_hint: None, None
                        size: 140, 140
                    ProgressRing:
                        id: ring_2
                        ring_color: get_color('#38BDF8')
                        radius_offset: 14
                        thickness: 8
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        size_hint: None, None
                        size: 140, 140
                    ProgressRing:
                        id: ring_3
                        ring_color: get_color('#F97316')
                        radius_offset: 28
                        thickness: 8
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        size_hint: None, None
                        size: 140, 140
                    Label:
                        text: "Daily"
                        font_size: '18sp'
                        bold: True
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

            # 🔹 AI COACH PANEL (Replaces terminal output)
            RNCard:
                size_hint_y: None
                height: max(100, advice_output.texture_size[1] + 40)
                Label:
                    text: "AI Coach"
                    color: get_color('#94A3B8')
                    size_hint_y: None
                    height: 20
                    text_size: self.size
                    halign: 'left'
                Label:
                    id: advice_output
                    text: "Ready to analyze your workout or meal..."
                    color: 1, 1, 1, 1
                    text_size: self.width, None
                    size_hint_y: None
                    height: self.texture_size[1]
                    halign: 'left'

            # 🔹 STATS GRID
            GridLayout:
                cols: 2
                spacing: 16
                size_hint_y: None
                height: 80
                RNCard:
                    Label:
                        text: "Steps"
                        color: get_color('#94A3B8')
                        text_size: self.size
                        halign: 'left'
                    Label:
                        text: "8,230"
                        font_size: '18sp'
                        bold: True
                        text_size: self.size
                        halign: 'left'
                RNCard:
                    Label:
                        text: "Calories"
                        color: get_color('#94A3B8')
                        text_size: self.size
                        halign: 'left'
                    Label:
                        text: "520 kcal"
                        font_size: '18sp'
                        bold: True
                        text_size: self.size
                        halign: 'left'

            # 🔹 ACTION BUTTONS (Replaces "Start Workout")
            RNCard:
                size_hint_y: None
                height: 180
                spacing: 12
                Label:
                    text: "Log Progress"
                    font_size: '18sp'
                    bold: True
                    size_hint_y: None
                    height: 25
                    text_size: self.size
                    halign: 'left'
                GridLayout:
                    cols: 2
                    spacing: 10
                    ActionBtn:
                        text: "📷 Camera"
                        bg_color: get_color('#22C55E')
                        on_press: root.toggle_camera('treadmill')
                    ActionBtn:
                        text: "🖼️ Gallery"
                        bg_color: get_color('#15803D')
                        on_press: root.open_gallery('treadmill')
                    ActionBtn:
                        text: "🥗 Meal Cam"
                        bg_color: get_color('#38BDF8')
                        on_press: root.toggle_camera('meal')
                    ActionBtn:
                        text: "🍽️ Meal Gal"
                        bg_color: get_color('#0369A1')
                        on_press: root.open_gallery('meal')

            # 🔹 HIDDEN CAMERA WIDGETS
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
            ActionBtn:
                id: capture_btn
                text: "SNAP PHOTO"
                size_hint_y: None
                height: 0
                opacity: 0
                bg_color: get_color('#F97316')
                on_press: root.capture_and_analyze()

    # 🔹 BOTTOM NAVIGATION
    BoxLayout:
        size_hint_y: 0.1
        canvas.before:
            Color:
                rgba: get_color('#1E293B')
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "Home"
            color: 1, 1, 1, 1
            bold: True
        Label:
            text: "Workout"
            color: get_color('#94A3B8')
        Label:
            text: "Stats"
            color: get_color('#94A3B8')
        Label:
            text: "Profile"
            color: get_color('#94A3B8')
"""

class ProgressRing(Widget):
    angle = NumericProperty(0)
    ring_color = ListProperty([1, 1, 1, 1])
    radius_offset = NumericProperty(0)
    thickness = NumericProperty(10)

    def animate_to(self, target_angle):
        # Creates the smooth fill effect
        anim = Animation(angle=target_angle, duration=1.2, t='out_quad')
        anim.start(self)

class FitnessRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_mode = None
        # Start ring animations half a second after the app boots
        Clock.schedule_once(self.trigger_animations, 0.5)

    def trigger_animations(self, dt):
        # 360 degrees is a full circle. (e.g., 270 is 75%)
        self.ids.ring_1.animate_to(270)  
        self.ids.ring_2.animate_to(216)  
        self.ids.ring_3.animate_to(144)  

    def open_gallery(self, mode):
        self.current_mode = mode
        self.ids.advice_output.text = "Opening File Manager..."
        try:
            filechooser.open_file(on_selection=self.handle_selection)
        except Exception as e:
            self.update_ui(f"Gallery Error: {str(e)}")

    def handle_selection(self, selection):
        if not selection:
            self.update_ui("Gallery upload cancelled.")
            return
        photo_path = selection[0]
        self.update_ui("[ PROCESSING: ANALYZING IMAGE... ]")
        Clock.schedule_once(lambda dt: threading.Thread(target=self.call_gemini_api, args=(photo_path, self.current_mode)).start(), 0.5)

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
            capture_btn.text = "ANALYZE TREADMILL"
            self.ids.advice_output.text = "Camera Active..."
        elif mode == 'meal':
            capture_btn.text = "ESTIMATE MEAL"
            self.ids.advice_output.text = "Camera Active..."

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
            request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE, Permission.INTERNET])
        Builder.load_string(KV_INTERFACE)
        return FitnessRoot()

if __name__ == '__main__':
    PersonalOptimizerApp().run()
