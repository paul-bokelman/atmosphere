import os
from dotenv import load_dotenv
import inquirer
from termcolor import colored
import google.generativeai as genai
from lib import timestamps as ts, mappings as map
from db.seed import seed

load_dotenv() # load in environment variables
genai.configure(api_key=os.getenv('GEMINI_API_KEY')) # configure gemini with api key

# generate immersive audio from input audio
def generate_immersive_audio():
  #? calculate estimated time?
  print(f'{colored("Generating immersive audio, this may take a while...", "grey")}')

  print(f'{colored("Generating timestamps...", "grey")}')
  timestamps = ts.generate("./media/woz1-rec.mp3", "./out/woz1-timestamps.json")
  print(f'{colored("Timestamps generated successfully", "green")}')

  print(f'{colored("Generating mappings...", "grey")}')
  mappings = map.generate(timestamps)
  print(f'{colored("Mappings generated successfully", "green")}')


# main interface loop
def main():
  print(f"Welcome to {colored('Atmosphere', 'light_magenta')}! Select an option below:")

  while True:
    print()

    questions = [
      inquirer.List('command', message="Commands", choices=["Generate Immersive Audio", "Seed Database", "Exit"]),
    ]

    answers = inquirer.prompt(questions)

    if answers is None:
      print("Thanks for using Atmosphere, exiting...")
      exit()

    match answers['command']:
      case "Generate Immersive Audio":
        generate_immersive_audio()
      case "Seed Database":
        seed()
      case "Exit":
        print("Thanks for using Atmosphere, exiting...")
        exit()

if __name__ == "__main__":
    main()