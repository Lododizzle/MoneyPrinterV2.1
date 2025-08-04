import argparse

from .youtube import YouTube
from .tts import TTS


def main() -> None:
    """
    Entry point for the barebones YouTube automation workflow.

    This script generates a YouTube Short video using a simplified workflow that
    assembles a topic, script, placeholder images, TTS audio and exports a video.
    """
    parser = argparse.ArgumentParser(description="Generate a YouTube Short using the barebones workflow.")
    parser.add_argument('--niche', type=str, default='technology', help='Topic or niche for the video.')
    parser.add_argument('--language', type=str, default='English', help='Language of the video.')
    parser.add_argument('--account_id', type=str, default='demo', help='Identifier used for naming the output file.')
    args = parser.parse_args()

    yt = YouTube(
        account_id=args.account_id,
        nickname=args.account_id,
        profile_path=None,
        niche=args.niche,
        language=args.language,
    )
    tts = TTS(lang='en')
    video_path = yt.generate_video(tts)
    print(f"Generated video saved at: {video_path}")


if __name__ == '__main__':
    main()
