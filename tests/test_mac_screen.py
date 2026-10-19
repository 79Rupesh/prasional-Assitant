from screen.mac_screen import MacScreen


screen = MacScreen()

output = "/tmp/ela_python_screen_test.png"

result = screen.capture(output)

print(f"Captured: {result}")