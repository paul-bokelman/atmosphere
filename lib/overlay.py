from typing import Optional, List
from lib.types import MappedTimestampSchema
import urllib.request
from pydub import AudioSegment
import constants
from lib.utils import time_to_ms, info, candidate_sfx_file, is_url

def do(original_recording: str, mappings: List[MappedTimestampSchema], out: Optional[str] = None) -> AudioSegment:
    """Overlay sound effects from mappings on an audio file"""
    # retrieve original recording for overlay
    recording = AudioSegment.from_mp3(urllib.request.urlretrieve(original_recording)[0] if is_url(original_recording) else original_recording)

    # overlay each sound effect on the recording
    for mapping in mappings:
        # configuration
        (left_margin, right_margin) = constants.audio_overlay_config['margins']
        gain = constants.audio_overlay_config['gain']
        (left_fade, right_fade) = constants.audio_overlay_config['fade']
        length = constants.audio_overlay_config['length']

        audio = candidate_sfx_file(mapping['sound_id']) # get sound effect
        position = time_to_ms(mapping['timestamp']['time']) - left_margin # position in milliseconds
        #/ fade and gain should be relative to audio length, margins current volume and recording volume
        audio = audio[0:length + right_margin].fade_in(left_fade).fade_out(right_fade).apply_gain(gain) # trim and fade
        recording = recording.overlay(audio, position=position) # overlay audio on recording
    
    # export recording to path if specified
    if out is not None:
        info(f"Exporting immersive audio to {out}...")
        recording.export(out, format="mp3")

    return recording