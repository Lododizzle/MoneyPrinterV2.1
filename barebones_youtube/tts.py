from gtts import gTTS
import os

class TTS:
    """Simple text-to-speech wrapper using gTTS."""

    def __init__(self, lang: str = "en"):
        self.lang = lang

    def synthesize(self, text: str, output_path: str) -> None:
        """
        Generate speech audio from text and save it to the specified path.
        The parent directory of ``output_path`` will be created if it does not exist.
        """
        tts = gTTS(text=text, lang=self.lang)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        tts.save(output_path)
