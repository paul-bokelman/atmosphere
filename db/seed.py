from termcolor import colored
import inquirer
from db.models import Keyword, Sound, SoundKeyword, db
from db.data.data import relations
from db.queries import get_or_insert_keyword, insert_sound, insert_relationships

# drop and create tables
def create_tables():
    # confirmation before dropping tables
    questions = [inquirer.Confirm("confirmation", message="This action will reset the database, continue?", default=False)]
    answers = inquirer.prompt(questions)
    
    # no answers -> return
    if answers is None:
        print(colored("No answers, returning to menu...", "red"))
        return

    # not yes -> return
    if not answers['confirmation']:
        print(colored("Create tables cancelled, returning to menu...", "yellow"))
        return

    print(colored("Creating tables...", "grey"))

    # drop and create tables
    models = (Keyword, Sound, SoundKeyword)
    db.connect()
    db.drop_tables(models)
    db.create_tables(models)

    print(colored("Successfully created tables ", "green"))

# seed database with data
def seed():
    # confirmation before wipe
    questions = [
        inquirer.Confirm("confirmation", message="This action will delete all current entries, continue?", default=False),
    ]
    
    answers = inquirer.prompt(questions)
    
    # no answers -> return
    if answers is None:
        print(colored("No answers, returning to menu...", "red"))
        return
    
    # not yes -> return
    if not answers['confirmation']:
        print(colored("Seed cancelled, returning to menu...", "yellow"))
        return
    
    print(colored("Seeding database...", "grey"))

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
        
        sound_id = insert_sound({'description': relation['description'], 'gid': relation['gid']}) # add sound to db
        insert_relationships(sound_id, keyword_ids) # create relationship between sound and keywords

    print(f'{colored("Successfully seeded database 🌴", "green")}')