from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.uix.slider import Slider
from android.permissions import request_permissions, Permission
from jnius import autoclass
import time

# Android classes
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Context = autoclass('android.content.Context')
AccessibilityService = autoclass('android.accessibilityservice.AccessibilityService')
MotionEvent = autoclass('android.view.MotionEvent')
System = autoclass('java.lang.System')

class AutoClickerLayout(BoxLayout):
    is_clicking = BooleanProperty(False)
    click_interval = NumericProperty(1.0)  # seconds
    click_count = NumericProperty(0)
    status_text = StringProperty("Ready")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        # Request permissions
        request_permissions([
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.BIND_ACCESSIBILITY_SERVICE
        ])

    def start_clicking(self):
        if not self.is_clicking:
            self.is_clicking = True
            self.status_text = "Auto-clicking started"
            self.click_count = 0
            Clock.schedule_interval(self.perform_click, self.click_interval)

    def stop_clicking(self):
        if self.is_clicking:
            self.is_clicking = False
            self.status_text = "Auto-clicking stopped"
            Clock.unschedule(self.perform_click)

    def perform_click(self, dt):
        try:
            # Get the current activity
            activity = PythonActivity.mActivity
            
            # Get window dimensions
            window = activity.getWindow()
            decor_view = window.getDecorView()
            width = decor_view.getWidth()
            height = decor_view.getHeight()
            
            # Click at center of screen
            x = width // 2
            y = height // 2
            
            # Create touch events
            down_time = System.currentTimeMillis()
            
            # Create down event
            down_event = MotionEvent.obtain(
                down_time, down_time, 
                MotionEvent.ACTION_DOWN, x, y, 0
            )
            
            # Create up event
            up_event = MotionEvent.obtain(
                down_time, System.currentTimeMillis(), 
                MotionEvent.ACTION_UP, x, y, 0
            )
            
            # Dispatch events
            decor_view.dispatchTouchEvent(down_event)
            decor_view.dispatchTouchEvent(up_event)
            
            # Recycle events
            down_event.recycle()
            up_event.recycle()
            
            self.click_count += 1
            self.status_text = f"Clicks: {self.click_count}"
            
        except Exception as e:
            self.status_text = f"Error: {str(e)}"
            self.stop_clicking()

    def show_accessibility_info(self):
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(
            text="For full functionality:\n\n" +
                 "1. Go to Settings → Accessibility\n" +
                 "2. Enable AutoClicker Service\n" +
                 "3. Grant necessary permissions\n\n" +
                 "This app requires accessibility service to perform clicks reliably.",
            size_hint_y=0.8
        ))
        
        btn = Button(text="OK", size_hint_y=0.2)
        popup = Popup(title="Accessibility Setup", content=content, size_hint=(0.8, 0.6))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        
        popup.open()

class AutoClickerApp(App):
    def build(self):
        return AutoClickerLayout()

if __name__ == '__main__':
    AutoClickerApp().run()