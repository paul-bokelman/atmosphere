from typing import Optional, List
from pydub import AudioSegment
from lib.mappings import MappedTimestampSchema
from lib.utils import sfx_path, timestamp_to_ms, info

# overlay sound effects from mappings on an audio file
def do(audio_path: str, mappings: List[MappedTimestampSchema], out: Optional[str] = None) -> AudioSegment:
    recording = AudioSegment.from_mp3(audio_path) # raw recording

    # overlay each sound effect on the recording
    for mapping in mappings:
        audio = AudioSegment.from_file(sfx_path(**mapping['sound'])) # convert to audio segment
        start, end = timestamp_to_ms(mapping['interval']) # get start and end timestamps
        #? should fade in and out relative to the interval?
        audio = audio[0:end-start].fade_in(500).fade_out(500) # trim and fade
        recording = recording.overlay(audio, position=start) # overlay audio on recording
    
    # export recording to path if specified
    if out is not None:
        info(f"Exporting immersive audio to {out}...")
        recording.export(out, format="mp3")

    return recording