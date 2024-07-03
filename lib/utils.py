from typing import Optional, List
import inquirer
from termcolor import _types, colored
from constants import sfx_dir

# seconds to milliseconds
def ms(seconds: int) -> int:
    return seconds * 1000

# function to convert interval to milliseconds
def time_to_ms(interval: str) -> int:
    minutes, seconds = interval.split(':')
    return (int(minutes) * 60 + int(seconds)) * 1000

# convert timestamp (<start>-<end>) to milliseconds
def interval_to_ms(interval: str) -> List[int]:
    start, end = interval.split('-')
    return [time_to_ms(start), time_to_ms(end)]

def sfx_path(category: str, name: str, ext: str, id: Optional[int] = None) -> str:
    return f"{sfx_dir}/{category}/{name}.{ext}"

# prompt user for confirmation 
def confirmation(message: str, ) -> bool:
    questions = [inquirer.Confirm("confirmation", message=message, default=False)]
    answers = inquirer.prompt(questions)
    # no answers -> return false
    if answers is None:
        print(colored("No answers, returning to menu...", "red"))
        return False
    return answers['confirmation']

# info message
def info(message: str, color: _types.Color = "grey"):
    print(colored(message, color))

# success message
def success(message: str):
    print(colored(message, "green"))

# error message
def error(message: str):
    print(colored(message, "red"))