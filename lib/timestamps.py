import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# configuration
API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=API_KEY)

# system instructions passed into model
instructions = """
Your job is to receive an audio book sample then find spots where ambient sound effects could be added. For each spot, return it's timestamp interval and a few keywords to describe the desired ambient sound effect. Your response should follow this schema: [{"interval": str, "keywords": str[]}, ...]
"""

# initialize model with system instructions and json response
model = genai.GenerativeModel(model_name='gemini-1.5-flash', 
                              system_instruction=instructions, 
                              generation_config={"response_mime_type": "application/json"})

f = genai.upload_file("./media/woz1-rec.mp3")
aud = genai.get_file(name=f.name) # get uploaded file from google servers
response = model.generate_content([aud]) # generate timestamps and keywords in JSON format

# output response to json file
f = open("out/woz1-timestamps.json", "w")
f.write(response.text)
f.close()