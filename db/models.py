from peewee import SqliteDatabase, SQL, Model, CharField, AutoField, ForeignKeyField
from typing import TypedDict, List

db = SqliteDatabase('sfx.db')

class SoundSchema(TypedDict):
    name: str
    category: str
    ext: str

class SoundSchemaWithId(SoundSchema, TypedDict):
    id: int

class SoundSchemaWithKeywords(SoundSchemaWithId):
    keywords: List[str]

class KeywordSchema(TypedDict):
    label: str

class KeywordSchemaWithId(KeywordSchema):
    id: int

class BaseModel(Model):
    class Meta:
        database = db

# individual keywords for reference
class Keyword(BaseModel):
    id = AutoField()
    label = CharField() # the value of the keyword

    class Meta:
        table_name = 'keywords'
        constraints = [SQL('UNIQUE (label)')]

# sound effect model 
class Sound(BaseModel):
    id = AutoField()
    name = CharField() # name of sound file
    ext = CharField() # store file extension
    category = CharField() # category of sound


    class Meta:
        table_name = 'sounds'

# define many to many relationship between models
class SoundKeyword(BaseModel):
    sound = ForeignKeyField(Sound, backref='sound_keywords')
    keyword = ForeignKeyField(Keyword, backref='keyword_sounds')

    class Meta:
        table_name = 'sound_keywords_relationships'