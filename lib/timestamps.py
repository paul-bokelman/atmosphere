from typing import TypedDict, List
import json
import os
import google.generativeai as genai
from constants import timestamps_out
from lib.utils import info, success
import constants

class TimestampSchema(TypedDict):
    time: str
    description: str
    category: str
    keywords: List[str]

timestamp_schema = '[{"time": "mm:ss", "description": str, "category": str, "keywords": str[]}]' # response schema

# system instructions for the model
instructions = f"""
Given an audio file, identify timestamps where the setting or environment is described. Your response should follow the schema: {timestamp_schema}
Where:
- time: the timestamp in the format mm:ss
- description: a brief description of the setting or environment
- category: the category that best describes the setting or environment from the given list
- keywords: a list of keywords that describe the setting or environment

"""

# generate timestamps for given audio following timestamp_schema
def generate(recording_path: str, output_path: str = timestamps_out, skip: bool = False) -> List[TimestampSchema]:
    # if skip and file exists, return file
    if skip and os.path.exists(output_path):
        info("Skipping timestamps generation, using existing file...")
        return json.load(open(output_path, "r"))

    # initialize model with system instructions and json response
    model = genai.GenerativeModel(model_name='gemini-1.5-pro', 
                                  system_instruction=instructions, 
                                  generation_config={"response_mime_type": "application/json"})
    
    info(f"Uploading audio file from '{recording_path}'...")
    file = genai.upload_file(recording_path) # upload file to google servers
    success("Successfully uploaded audio file")

    response = model.generate_content([file, ', '.join(constants.categories)]) # generate timestamps and keywords in JSON format
    response_json = json.loads(response.text)
    
    # output response to json file
    if output_path is not None:
        with open(output_path, 'w') as file:
            json.dump(response_json, file, indent=4)

    # convert output to python dictionary
    return json.loads(response.text)

