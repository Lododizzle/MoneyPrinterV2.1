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
import re
import g4f
import json
import time
import requests
import assemblyai as aai

from utils import *
from cache import *
from .Tts import TTS
from config import *
from status import *
from uuid import uuid4
from constants import *
from typing import List
from moviepy.editor import *
from termcolor import colored
from selenium_firefox import *
from selenium import webdriver
from moviepy.video.fx.all import crop
from moviepy.config import change_settings
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from moviepy.video.tools.subtitles import SubtitlesClip
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime

# Set ImageMagick Path
change_settings({"IMAGEMAGICK_BINARY": get_imagemagick_path()})

class YouTube:
    """
    Class for YouTube Automation.

    Steps to create a YouTube Short:
    1. Generate a topic [DONE]
    2. Generate a script [DONE]
    3. Generate metadata (Title, Description, Tags) [DONE]
    4. Generate AI Image Prompts [DONE]
    4. Generate Images based on generated Prompts [DONE]
    5. Convert Text-to-Speech [DONE]
    6. Show images each for n seconds, n: Duration of TTS / Amount of images [DONE]
    7. Combine Concatenated Images with the Text-to-Speech [DONE]
    """
    def __init__(self, account_uuid: str, account_nickname: str, fp_profile_path: str, niche: str, language: str) -> None:
        """
        Constructor for YouTube Class.

        Args:
            account_uuid (str): The unique identifier for the YouTube account.
            account_nickname (str): The nickname for the YouTube account.
            fp_profile_path (str): Path to the firefox profile that is logged into the specificed YouTube Account.
            niche (str): The niche of the provided YouTube Channel.
            language (str): The language of the Automation.

        Returns:
            None
        """
        self._account_uuid: str = account_uuid
        self._account_nickname: str = account_nickname
        self._fp_profile_path: str = fp_profile_path
        self._niche: str = niche
        self._language: str = language

        self.video_paths = []

        # Initialize the Firefox profile
        self.options: Options = Options()
        
        # Set headless state of browser
        if get_headless():
            self.options.add_argument("--headless")

        profile = webdriver.FirefoxProfile(self._fp_profile_path)
        self.options.profile = profile

        # Set the service
        self.service: Service = Service(GeckoDriverManager().install())

        # Initialize the browser
        self.browser: webdriver.Firefox = webdriver.Firefox(service=self.service, options=self.options)

    @property
    def niche(self) -> str:
        """
        Getter Method for the niche.

        Returns:
            niche (str): The niche
        """
        return self._niche
    
    @property
    def language(self) -> str:
        """
        Getter Method for the language to use.

        Returns:
            language (str): The language
        """
        return self._language
    
    def generate_response(self, prompt: str, model: any = None) -> str:
        """
        Generates an LLM Response based on a prompt and the user-provided model.

        Args:
            prompt (str): The prompt to use in the text generation.

        Returns:
            response (str): The generated AI Repsonse.
        """
        if not model:
            return g4f.ChatCompletion.create(
                model=parse_model(get_model()),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        else:
            return g4f.ChatCompletion.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

    def generate_topic(self) -> str:
        """
        Generates a topic based on the YouTube Channel niche.

        Returns:
            topic (str): The generated topic.
        """
        completion = self.generate_response(f"Please generate a specific video idea that takes about the following topic: {self.niche}. Make it exactly one sentence. Only return the topic, nothing else.")

        if not completion:
            error("Failed to generate Topic.")

        self.subject = completion

        return completion

    def generate_script(self) -> dict:
        """
        Generates a script for a video, including the voiceover text and suggested sound effects.

        Returns:
            dict: A dictionary containing the 'script' text and a list of 'sfx' cues.
        """
        sentence_length = get_script_sentence_length()
        prompt = f"""
        Generate a script for a short, fast-paced vertical video on the given subject. The script must be in {self.language}.
        The response MUST be a JSON object with two keys: "script" and "sfx".

        1.  "script": A string containing the voiceover script. It should follow this structure:
            - **Hook (First Sentence):** An intriguing question or statement.
            - **Main Content ({sentence_length - 2} sentences):** Explain the core topic with a mix of short and long sentences.
            - **Call to Action (Last Sentence):** A clear call to action.
            - **Constraints:** Total length must be exactly {sentence_length} sentences. Tone must be energetic and confident.

        2.  "sfx": An array of strings, with one entry for each sentence in the script. Each string should be a concise, 1-3 word description of a suggested sound effect (e.g., "mouse click", "rocket whoosh", "camera shutter"). If no sound effect is appropriate for a sentence, the value should be `null`.

        Example response format:
        {{
          "script": "Did you know you can do this? It's super easy to set up. Let me know what you think!",
          "sfx": ["question_sfx", "typing_sfx", null]
        }}

        **Subject:** {self.subject}
        """
        completion = self.generate_response(prompt)
        
        try:
            # Clean the response by removing markdown and extracting the JSON object
            json_match = re.search(r'\{.*\}', completion, re.DOTALL)
            if not json_match:
                raise json.JSONDecodeError("No JSON object found in response.", completion, 0)

            json_str = json_match.group(0)
            script_data = json.loads(json_str)

            if 'script' not in script_data or 'sfx' not in script_data:
                raise ValueError("JSON response is missing 'script' or 'sfx' key.")

            # Store the script text for other methods to use
            self.script = script_data['script']
            return script_data

        except (json.JSONDecodeError, ValueError) as e:
            error(f"Failed to parse script from LLM response: {e}. Retrying...")
            # Fallback to generating script without sfx if parsing fails
            return self.generate_script()

    def generate_metadata(self) -> dict:
        """
        Generates Video metadata for the to-be-uploaded YouTube Short (Title, Description).

        Returns:
            metadata (dict): The generated metadata.
        """
        title = self.generate_response(f"Please generate a YouTube Video Title for the following subject, including hashtags: {self.subject}. Only return the title, nothing else. Limit the title under 100 characters.")

        if len(title) > 100:
            if get_verbose():
                warning("Generated Title is too long. Retrying...")
            return self.generate_metadata()

        description = self.generate_response(f"Please generate a YouTube Video Description for the following script: {self.script}. Only return the description, nothing else.")
        
        self.metadata = {
            "title": title,
            "description": description
        }

        return self.metadata
    
    def _generate_video_search_terms(self) -> List[str]:
        """
        Generates video search terms based on the video script.
        """
        # Calculate number of search terms based on script length
        n_search_terms = len(self.script.split('.')) - 1

        prompt = f"""
        Generate {n_search_terms} concise search terms for a stock video API based on the following video script.
        The search terms should be 2-4 words long, capturing the main action or mood of each sentence.
        Return the terms as a JSON array of strings.

        Here is an example of a JSON-Array of strings:
        ["fast car driving", "mountain sunset", "person writing letter"]

        YOU MUST ONLY RETURN THE JSON-ARRAY OF STRINGS.
        YOU MUST NOT RETURN ANYTHING ELSE.

        For context, here is the full script:
        {self.script}
        """

        completion = str(self.generate_response(prompt, model=parse_model(get_image_prompt_llm())))\
            .replace("```json", "") \
            .replace("```", "")

        search_terms = []
        try:
            search_terms = json.loads(completion)
            if get_verbose():
                info(f" => Generated Video Search Terms: {search_terms}")
        except Exception:
            if get_verbose():
                warning("GPT returned an unformatted response. Attempting to clean...")
            r = re.compile(r'\[.*\]')
            match = r.search(completion)
            if match:
                try:
                    search_terms = json.loads(match.group(0))
                except Exception as e:
                    error(f"Failed to parse search terms from cleaned response: {e}")
                    return []
            else:
                error("Failed to generate or parse video search terms.")
                return []

        self.video_search_terms = search_terms
        success(f"Generated {len(search_terms)} video search terms.")
        return search_terms

    def _download_videos(self):
        """
        Downloads videos from Pexels based on the search terms.
        """
        info("Downloading videos from Pexels...")
        self.video_paths = []
        api_key = get_pexels_api_key()

        if not api_key:
            error("Pexels API key is missing from config.json. Cannot download videos.")
            return

        headers = {
            "Authorization": api_key
        }

        for term in self.video_search_terms:
            try:
                url = f"https://api.pexels.com/videos/search?query={term}&per_page=1&orientation=portrait"
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise an exception for bad status codes

                data = response.json()
                if not data.get("videos"):
                    warning(f"No videos found for search term: '{term}'")
                    continue

                video_url = None
                # Find a suitable video file, prefer smaller resolution for faster processing
                for video_file in sorted(data["videos"][0]["video_files"], key=lambda x: x['width']):
                     if 'hd' in video_file['quality']:
                        video_url = video_file['link']
                        break

                if not video_url:
                    warning(f"No suitable HD video file found for '{term}'. Skipping.")
                    continue

                # Download the video
                video_response = requests.get(video_url)
                video_response.raise_for_status()

                video_path = os.path.join(ROOT_DIR, ".mp", f"{uuid4()}.mp4")
                with open(video_path, "wb") as f:
                    f.write(video_response.content)

                self.video_paths.append(video_path)
                success(f"Downloaded video for '{term}'.")

            except requests.exceptions.RequestException as e:
                error(f"Failed to download video for term '{term}': {e}")
            except Exception as e:
                error(f"An unexpected error occurred while processing term '{term}': {e}")


    def generate_script_to_speech(self, tts_instance: TTS) -> str:
        """
        Converts the generated script into Speech using CoquiTTS and returns the path to the wav file.

        Args:
            tts_instance (tts): Instance of TTS Class.

        Returns:
            path_to_wav (str): Path to generated audio (WAV Format).
        """
        path = os.path.join(ROOT_DIR, ".mp", str(uuid4()) + ".wav")

        # Clean script, remove every character that is not a word character, a space, a period, a question mark, or an exclamation mark.
        self.script = re.sub(r'[^\w\s.?!]', '', self.script)

        tts_instance.synthesize(self.script, path)

        self.tts_path = path

        if get_verbose():
            info(f" => Wrote TTS to \"{path}\"")

        return path
    
    def add_video(self, video: dict) -> None:
        """
        Adds a video to the cache.

        Args:
            video (dict): The video to add

        Returns:
            None
        """
        videos = self.get_videos()
        videos.append(video)

        cache = get_youtube_cache_path()

        with open(cache, "r") as file:
            previous_json = json.loads(file.read())
            
            # Find our account
            accounts = previous_json["accounts"]
            for account in accounts:
                if account["id"] == self._account_uuid:
                    account["videos"].append(video)
            
            # Commit changes
            with open(cache, "w") as f:
                f.write(json.dumps(previous_json))

    def generate_subtitles(self, audio_path: str) -> str:
        """
        Generates subtitles for the audio using AssemblyAI.

        Args:
            audio_path (str): The path to the audio file.

        Returns:
            path (str): The path to the generated SRT File.
        """
        # Turn the video into audio
        aai.settings.api_key = get_assemblyai_api_key()
        config = aai.TranscriptionConfig()
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(audio_path)
        subtitles = transcript.export_subtitles_srt()

        srt_path = os.path.join(ROOT_DIR, ".mp", str(uuid4()) + ".srt")

        with open(srt_path, "w") as file:
            file.write(subtitles)

        return srt_path

    def combine(self) -> str:
        """
        Combines the downloaded video clips into the final video.
        """
        combined_video_path = os.path.join(ROOT_DIR, ".mp", str(uuid4()) + ".mp4")
        threads = get_threads()
        tts_clip = AudioFileClip(self.tts_path)
        max_duration = tts_clip.duration

        if not self.video_paths:
            error("No videos were downloaded to combine.")
            return None

        req_dur = max_duration / len(self.video_paths)

        # --- Text Subtitles Generator ---
        generator = lambda txt: TextClip(
            txt,
            font=os.path.join(get_fonts_dir(), get_font()),
            fontsize=100,
            color="#FFFF00",
            stroke_color="black",
            stroke_width=5,
            size=(1080, 1920),
            method="caption",
        )

        print(colored("[+] Combining downloaded video clips...", "blue"))

        clips = []
        for video_path in self.video_paths:
            clip = VideoFileClip(video_path)

            # If clip is shorter than required, loop it
            if clip.duration < req_dur:
                clip = clip.fx(vfx.loop, duration=req_dur)
            # If clip is longer, take a random subclip
            else:
                start_time = random.uniform(0, clip.duration - req_dur)
                clip = clip.subclip(start_time, start_time + req_dur)

            # Resize and crop to target 9:16 aspect ratio
            target_size = (1080, 1920)
            clip = clip.resize(height=target_size[1])
            if clip.w < target_size[0]:
                clip = clip.resize(width=target_size[0])

            clip = crop(clip, width=target_size[0], height=target_size[1], x_center=clip.w/2, y_center=clip.h/2)

            clips.append(clip.set_fps(30))

        # --- Video and Audio Concatenation with Transitions ---
        transition_duration = get_transition_duration()

        # Set the start time for each clip and apply crossfade
        final_clips = [clips[0]]
        for i, clip in enumerate(clips[1:]):
            previous_clip = final_clips[i]
            clip = clip.set_start(previous_clip.end - transition_duration)
            clip = clip.crossfadein(transition_duration)
            final_clips.append(clip)

        final_clip = CompositeVideoClip(final_clips).set_duration(max_duration)
        final_clip = final_clip.set_fps(30)
        
        # --- Audio Composition ---
        random_song = choose_random_song()
        random_song_clip = AudioFileClip(random_song)
        subtitles_path = self.generate_subtitles(self.tts_path)

        # Apply audio ducking
        ducking_config = get_audio_ducking_config()
        if ducking_config["enabled"]:
            try:
                with open(subtitles_path, 'r') as f:
                    lines = f.readlines()

                timestamps = []
                for i, line in enumerate(lines):
                    if "-->" in line:
                        start_str, end_str = line.split(" --> ")
                        def srt_time_to_seconds(s):
                            h, m, s_ms = s.split(':')
                            s, ms = s_ms.split(',')
                            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
                        timestamps.append((srt_time_to_seconds(start_str.strip()), srt_time_to_seconds(end_str.strip())))

                def volume_filter(t):
                    for start, end in timestamps:
                        if start <= t <= end:
                            return ducking_config["speech_volume"]
                    return ducking_config["silence_volume"]

                random_song_clip = random_song_clip.fx(afx.volumex, volume_filter)
            except Exception as e:
                error(f"Failed to apply audio ducking: {e}. Using static volume.")
                random_song_clip = random_song_clip.fx(afx.volumex, 0.1)
        else:
            random_song_clip = random_song_clip.fx(afx.volumex, 0.1)

        audio_clips = [tts_clip.set_fps(44100), random_song_clip]

        # Add sound effects if enabled
        sfx_config = get_sfx_config()
        if sfx_config["enabled"]:
            sfx_cues = self.script_data.get("sfx", [])
            # Ensure we have the same number of cues as timestamps
            if len(sfx_cues) == len(timestamps):
                for i, sfx_cue in enumerate(sfx_cues):
                    if sfx_cue:
                        # Try to find the sound effect file (e.g., "rocket_whoosh.mp3")
                        sfx_file_name = f"{sfx_cue.replace(' ', '_')}.mp3"
                        sfx_path = os.path.join(sfx_config["path"], sfx_file_name)
                        if os.path.exists(sfx_path):
                            try:
                                sfx_clip = AudioFileClip(sfx_path)
                                sfx_clip = sfx_clip.set_start(timestamps[i][0]) # Set start time to match sentence
                                audio_clips.append(sfx_clip)
                                info(f"Added sound effect: {sfx_file_name}")
                            except Exception as e:
                                error(f"Failed to process sound effect file {sfx_path}: {e}")
                        else:
                            warning(f"Sound effect file not found: {sfx_path}")

        comp_audio = CompositeAudioClip(audio_clips)
        final_clip.audio = comp_audio.set_duration(max_duration)

        # --- Subtitles ---
        equalize_subtitles(subtitles_path, 10)
        subtitles = SubtitlesClip(subtitles_path, generator).set_pos(("center", "center"))

        # --- Final Composition ---
        final_clip = CompositeVideoClip([final_clip, subtitles])
        final_clip.write_videofile(combined_image_path, threads=threads)

        success(f"Wrote Video to \"{combined_image_path}\"")
        return combined_image_path

    def generate_video(self, tts_instance: TTS) -> str:
        """
        Generates a YouTube Short based on the provided niche and language.

        Args:
            tts_instance (TTS): Instance of TTS Class.

        Returns:
            path (str): The path to the generated MP4 File.
        """
        # Generate the Topic
        self.generate_topic()

        # Generate the Script
        script_data = self.generate_script()
        self.script_data = script_data

        # Generate the Metadata
        self.generate_metadata()

        # Generate video search terms
        self._generate_video_search_terms()

        # Download videos
        self._download_videos()

        # Generate the TTS
        self.generate_script_to_speech(tts_instance)

        # Combine everything
        path = self.combine()

        if get_verbose():
            info(f" => Generated Video: {path}")

        self.video_path = os.path.abspath(path)

        return path
    
    def get_channel_id(self) -> str:
        """
        Gets the Channel ID of the YouTube Account.

        Returns:
            channel_id (str): The Channel ID.
        """
        driver = self.browser
        driver.get("https://studio.youtube.com")
        time.sleep(2)
        channel_id = driver.current_url.split("/")[-1]
        self.channel_id = channel_id

        return channel_id

    def upload_video(self) -> bool:
        """
        Uploads the video to YouTube.

        Returns:
            success (bool): Whether the upload was successful or not.
        """
        try:
            self.get_channel_id()

            driver = self.browser
            verbose = get_verbose()

            # Go to youtube.com/upload
            driver.get("https://www.youtube.com/upload")

            # Set video file
            FILE_PICKER_TAG = "ytcp-uploads-file-picker"
            file_picker = driver.find_element(By.TAG_NAME, FILE_PICKER_TAG)
            INPUT_TAG = "input"
            file_input = file_picker.find_element(By.TAG_NAME, INPUT_TAG)
            file_input.send_keys(self.video_path)

            # Wait for upload to finish
            time.sleep(5)

            # Set title
            textboxes = driver.find_elements(By.ID, YOUTUBE_TEXTBOX_ID)

            title_el = textboxes[0]
            description_el = textboxes[-1]

            if verbose:
                info("\t=> Setting title...")

            title_el.click()
            time.sleep(1)
            title_el.clear()
            title_el.send_keys(self.metadata["title"])

            if verbose:
                info("\t=> Setting description...")

            # Set description
            time.sleep(10)
            description_el.click()
            time.sleep(0.5)
            description_el.clear()
            description_el.send_keys(self.metadata["description"])

            time.sleep(0.5)

            # Set `made for kids` option
            if verbose:
                info("\t=> Setting `made for kids` option...")

            is_for_kids_checkbox = driver.find_element(By.NAME, YOUTUBE_MADE_FOR_KIDS_NAME)
            is_not_for_kids_checkbox = driver.find_element(By.NAME, YOUTUBE_NOT_MADE_FOR_KIDS_NAME)

            if not get_is_for_kids():
                is_not_for_kids_checkbox.click()
            else:
                is_for_kids_checkbox.click()

            time.sleep(0.5)

            # Click next
            if verbose:
                info("\t=> Clicking next...")

            next_button = driver.find_element(By.ID, YOUTUBE_NEXT_BUTTON_ID)
            next_button.click()

            # Click next again
            if verbose:
                info("\t=> Clicking next again...")
            next_button = driver.find_element(By.ID, YOUTUBE_NEXT_BUTTON_ID)
            next_button.click()

            # Wait for 2 seconds
            time.sleep(2)

            # Click next again
            if verbose:
                info("\t=> Clicking next again...")
            next_button = driver.find_element(By.ID, YOUTUBE_NEXT_BUTTON_ID)
            next_button.click()

            # Set as unlisted
            if verbose:
                info("\t=> Setting as unlisted...")
            
            radio_button = driver.find_elements(By.XPATH, YOUTUBE_RADIO_BUTTON_XPATH)
            radio_button[2].click()

            if verbose:
                info("\t=> Clicking done button...")

            # Click done button
            done_button = driver.find_element(By.ID, YOUTUBE_DONE_BUTTON_ID)
            done_button.click()

            # Wait for 2 seconds
            time.sleep(2)

            # Get latest video
            if verbose:
                info("\t=> Getting video URL...")

            # Get the latest uploaded video URL
            driver.get(f"https://studio.youtube.com/channel/{self.channel_id}/videos/short")
            time.sleep(2)
            videos = driver.find_elements(By.TAG_NAME, "ytcp-video-row")
            first_video = videos[0]
            anchor_tag = first_video.find_element(By.TAG_NAME, "a")
            href = anchor_tag.get_attribute("href")
            if verbose:
                info(f"\t=> Extracting video ID from URL: {href}")
            video_id = href.split("/")[-2]

            # Build URL
            url = build_url(video_id)

            self.uploaded_video_url = url

            if verbose:
                success(f" => Uploaded Video: {url}")

            # Add video to cache
            self.add_video({
                "title": self.metadata["title"],
                "description": self.metadata["description"],
                "url": url,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # Close the browser
            driver.quit()

            return True
        except:
            self.browser.quit()
            return False


    def get_videos(self) -> List[dict]:
        """
        Gets the uploaded videos from the YouTube Channel.

        Returns:
            videos (List[dict]): The uploaded videos.
        """
        if not os.path.exists(get_youtube_cache_path()):
            # Create the cache file
            with open(get_youtube_cache_path(), 'w') as file:
                json.dump({
                    "videos": []
                }, file, indent=4)
            return []

        videos = []
        # Read the cache file
        with open(get_youtube_cache_path(), 'r') as file:
            previous_json = json.loads(file.read())
            # Find our account
            accounts = previous_json["accounts"]
            for account in accounts:
                if account["id"] == self._account_uuid:
                    videos = account["videos"]

        return videos
