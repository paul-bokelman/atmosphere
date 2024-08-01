from typing import TypedDict, Union, NotRequired, List

# -------------------------------- ATMOSPHERE -------------------------------- #

class GeneratorOptionsSchema(TypedDict):
    recording_location: str # local file or url
    timestamps_out: NotRequired[str]
    mappings_out: NotRequired[str]
    out: NotRequired[str]

class AudioOverlayConfigSchema(TypedDict):
    margins: tuple[int, int]
    gain: int # dB
    fade: tuple[int, int]
    length: int

class TimestampSchema(TypedDict):
    time: str
    description: str
    category: str
    keywords: List[str]

# adjusted schema for the addition of sound
class MappedTimestampSchema(TimestampSchema):
    sound_id: str

# --------------------------------- INTERNAL --------------------------------- #

class AmbientSectionSchema(TypedDict):
    start: int
    end: int
    description: str

class ChapterSchema(TypedDict):
    number: int
    name: str
    audio: str
    text: str
    ambientSections: list[AmbientSectionSchema]

class BookSchema(TypedDict):
    title: str
    slug: str
    author: str
    description: str
    year: int
    genre: str
    cover: NotRequired[str]
    accentColor: NotRequired[str]
    chapters: list[ChapterSchema]

class SeedDataSchema(TypedDict):
    cover: str
    accentColor: str
    url: str