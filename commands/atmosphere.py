from lib import timestamps as ts, mappings as map, overlay
from lib.utils import info, success

# generate immersive audio from input audio
def generate() -> None:
  info("Generating immersive audio, this may take a while 🌟...")

  # generate timestamps
  info("Generating timestamps ⏳...")
  timestamps = ts.generate(recording_path="./media/woz1-rec.mp3", skip=False)
  success("Timestamps generated successfully ⌛️")

  # generate mappings
  info("Generating mappings 🧭...")
  mappings = map.generate(timestamps=timestamps, skip=False)
  success("Mappings generated successfully 📍")

  # overlay sound effects
  info("Overlaying sound effects 🔎...")
  overlay.do(audio_path="./media/woz1-rec.mp3", mappings=mappings, out="./out/woz1-immersive.mp3")
  success("Successfully overlaid sound effects 🎯")

  # everything is complete 
  success("Audio immersion successful! 🔥")