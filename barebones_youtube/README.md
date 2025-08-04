# Barebones YouTube Automation

This package contains a minimal subset of the MoneyPrinterV2 codebase focused solely on generating a YouTube Short video. It performs the following steps:

1. Generates a topic and script using a language model via the `g4f` library.
2. Derives image prompts from the script and creates simple placeholder images using Pillow.
3. Converts the script to speech using `gtts`.
4. Generates a basic subtitles file with evenly divided timings.
5. Combines the images and audio into an MP4 file using MoviePy.

Uploading to YouTube or any Selenium automation is intentionally excluded.

## Installation

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run the driver script with your desired parameters:

```bash
python -m barebones_youtube.run --niche "technology" --language "English" --account_id "demo"
```

The generated video and supporting files will be saved into the `barebones_output/` directory in the current working directory.

## Notes

- The script uses the `g4f` library to access a language model without requiring an API key. Network access is needed for this call.
- `gtts` (Google Text-to-Speech) requires an internet connection. You can replace it with a local TTS library if preferred.
- Placeholder images are generated locally; replace the `generate_image` method in `youtube.py` with calls to your preferred image provider for more realistic visuals.
- This stripped-down module does not require any authentication or cached account information, and no secrets are stored in the repository.
