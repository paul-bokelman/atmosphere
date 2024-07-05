from typing import List
import os
import json
import inquirer
import google.generativeai as genai
import time
from constants import sfx_dir, classifications_out
from db.models import db, Keyword, Sound, SoundKeyword, SoundSchema
from db.queries import get_or_insert_keyword, insert_sound, insert_relationships
from lib.utils import confirmation, info, success, error


# should be moved...
class ClassificationSchema(SoundSchema):
    keywords: List[str]

# assign keywords to each raw sound (continue from saved classifications)
def classify():
    sounds: List[SoundSchema] = []
    categories = os.listdir(sfx_dir)

    info("Fetching all sounds...")

    # extract all sound effects and their categories
    for category in categories:
        category_path = os.path.join(sfx_dir, category)
        sfx_files = os.listdir(category_path)

        for sfx_file in sfx_files:
            name, ext = os.path.splitext(sfx_file)
            sounds.append({'category': category, 'name': name, 'ext': ext.replace('.', '')})

    success(f"Found {len(sounds)} sounds")

    relations: List[ClassificationSchema] = [] # store all sound effect classifications
    total_sounds = len(sounds)

    # check if there are any saved classifications
    if os.path.exists(classifications_out):
        relations = json.loads(open(classifications_out, "r").read())

        # check if all sounds have been classified
        if len(relations) == total_sounds:
            # already classified -> prompt user to reset
            if not confirmation("All sounds have been classified, reset classifications?"):
                return info("Returning to menu...")
            
            # double check before reset
            if not confirmation("Are you sure you want to reset all classifications?"):
                return info("Reset cancelled, returning to menu...")
            
            info("Resetting classifications...")
            relations = [] # reset classifications
            info("Classifications reset")

    if len(relations) == 0 or (not os.path.exists(classifications_out)): 
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')

        if not os.path.exists(classifications_out):
            new_classifications_file = open(classifications_out, "w")
            new_classifications_file.write("[]")
            new_classifications_file.close()

        
        for s in sounds:
            info(f"Sound {len(relations) + 1}/{total_sounds} - {s['category']}/{s['name']} being described by Gemini...", "cyan") # print sound info
            aud_name = s['name']
            response = model.generate_content(f"""Describe in two sentences an audio recording of {aud_name}.""")
            relations.append({**s, 'keywords': [response.text]}) # add sound and keywords to relations
            time.sleep(5)

        with open(classifications_out, "w") as classifications_file:
                classifications_file.write(json.dumps(relations, indent=4))

    success("\nSuccessfully classified all sounds 💪")

# seed database with data
def seed():
    # check for classifications
    if not os.path.exists(classifications_out):
        return error("No classifications found, please classify sounds before seeding")

    # confirmation before wipe
    if not confirmation("This action will delete all current entries, continue?"):
        return info("Seed cancelled, returning to menu...")
    
    info("Seeding database...")

    # drop and create tables
    models = (Keyword, Sound, SoundKeyword)
    db.connect()
    db.drop_tables(models)
    db.create_tables(models)

    classifications: List[ClassificationSchema] = json.loads(open(classifications_out, "r").read())

    # add and connect all data
    for cf in classifications:
        keyword_ids = [] # store keyword ids

        # retrieve or add each keyword to db
        for keyword in cf['keywords']:
            id = get_or_insert_keyword(keyword)
            keyword_ids.append(id)
        
        sound_id = insert_sound({'name': cf['name'],'category': cf['category'], "ext": cf['ext']}) # add sound to db
        insert_relationships(sound_id, keyword_ids) # create relationship between sound and keywords

    success("Successfully seeded database 🌴")