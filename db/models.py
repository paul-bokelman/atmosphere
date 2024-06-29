from peewee import SqliteDatabase, SQL, Model, CharField, ForeignKeyField
from typing import TypedDict

db = SqliteDatabase('sfx.db')

class SoundSchema(TypedDict):
    description: str
    url: str

class SoundSchemaWithId(SoundSchema, TypedDict):
    id: int

class KeywordSchema(TypedDict):
    label: str

class KeywordSchemaWithId(KeywordSchema):
    id: int

class BaseModel(Model):
    class Meta:
        database = db

# individual keywords for reference
class Keyword(BaseModel):
    label = CharField() # the value of the keyword

    class Meta:
        table_name = 'keywords'
        constraints = [SQL('UNIQUE (label)')]

# sound effect model 
class Sound(BaseModel):
    description = CharField() # simple description of sound
    url = CharField() # store url to sound effect (would be nice to store raw audio)

    class Meta:
        table_name = 'sounds'

# define many to many relationship between models
class SoundKeyword(BaseModel):
    sound = ForeignKeyField(Sound, backref='sound_keywords')
    keyword = ForeignKeyField(Keyword, backref='keyword_sounds')

    class Meta:
        table_name = 'sound_keywords_relationships'

db.connect()
db.create_tables([Keyword, Sound, SoundKeyword])