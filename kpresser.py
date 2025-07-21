import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import keyboard
import threading
import time
import os
import sys
import webbrowser

UPPERCASE_KEYS = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
LOWERCASE_AND_SPECIAL_KEYS = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'enter', 'space', 'tab', 'esc', 'backspace', 'delete',
    'up', 'down', 'left', 'right',
    'ctrl', 'alt', 'shift', 'win'
]
KEY_LIST = UPPERCASE_KEYS + LOWERCASE_AND_SPECIAL_KEYS
COMMAND_KEYS = [
    'enter', 'space', 'tab', 'esc', 'backspace', 'delete',
    'up', 'down', 'left', 'right',
    'ctrl', 'alt', 'shift', 'win'
]
class KeyPresserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KeyPresser")
        self.root.geometry("420x350")
        
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, 'icon.ico')
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load window icon: {e}")

        self.root.resizable(False, False)

        self.is_running = False
        self.press_thread = None
        self.current_hotkey_ref = None

        style = ttk.Style(self.root)
        style.theme_use('clam')

        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(expand=True)
        
        footer_frame = ttk.Frame(self.root, padding=(10, 10))
        footer_frame.pack(side="bottom", fill="x")

        # Controles
        ttk.Label(main_frame, text="Key to Press:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.key_to_press_var = tk.StringVar(value='A')
        self.key_combo = ttk.Combobox(main_frame, textvariable=self.key_to_press_var, values=KEY_LIST, state='readonly', width=25)
        self.key_combo.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5)

        ttk.Label(main_frame, text="Interval (ms):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.speed_var = tk.IntVar(value=100)
        
        self.speed_scale = ttk.Scale(main_frame, from_=1, to=2000, orient='horizontal', variable=self.speed_var, command=self.update_speed_from_slider)
        self.speed_scale.grid(row=1, column=1, sticky="ew", padx=5)
        
        self.speed_entry = ttk.Entry(main_frame, width=7)
        self.speed_entry.grid(row=1, column=2, padx=5)
        self.speed_entry.insert(0, str(self.speed_var.get()))
        self.speed_entry.bind("<Return>", self.update_speed_from_entry)
        
        ttk.Label(main_frame, text="Hotkey (Start/Stop):").grid(row=2, column=0, sticky="w", pady=10, padx=5)
        hotkey_options = [f'f{i}' for i in range(1, 13)]
        self.hotkey_var = tk.StringVar(value='f6')
        self.hotkey_combo = ttk.Combobox(main_frame, textvariable=self.hotkey_var, values=hotkey_options, state='readonly')
        self.hotkey_combo.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5)
        self.hotkey_combo.bind("<<ComboboxSelected>>", self.setup_hotkey)

        self.status_label = ttk.Label(main_frame, text="Status: Ready", font=("Segoe UI", 10, "bold"), anchor="center")
        self.status_label.grid(row=3, column=0, columnspan=3, pady=(25, 10))
        
        footer_content = ttk.Frame(footer_frame)
        footer_content.pack()
        
        github_url = "https://github.com/Marvinzada"
        try:
            logo_path = os.path.join(base_path, 'github_logo.png')
            self.github_logo_img = Image.open(logo_path).convert("RGBA")
            self.github_logo_icon = ImageTk.PhotoImage(self.github_logo_img)
            logo_label = ttk.Label(footer_content, image=self.github_logo_icon, cursor="hand2")
            logo_label.image = self.github_logo_icon
            logo_label.pack(side="left", padx=(5, 0))
            logo_label.bind("<Button-1>", lambda e: self.open_link(github_url))
        except Exception as e:
            print(f"Could not load logo: {e}")
            
        copyright_label = ttk.Label(footer_content, text="Made by Marvinzada", cursor="hand2")
        copyright_label.pack(side="left")
        copyright_label.bind("<Button-1>", lambda e: self.open_link(github_url))
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_hotkey()

    def open_link(self, url):
        webbrowser.open_new_tab(url)

    def update_speed_from_slider(self, value):
        val_int = int(float(value))
        self.speed_entry.delete(0, tk.END)
        self.speed_entry.insert(0, str(val_int))

    def update_speed_from_entry(self, event=None):
        try:
            val = int(self.speed_entry.get())
            if 1 <= val <= 2000: self.speed_var.set(val)
            else: self.speed_entry.delete(0, tk.END); self.speed_entry.insert(0, str(self.speed_var.get()))
        except ValueError: self.speed_entry.delete(0, tk.END); self.speed_entry.insert(0, str(self.speed_var.get()))
        self.root.focus()

    def setup_hotkey(self, event=None):
        try:
            if self.current_hotkey_ref:
                keyboard.remove_hotkey(self.current_hotkey_ref)
            hotkey = self.hotkey_var.get()
            self.current_hotkey_ref = keyboard.add_hotkey(hotkey, self.toggle_pressing)
            self.status_label.config(text=f"Status: Ready! Press '{hotkey}' to start.")
            self.root.focus()
        except Exception as e:
            self.status_label.config(text=f"Error setting hotkey: {e}")

    def toggle_pressing(self):
        self.is_running = not self.is_running
        self.toggle_controls(self.is_running)
        if self.is_running:
            self.press_thread = threading.Thread(target=self.press_key_loop, daemon=True); self.press_thread.start()
            self.status_label.config(text="Status: Running...")
        else:
            hotkey_name = self.hotkey_var.get()
            self.status_label.config(text=f"Status: Stopped. Press '{hotkey_name}' to start.")

    def toggle_controls(self, is_running):
        state = 'disabled' if is_running else 'readonly'
        entry_state = 'disabled' if is_running else 'normal'
        self.key_combo.config(state=state)
        self.speed_scale.config(state=entry_state)
        self.speed_entry.config(state=entry_state)
        self.hotkey_combo.config(state=state)

    def press_key_loop(self):
        key_to_press = self.key_to_press_var.get()
        while self.is_running:
            try:
                if key_to_press in COMMAND_KEYS:
                    keyboard.press_and_release(key_to_press)
                else:
                    keyboard.write(key_to_press)
                
                interval = self.speed_var.get() / 1000.0
                time.sleep(interval)
            except Exception as e:
                self.is_running = False
                self.root.after(0, self.status_label.config, {"text": f"Error: {e}"})
                self.root.after(0, self.toggle_controls, False)
                break

    def on_closing(self):
        self.is_running = False
        keyboard.remove_all_hotkeys()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyPresserApp(root)
    root.mainloop()