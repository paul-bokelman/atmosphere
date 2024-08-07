![gh-banner](https://github.com/user-attachments/assets/093a37cf-c353-4ec2-96e8-7228ed6e7d1e)

# Atmosphere: Immersive Audio Book Generation

Built for [Gemini API Developer Competition](https://ai.google.dev/competition)

Atmosphere Showcase: [atmosphere.pab.dev](https://atmosphere.pab.dev/)

Atmosphere Showcase Repository: [paul-bokelman/atmosphere-showcase](https://github.com/paul-bokelman/atmosphere-showcase)

## About

Atmosphere aims to enhance the storytelling experience by overlaying ambient audio onto audio book segments with strong auditory and sensory scenes. By utilizing the BBC sound effects library, Atmosphere is able to provide a rich and immersive experience for listeners. Atmosphere is built with Python and utilizes the Gemini API to generate immersive audio books.

## Under the hood

Atmosphere interacts with the [Google Gemini Flash](https://deepmind.google/technologies/gemini/flash/) API in 2 independent steps to generate immersive and cohesive audio recordings.

### Step 1: Timestamps

[Timestamp Schema](https://github.com/paul-bokelman/atmosphere/blob/1bba0e11c3f146088034c5da78de67efaceb462e/lib/types.py#L17-L21)

Initially, Atmosphere is provided with the audio recording in its entirety, and is tasked with locating timestamps within the audio book that correspond to scenes that would be enhanced by ambient audio. In addition to providing the timestamp of these scenes, Gemini also produces a concise description of the context of the scene, and salient keywords from the scene that construct the overall tone of the segment.

### Step 2: Mappings

[Mappings Schema](https://github.com/paul-bokelman/atmosphere/blob/1bba0e11c3f146088034c5da78de67efaceb462e/lib/types.py#L24-L27)

Using the keywords gathered for each scene identified by Gemini, Atmosphere sifts through the 33,000+ sound effects and their associated keywords in the BBC sound effects library, and acquires all sounds with at least one keyword matching that of the scene. With all sound effects a minimum of one matching keyword compiled into a list, Gemini is prompted to pick the sound from the list that best matches the scene description created by Gemini in step 1.

### Step 3: Overlay

Once all sounds have been selected for each scene, Atmosphere normalizes, fades, trims then overlays the selected sound effects onto the corresponding audio book segments.

## Running Atmosphere Locally

1. Clone the Atmosphere repository to your local machine.
2. Create and use a virtual environment by running `python3.11 -m venv env && source env/bin/activate`.
3. Install the required dependencies by running `python3.11 -m pip install -r requirements.txt`.
4. Add your Gemini API key to the `.env.development` as `GEMINI_API_KEY` file in the root of the Atmosphere directory.
5. Create a `recordings` and `out` directory under a `media'`directory in the root of the Atmosphere directory (`/media/recordings/`, `/media/out`). This is where you will place the audio book you would like to generate an immersive version of.
6. Place the audio book you would like to generate an immersive version of in the 'recordings' directory.
7. Enter the command `python3.11 main.py`. This will beginning running the generator.
8. Once running, select "Generate Immersive Audio" in the drop down menu, and press enter.
9. Follow the prompts to select the audio book you would like to generate an immersive version of
10. The output mp3 file will be found in `/media/out/{YOUR_AUDIO_BOOK_NAME}/{YOUR_AUDIO_BOOK_NAME}-immersive.mp3`
11. Show off your immersive audio book to your friends and family!

## Inspiration and Use Cases

Atmosphere was inspired by the idea of enhancing the storytelling experience by providing listeners with a more immersive and sensory-rich experience. By overlaying ambient audio onto audio book segments with strong auditory and sensory scenes, Atmosphere is able to provide a rich and immersive experience for listeners. Atmosphere could be used to enhance the storytelling experience for a wide variety of audio books, including fiction, non-fiction, and educational audio books. An immersive audio book could be used to help listeners better understand and visualize the story, and could be used to help listeners better engage with the story.

Ultimately, a product like Atmosphere could be added onto audio book streaming services such as Google Play and Audible to offer customers an immersive option alongside standard audio books, this would be especially desireable for heavily descriptive books and really try to invest the reader in the environment/scene. Atmosphere could also help improve the accessibility of audio books for people with visual impairments or poor visualization skills, by providing additional sensory information to help listeners better understand and connect with the story.

## Room for Improvement

Atmosphere excels at locating and assigning sounds for scenes that are general and require little to no contextualization or background information to properly classify. Examples of such scenes might be that of a river flowing in the distance, the hustle and bustle of a factory, or birds chirping. Scenes such as these can be simply taken at face value and directly interpreted without strict examination of tone, setting, and figurative language.

Admittedly, Atmosphere predictably struggles to convey adequate sensory enhancement in scenes that can not be snipped out of their place within the context of the story as a whole. Often Atmosphere takes scenes too literally and fails to understand the nuance of metaphors and may lose sight of the original scene. Similarly, Atmosphere has a tendency to place sound effects from far-removed and unfitting time frames into scenes; a habit that can be disorienting and distracting to listeners. Atmosphere regularly fails to recognize the nuanced differences between a busy medieval marketplace, and Times Square in the early 21st century. Again, this inadequacy is rooted in a lack of context for Gemini to draw from.

We believe that Atmosphere could be improved by providing Gemini with more context and background information about the audio book it is analyzing. By providing Gemini with more information about the setting, characters, and themes of the audio book, Gemini would be better equipped to identify and classify scenes that require more nuanced interpretation. Additionally, Atmosphere could be improved by providing Gemini with more information about the tone and style of the audio book, so that Gemini can better match the sound effects to the mood and atmosphere of the audio book.
