"""Place the active work window on the left half of the display."""

import subprocess
import time

from core.platform_support import current_platform


class WindowManager:
    def snap_active_left(self) -> bool:
        if current_platform() == "windows":
            try:
                import pyautogui
                time.sleep(0.4)
                pyautogui.hotkey("win", "left")
                return True
            except Exception as error:
                print(f"Could not arrange the active window: {error}")
                return False

        try:
            import pyautogui
            width, height = pyautogui.size()
            script = f'''tell application "System Events"
                set activeProcess to first application process whose frontmost is true
                tell activeProcess
                    if (count of windows) > 0 then
                        set position of front window to {{0, 25}}
                        set size of front window to {{{int(width / 2)}, {int(height - 25)}}}
                    else
                        error "No active application window"
                    end if
                end tell
            end tell'''
            subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )
            return True
        except Exception as error:
            print(
                "Could not arrange the active macOS window. "
                "Check Accessibility permission: "
                f"{type(error).__name__}: {error}"
            )
            return False
