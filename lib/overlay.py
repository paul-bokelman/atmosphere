from typing import Optional, List
from pydub import AudioSegment
from lib.mappings import MappedTimestampSchema
from lib.utils import time_to_ms, info, candidate_sfx_file

# audio configuration
action_margins = [500, 500] 
environment_margins = [3000, 3000] 
action_gain = -30 # dB
environment_gain = -26 # dB
environment_fade = [3000, 3000] 
action_fade = [500, 500]
environment_length = 15000 
action_length = 2000

# get audio configuration based on type
def get_audio_config(type: str = "environment") -> tuple[list[int], int, list[int], int]:
    return (action_margins, action_gain, action_fade, action_length) if type == 'action' else (environment_margins, environment_gain, environment_fade, environment_length)

# overlay sound effects from mappings on an audio file
def do(audio_path: str, mappings: List[MappedTimestampSchema], out: Optional[str] = None) -> AudioSegment:
    recording = AudioSegment.from_mp3(audio_path) # raw recording

    # overlay each sound effect on the recording
    for mapping in mappings:
        (left_margin, right_margin), gain, (left_fade, right_fade), length = get_audio_config()
        audio = candidate_sfx_file(mapping['sound_id']) # get sound effect
        position = time_to_ms(mapping['time']) - left_margin # position in milliseconds
        #/ fade and gain should be relative to audio length, margins current volume and recording volume
        audio = audio[0:length + right_margin].fade_in(left_fade).fade_out(right_fade).apply_gain(gain) # trim and fade
        recording = recording.overlay(audio, position=position) # overlay audio on recording
    
    # export recording to path if specified
    if out is not None:
        info(f"Exporting immersive audio to {out}...")
        recording.export(out, format="mp3")

    return recording