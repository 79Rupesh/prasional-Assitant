from actions.computer.open_app import OpenAppAction


action = OpenAppAction()

result = action.execute("Safari")

print(result)