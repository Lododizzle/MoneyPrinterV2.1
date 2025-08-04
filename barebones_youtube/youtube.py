import os
import re
from typing import List, Optional
from datetime import timedelta

from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import g4f

from .helpers import (
    info, success, warning, error,
    get_script_sentence_length, get_image_prompt_llm, get_model,
    get_font, get_fonts_dir, choose_random_song,
    equalize_subtitles, parse_model
)


class YouTube:
    def __init__(self, account_id: str, nickname: str, profile_path: Optional[str],
                 niche: str, language: str):
        self.account_id = account_id
        self.nickname = nickname
        self.profile_path = profile_path
        self.niche = niche
        self.language = language

        self.subject: Optional[str] = None
        self.script: Optional[str] = None
        self.metadata = {}
        self.image_prompts: List[str] = []
        self.images: List[str] = []
        self.tts_path: Optional[str] = None
        self.output_dir = os.path.join(os.getcwd(), "barebones_output")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_response(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Query a language model via g4f and return the generated text.
        """
        chosen_model = parse_model(model or get_model())
        try:
            response = g4f.ChatCompletion.create(
                model=chosen_model,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as ex:
            error(f"LLM generation failed: {ex}")
            raise
        # g4f returns the string directly
        return response.strip()

    def generate_topic(self) -> str:
        prompt = (
            f"Generate a single-sentence topic for a YouTube Short in {self.language} "
            f"about: {self.niche}. Return only the topic sentence without quotes."
        )
        self.subject = self.generate_response(prompt)
        info(f"Generated topic: {self.subject}")
        return self.subject

    def generate_script(self) -> str:
        num_sentences = get_script_sentence_length()
        prompt = (
            f"Write a {num_sentences}-sentence YouTube Short script in {self.language} "
            f"about: {self.subject}. Use simple language and end each sentence with a period."
        )
        script = self.generate_response(prompt)
        # Remove asterisks or bullet characters
        script = re.sub(r"[*•]", "", script).strip()
        self.script = script
        info("Generated script.")
        return self.script

    def generate_metadata(self) -> dict:
        # Title
        title_prompt = (
            f"Write a catchy YouTube title (max 100 characters) for a Short in {self.language} "
            f"about: {self.subject}."
        )
        title = self.generate_response(title_prompt)
        # Description
        description_prompt = (
            f"Write a YouTube description in {self.language} for the following script:\n{self.script}"
        )
        description = self.generate_response(description_prompt)
        self.metadata = {"title": title, "description": description}
        info("Generated metadata.")
        return self.metadata

    def generate_prompts(self) -> List[str]:
        # Derive prompts from sentences in the script
        sentences = [s.strip() for s in re.split(r"[.!?]", self.script) if s.strip()]
        self.image_prompts = sentences
        info(f"Generated {len(self.image_prompts)} image prompts.")
        return self.image_prompts

    def generate_image(self, prompt: str) -> str:
        """
        Create a simple placeholder image containing the prompt text.
        """
        width, height = 720, 1280
        img = Image.new("RGB", (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Use default font; fallback if not available
        try:
            font_path = os.path.join(get_fonts_dir(), get_font())
            font = ImageFont.truetype(font_path, size=36)
        except Exception:
            font = ImageFont.load_default()

        text = prompt[:200]  # limit to avoid overflow
        # wrap text into multiple lines
        lines = []
        max_width = width - 20
        for word in text.split():
            if not lines:
                lines.append(word)
                continue
            if draw.textsize(lines[-1] + ' ' + word, font=font)[0] <= max_width:
                lines[-1] += ' ' + word
            else:
                lines.append(word)
        y = (height - len(lines) * 40) // 2
        for line in lines:
            line_width, line_height = draw.textsize(line, font=font)
            x = (width - line_width) // 2
            draw.text((x, y), line, font=font, fill=(0, 0, 0))
            y += line_height + 4

        os.makedirs(self.output_dir, exist_ok=True)
        idx = len(self.images)
        path = os.path.join(self.output_dir, f"image_{idx}.png")
        img.save(path)
        return path

    def generate_script_to_speech(self, tts_instance) -> str:
        self.tts_path = os.path.join(self.output_dir, "narration.mp3")
        tts_instance.synthesize(self.script, self.tts_path)
        info("Generated speech audio.")
        return self.tts_path

    def generate_subtitles(self, audio_path: str) -> str:
        """
        Create a simple SRT file with uniform durations for each sentence.
        """
        sentences = [s.strip() for s in re.split(r"[.!?]", self.script) if s.strip()]
        audio = AudioFileClip(audio_path)
        total_duration = audio.duration
        per = total_duration / max(len(sentences), 1)

        def format_time(seconds: float) -> str:
            td = timedelta(seconds=seconds)
            hours, remainder = divmod(int(td.total_seconds()), 3600)
            minutes, secs = divmod(remainder, 60)
            milliseconds = int((td.total_seconds() - int(td.total_seconds())) * 1000)
            return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

        subtitles_path = os.path.join(self.output_dir, "subtitles.srt")
        with open(subtitles_path, "w", encoding="utf-8") as f:
            for i, sentence in enumerate(sentences):
                start = i * per
                end = (i + 1) * per
                f.write(f"{i+1}\n{format_time(start)} --> {format_time(end)}\n{sentence}\n\n")
        info("Generated subtitles.")
        return subtitles_path

    def combine(self) -> str:
        """
        Combine images, audio and subtitles into a final video file.
        """
        audio_clip = AudioFileClip(self.tts_path)
        duration = audio_clip.duration
        num_images = max(len(self.images), 1)
        per = duration / num_images

        clips = []
        for img_path in self.images:
            img_clip = ImageClip(img_path).set_duration(per)
            clips.append(img_clip)
        video = concatenate_videoclips(clips, method="compose")

        # Set audio
        video = video.set_audio(audio_clip)

        # Write video to file
        final_path = os.path.join(self.output_dir, f"final_{self.account_id}.mp4")
        video.write_videofile(final_path, fps=24, codec="libx264", audio_codec="aac")
        success(f"Video saved to {final_path}")
        return final_path

    def generate_video(self, tts_instance):
        """
        Orchestrate the video generation process up to (but not including) the upload step.
        """
        self.generate_topic()
        self.generate_script()
        self.generate_metadata()
        self.generate_prompts()
        # Generate images
        for prompt in self.image_prompts:
            path = self.generate_image(prompt)
            self.images.append(path)
        # Speech
        self.generate_script_to_speech(tts_instance)
        # Subtitles
        self.generate_subtitles(self.tts_path)
        # Combine into final video
        return self.combine()
