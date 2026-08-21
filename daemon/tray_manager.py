"""
Bartholomew System Tray & Background Manager
Manages the background daemon process with desktop tray controls.
"""

import sys
import os
import subprocess
import webbrowser
import threading
import time


def launch_tray():
    """
    Launches system tray menu if pystray/PIL is available; otherwise provides console daemon manager.
    """
    try:
        import pystray
        from PIL import Image, ImageDraw

        def create_image():
            # Generate sharp 64x64 green shield icon
            img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            # Emerald green rounded shield
            d.polygon([(32, 4), (56, 16), (56, 38), (32, 60), (8, 38), (8, 16)], fill=(16, 185, 129, 255))
            d.polygon([(32, 10), (50, 20), (50, 36), (32, 54), (14, 36), (14, 20)], fill=(0, 0, 0, 255))
            d.rectangle([(28, 22), (36, 42)], fill=(245, 158, 11, 255))
            return img

        def open_portal(icon, item):
            webbrowser.open("http://127.0.0.1:8080/dashboard/operator-portal-secure.html")

        def open_website(icon, item):
            webbrowser.open("https://bartholomew.info")

        def exit_action(icon, item):
            icon.stop()
            sys.exit(0)

        menu = pystray.Menu(
            pystray.MenuItem("🟢 Bartholomew Guard: Active", lambda: None, enabled=False),
            pystray.MenuItem("Open Operator Portal", open_portal, default=True),
            pystray.MenuItem("Visit bartholomew.info", open_website),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit Guard Daemon", exit_action)
        )

        icon = pystray.Icon("Bartholomew", create_image(), "Bartholomew BTP Guard", menu)
        icon.run()
    except ImportError:
        # Fallback if GUI libraries aren't installed
        print("[BARTHOLOMEW TRAY] Running in headless mode (pystray not installed). Daemon active on 127.0.0.1:8080.")


if __name__ == "__main__":
    launch_tray()
