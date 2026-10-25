from actions.computer.mac_app_discovery import MacAppDiscovery


def main():
    discovery = MacAppDiscovery()

    for app in ("Safari", "Calculator", "Finder", "Terminal"):
        print(f"{app} -> {discovery.find(app)}")


if __name__ == "__main__":
    main()
