from audio.microphone.microphone import Microphone


class FakeMicrophone(Microphone):

    def record(self) -> bytes:
        return b"fake audio data"


microphone = FakeMicrophone()

audio = microphone.record()

print(f"Audio received: {audio}")