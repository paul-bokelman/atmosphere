import os
from dotenv import load_dotenv
import inquirer
from termcolor import colored
import google.generativeai as genai
from commands import atmosphere, helpers

load_dotenv() # load in environment variables
genai.configure(api_key=os.getenv('GEMINI_API_KEY')) # configure gemini with api key

def exit_command():
    print("Thanks for using Atmosphere, exiting...")
    return exit()

commands = {
    "Generate Immersive Audio 💫": atmosphere.generate,
    "Helpers 🛠": helpers.commands,
    "Exit 🚪": exit_command,
}

# main interface loop
def main():
  print(f"Welcome to {colored('Atmosphere', 'light_magenta')}! Select an option below:")

  # continuously prompt user for commands until exit
  while True:
    print() # newline

    # prompt user for command
    questions = [inquirer.List('command', message="Commands", choices=[l for l in commands.keys()])]
    answers = inquirer.prompt(questions)

    # no answers -> exit
    if answers is None:
      return exit_command()

    commands[answers['command']]() # execute command

# run main function
if __name__ == "__main__":
    main()