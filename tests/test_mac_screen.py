from screen.mac_screen import MacScreen


def main():
    screen = MacScreen()
    output = "/tmp/ela_python_screen_test.png"
    print(f"Captured: {screen.capture(output)}")


if __name__ == "__main__":
    main()
