from typing import Optional, List, Any
import requests
import inquirer
from io import BytesIO
from termcolor import _types, colored
from pydub import AudioSegment
from constants import sfx_dir, bbc_sfx_url, bbc_sfx_media_url

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

# get sound effect candidates
def sfx_candidates(category: str, keywords: List[str]):
    #formatted_candidates = "" # formatted candidates for model
    r = requests.post(bbc_sfx_url, json={
        "criteria":{"from":0,"size":1000,"tags":keywords,"categories":[category],"durations":None,"continents":None,"sortBy":None,"source":None,"recordist":None,"habitat":None}
    })

    return r.json()['results']   #formatted_candidates

# download sound effects given id
def candidate_sfx_file(id: str) -> AudioSegment:
    url = f"{bbc_sfx_media_url}/{id}.mp3"
    response = requests.get(url)
    bytes: Any = BytesIO(response.content)
    audio = AudioSegment.from_file(bytes)
    return audio