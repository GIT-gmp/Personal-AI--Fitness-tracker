import json
import base64
import os
import requests
import threading
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivy.utils import platform
from PIL import Image as PILImage

HISTORY_FILE = "analysis_history.json"

# V2.4 CLEAN UI DASHBOARD WITH UPLOAD + HISTORY
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
            spacing: 20
            size_hint_y: None
            height: self.minimum_height

            # HEALTH OVERVIEW CARD
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: 240
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
                    size_hint_y: 0.3
                    text_size: self.size
                    halign: 'left'
                GridLayout:
                    cols: 1
                    spacing: 5
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
                height: 140
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

            # STREAK CARD
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: 120
                padding: 15
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [15]
                Label:
                    text: "Daily Streak"
                    bold: True
                    text_size: self.size
                    halign: 'left'
                    size_hint_y: 0.4
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

            # ON-DEMAND CAMERA CONTAINER (camera added dynamically)
            BoxLayout:
                id: camera_container
                orientation: 'vertical'
                size_hint_y: None
                height: 0
                opacity: 0

            # DYNAMIC CAPTURE BUTTON
            Button:
                id: capture_btn
                text: "CAPTURE"
                size_hint_y: None
                height: 0
                opacity: 0
                background_color: 0, 0.8, 0.3, 1
                on_press: root.capture_and_analyze()

            # ACTION BUTTONS (camera)
            GridLayout:
                cols: 2
                spacing: 10
                size_hint_y: None
                height: 60
                Button:
                    text: "Treadmill"
                    background_color: 0.2, 0.6, 1, 1
                    on_press: root.toggle_camera('treadmill')
                Button:
                    text: "Meal Planner"
                    background_color: 1, 0.6, 0.2, 1
                    on_press: root.toggle_camera('meal')

            # UPLOAD + HISTORY BUTTONS
            GridLayout:
                cols: 2
                spacing: 10
                size_hint_y: None
                height: 55
                Button:
                    text: "Upload Picture"
                    background_color: 0.5, 0.2, 0.9, 1
                    bold: True
                    on_press: root.open_upload_picker()
                Button:
                    text: "View History"
                    background_color: 0.15, 0.5, 0.45, 1
                    bold: True
                    on_press: root.open_history_popup()

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


# ── History persistence ────────────────────────────────────────────────────────

def load_history():
    if not os.path.isfile(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_history_entry(mode, result_text):
    entries = load_history()
    entries.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mode": "Treadmill" if mode == "treadmill" else "Meal",
        "result": result_text,
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(entries, f, indent=2)


# ── Main widget ────────────────────────────────────────────────────────────────

class FitnessRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_mode = None
        self._camera = None
        self._pending_upload_path = None

    # ── Camera helpers ─────────────────────────────────────────────────────────

    def _get_or_create_camera(self):
        if self._camera is not None:
            return self._camera
        try:
            from kivy.uix.camera import Camera
            cam = Camera(resolution=(640, 480), play=False)
            self.ids.camera_container.add_widget(cam)
            self._camera = cam
        except Exception as e:
            self.ids.advice_output.text = f"Camera unavailable: {str(e)}"
        return self._camera

    def toggle_camera(self, mode):
        self.current_mode = mode
        camera = self._get_or_create_camera()
        if camera is None:
            return

        self.ids.camera_container.height = 300
        self.ids.camera_container.opacity = 1
        self.ids.capture_btn.height = 60
        self.ids.capture_btn.opacity = 1
        camera.play = True

        if mode == 'treadmill':
            self.ids.capture_btn.text = "ANALYZE TREADMILL"
            self.ids.advice_output.text = "Point camera at treadmill display..."
        elif mode == 'meal':
            self.ids.capture_btn.text = "ESTIMATE CALORIES"
            self.ids.advice_output.text = "Point camera at food or menu..."

    def capture_and_analyze(self):
        camera = self._camera
        if camera is None:
            self.ids.advice_output.text = "No camera available."
            return

        self.ids.advice_output.text = "[ PROCESSING: CONNECTING TO BRAIN... ]"

        photo_path = "capture.png"
        camera.export_to_png(photo_path)

        camera.play = False
        self.ids.camera_container.height = 0
        self.ids.camera_container.opacity = 0
        self.ids.capture_btn.height = 0
        self.ids.capture_btn.opacity = 0

        Clock.schedule_once(
            lambda dt: threading.Thread(
                target=self.call_gemini_api,
                args=(photo_path, self.current_mode)
            ).start(),
            0.5
        )

    # ── Upload helpers ─────────────────────────────────────────────────────────

    def open_upload_picker(self):
        content = BoxLayout(orientation='vertical', spacing=8, padding=10)

        chooser = FileChooserIconView(
            filters=['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif', '*.webp'],
            path=os.path.expanduser('~'),
        )
        content.add_widget(chooser)

        btn_row = BoxLayout(size_hint_y=None, height=50, spacing=8)
        select_btn = Button(text='Select', background_color=(0.2, 0.7, 0.3, 1))
        cancel_btn = Button(text='Cancel', background_color=(0.7, 0.2, 0.2, 1))
        btn_row.add_widget(select_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup = Popup(title='Select an Image', content=content, size_hint=(0.95, 0.9))
        select_btn.bind(on_press=lambda _: self._on_file_selected(chooser.selection, popup))
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _on_file_selected(self, selection, file_popup):
        if not selection or not os.path.isfile(selection[0]):
            self.ids.advice_output.text = "No valid file selected."
            file_popup.dismiss()
            return

        self._pending_upload_path = selection[0]
        file_popup.dismiss()
        self._open_mode_picker()

    def _open_mode_picker(self):
        content = BoxLayout(orientation='vertical', spacing=12, padding=15)
        content.add_widget(Label(
            text='What would you like to analyze?',
            font_size='16sp', size_hint_y=None, height=40,
        ))

        treadmill_btn = Button(text='Treadmill Display', background_color=(0.2, 0.6, 1, 1), size_hint_y=None, height=55)
        meal_btn = Button(text='Meal / Food', background_color=(1, 0.6, 0.2, 1), size_hint_y=None, height=55)
        cancel_btn = Button(text='Cancel', background_color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=45)

        content.add_widget(treadmill_btn)
        content.add_widget(meal_btn)
        content.add_widget(cancel_btn)

        popup = Popup(title='Analysis Mode', content=content, size_hint=(0.8, 0.5))
        treadmill_btn.bind(on_press=lambda _: self._run_upload_analysis('treadmill', popup))
        meal_btn.bind(on_press=lambda _: self._run_upload_analysis('meal', popup))
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _run_upload_analysis(self, mode, popup):
        popup.dismiss()
        path = self._pending_upload_path
        if not path:
            return

        self.ids.advice_output.text = "[ PROCESSING: CONNECTING TO BRAIN... ]"

        converted_path = "uploaded_image.png"
        try:
            img = PILImage.open(path).convert('RGB')
            img.save(converted_path, 'PNG')
        except Exception as e:
            self.ids.advice_output.text = f"Image error: {str(e)}"
            return

        threading.Thread(
            target=self.call_gemini_api,
            args=(converted_path, mode)
        ).start()

    # ── History popup ──────────────────────────────────────────────────────────

    def open_history_popup(self):
        entries = load_history()

        outer = BoxLayout(orientation='vertical', spacing=8, padding=8)

        if not entries:
            outer.add_widget(Label(
                text="No analysis history yet.\nRun a Treadmill or Meal analysis to see results here.",
                halign='center',
                color=(0.7, 0.7, 0.7, 1),
            ))
        else:
            scroll = ScrollView()
            inner = BoxLayout(
                orientation='vertical',
                spacing=10,
                padding=5,
                size_hint_y=None,
            )
            inner.bind(minimum_height=inner.setter('height'))

            # Newest first
            for entry in reversed(entries):
                card = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    padding=10,
                    spacing=4,
                )

                mode_color = (0.2, 0.6, 1, 1) if entry['mode'] == 'Treadmill' else (1, 0.6, 0.2, 1)

                header = Label(
                    text=f"[b][color={self._rgba_to_hex(mode_color)}]{entry['mode']}[/color][/b]  {entry['timestamp']}",
                    markup=True,
                    font_size='13sp',
                    size_hint_y=None,
                    height=24,
                    halign='left',
                    text_size=(None, None),
                )
                result_lbl = Label(
                    text=entry['result'],
                    font_size='12sp',
                    halign='left',
                    size_hint_y=None,
                    color=(0.85, 0.85, 0.85, 1),
                )
                result_lbl.bind(
                    width=lambda lbl, w: setattr(lbl, 'text_size', (w, None))
                )
                result_lbl.bind(
                    texture_size=lambda lbl, ts: setattr(lbl, 'height', ts[1])
                )

                card.bind(minimum_height=card.setter('height'))
                card.add_widget(header)
                card.add_widget(result_lbl)

                # Divider
                divider = Label(
                    text='─' * 60,
                    font_size='10sp',
                    size_hint_y=None,
                    height=16,
                    color=(0.3, 0.3, 0.3, 1),
                )

                inner.add_widget(card)
                inner.add_widget(divider)

            scroll.add_widget(inner)
            outer.add_widget(scroll)

        # Clear all + close buttons
        btn_row = BoxLayout(size_hint_y=None, height=48, spacing=8)
        clear_btn = Button(text='Clear All', background_color=(0.6, 0.15, 0.15, 1))
        close_btn = Button(text='Close', background_color=(0.25, 0.25, 0.25, 1))
        btn_row.add_widget(clear_btn)
        btn_row.add_widget(close_btn)
        outer.add_widget(btn_row)

        popup = Popup(title=f'Analysis History ({len(entries)} entries)', content=outer, size_hint=(0.95, 0.92))

        def clear_history(_):
            if os.path.isfile(HISTORY_FILE):
                os.remove(HISTORY_FILE)
            popup.dismiss()
            self.ids.advice_output.text = "History cleared."

        clear_btn.bind(on_press=clear_history)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    @staticmethod
    def _rgba_to_hex(rgba):
        r, g, b, _ = [int(c * 255) for c in rgba]
        return f"{r:02x}{g:02x}{b:02x}"

    # ── Gemini API ─────────────────────────────────────────────────────────────

    @mainthread
    def update_ui(self, message):
        self.ids.advice_output.text = message

    def call_gemini_api(self, path, mode):
        api_key = "AQ.Ab8RN6JDhwc4Jvn1kTrsJUN4cqTPY8Sx_-nVS0rOzSRyh_8eBg"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

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
                save_history_entry(mode, advice)
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
