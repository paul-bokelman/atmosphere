![gh-banner](https://github.com/user-attachments/assets/093a37cf-c353-4ec2-96e8-7228ed6e7d1e)

# Atmosphere - Immersive Audio Books

Built for [Gemini API Developer Competition](https://ai.google.dev/competition)

# About Atmosphere

Atmosphere aims to enhance the storytelling experience by overlaying ambient audio onto audio book segments with strong auditory and sensory scenes. Atmosphere interacts with Gemini in 3 independent stages.
1. Initially, Atmosphere is provided with the audio book in its entirety, and is tasked with locating timestamps within the audio book that correspond to scenes that would be enhanced by ambient audio. In addition to providing the timestamp of these scenes, Gemini also produces a concise description of the context of the scene, and salient keywords from the scene that construct the overall tone of the segment.
2. Using the keywords gathered for each scene identified by Gemini, Atmosphere sifts through the 33,000+ sound effects and their associated keywords in the BBC sound effects library, and acquires all sounds with at least one keyword matching that of the scene. With all sound effects a minimum of one matching keyword compiled into a list, Gemini is prompted to pick the sound from the list that best matches the scene description created by Gemini in step 1.
3. Once Gemini has made a choice for the best fitting sound amongst the candidates, Gemini is given the mp3 file for the sound effect, and is prompted to listen and determine if its own choice really matches the scene at hand. If so, the next scene is evaluated, otherwise Gemini picks a new sound and is prompted to confirm again. 
