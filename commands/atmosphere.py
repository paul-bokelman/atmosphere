from lib import timestamps as ts, mappings as map, overlay
from lib.utils import info, success

# initialize atmosphere
def initialize() -> None:
  pass

# generate immersive audio from input audio
def generate() -> None:
  #? calculate estimated time?
  info("Generating immersive audio, this may take a while 🌟...")

  # generate timestamps
  info("Generating timestamps ⏳...")
  timestamps = ts.generate("./media/woz1-rec.mp3")
  success("Timestamps generated successfully ⌛️")

  # generate mappings
  info("Generating mappings 🧭...")
  mappings = map.generate(timestamps)
  success("Mappings generated successfully 📍")

  # overlay sound effects
  info("Overlaying sound effects 🔎...")
  overlay.do(audio_path="./media/woz1-rec.mp3", mappings=mappings, out="./out/woz1-immersive.mp3")
  success("Successfully overlaid sound effects 🎯")

  # everything is complete 
  success("Audio immersion successful! 🔥")