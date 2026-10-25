import os
from unittest.mock import patch

from audio.microphone.real_microphone import RealMicrophone


def test_quiet_microphone_uses_low_but_safe_start_threshold():
    start, continuation = RealMicrophone._thresholds_for_noise(10, 1.0)
    assert start == 75.0
    assert continuation == 35.0


def test_loud_room_threshold_is_calibrated_and_capped():
    start, continuation = RealMicrophone._thresholds_for_noise(1000, 1.0)
    assert start == 900.0
    assert continuation == 585.0


def test_higher_sensitivity_reduces_required_speech_level():
    normal, _ = RealMicrophone._thresholds_for_noise(80, 1.0)
    sensitive, _ = RealMicrophone._thresholds_for_noise(80, 2.0)
    assert sensitive < normal


def test_start_requires_multiple_speech_blocks():
    assert not RealMicrophone._speech_started([100], 75)
    assert RealMicrophone._speech_started([100, 100], 75)
    assert not RealMicrophone._speech_started([100, 20, 20], 75)


def test_microphone_device_can_be_selected_from_environment():
    with patch.dict(os.environ, {"ELA_MIC_DEVICE": "5"}, clear=False):
        assert RealMicrophone().device == 5
