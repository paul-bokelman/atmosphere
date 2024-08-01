from typing import Optional, List
from lib.types import TimestampSchema
import json
import os
import urllib.request
import google.generativeai as genai
import constants
from lib.utils import info, success, is_url

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

def generate(recording: str, out: Optional[str] = None, skip: bool = False) -> List[TimestampSchema]:
    """Generate timestamps from input recording"""
    # if skip and file exists, return file
    if skip and out is not None and os.path.exists(out):
        info("Skipping timestamps generation, using existing file...")
        return json.load(open(out, "r"))

    # initialize model with system instructions and json response
    model = genai.GenerativeModel(model_name='gemini-1.5-flash', 
                                system_instruction=instructions, 
                                generation_config={"response_mime_type": "application/json"})
    
    info(f"Uploading audio file from '{recording}'...")
    # upload file to google servers whether it's a url or local file
    file = genai.upload_file(urllib.request.urlretrieve(recording)[0], mime_type='audio/mpeg') if is_url(recording) else genai.upload_file(recording) 
    success("Successfully uploaded audio file")

    response = model.generate_content([file, ', '.join(constants.categories)]) # generate timestamps
    response_json = json.loads(response.text)
    
    # output response to json file
    if out is not None:
        with open(out, 'w') as file:
            json.dump(response_json, file, indent=4)

    # convert output to python dictionary
    return json.loads(response.text)

