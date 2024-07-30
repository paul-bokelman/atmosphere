import inquirer

helper_commands = {
    "Back 🔙": lambda: None
}

# prompt user for one of the helper commands
def commands():
    # prompt user for command
    questions = [inquirer.List('command', message="Helpers", choices=[l for l in helper_commands.keys()])]
    answers = inquirer.prompt(questions)

    # no answers -> return
    if answers is None:
        return

    helper_commands[answers['command']]() # execute command