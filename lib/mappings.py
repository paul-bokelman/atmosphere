from typing import Optional, List
import json
import os
import time
from termcolor import colored
import google.generativeai as genai
from constants import mappings_out
from lib.timestamps import TimestampSchema
from lib.utils import info, sfx_candidates, candidate_sfx_file

# adjusted schema for the addition of sound
class MappedTimestampSchema(TimestampSchema):
    sound_id: str

# system instructions passed into model
instructions = f"""
Choose the sound effect that best matches the given description. Your response should return the just the id of the selected sound or -1 if there was no reasonably close match.
"""

instructions_check = f"""
Listen to the following audio. Does the uploaded audio match the feel and setting of the text description? Respond 1 if the audio and description match, and 0 otherwise. The audio and description do NOT need to match perfectly, but must match to 65% accuracy. RESPOND WITH ONLY a 0 or a 1!
"""

# generate mapped timestamps
def generate(timestamps: List[TimestampSchema], out: Optional[str] = mappings_out, skip: bool = False) -> List[MappedTimestampSchema]:
    # if skip and file exists, return file
    if skip and out is not None and os.path.exists(out):
        info("Skipping mappings generation, using existing file...")
        return json.load(open(out, "r"))

    mapped_timestamps: List[MappedTimestampSchema] = [] # newly mapped timestamps

    # initialize model with system instructions and json response
    model = genai.GenerativeModel(model_name='gemini-1.5-flash', 
                                  system_instruction=instructions, 
                                  generation_config={"response_mime_type": "text/plain"})
    
    model2 = genai.GenerativeModel(model_name='gemini-1.5-pro', 
                                  system_instruction=instructions_check,
                                  generation_config={"response_mime_type": "text/plain"})

    # timestamp -> find suitable sound -> add to mapped_timestamps
    for timestamp in timestamps:

        candidates_dict = sfx_candidates(category=timestamp['category'], keywords=timestamp['keywords']) # get sound candidates
    
        if len(candidates_dict) == 0:
            candidates_dict = sfx_candidates(category=timestamp['category'], keywords = None)


        for i in range(10):
            candidates = ""
            for s in candidates_dict:
                candidates += f"{s['description']} ({s['id']})\n"
            #print(candidates)

            response = model.generate_content([timestamp['description'], candidates]) # get sound id from model response
            sound_id = response.text.strip() # get sound id from response

            # no similar sound found -> notify and skip
            if sound_id == "-1":
                print(f"{colored('NOTHING FOUND', 'red')} - '{timestamp['description']}' with keywords {timestamp['keywords']} in category {timestamp['category']}")
                break
            else:
                #upload choice by id to gemini and ask for confimation
                audio = candidate_sfx_file(sound_id)
                audio.export("out/candidate.mp3")
                file = genai.upload_file("out/candidate.mp3")

                response = model2.generate_content([file, ', ', timestamp['description']]) 
                

                if response.text.strip() == "1":
                    print(f"{colored('FOUND', 'green')} - '{timestamp['description']}' with keywords {timestamp['keywords']} in category {timestamp['category']}.")
                    break
                else: #remove tested candidate from candidates
                    candidates_dict = [d for d in candidates_dict if d['id'] != sound_id]
                    

        

        # add mapped timestamp to list
        mapped_timestamps.append({ "time": timestamp['time'], "description": timestamp['description'], 'category': timestamp['category'], 'keywords': timestamp['keywords'], "sound_id": sound_id})
        time.sleep(5)

    # write mapped timestamps to file if specified
    if out is not None:
        with open(out, 'w') as file:
            json.dump(mapped_timestamps, file, indent=4)

    return mapped_timestamps