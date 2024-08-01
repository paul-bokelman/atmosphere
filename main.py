import os
import argparse
from dotenv import load_dotenv
import inquirer
from termcolor import colored
import google.generativeai as genai
from lib.commands.general.generator import generate
from lib.commands.interfaces import general_interface, internal_interface
from lib.utils import info
from absl import logging

logging.set_verbosity(logging.FATAL) # only log fatal errors

def exit_command():
    print("Thanks for using Atmosphere, exiting...")
    return exit()

commands = {
    "Generate Immersive Audio 💫": generate,
    "General 🚀": general_interface.commands,
    "Internal 🔒": internal_interface.commands,
    "Exit 🚪": exit_command,
}

# main interface loop
def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-e", "--env", help="Environment file to load", type=str)
  args = parser.parse_args()

  env = args.env if args.env else "development"

  if env not in ["development", "production"]:
    print("Invalid environment, please use 'development' or 'production'")
    return
  
  info(f"Loading environment file .env.{env}")

  if env == "production":
    print(colored(f"Atmosphere is running in {env} environment", 'yellow'))

  load_dotenv(f".env.{env}", verbose=True) 

  genai.configure(api_key=os.getenv('GEMINI_API_KEY')) # configure gemini with api key

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