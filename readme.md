![gh-banner](https://github.com/user-attachments/assets/093a37cf-c353-4ec2-96e8-7228ed6e7d1e)

# Atmosphere - Immersive Audio Books

Built for [Gemini API Developer Competition](https://ai.google.dev/competition)




# About Atmosphere

Atmosphere aims to enhance the storytelling experience by overlaying ambient audio onto audio book segments with strong auditory and sensory scenes. Atmosphere interacts with Gemini in three independent stages.
1. Initially, Atmosphere is provided with the audio book in its entirety, and is tasked with locating timestamps within the audio book that correspond to scenes that would be enhanced by ambient audio. In addition to providing the timestamp of these scenes, Gemini also produces a concise description of the context of the scene, and salient keywords from the scene that construct the overall tone of the segment.
2. Using the keywords gathered for each scene identified by Gemini, Atmosphere sifts through the 33,000+ sound effects and their associated keywords in the BBC sound effects library, and acquires all sounds with at least one keyword matching that of the scene. With all sound effects a minimum of one matching keyword compiled into a list, Gemini is prompted to pick the sound from the list that best matches the scene description created by Gemini in step 1.
3. Once Gemini has made a choice for the best fitting sound amongst the candidates, Gemini is given the mp3 file for the sound effect, and is prompted to listen and determine if its own choice really matches the scene at hand. If so, the next scene is evaluated, otherwise Gemini picks a new sound and is prompted to confirm again.

A gallery of Atmosphere's work can be accessed through a showcase web app located at https://github.com/paul-bokelman/atmosphere-showcase .


# Using Atmosphere Locally

1. On the main page of the repo, click the green "Code" button. Copy either the SSH or HTTPS link.
2. In your local terminal, navigate to a folder that you would like to place Atmosphere into.
3. Once in such a folder, type the command "git clone PLACEHOLDER" where PLACEHOLDER is the SSH or HTTPS link.
4. Enter the Atmosphere folder that is now in your local directory. By default, Atmosphere will generate an immersive version of "The Wizard of Oz". However, to change the input audio book, navigate to the "media" folder, and replace the mp3 file with an audio book of your choice in mp3 format.
5. Enter the command "python3 main.py". This will beginning running the generator.
6. Once running, select "Generate Immersive Audio" in the drop down menu, and press enter.
7. Once the generator is finished running, you can select to rerun the generator by selecting "Generate Immersive Audio" once again, or exit the program by selecting "Exit".
8. The output mp3 file will be found in the out directory.

# Inspiration and Possibilities




# Reflection and Shortcomings

Atmosphere excels at locating and assigning sounds for scenes that are general and require little to no contextualization or background information to properly classify. Examples of such scenes might be that of a river flowing in the distance, the hustle and bustle of a factory, or birds chirping. Scenes such as these can be simply taken at face value and directly interpreted without strict examination of tone, setting, and figurative language.

  Admittedly, Atmosphere predictably struggles to convey adequate sensory enhancement in scenes that can not be snipped out of their place within the context of the story as a whole. Often Atmosphere takes scenes too literally and fails to understand the nuance of metaphors and may lose sight of the original scene. Similarly, Atmosphere has a tendency to place sound effects from far-removed and unfitting time frames into scenes; a habit that can be disorienting and distracting to listeners. Atmosphere regularly fails to recognize the nuanced differences between a busy medieval marketplace, and Times Square in the early 21st century. Again, this inadequacy is rooted in a lack of context for Gemini to draw from.


