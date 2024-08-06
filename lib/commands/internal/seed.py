from typing import List
from lib.types import BookSchema, SeedDataSchema, AmbientSectionSchema, MappedTimestampSchema
import os
import copy
import json
import inquirer
import constants
from lib.commands.general import generator
from lib.utils import info, success, error, time_to_ms, ms_to_s, upload_to_s3, confirmation
from lib.commands.internal.helpers import scrape, upload
        
def seed():
    """Seed the showcase server with seed data urls and generate immersive audio for each chapter"""
    unprocessed_books: List[BookSchema] = []

    skip_immersion = confirmation("Skip chapter immersion?")
    process_all = confirmation("Process all books?")
    delete_on_collision = confirmation("Delete existing books on collision?")
    save_request = confirmation("Save request data?")

    # load seed data
    with open(constants.showcase_seed_path, "r") as f:
        seed_data: List[SeedDataSchema] = json.load(f)
        info(f"Loaded {len(seed_data)} entries...")

        if not process_all:
            # parse book name from url for better readability
            slugs = [s['url'].replace('https://etc.usf.edu/lit2go/', '').split('/')[1].replace('/', '') for s in seed_data]

            questions = [inquirer.Checkbox('books', message="Select books to process (Press <space> to select, Enter when finished)", choices=slugs)]
            answers = inquirer.prompt(questions)

            # no answers -> exit
            if answers is None:
                error("No books selected, exiting...")
                return

            # filter seed data based on selected books
            seed_data = [s for s in seed_data if s['url'].replace('https://etc.usf.edu/lit2go/', '').split('/')[1].replace('/', '') in answers['books']]

        if len(seed_data) == 0:
            info("No books selected, exiting...")
            return
        
        for seed in seed_data:
            info(f"Scraping {seed['url']}...")
            unprocessed_book = scrape.book(seed['url']) # scrape website for book data
            unprocessed_book["accentColor"] = seed["accentColor"]
            unprocessed_book["cover"] = seed["cover"]

            unprocessed_books.append(unprocessed_book)
            success(f"Successfully scraped {unprocessed_book['title']}")

    # run atmosphere generator on each chapter of each book
    for unprocessed_book in unprocessed_books:
        info(f"Processing {unprocessed_book['title']}...")

        book_shell: BookSchema = copy.deepcopy(unprocessed_book)
        book_shell['chapters'] = []

        # upload basic book info to server (without chapters)
        upload.book(book_shell, delete_on_collision, save_request)

        # process each chapter
        for chapter in unprocessed_book['chapters']:
            if skip_immersion:
                info("Skipping chapter immersion...")
                upload.chapter(unprocessed_book['slug'], chapter, delete_on_collision, save_request) # upload chapter without immersive audio
                continue

            info(f"Processing chapter {chapter['number']}...")

            temp_out_path = f"./{unprocessed_book['slug']}-{chapter['number']}.mp3"
            temp_mappings_out_path = f"./mappings-{unprocessed_book['slug']}-{chapter['number']}.json"

            # generate immersive audio for chapter audio
            generator.generate({"recording_location": chapter['audio'], "mappings_out": temp_mappings_out_path, "out": temp_out_path})

            # upload generated audio to s3 and get url
            url = upload_to_s3(temp_out_path, f'{unprocessed_book["slug"]}-{chapter["number"]}.mp3')

            ambient_sections: List[AmbientSectionSchema] = []

            # get all ambient sections
            with open(temp_mappings_out_path, "r") as f:
                mappings: List[MappedTimestampSchema] = json.load(f)
                # get mappings for ambient sections
                for mapping in mappings:
                    start_position = ms_to_s(time_to_ms(mapping['timestamp']['time']) - constants.audio_overlay_config['margins'][0])
                    end_position = start_position + ms_to_s(constants.audio_overlay_config['length'] + constants.audio_overlay_config['margins'][1])
                    ambient_section: AmbientSectionSchema = {
                        'start': start_position,
                        'end': end_position,
                        'description': mapping['sound_description']
                    }
                    ambient_sections.append(ambient_section)
            
            # delete temp files after upload
            os.remove(temp_out_path)
            os.remove(temp_mappings_out_path)

            chapter['audio'] = url
            chapter['ambientSections'] = ambient_sections

            # upload chapter to server
            upload.chapter(unprocessed_book['slug'], chapter, delete_on_collision, save_request)
