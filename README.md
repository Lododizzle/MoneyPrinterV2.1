# MoneyPrinter V2

> ♥︎ **Sponsor**: The Best AI Chat App: [shiori.ai](https://www.shiori.ai)

---

> 𝕏 Also, follow me on X: [@DevBySami](https://x.com/DevBySami).

[![madewithlove](https://img.shields.io/badge/made_with-%E2%9D%A4-red?style=for-the-badge&labelColor=orange)](https://github.com/FujiwaraChoki/MoneyPrinterV2)

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-brightgreen?logo=buymeacoffee)](https://www.buymeacoffee.com/fujicodes)
[![GitHub license](https://img.shields.io/github/license/FujiwaraChoki/MoneyPrinterV2?style=for-the-badge)](https://github.com/FujiwaraChoki/MoneyPrinterV2/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/FujiwaraChoki/MoneyPrinterV2?style=for-the-badge)](https://github.com/FujiwaraChoki/MoneyPrinterV2/issues)
[![GitHub stars](https://img.shields.io/github/stars/FujiwaraChoki/MoneyPrinterV2?style=for-the-badge)](https://github.com/FujiwaraChoki/MoneyPrinterV2/stargazers)
[![Discord](https://img.shields.io/discord/1134848537704804432?style=for-the-badge)](https://dsc.gg/fuji-community)

An Application that automates the process of making money online.
MPV2 (MoneyPrinter Version 2) is, as the name suggests, the second version of the MoneyPrinter project. It is a complete rewrite of the original project, with a focus on a wider range of features and a more modular architecture.

> **Note:** MPV2 needs Python 3.9 to function effectively.
> Watch the YouTube video [here](https://youtu.be/wAZ_ZSuIqfk)

## Features

- [x] Twitter Bot (with CRON Jobs => `scheduler`)
- [x] YouTube Shorts Automater (with CRON Jobs => `scheduler`)
- [x] Affiliate Marketing (Amazon + Twitter)
- [x] Find local businesses & cold outreach

## Versions

MoneyPrinter has different versions for multiple languages developed by the community for the community. Here are some known versions:

- Chinese: [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)

If you would like to submit your own version/fork of MoneyPrinter, please open an issue describing the changes you made to the fork.

## Installation

Getting MoneyPrinterV2 running involves two main stages: installing the necessary prerequisites on your system, and then setting up the Python environment and configuring the application.

### 1. Prerequisites

Before you begin, you need to install several system dependencies.

| Dependency                                                                              | Windows                                                                                                                              | Linux (Debian/Ubuntu)                                                                        | Notes                                                                                                                                                             |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Git**                                                                                 | [Download & Install Git for Windows](https://git-scm.com/download/win)                                                              | `sudo apt update && sudo apt install git`                                                    | Required to clone the repository.                                                                                                                                 |
| **Python**                                                                              | [Download & Install Python 3.9](https://www.python.org/downloads/release/python-3913/) (Ensure you add Python to your PATH)        | `sudo apt install python3.9 python3.9-venv`                                                  | **Version 3.9 is required.**                                                                                                                                      |
| **MSVC++ Build Tools**                                                                  | [Download & Install Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (Select "C++ build tools" in installer) | Not Required                                                                                 | Required by the CoquiTTS engine on Windows.                                                                                                                       |
| **Go Language**                                                                         | [Download & Install Go](https://golang.org/dl/)                                                                                     | `sudo apt install golang-go`                                                                 | Only required if you plan to use the email outreach feature.                                                                                                      |
| **ImageMagick**                                                                         | [Download & Install ImageMagick](https://imagemagick.org/script/download.php#windows) (Ensure it's added to your PATH)           | `sudo apt install imagemagick`                                                               | Required for advanced video processing effects.                                                                                                                   |
| **Docker**                                                                              | [Download & Install Docker Desktop](https://www.docker.com/products/docker-desktop/)                                                 | [Install Docker Engine](https://docs.docker.com/engine/install/ubuntu/)                      | Only required if you want to use the high-quality **Kokoro TTS** engine. You will also need an **NVIDIA GPU** with CUDA drivers installed to run the GPU version. |


### 2. Application Setup

Once the prerequisites are installed, you can set up the MoneyPrinterV2 application.

**1. Clone the Repository**

Open your terminal or command prompt and run the following command:
```bash
git clone https://github.com/FujiwaraChoki/MoneyPrinterV2.git
cd MoneyPrinterV2
```

**2. Create and Activate Virtual Environment**

It is highly recommended to use a virtual environment to manage dependencies.

*   **On Windows:**
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```

*   **On Linux:**
    ```bash
    python3.9 -m venv venv
    source venv/bin/activate
    ```

**3. Install Python Dependencies**

Install all the required Python packages using pip:
```bash
pip install -r requirements.txt
```

**4. Configure the Application**

Create your configuration file by copying the example file.

*   **On Windows:**
    ```powershell
    copy config.example.json config.json
    ```

*   **On Linux:**
    ```bash
    cp config.example.json config.json
    ```

Now, open `config.json` in a text editor and fill in the required values. See the **Configuration** section below for details on each setting.


### 3. Running the Kokoro TTS Engine (Optional)

If you want to use the high-quality Kokoro TTS engine, you must run its Docker container locally. Make sure Docker is running on your system.

*   **For NVIDIA GPU (Recommended):**
    ```bash
    docker run --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu:latest
    ```

*   **For CPU-only:**
    ```bash
    docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest
    ```
This will start a server on your machine at `http://localhost:8880`. You must set `"tts_engine": "kokoro"` in your `config.json` to use it.


## Configuration

The `config.json` file controls all major features of the application.

| Key                             | Description                                                                                                                                                           |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `verbose`                       | Set to `true` to see detailed logs in the console.                                                                                                                    |
| `headless`                      | Set to `true` to run the browser automation (Selenium) in the background without a visible UI.                                                                          |
| `pexels_api_key`                | **Required for Video Generation.** Your API key from [Pexels](https://www.pexels.com/api/).                                                                             |
| `tts_engine`                    | The Text-to-Speech engine to use. Can be `"coqui"` (default, runs on CPU) or `"kokoro"` (requires running the Docker container, much higher quality).                    |
| `kokoro_api_url`                | The URL of your local Kokoro-FastAPI server. Defaults to `"http://localhost:8880"`.                                                                                    |
| `transition_duration`           | The duration of the cross-fade transition between video clips, in seconds. Defaults to `0.5`.                                                                         |
| `audio_ducking_enabled`         | Set to `true` to automatically lower the background music volume during speech.                                                                                       |
| `audio_ducking_volume_speech`   | The volume of the background music when speech is present (e.g., `0.1` for 10%).                                                                                        |
| `audio_ducking_volume_silence`  | The volume of the background music when there is silence (e.g., `0.3` for 30%).                                                                                        |
| `sound_effects_enabled`         | Set to `true` to enable automatically layered sound effects.                                                                                                          |
| `sound_effects_path`            | The local folder path where you store your `.mp3` sound effect files (e.g., `"sfx"`).                                                                                    |
| `imagemagick_path`              | **Required on Windows.** The full path to your `magick.exe` file. On Linux, this can usually be left as is.                                                              |

## Usage

```bash
# Run the application
python src/main.py
```

## Documentation

All relevant document can be found [here](docs/).

## Scripts

For easier usage, there are some scripts in the `scripts` directory, that can be used to directly access the core functionality of MPV2, without the need of user interaction.

All scripts need to be run from the root directory of the project, e.g. `bash scripts/upload_video.sh`.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us. Check out [docs/Roadmap.md](docs/Roadmap.md) for a list of features that need to be implemented.

## Code of Conduct

Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details on our code of conduct, and the process for submitting pull requests to us.

## License

MoneyPrinterV2 is licensed under `Affero General Public License v3.0`. See [LICENSE](LICENSE) for more information.

## Acknowledgments

- [CoquiTTS](https://github.com/coqui-ai/TTS)
- [gpt4free](https://github.com/xtekky/gpt4free)

## Disclaimer

This project is for educational purposes only. The author will not be responsible for any misuse of the information provided. All the information on this website is published in good faith and for general information purpose only. The author does not make any warranties about the completeness, reliability, and accuracy of this information. Any action you take upon the information you find on this website (FujiwaraChoki/MoneyPrinterV2), is strictly at your own risk. The author will not be liable for any losses and/or damages in connection with the use of our website.
