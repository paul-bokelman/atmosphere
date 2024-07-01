from typing import Optional, List, Any
import requests
from io import BytesIO
from termcolor import colored
from pydub import AudioSegment
from lib.mappings import MappedTimestampSchema
from lib.utils import g_link, timestamp_to_ms

# overlay sound effects from mappings on an audio file
def do(audio_path: str, mappings: List[MappedTimestampSchema], out: Optional[str] = None) -> AudioSegment:
    recording = AudioSegment.from_mp3(audio_path) # raw recording

    # overlay each sound effect on the recording
    for mapping in mappings:
        response = requests.get(g_link(mapping['sound']['gid'])) # get sound from google drive
        audio_data: Any = BytesIO(response.content) # convert to bytes
        audio = AudioSegment.from_file(audio_data) # convert to audio segment
        start, end = timestamp_to_ms(mapping['interval']) # get start and end timestamps
        #? should fade in and out relative to the interval?
        audio = audio[0:end-start].fade_in(500).fade_out(500) # trim and fade
        recording = recording.overlay(audio, position=start) # overlay audio on recording
    
    # export recording to path if specified
    if out is not None:
        print(colored(f"Exporting immersive audio to {out}...", "grey"))
        recording.export(out, format="mp3")

    return recording