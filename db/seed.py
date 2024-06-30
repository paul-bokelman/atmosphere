from db.models import Keyword, Sound, SoundKeyword
from termcolor import colored
import inquirer
from db.data.data import relations
from db.queries import get_or_insert_keyword, insert_sound, insert_relationships


def seed():
    # confirmation before wipe

    questions = [
        inquirer.Confirm("confirmation", message="This action will delete all current entries, continue?", default=False),
    ]
    
    answers = inquirer.prompt(questions)

    if answers is None:
        print(colored("No answers, returning to menu...", "red"))
        return

    confirmation = answers['confirmation']

    if not confirmation:
        print(colored("Seed cancelled, returning to menu...", "grey"))
        return

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