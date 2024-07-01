from typing import List

# get google drive download link
def g_link(gid: str) -> str:
    return f"https://drive.google.com/uc?export=download&id={gid}"

# internal function to convert interval to milliseconds
def _interval_to_ms(interval: str) -> int:
    minutes, seconds = interval.split(':')
    return (int(minutes) * 60 + int(seconds)) * 1000

# convert timestamp (<start>-<end>) to milliseconds
def timestamp_to_ms(interval: str) -> List[int]:
    start, end = interval.split('-')
    return [_interval_to_ms(start), _interval_to_ms(end)]