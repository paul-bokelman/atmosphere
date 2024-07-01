import os
from dotenv import load_dotenv
import inquirer
from termcolor import colored
import google.generativeai as genai
from lib import timestamps as ts, mappings as map, overlay
from db.seed import seed, create_tables

load_dotenv() # load in environment variables
genai.configure(api_key=os.getenv('GEMINI_API_KEY')) # configure gemini with api key

# generate immersive audio from input audio
def generate_immersive_audio():
  #? calculate estimated time?
  print(f'{colored("Generating immersive audio, this may take a while 🌟...", "grey")}')

  # generate timestamps
  print(f'{colored("Generating timestamps ⏳...", "grey")}')
  timestamps = ts.generate("./media/woz1-rec.mp3", "./out/woz1-timestamps.json")
  print(f'{colored("Timestamps generated successfully ⌛️", "green")}')

  # generate mappings
  print(f'{colored("Generating mappings 🧭...", "grey")}')
  mappings = map.generate(timestamps, out="./out/woz1-mappings.json")
  print(f'{colored("Mappings generated successfully 📍", "green")}')

  # overlay sound effects
  print(f'{colored("Overlaying sound effects 🔎...", "grey")}')
  overlay.do(audio_path="./media/woz1-rec.mp3", mappings=mappings, out="./out/woz1-immersive.mp3")
  print(f'{colored("Successfully overlaid sound effects 🎯", "green")}')

  # everything is complete 
  print(f'{colored("Audio immersion successful! 🔥", "green")}')


# main interface loop
def main():
  print(f"Welcome to {colored('Atmosphere', 'light_magenta')}! Select an option below:")

  # continuously prompt user for commands until exit
  while True:
    print()

    # prompt user for command
    questions = [inquirer.List('command', message="Commands", choices=["Generate Immersive Audio 💫", "Create Tables 🛠", "Seed Database 🌱", "Exit 🚪"])]
    answers = inquirer.prompt(questions)

    # no answers -> exit
    if answers is None:
      print("Thanks for using Atmosphere, exiting...")
      exit()

    # match command to function
    match answers['command']:
      case "Generate Immersive Audio 💫":
        generate_immersive_audio()
      case "Create Tables 🛠":
        create_tables()
      case "Seed Database 🌱":
        seed()
      case "Exit 🚪":
        print("Thanks for using Atmosphere, exiting...")
        exit()

# run main function
if __name__ == "__main__":
    main()