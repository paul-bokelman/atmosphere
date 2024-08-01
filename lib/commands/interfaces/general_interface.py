import inquirer
from lib.commands.general.generator import generate

general_commands = {
    "Generate 💫": generate,
    "Back 🔙": lambda: None
}

def commands():
    """General commands interface"""

    # prompt user for command
    questions = [inquirer.List('command', message="General Commands", choices=[l for l in general_commands.keys()])]
    answers = inquirer.prompt(questions)

    # no answers -> return
    if answers is None:
        return

    general_commands[answers['command']]() # execute command