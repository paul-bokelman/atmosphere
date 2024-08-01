from typing import Optional
from lib.types import GeneratorOptionsSchema
import os
import constants
import inquirer
from lib import timestamps as ts, mappings as map, overlay
from lib.utils import info, success, error

def generate(options: Optional[GeneratorOptionsSchema] = None) -> None:
  """Generate immersive audio from input recording"""

  if os.path.exists(constants.recordings_dir) is False or os.path.exists(constants.out_dir) is False:
    error("Media folder not found! Please ensure the media folder with subdirectories 'recordings' and 'out' exists.")
    return
  
  present_recordings = [rec for rec in os.listdir(constants.recordings_dir) if rec.endswith('.mp3')]

  # no options -> prompt user for required fields
  if options is None:
    if len(present_recordings) == 0:
      error("No recordings found in media/recordings, please add recordings to continue.")
      return

    questions = [
      inquirer.List('recording_location', message="Choose recording from media/recordings", choices=present_recordings),
      inquirer.Confirm('timestamps_out', message="Output timestamps?", default=False),
      inquirer.Confirm('mappings_out', message="Output mappings?", default=False),
    ]

    answers = inquirer.prompt(questions)

    # no answers -> return
    if answers is None:
      error("Invalid input, returning to menu...")
      return
    
    options = {
      "recording_location": f'{constants.recordings_dir}/{answers["recording_location"]}',
    }

    assert "recording_location" in answers, "Recording location is required to generate immersive audio"

    recording_location = answers['recording_location']
    assert isinstance(recording_location, str), "Recording location must be a string" 

    # ensure recording is an mp3 file
    if recording_location.endswith('.mp3') is False:
      error("Invalid recording format, please provide an mp3 file")
      return
    
    recording_name = recording_location.split('.')[0]
    recording_out_dir = f'{constants.out_dir}/{recording_name}' 

    if not os.path.exists(recording_out_dir):
      os.makedirs(recording_out_dir)

    # store timestamps and mappings if requested (/media/out/{recording_name}/[timestamps.json,mappings.json])
    if answers['timestamps_out'] is True:
      options['timestamps_out'] = f'{recording_out_dir}/timestamps.json'
    if answers['mappings_out'] is True:
      options['mappings_out'] = f'{recording_out_dir}/mappings.json'

    options['out'] = f'{recording_out_dir}/{recording_name}-immersive.mp3'
    
  info("Generating immersive audio, this may take a while 🌟...")

  # required information checks
  assert options is not None, "Options are required to generate immersive audio"
  assert "recording_location" in options, "Recording location is required to generate immersive audio"

  # generate timestamps
  info("Generating timestamps ⏳...")
  timestamps_out = options["timestamps_out"] if "timestamps_out" in options else None
  timestamps = ts.generate(recording=options["recording_location"], out=timestamps_out, skip=False)
  success("Timestamps generated successfully ⌛️")

  # generate mappings
  info("Generating mappings 🧭...")
  mappings_out = options['mappings_out'] if 'mappings_out' in options else None
  mappings = map.generate(timestamps=timestamps, out=mappings_out, skip=False)
  success("Mappings generated successfully 📍")

  # overlay sound effects
  info("Overlaying sound effects 🔎...")

  output_location = options['out'] if 'out' in options else constants.media_out
  overlay.do(original_recording=options['recording_location'], mappings=mappings, out=output_location)
  success("Successfully overlaid sound effects 🎯")

  # everything is complete 
  success("Audio immersion successful! 🔥")