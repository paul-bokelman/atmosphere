from typing import Optional, TypedDict, List
import json
import google.generativeai as genai
from constants import timestamps_out
from lib.utils import info, success
from db.queries import get_keywords

class TimestampSchema(TypedDict):
    time: str
    description: str
    category: str
    type: str

timestamp_schema = '[{"time": "mm:ss", "description": str, "category": str, "type": "action" | "environment"}]' # response schema

# system instructions for the model
instructions = f"""
Listen to the provided audiobook recording and identify segments where the addition of ambient sound effects would enhance the depiction of the setting or environment. Specifically, focus on:
- Descriptions of settings or environments (e.g., a forest, city streets, a rainy day).

Descriptions should abstractly describe the setting or environment without referencing specific characters or plot points and provide additional context for before and after the segment.

Provide the results in the following JSON format: {timestamp_schema}
Where:
- time is the timestamp of the segment in the format mm:ss
- description is a brief description of the segment with keywords that describe the setting or environment
- category is a single category that best describes the segment chosen from the provided list in prompt
- type is the type of segment (action or environment)

Requirements:
- Describe the setting or environment in 1-2 sentences.
- There should be a minimum of 5 segments identified for 8 minutes of audio

Ensure that the identified segments are relevant and the added sound effects will complement and not distract from the narration.
"""

# generate timestamps for given audio following timestamp_schema
def generate(recording_path: str, output_path: Optional[str] = timestamps_out) -> List[TimestampSchema]:
    # initialize model with system instructions and json response
    model = genai.GenerativeModel(model_name='gemini-1.5-pro', 
                                  system_instruction=instructions, 
                                  generation_config={"response_mime_type": "application/json"})
    
    info(f"Uploading audio file from '{recording_path}'...")
    file = genai.upload_file(recording_path) # upload file to google servers
    success("Successfully uploaded audio file")

    response = model.generate_content([file, ', '.join(get_keywords())]) # generate timestamps and keywords in JSON format

    # output response to json file
    if output_path is not None:
        f = open(output_path, "w")
        f.write(response.text)
        f.close()

    # convert output to python dictionary
    return json.loads(response.text)

