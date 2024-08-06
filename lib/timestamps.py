from typing import Optional, List
from lib.types import TimestampSchema
import json
import os
import urllib.request
import google.generativeai as genai
import constants
from lib.utils import info, success, is_url

# todo: convert to proper response_schema object


timestamps_response_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "time": {"type": "string"},
            "description": {"type": "string"},
            "category": {"type": "string"},
            "keywords": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["time", "description", "category", "keywords"]
    }
}

# system instructions for the model
instructions = f"""
Your job is to listen to an audio book recording and identify areas where the setting or environment is described. When you hear a setting or environment described, note the timestamp, give a detailed general description of the setting or environment, choose the category that best describes the setting or environment, and give a brief list of keywords that are related description. Additionally ensure the timestamp is in the format mm:ss and the category is one of the following: {', '.join(constants.categories)}.
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
                                  generation_config={
                                      "response_mime_type": "application/json",
                                      "response_schema": timestamps_response_schema
                                    }
                                )   
    
    info(f"Uploading audio file from '{recording}'...")

    # upload file to google servers whether it's a url or local file
    file_path = urllib.request.urlretrieve(recording)[0] if is_url(recording) else recording
    file = genai.upload_file(file_path, mime_type='audio/mpeg')
    success("Successfully uploaded audio file")

    response = model.generate_content([file]) # generate timestamps
    timestamps = json.loads(response.text)
    
    # output response to json file
    if out is not None:
        with open(out, 'w') as file:
            json.dump(timestamps, file, indent=4)

    info(f"Generated {len(timestamps)} timestamps")

    # convert output to python dictionary
    return timestamps

