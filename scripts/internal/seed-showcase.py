from typing import TypedDict, NotRequired
import requests
import os
import re
import json
from dotenv import load_dotenv
from termcolor import colored
from bs4 import BeautifulSoup, Tag

class AmbientSectionSchema(TypedDict):
    start: str
    end: str
    description: str

class ChapterSchema(TypedDict):
    number: int
    name: str
    audio: str
    text: str
    ambientSections: list[AmbientSectionSchema]

class BookSchema(TypedDict):
    title: str
    slug: str
    author: str
    description: str
    year: int
    genre: str
    cover: NotRequired[str]
    accentColor: NotRequired[str]
    chapters: list[ChapterSchema]

class SeedDataSchema(TypedDict):
    cover: str
    accentColor: str
    url: str

load_dotenv()

def scrape_book(url: str) -> BookSchema:
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

    chapter_urls: list[str] = []

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

        print(f"Scraping chapter {chapter_index + 1} of {book['title']}")

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

        print(colored(f"Successfully scraped chapter {chapter['number']} of {book['title']}", 'green'))

    return book

unprocessed_books: list[BookSchema] = []

with open("scripts/internal/seed-data.json", "r") as f:
    seed_data: list[SeedDataSchema] = json.load(f)

    print(f"Loaded {len(seed_data)} entries...")

    for seed in seed_data:
        print(f"Scraping {seed['url']}...")
        pre_book = scrape_book(seed['url'])
        pre_book["accentColor"] = seed["accentColor"]
        pre_book["cover"] = seed["cover"]

        unprocessed_books.append(pre_book)
        print(colored(f"Successfully scraped {pre_book['title']}", 'green'))

for unprocessed_book in unprocessed_books:
    print(f"Uploading {unprocessed_book['title']}...")

    try: 
        r = requests.post(f"{os.getenv('SERVER_URL')}/books", json=unprocessed_book, headers={"Authorization": f"Bearer {os.getenv('AUTH_KEY')}"})
        r.raise_for_status()
        print(colored(f"Successfully uploaded {unprocessed_book['title']}", 'green'))
    except requests.exceptions.HTTPError as e:
        print(e)
        print(colored(f"Failed to upload {unprocessed_book['title']}", 'red'))
    except Exception as e:
        print(colored(f"An unexpected error occurred while uploading {unprocessed_book['title']}", 'red'))

books = []