from audio.microphone.real_microphone import RealMicrophone
from audio.stt.whisper_stt import WhisperSTT


microphone = RealMicrophone()
stt = WhisperSTT()

audio = microphone.record()

text = stt.transcribe(audio)

print(f"You said: {text}")