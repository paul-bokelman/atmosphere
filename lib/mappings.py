from typing import Optional, List
import json
from termcolor import colored
import google.generativeai as genai
from lib.timestamps import TimestampSchema
from db.models import SoundSchemaWithId
from db.queries import get_sounds, get_sound

# adjusted schema for the addition of sound
class MappedTimestampSchema(TimestampSchema):
    sound: SoundSchemaWithId

mappings_schema = '{"id": <sound_id>, "", "confidence": <accuracy percentage number>}' # response schema

# system instructions passed into model
instructions = f"""
You will be given a list of keywords and your job is to compare them with pairs of descriptions and keywords to determine the best sound to choose for the given keywords. Your response should return the id of the selected sound or -1 if there was no reasonably close match. Additionally, each response should include an 'accuracy percentage' which is a measure of how well you think the audio describes the keywords. Lastly, the response should be in the following format: {mappings_schema}.
"""

# ingest timestamps and properly map to sounds
def generate(timestamps: List[TimestampSchema], out: Optional[str] = None) -> List[MappedTimestampSchema]:
    mapped_timestamps: List[MappedTimestampSchema] = [] # newly mapped timestamps
    sounds = get_sounds()

    # initialize model with system instructions and json response
    model = genai.GenerativeModel(model_name='gemini-1.5-flash', 
                                  system_instruction=instructions, 
                                  generation_config={"response_mime_type": "application/json"})

    # timestamp -> find suitable sound -> add to mapped_timestamps
    for timestamp in timestamps:
        content = json.dumps({"input": timestamp['keywords'],"sounds": sounds}) # json content for model

        response = json.loads(model.generate_content(content).text) # get sound id from model response
        sound_id = int(response['id'])
        accuracy = response['confidence']

        # no similar sound found -> notify and skip
        if sound_id == -1:
            print(f"{colored('MISSING', 'red')} - No suitable sound found for keywords: {timestamp['keywords']}")
            continue
        
        selected_sound = get_sound(sound_id) # get sound from database

        # sound not found in database -> notify and skip
        if selected_sound is None:
            print(f"Sound with id {sound_id} not found in database")
            continue

        accuracy_color = 'green' if accuracy >= 80 else 'yellow' if accuracy >= 60 else 'red'
        
        print(f"Selected '{selected_sound['description']}' for keywords {timestamp['keywords']} with {colored(f'{accuracy}%', accuracy_color)} confidence")

        # add mapped timestamp to list
        mapped_timestamps.append({ "interval": timestamp['interval'], "keywords": timestamp['keywords'], "sound": selected_sound })

    # write mapped timestamps to file if specified
    if out is not None:
        with open(out, 'w') as file:
            json.dump(mapped_timestamps, file, indent=4)

    return mapped_timestamps