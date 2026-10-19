from actions.computer.computer_controller import ComputerController


def main():
    computer = ComputerController()

    result = computer.double_click_text("Explorer")

    print(result)


if __name__ == "__main__":
    main()