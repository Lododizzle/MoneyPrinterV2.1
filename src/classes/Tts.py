# MoneyPrinterV2 - An Application that automates the process of making money online.
# Copyright (C) 2024  FujiwaraChoki
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import os
import sys
import site
import requests

from config import ROOT_DIR, get_tts_engine, get_kokoro_api_url
from status import error, success
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer

class TTS:
    """
    Class for Text-to-Speech, supporting multiple TTS engines.
    """
    def __init__(self) -> None:
        """
        Initializes the TTS class based on the configured engine.
        """
        self.engine = get_tts_engine()
        self._synthesizer = None

        if self.engine == "coqui":
            self._initialize_coqui()
        elif self.engine == "kokoro":
            # No initialization needed for Kokoro as it's an API call
            pass
        else:
            error(f"Unknown TTS engine '{self.engine}' configured. Defaulting to 'coqui'.")
            self.engine = "coqui"
            self._initialize_coqui()

    def _initialize_coqui(self):
        """Initializes the Coqui TTS synthesizer."""
        # Detect virtual environment site packages
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            site_packages = site.getsitepackages()[0]
        else:
            site_packages = site.getusersitepackages()

        models_json_path = os.path.join(site_packages, "TTS", ".models.json")
        tts_dir = os.path.dirname(models_json_path)
        if not os.path.exists(tts_dir):
            os.makedirs(tts_dir)

        self._model_manager = ModelManager(models_json_path)
        self._model_path, self._config_path, self._model_item = \
            self._model_manager.download_model("tts_models/en/ljspeech/tacotron2-DDC_ph")
        voc_path, voc_config_path, _ = self._model_manager.download_model("vocoder_models/en/ljspeech/univnet")
        
        self._synthesizer = Synthesizer(
            tts_checkpoint=self._model_path,
            tts_config_path=self._config_path,
            vocoder_checkpoint=voc_path,
            vocoder_config=voc_config_path
        )

    def _synthesize_kokoro(self, text: str, output_file: str) -> str:
        """Synthesizes text using the Kokoro-FastAPI server."""
        api_url = get_kokoro_api_url()
        speech_url = f"{api_url.rstrip('/')}/v1/audio/speech"

        payload = {
            "model": "kokoro",
            "input": text,
            "voice": "af_bella",
            "response_format": "wav"
        }

        try:
            response = requests.post(speech_url, json=payload)
            response.raise_for_status()

            with open(output_file, "wb") as f:
                f.write(response.content)

            success(f"Successfully synthesized audio with Kokoro TTS to {output_file}")
            return output_file
        except requests.exceptions.RequestException as e:
            error(f"Failed to connect to Kokoro-FastAPI at {speech_url}: {e}")
            return None
        except Exception as e:
            error(f"An unexpected error occurred during Kokoro TTS synthesis: {e}")
            return None

    def synthesize(self, text: str, output_file: str = os.path.join(ROOT_DIR, ".mp", "audio.wav")) -> str:
        """
        Synthesizes the given text into speech using the configured engine.
        """
        if self.engine == "kokoro":
            return self._synthesize_kokoro(text, output_file)

        # Default to Coqui if engine is not kokoro or synthesizer is not ready
        if not self._synthesizer:
            error("Coqui TTS synthesizer is not initialized.")
            return None

        outputs = self._synthesizer.tts(text)
        self._synthesizer.save_wav(outputs, output_file)
        success(f"Successfully synthesized audio with Coqui TTS to {output_file}")
        return output_file

