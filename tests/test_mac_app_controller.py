from actions.computer.mac_app_controller import MacAppController


def main():
    controller = MacAppController()
    print("Opening Calculator...")
    print(controller.open("Calculator"))
    print()
    print("Closing Calculator...")
    print(controller.close("Calculator"))


if __name__ == "__main__":
    main()
