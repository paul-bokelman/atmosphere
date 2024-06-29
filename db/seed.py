# seed db with data
from models import Keyword, Sound, SoundKeyword
from termcolor import colored
from data.data import relations
from queries import get_or_insert_keyword, insert_sound, insert_relationships

# confirmation before wipe
confirmation = input("This action will delete all current entries, continue? (y/n) ")

if confirmation != 'y':
    print(f'{colored("Confirmation failed, exiting", "yellow")}')
    exit()

# wipe database
Keyword().delete().execute()
Sound().delete().execute()
SoundKeyword().delete().execute()

# add and connect all data
for relation in relations:
    keyword_ids = [] # store keyword ids

    # retrieve or add each keyword to db
    for keyword in relation['keywords']:
        id = get_or_insert_keyword(keyword)
        keyword_ids.append(id)
    
    sound_id = insert_sound({'description': relation['description'], 'url': relation['url']}) #  add sound
    insert_relationships(sound_id, keyword_ids) # form connections between sound and keywords

print(f'{colored("Successfully seeded database", "green")}')