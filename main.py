from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
import google.generativeai as genai

# UI DESIGN (Kivy Language)
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
        text: "PERSONAL OPTIMIZER v1.0"
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
        camera = self.ids.camera
        photo_path = "workout_capture.png"
        
        # Save the image from the camera feed
        camera.export_to_png(photo_path)
        
        # Give the system 1 second to write the file before reading it
        Clock.schedule_once(lambda dt: self.call_gemini_api(photo_path), 1.0)

    def call_gemini_api(self, path):
        # API CONFIG (The key you provided earlier)
        genai.configure(api_key="AQ.Ab8RN6JDhwc4Jvn1kTrsJUN4cqTPY8Sx_-nVS0rOzSRyh_8eBg")
        model = genai.GenerativeModel('gemini-1.5-flash')

        try:
            # The "Developer Prompt" tailored to your fitness goals
            prompt = (
                "Analyze this treadmill display. Extract Distance, Time, and Speed. "
                "User Profile: 89kg, 169cm. Goal: 75kg. "
                "Current Routine: 3km run + 1.2km walk (15% incline). "
                "Based on this photo, provide one specific technical optimization for tomorrow's session."
            )
            
            with open(path, 'rb') as f:
                img_data = f.read()
            
            response = model.generate_content([
                prompt,
                {'mime_type': 'image/png', 'data': img_data}
            ])
            
            self.ids.advice_output.text = response.text
        except Exception as e:
            self.ids.advice_output.text = f"CONNECTION ERROR: {str(e)}"

class PersonalOptimizerApp(App):
    def build(self):
        # Ensure camera permissions are handled on Android
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE])
            
        Builder.load_string(KV_INTERFACE)
        return FitnessRoot()

if __name__ == '__main__':
    PersonalOptimizerApp().run()
