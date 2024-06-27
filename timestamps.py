import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=API_KEY)

instructions = "Your job is to receive an audio book sample and understand the setting. Find 5-10 timestamps throughout the audio to place ambient sound effects like 'leaves rustling' or 'water flowing'. Example response: 0:15-0:32 - leaves rustling in the wind."

model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=instructions)

aud = genai.get_file(name="files/8l3chfazgyw3")

prompt = "Give short responses of some timestamps and what general sound effect might be heard. For example: 0:15-0:32 - leaves rustling in the wind."

prompt2 = "Give a general ambient sound for the overall setting of area."

response = model.generate_content([aud])
print(response.text)