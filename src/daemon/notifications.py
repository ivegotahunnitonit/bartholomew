"""
Bartholomew Local Daemon: Cross-Platform OS Notification Engine
Emits instant desktop alerts on threat interceptions and approval requests.
"""

import sys
import os
import subprocess
import threading


def send_desktop_notification(title: str, message: str, is_threat: bool = False):
    """
    Dispatches a native OS toast notification asynchronously with zero UI blocking.
    """
    def _notify():
        try:
            if sys.platform == "win32":
                # PowerShell BurntToast or Windows Script Host Toast
                ps_script = f"""
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
                $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
                $textNodes = $template.GetElementsByTagName("text")
                $textNodes.Item(0).AppendChild($template.CreateTextNode("{title}")) > $null
                $textNodes.Item(1).AppendChild($template.CreateTextNode("{message}")) > $null
                $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Bartholomew AI Guard")
                $notification = [Windows.UI.Notifications.ToastNotification]::new($template)
                $notifier.Show($notification)
                """
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_script],
                    capture_output=True,
                    timeout=3,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            elif sys.platform == "darwin":
                # macOS osascript
                apple_script = f'display notification "{message}" with title "{title}" subtitle "Bartholomew BTP Guard"'
                subprocess.run(["osascript", "-e", apple_script], capture_output=True, timeout=3)
            elif sys.platform.startswith("linux"):
                # Linux notify-send
                urgency = "critical" if is_threat else "normal"
                subprocess.run(["notify-send", "-u", urgency, "-a", "Bartholomew Guard", title, message], capture_output=True, timeout=3)
        except Exception:
            # Silent fallback to console
            pass

    threading.Thread(target=_notify, daemon=True).start()
