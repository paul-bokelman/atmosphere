from typing import Optional, List
from lib.types import MappedTimestampSchema, TimestampSchema
import json
import os
import time
from termcolor import colored
import google.generativeai as genai
import constants
from lib.utils import info, warn,error, sfx_candidates

mappings_response_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "description": {"type": "string"}
    }
}

# system instructions passed into model
instructions = f"""
You will be given a list of sound effects in the format [(ID) | description] and a description of a setting or environment. Your job is to choose the sound effect from the list that best matches the given description. When the sound effect is found return it's id and description. If no sound effect is found, return -1 and an empty description.
"""

def generate(timestamps: List[TimestampSchema], out: Optional[str], skip: bool = False) -> List[MappedTimestampSchema]:
    """Generate mapped timestamps from input timestamps"""
    if len(timestamps) == 0:
        info("No timestamps found, proceeding with empty mappings...")
        return []
    
    # if skip and file exists, return file
    if skip and out is not None and os.path.exists(out):
        info("Skipping mappings generation, using existing file...")
        return json.load(open(out, "r"))

    mapped_timestamps: List[MappedTimestampSchema] = [] # newly mapped timestamps

    # initialize model with system instructions and response schema
    model = genai.GenerativeModel(model_name='gemini-1.5-flash', 
                                  system_instruction=instructions, 
                                  generation_config={
                                      "response_mime_type": "application/json", 
                                      "response_schema": mappings_response_schema
                                    }
                                )
    
    # timestamp -> find suitable sound -> add to mapped_timestamps
    for (index, timestamp) in enumerate(timestamps):
        if index > 0 and index % 13 == 0:
            warn("API rate limit reached, waiting for 20 seconds before continuing...")
            time.sleep(20)

        category = timestamp['category'] if timestamp['category'] in constants.categories else None # ensure category is valid
        candidates = sfx_candidates(category=category, keywords=timestamp['keywords']) # get sound candidates
        
        # if no candidates found, search without keywords
        if len(candidates) == 0:
            candidates = sfx_candidates(category=timestamp['category'], keywords = [])
            # if still no candidates found, notify and skip
            if len(candidates) == 0:
                warn(f"No candidates found for timestamp at index {index}")
                continue
        
        candidates_str = "" # candidates string for model input

        # format candidates for model input
        for c in candidates:
            candidate_str  = f"{(c['id'])} | "

            # add band description if available
            if 'additionalMetadata' in c:
                if 'bandDescription' in c['additionalMetadata']:
                    candidate_str += f"{c['additionalMetadata']['bandDescription']} - "

            candidate_str += f"{c['description']}"
            candidates_str += candidate_str + "\n"

        response = model.generate_content([timestamp['description'], candidates_str]) # get sound id from model response

        try:
            # extract id and description from model response
            json_response = json.loads(response.text)
            id, description = json_response['id'], json_response['description']

            # no similar sound found -> notify and continue
            if id == "-1":
                warn(f"No suitable sfx found for timestamp at index {index} from list of {len(candidates)} candidates")
                continue

            # add mapped timestamp to list
            print(f"{colored('Selected', 'grey')} {colored(id, 'green')} {colored(f'from list of {len(candidates)} candidates for timestamp at index {index}', 'grey')}")

            # add mapped timestamp to list
            mapped_timestamps.append({
                "timestamp": timestamp,
                'sound_id': id,
                'sound_description': description,
            })
        except ValueError:
            error(f"Invalid response from model at index {index}, skipping...")
            error(f'Received: {response.text}')
            continue
        except Exception as e:
            print(e)
            error(f"Error processing timestamp at index {index}, skipping...")
            continue

    # write mapped timestamps to file if specified
    if out is not None:
        with open(out, 'w') as file:
            json.dump(mapped_timestamps, file, indent=4)

    return mapped_timestamps