from app.voice_assistant import VoiceAssistant
from auth.authenticator import Authenticator
from core.config.settings import settings


def main():

    print("Ela is starting...")

    if not settings.ela_pin:
        print("ELA_PIN is not configured.")
        return

    authenticator = Authenticator(settings.ela_pin)

    if not authenticator.authenticate():
        print("Ela cannot start.")
        return

    ela = VoiceAssistant()

    ela.run_forever()


if __name__ == "__main__":
    main()