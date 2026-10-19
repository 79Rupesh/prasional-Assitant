from actions.computer.mac_app_discovery import MacAppDiscovery


discovery = MacAppDiscovery()

apps = [
    "Safari",
    "Calculator",
    "Finder",
    "Terminal"
]

for app in apps:

    result = discovery.find(app)

    print(f"{app} -> {result}")