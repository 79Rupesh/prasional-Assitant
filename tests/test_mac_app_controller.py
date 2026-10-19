from actions.computer.mac_app_controller import MacAppController


controller = MacAppController()

print("Opening Calculator...")
print(controller.open("Calculator"))

print()
print("Closing Calculator...")
print(controller.close("Calculator"))