"""List input devices that Ela can use without recording audio."""

import sounddevice as sd

from audio.microphone.real_microphone import RealMicrophone


def main():
    default_input, _default_output = sd.default.device
    devices = sd.query_devices()
    found = False

    print("Available input devices:")
    for index, device in enumerate(devices):
        if device["max_input_channels"] < 1:
            continue

        found = True
        default_marker = " (default)" if index == default_input else ""
        print(
            f"  {index}: {device['name']} — "
            f"{device['max_input_channels']} channel(s), "
            f"{device['default_samplerate']:.0f} Hz{default_marker}"
        )

    if not found:
        print("No input device was found. Connect/enable a microphone and try again.")
        return 1

    selected = RealMicrophone().device
    print(f"Ela will use: {selected if selected is not None else 'the system default input'}")
    print("To choose a different device, set ELA_MIC_DEVICE to its number.")
    print("If your voice is very quiet, set ELA_MIC_SENSITIVITY=1.5 (range: 0.5–3).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
