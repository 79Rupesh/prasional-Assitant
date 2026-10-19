import getpass


class Authenticator:

    def __init__(self, pin: str):
        self.pin = pin

    def authenticate(self) -> bool:
        entered_pin = getpass.getpass("Enter Ela PIN: ")

        if entered_pin == self.pin:
            print("Authentication successful.")
            return True

        print("Authentication failed.")
        return False