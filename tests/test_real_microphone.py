from audio.microphone.real_microphone import RealMicrophone


microphone = RealMicrophone()

audio = microphone.record()

print(f"Captured audio bytes: {len(audio)}")