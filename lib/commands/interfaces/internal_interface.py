import inquirer
import os
import requests
from lib.utils import info, error, success
from lib.commands.internal.seed import seed

internal_commands = {
    "Seed Showcase 🌱": seed,
    "Back 🔙": lambda: None
}

def commands():
    """Internal commands interface"""
    key = os.getenv('AUTH_KEY')

    # not set -> exit
    if key is None:
        error("Authorization key is not set")
        return
    
    # check if AUTH_KEY is valid
    try: 
        info("Checking authorization key...")
        r = requests.get(f"{os.getenv('SERVER_URL')}/authorized", headers={"Authorization": f"Bearer {key}"})
        r.raise_for_status()
        success("Authorization key is valid")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            error("Authentication failed, generator and server keys do not match")
        else:
            error("An unexpected error occurred while validating AUTH_KEY")
        return
    except Exception as e:
        error("An unexpected error occurred")
        return 

    # prompt user for command
    questions = [inquirer.List('command', message="Internal Commands", choices=[l for l in internal_commands.keys()])]
    answers = inquirer.prompt(questions)

    # no answers -> return
    if answers is None:
        return

    internal_commands[answers['command']]() # execute command