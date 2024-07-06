from typing import Optional, TypedDict, List
import json
import google.generativeai as genai
from constants import timestamps_out
from lib.utils import info, success

# dictionary format for timestamps
class TimestampSchema(TypedDict):
    time: str
    keywords: List[str]
    type: str

# timestamp_schema = '[{"interval": "<start>-<end>, "keywords": str[]}...]' # response schema
timestamp_schema = '[{"time": "mm:ss", "keywords": str[]..., "type": "action" | "environment"}]' # response schema

# system instructions for the model
instructions = f"""
Listen to the provided audiobook recording and identify segments where the addition of ambient sound effects would enhance the depiction of the setting or environment. Specifically, focus on:
- Descriptions of settings or environments (e.g., a forest, city streets, a rainy day).
- Interactions with the environment (e.g., opening a door, walking on gravel, rustling leaves).

Provide the results in the following JSON format: {timestamp_schema}
Where:
- time is the timestamp of the segment in the format mm:ss
- <keyword1>, <keyword2>, etc., are keywords describing the context of the segment and the suggested ambient sound effects.
- type is the type of segment (action or environment)

Requirements:
- Chosen segments should be relatively spaced out and not too close together (at least 30 seconds apart). If there are no suitable segments, please provide a message indicating that no segments were found.

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

    response = model.generate_content(file) # generate timestamps and keywords in JSON format

    # output response to json file
    if output_path is not None:
        f = open(output_path, "w")
        f.write(response.text)
        f.close()

    # convert output to python dictionary
    return json.loads(response.text)

