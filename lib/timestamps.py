from typing import Optional, TypedDict, List
import json
from termcolor import colored
import google.generativeai as genai

# dictionary format for timestamps
class TimestampSchema(TypedDict):
    interval: str
    keywords: List[str]

timestamp_schema = '[{"interval": "<start>-<end>, "keywords": str[]}...]' # response schema

# system instructions passed into model
instructions = f"""
Your job is to receive an audio book sample then find spots where ambient sound effects could be added. For each spot, return it's timestamp interval and a few keywords to describe the desired ambient sound effect. Your response should follow this schema: {timestamp_schema} and should be relatively sparse (2-8 for 8 min audio). In addition, list of keywords should be relatively unique and not too similar to each other with a length of 3-5 words.
"""

# generate timestamps for given audio following timestamp_schema
def generate(audio_url: str, output_path: Optional[str] = None) -> List[TimestampSchema]:
    # initialize model with system instructions and json response
    model = genai.GenerativeModel(model_name='gemini-1.5-flash', 
                                  system_instruction=instructions, 
                                  generation_config={"response_mime_type": "application/json"})
    
    print(colored(f"Uploading audio file from '{audio_url}'...", 'grey'))
    uploaded_file = genai.upload_file(audio_url) # upload file to google servers
    print(colored("Successfully uploaded audio file", "green"))

    aud = genai.get_file(name=uploaded_file.name) # get uploaded file from google servers
    response = model.generate_content([aud]) # generate timestamps and keywords in JSON format

    # output response to json file
    if output_path is not None:
        f = open(output_path, "w")
        f.write(response.text)
        f.close()

    # convert output to python dictionary
    return json.loads(response.text)

