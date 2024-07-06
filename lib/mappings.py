from typing import Optional, List
import json
from termcolor import colored
import google.generativeai as genai
from constants import mappings_out
from lib.timestamps import TimestampSchema
from db.models import SoundSchemaWithId
from db.queries import get_sound, get_associated_sounds

# adjusted schema for the addition of sound
class MappedTimestampSchema(TimestampSchema):
    sound: SoundSchemaWithId

mappings_schema = '{"id": <sound_id>, "", "confidence": <accuracy percentage number>}' # response schema

# system instructions passed into model
instructions = f"""
Given a description of a segment of audio and a list of 'sound' options to choose from, choose the best sound to match the description. Your response should return the id of the selected sound or -1 if there was no reasonably close match. Additionally, each response should include an 'accuracy percentage' which is a measure of how well you think the audio describes the keywords. Lastly, the response should be in the following format: {mappings_schema}. 
"""

# generate mapped timestamps
def generate(timestamps: List[TimestampSchema], out: Optional[str] = mappings_out) -> List[MappedTimestampSchema]:
    mapped_timestamps: List[MappedTimestampSchema] = [] # newly mapped timestamps

    # initialize model with system instructions and json response
    model = genai.GenerativeModel(model_name='gemini-1.5-flash', 
                                  system_instruction=instructions, 
                                  generation_config={"response_mime_type": "application/json"})

    # timestamp -> find suitable sound -> add to mapped_timestamps
    for timestamp in timestamps:
        associated_sounds = get_associated_sounds([timestamp['category']])
        options = json.dumps({"description": timestamp['description'], "sounds": associated_sounds}) # json content for model
        response = json.loads(model.generate_content(options).text) # get sound id from model response
        sound_id = int(response['id'])
        accuracy = response['confidence']

        # no similar sound found -> notify and skip
        if sound_id == -1:
            print(f"{colored('MISSING', 'red')} - No suitable sound found for: {timestamp['description']}")
            continue
        
        selected_sound = get_sound(sound_id) # get sound from database

        # sound not found in database -> notify and skip
        if selected_sound is None:
            print(f"Sound with id {sound_id} not found in database")
            continue

        accuracy_color = 'green' if accuracy >= 80 else 'yellow' if accuracy >= 60 else 'red'
        
        print(f"Selected '{selected_sound['name']}' for '{timestamp['description']}' with {colored(f'{accuracy}%', accuracy_color)} confidence")

        # add mapped timestamp to list
        mapped_timestamps.append({ "time": timestamp['time'], "description": timestamp['description'], 'category': timestamp['category'], "type": timestamp['type'], "sound": selected_sound })

    # write mapped timestamps to file if specified
    if out is not None:
        with open(out, 'w') as file:
            json.dump(mapped_timestamps, file, indent=4)

    return mapped_timestamps