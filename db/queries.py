from models import Keyword, Sound, SoundKeyword, SoundSchema, SoundSchemaWithId
from typing import List

# ---------------------------------- KEYWORD --------------------------------- #

# get keyword
def get_keyword(keyword: str) -> int:
    try: 
        keyword_id = Keyword.get(Keyword.label == keyword)
        return keyword_id
    except: 
        return -1
    
# get or insert keyword
def get_or_insert_keyword(keyword: str) -> int:
    existing = get_keyword(keyword)
    if existing != -1:
        return existing
    
    new_keyword = Keyword(label=keyword)
    new_keyword.save()
    return new_keyword.get_id()

# get all keywords
def get_keywords() -> List[str]:
    keywords = Keyword.select()
    return [keyword.label for keyword in keywords]

# ----------------------------------- SOUND ---------------------------------- #

# get sound
def get_sound(id: int) -> int:
    try: 
        sound = Sound.get_by_id(id)
        return sound
    except: 
        return -1

# insert sound
def insert_sound(sound: SoundSchema) -> int:
    new_sound = Sound(description=sound['description'], url=sound['url'])
    new_sound.save()
    return new_sound.get_id()

# get all sounds
def get_sounds() -> List[str]:
    sounds = Sound.select()
    return [sound for sound in sounds]

# ------------------------------- SOUND_KEYWORD ------------------------------ #

# create relationship between sound and keywords
def insert_relationships(sound_id: int, keyword_ids: List[int]):
    SoundKeyword.insert_many([{"sound": sound_id, "keyword": k_id} for k_id in keyword_ids]).execute()

# get sounds with matching keywords
def get_associated_sounds(keywords: List[str]) -> List[SoundSchemaWithId]:
    associated_sounds = Sound.select().join(SoundKeyword).join(Keyword).where(Keyword.label.in_(keywords))
    return [{"id": s.id, "description": s.description, "url": s.url} for s in associated_sounds]