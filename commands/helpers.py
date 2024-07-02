import inquirer
from db import helpers

helper_commands = {
    "Seed 🌱": helpers.seed,
    "Classify 🔍": helpers.classify,
    "Back 🔙": lambda: None
}

# prompt user for one of the following: seed, build tables, reclassify, or back
def commands():
    # prompt user for command
    questions = [inquirer.List('command', message="Helpers", choices=[l for l in helper_commands.keys()])]
    answers = inquirer.prompt(questions)

    # no answers -> return
    if answers is None:
        return

    helper_commands[answers['command']]() # execute command