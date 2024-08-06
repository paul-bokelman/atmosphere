from typing import List
from lib.types import BookSchema, ChapterSchema, SeedDataSchema, AmbientSectionSchema, MappedTimestampSchema
import os
import re
import json
import requests
import inquirer
from bs4 import BeautifulSoup, Tag
import constants
from lib.commands.general import generator
from lib.utils import info, success, error, warn, time_to_ms, ms_to_s, upload_to_s3, confirmation

def _scrape_book(url: str) -> BookSchema:
    """Given a URL, scrape the website for book data and return a BookSchema object"""
    assert "https://etc.usf.edu/lit2go/" in url, "Invalid URL" # only lit2go urls are supported
    r = requests.get(url)

    assert r.status_code == 200, "Failed to fetch page"

    soup = BeautifulSoup(r.content, 'html.parser')

    assert soup.h2 is not None, "No title found"
    assert soup.h3 is not None, "No author found"

    title = soup.h2.text.strip()
    author = soup.h3.text.replace("by ", "").strip()
    slug = title.lower().replace(" ", "-")

    description_container = soup.find('div', attrs={'id': 'column_primary'})

    assert description_container is not None, "Description container not found"
    assert isinstance(description_container, Tag), "Description container is not a Tag"
    description_p = description_container.find_all('p')[1]

    assert description_p is not None, "No description found"
    assert isinstance(description_p, Tag), "Description is not a Tag"

    description = description_p.text.strip()

    year_container = soup.find(string=re.compile(r'Year Published:'))
    assert year_container is not None, "No year found"
    assert year_container.parent is not None, "No year container found"
    assert year_container.parent.next_sibling is not None, "No year sibling found"

    year = year_container.parent.next_sibling.text.strip()

    genre_container = soup.find(string=re.compile(r'Genre:'))
    assert genre_container is not None, "No genre found"
    assert genre_container.parent is not None, "No genre container found"
    genre_link = genre_container.parent.find_next("a")
    assert genre_link is not None, "No genre sibling found"

    genre = genre_link.text.strip()

    book = BookSchema(
        title=title, 
        slug=slug, 
        year=int(year), 
        genre=genre, 
        author=author, 
        description=description, 
        chapters=[]
    )

    chapters_container = soup.find('dl')
    assert chapters_container is not None, "Chapters container not found"
    assert isinstance(chapters_container, Tag), "Chapters container is not a Tag"

    chapter_urls: List[str] = []

    # get all basic chapter info and urls
    for chapter_ele in chapters_container.find_all('dt'):
        assert isinstance(chapter_ele, Tag), "Chapter element is not a Tag"

        link = chapter_ele.find('a')
        assert isinstance(link, Tag), "No link found"
        url = link.attrs['href']

        chapter_urls.append(url)

    # get audio and text from each chapter
    for (chapter_index, chapter_url) in enumerate(chapter_urls):
        r = requests.get(chapter_url)
        cs = BeautifulSoup(r.content, 'html.parser') # get chapter page soup

        info(f"Scraping chapter {chapter_index + 1} of {book['title']}")

        assert cs.h4 is not None, "No chapter name found"
        name = cs.h4.text.strip().replace("“", "").replace("”", "")

        text_container = cs.find('div', attrs={'id': 'i_apologize_for_the_soup'})
        assert text_container is not None, "No text container found"
        assert isinstance(text_container, Tag), "Text container is not a Tag"

        audio_container = cs.find('audio')
        assert audio_container is not None, "No audio container found"
        assert isinstance(audio_container, Tag), "Audio container is not a Tag"

        audio_source  = audio_container.find('source', attrs={'type': 'audio/mpeg'})
        assert audio_source is not None, "No audio source found"
        assert isinstance(audio_source, Tag), "Audio source is not a Tag"

        audio_url = audio_source.attrs['src']

        paragraphs = []
        for p in text_container.find_all('p'):
            assert isinstance(p, Tag), "Paragraph is not a Tag"
            paragraphs.append(p.text.strip())

        text = "\n".join(paragraphs)
        
        chapter = ChapterSchema(
            number=(chapter_index + 1),
            name=name,
            audio=audio_url, 
            text=text, 
            ambientSections=[],
        )

        book['chapters'].append(chapter)

        success(f"Successfully scraped chapter {chapter['number']} of {book['title']}")

    return book

def _upload_to_server(books: List[BookSchema], delete_on_collision: bool = False, save_request = False, second_attempt: bool = False):
    """Upload books to showcase server"""
    collisions = []
    for book in books:
        info(f"Uploading {book['title']}...")

        if save_request:
            if not os.path.exists(constants.seed_req_out_dir):
                os.mkdir(constants.seed_req_out_dir)
            with open(f"{constants.seed_req_out_dir}/{book['slug']}.json", "w") as f:
                json.dump(book, f)

        try: 
            r = requests.post(f"{os.getenv('SERVER_URL')}/books", json=book, headers={"Authorization": f"Bearer {os.getenv('AUTH_KEY')}"})
            r.raise_for_status()
            success(f"Successfully uploaded {book['title']}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                warn(f"Collision detected for {book['title']}, {'deleting...' if delete_on_collision else 'skipping...' }")
                if delete_on_collision:
                    delete_r = requests.delete(f"{os.getenv('SERVER_URL')}/books/{book['slug']}", headers={"Authorization": f"Bearer {os.getenv('AUTH_KEY')}"})

                    # successfully deleted book -> reupload (add to collisions)
                    if delete_r.status_code == 200:
                        info(f"Deleted {book['title']}")
                        collisions.append(book)
                    else:
                        error(f"Failed to delete {book['title']}")
            else:
                if e.response.status_code == 504:
                    warn(f"Gateway timeout while uploading {book['title']}. Book may have been uploaded, please check server.")
                else:
                    error(f"Failed to upload {book['title']}")
        except Exception as e:
            error(f"An unexpected error occurred while uploading {book['title']}")
    
    # try to reupload books that collided
    if len(collisions) > 0 and not second_attempt:
        _upload_to_server(collisions, delete_on_collision, save_request, second_attempt=True)
        
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
            unprocessed_book = _scrape_book(seed['url']) # scrape website for book data
            unprocessed_book["accentColor"] = seed["accentColor"]
            unprocessed_book["cover"] = seed["cover"]

            unprocessed_books.append(unprocessed_book)
            success(f"Successfully scraped {unprocessed_book['title']}")

    if skip_immersion:
        info("Skipping chapter immersion...")
        _upload_to_server(unprocessed_books, delete_on_collision, save_request)
        return

    books: List[BookSchema] = []

    # run atmosphere generator on each chapter of each book
    for unprocessed_book in unprocessed_books:
        info(f"Processing {unprocessed_book['title']}...")

        # process each chapter
        for chapter in unprocessed_book['chapters']:
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
                    ambient_section: AmbientSectionSchema = {
                        'start': ms_to_s(time_to_ms(mapping['timestamp']['time']) - constants.audio_overlay_config['margins'][0]),
                        'end': ms_to_s(time_to_ms(mapping['timestamp']['time']) +  constants.audio_overlay_config['margins'][1]),
                        'description': mapping['sound_description']
                    }
                    ambient_sections.append(ambient_section)
            
            # delete temp files after upload
            os.remove(temp_out_path)
            os.remove(temp_mappings_out_path)

            chapter['audio'] = url
            chapter['ambientSections'] = ambient_sections

        books.append(unprocessed_book)

    # upload all immersive books to showcase server
    _upload_to_server(books, delete_on_collision, save_request)
