from lib.types import AudioOverlayConfigSchema

timestamps_out = "./out/timestamps.json"
mappings_out = "./out/mappings.json"
bbc_sfx_url = "https://sound-effects-api.bbcrewind.co.uk/api/sfx/search"
bbc_sfx_media_url = "https://sound-effects-media.bbcrewind.co.uk/mp3"
showcase_seed_path = "./static/seed-data.json"
recordings_dir = "./media/recordings"
out_dir = "./media/out"
media_out = f"{out_dir}/generated.mp3"
seed_req_out_dir = f"{out_dir}/seed-requests"

# removed: Events, Comedy, Toys, Birds
categories = ['Aircraft', 'Animals', 'Applause', 'Atmosphere', 'Bells', 'Clocks', 'Crowds', 'Daily Life', 'Destruction', 'Electronics', 'Fire', 'Footsteps', 'Industry', 'Machines', 'Medical', 'Military', 'Nature', 'Sport', 'Transport']


# audio overlay configuration
audio_overlay_config: AudioOverlayConfigSchema = {
    "margins": (3000, 3000),
    "gain": -24, # dB
    "fade": (3000, 3000),
    "length": 15000,
}
