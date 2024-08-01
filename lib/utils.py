from typing import List, Any
from mypy_boto3_s3 import S3Client
import os
import requests
import inquirer
from io import BytesIO
import boto3
from termcolor import _types, colored
from pydub import AudioSegment
import constants

def ms(seconds: int) -> int:
    """Convert seconds to milliseconds"""
    return seconds * 1000

def time_to_ms(interval: str) -> int:
    """Convert time string to milliseconds"""
    minutes, seconds = interval.split(':')
    return (int(minutes) * 60 + int(seconds)) * 1000

def time_to_s(interval: str) -> int:
    """Convert time string to seconds"""
    minutes, seconds = interval.split(':')
    return int(int(minutes) * 60 + int(seconds))

# function to convert ms to time string
def ms_to_s(ms: int):
    """Convert milliseconds to seconds"""
    return int(ms / 1000)

def is_url(path: str):
    """Check if path is a URL"""
    return path.startswith("http")

def interval_to_ms(interval: str) -> List[int]:
    """Convert timestamp interval (<start>-<end>) to milliseconds"""
    start, end = interval.split('-')
    return [time_to_ms(start), time_to_ms(end)]

def confirmation(message: str) -> bool:
    """Prompt user for confirmation with message"""
    questions = [inquirer.Confirm("confirmation", message=message, default=False)]
    answers = inquirer.prompt(questions)
    # no answers -> return false
    if answers is None:
        print(colored("No answers, returning to menu...", "red"))
        return False
    return answers['confirmation']

def info(message: str, color: _types.Color = "grey"):
    """Print info message"""
    print(colored(message, color))

def success(message: str):
    """Print success message"""
    print(colored(message, "green"))

def error(message: str):
    """Print error message"""
    print(colored(message, "red"))

def sfx_candidates(category: str, keywords: List[str]):
    """Get sound effects candidates from BBC SFX API"""
    r = requests.post(constants.bbc_sfx_url, json={
        "criteria":{"from":0,"size":1000,"tags":keywords,"categories":[category],"durations":None,"continents":None,"sortBy":None,"source":None,"recordist":None,"habitat":None}
    })

    return r.json()['results']  # formatted_candidates

def candidate_sfx_file(id: str) -> AudioSegment:
    """Get sound effect file from BBC SFX API"""
    url = f"{constants.bbc_sfx_media_url}/{id}.mp3"
    response = requests.get(url)
    bytes: Any = BytesIO(response.content)
    audio = AudioSegment.from_file(bytes)
    return audio

def get_url_from_bucket(key: str): 
    """Get URL from AWS S3 bucket"""
    region = os.getenv('AWS_BUCKET_REGION')
    bucket_name = os.getenv('AWS_BUCKET')
    assert region is not None, "AWS_BUCKET_REGION not found"
    assert bucket_name is not None, "AWS_BUCKET not found"
    return f'https://{bucket_name}.s3.{region}.amazonaws.com/{key}'

def upload_to_s3(path: str, object_name: str) -> str:
    """Upload file to AWS S3 bucket"""
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.getenv('AWS_BUCKET')
    
    # check if environment variables are set
    assert access_key is not None, "AWS_ACCESS_KEY_ID not found"
    assert secret_key is not None, "AWS_SECRET_ACCESS_KEY not found"
    assert bucket_name is not None, "AWS_BUCKET not found"

    session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    s3: S3Client = session.client('s3')
    s3.upload_file(Filename=path, Bucket=bucket_name, Key=object_name)

    return get_url_from_bucket(object_name)