from db.models import Keyword, Sound, SoundKeyword, SoundSchema, SoundSchemaWithId, SoundSchemaWithKeywords
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
def get_sound(id: int) -> SoundSchemaWithId | None:
    try: 
        sound = Sound.get(Sound.id == id)
        return {"id": sound.id, "name": sound.name, "category": sound.category, "ext": sound.ext}
    except: 
        return None

# insert sound
def insert_sound(sound: SoundSchema) -> int:
    new_sound = Sound(name=sound['name'], category=sound['category'], ext=sound['ext'])
    new_sound.save()
    return new_sound.get_id()

# get all sounds
def get_sounds() -> List[SoundSchemaWithKeywords]:
    sounds = Sound.select() # get all sounds

    # get all keywords for each sound
    sounds_with_keywords: List[SoundSchemaWithKeywords] = []
    for sound in sounds:
        keywords = Keyword.select().join(SoundKeyword).join(Sound).where(Sound.id == sound.id)
        keywords = [keyword.label for keyword in keywords]
        sounds_with_keywords.append({"id": sound.id, "name": sound.name, "category": sound.category, "ext": sound.ext, "keywords": keywords})

    return sounds_with_keywords
    

# ------------------------------- SOUND_KEYWORD ------------------------------ #

# create relationship between sound and keywords
def insert_relationships(sound_id: int, keyword_ids: List[int]):
    SoundKeyword.insert_many([{"sound": sound_id, "keyword": k_id} for k_id in keyword_ids]).execute()

# get sounds with matching keywords
def get_associated_sounds(keywords: List[str]) -> List[SoundSchemaWithId]:
    associated_sounds = Sound.select().join(SoundKeyword).join(Keyword).where(Keyword.label.in_(keywords))
    return [{"name": s.name, "category": s.category, "ext": s.ext, "id": s.id} for s in associated_sounds]