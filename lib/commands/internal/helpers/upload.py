from lib.types import BookSchema, ChapterSchema
import os
import json
import requests
import constants
from lib.utils import info, success, error, warn

def chapter(book_slug: str, chapter_data: ChapterSchema, delete_on_collision = False, second_attempt = False):
    """Upload a chapter related to a book to the showcase server"""
    collision = False
    info(f"Uploading chapter: {chapter_data['name']}...")

    url = f"{os.getenv('SERVER_URL')}/books/{book_slug}/{chapter_data['number']}"

    # cache request to file
    if not os.path.exists(constants.seed_cache_dir):
        os.mkdir(constants.seed_cache_dir)
    if not os.path.exists(f"{constants.seed_cache_dir}/{book_slug}"):
        os.mkdir(f"{constants.seed_cache_dir}/{book_slug}")
    with open(f"{constants.seed_cache_dir}/{book_slug}/{book_slug}-c{chapter_data['number']}.json", "w") as f:
        json.dump(chapter_data, f)

    try: 
        r = requests.post(url, json=chapter_data, headers={"Authorization": f"Bearer {os.getenv('AUTH_KEY')}"})
        r.raise_for_status()
        success(f"Successfully uploaded chapter: {chapter_data['name']}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            warn(f"Collision detected for chapter: {chapter_data['name']}, {'deleting...' if delete_on_collision else 'skipping...' }")
            if delete_on_collision:
                delete_r = requests.delete(url, headers={"Authorization": f"Bearer {os.getenv('AUTH_KEY')}"})

                # successfully deleted book -> reupload (add to collisions)
                if delete_r.status_code == 200:
                    info(f"Deleted chapter: {chapter_data['name']}")
                    collision = True
                else:
                    error(f"Failed to delete chapter: {chapter_data['name']}")
        else:
            if e.response.status_code == 504:
                warn(f"Gateway timeout while uploading chapter: {chapter_data['name']}")
            else:
                error(f"Failed to upload chapter: {chapter_data['name']}")
    except Exception as e:
        error(f"An unexpected error occurred while uploading chapter: {chapter_data['name']}")

    # try to reupload book if collision (only once)
    if collision and not second_attempt:
        chapter(book_slug, chapter_data, delete_on_collision, second_attempt=True)

def book(book_data: BookSchema, delete_on_collision = False, second_attempt = False):
    """Upload a book to the showcase server"""
    collision = False
    info(f"Uploading book: {book_data['title']}...")

    post_url = f"{os.getenv('SERVER_URL')}/books"
    delete_url = f"{os.getenv('SERVER_URL')}/books/{book_data['slug']}"
    
    # cache request to file
    if not os.path.exists(constants.seed_cache_dir):
        os.mkdir(constants.seed_cache_dir)
    if not os.path.exists(f"{constants.seed_cache_dir}/{book_data['slug']}"):
        os.mkdir(f"{constants.seed_cache_dir}/{book_data['slug']}")
    with open(f"{constants.seed_cache_dir}/{book_data['slug']}/{book_data['slug']}.json", "w") as f:
        json.dump(book_data, f)

    try: 
        r = requests.post(post_url, json=book_data, headers={"Authorization": f"Bearer {os.getenv('AUTH_KEY')}"})
        r.raise_for_status()
        success(f"Successfully uploaded book: {book_data['title']}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            warn(f"Collision detected for book: {book_data['title']}, {'deleting...' if delete_on_collision else 'skipping...' }")
            if delete_on_collision:
                delete_r = requests.delete(delete_url, headers={"Authorization": f"Bearer {os.getenv('AUTH_KEY')}"})

                # successfully deleted book -> reupload (add to collisions)
                if delete_r.status_code == 200:
                    info(f"Deleted book: {book_data['title']}")
                    collision = True
                else:
                    error(f"Failed to delete book: {book_data['title']}")
        else:
            if e.response.status_code == 504:
                warn(f"Gateway timeout while uploading book: {book_data['title']}. Book may have been uploaded, please check server.")
            else:
                error(f"Failed to upload book: {book_data['title']}")
    except Exception as e:
        error(f"An unexpected error occurred while uploading book: {book_data['title']}")

    # try to reupload book if collision (only once)
    if collision and not second_attempt:
        book(book_data, delete_on_collision, second_attempt=True)