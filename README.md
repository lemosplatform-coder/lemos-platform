# Whisper Video Transcriber CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI API](https://img.shields.io/badge/OpenAI-Whisper-orange.svg)](https://platform.openai.com/docs/guides/speech-to-text)

A simple, robust, and developer-friendly Command Line Interface (CLI) tool designed to automate the process of extracting, splitting, and transcribing audio from video files using the OpenAI Whisper API.

OpenAI's Whisper API imposes a strict 25MB file size limit for audio uploads. **Whisper Video Transcriber CLI** solves this by automatically extracting audio from your high-definition video, splitting it into optimized segments (using FFmpeg segmenting), running transcriptions, and consolidating all transcripts into a single formatted text file.

---

## 🚀 Key Features

* 🎥 **Direct Video Processing:** Extract audio files from videos natively.
* 📦 **Automatic Segmentation:** Splits large audio files automatically using FFmpeg segmenting, ensuring you never run into the Whisper API 25MB upload limit.
* ⚡ **OpenAI Whisper Integration:** Transcribes audio accurately with speed and language configuration.
* 🧪 **Dry-Run / Test Mode:** Transcribe only the first 30 seconds of a video to verify API credentials and quality before consuming credits.
* 🛠️ **Developer-Ready CLI:** Pass input videos, output paths, languages, and settings seamlessly as arguments.

---

## 📦 Installation & Setup

### Prerequisites

* **Python 3.8+**
* **FFmpeg:** FFmpeg is required for audio manipulation. The tool uses `imageio-ffmpeg` to automatically fetch/manage the FFmpeg binary executable, but you can also install it system-wide.

### 1. Clone & Set Up Directory

Create a directory or clone the code to your workspace:

```bash
mkdir whisper-video-transcriber
cd whisper-video-transcriber
# Move the files into this folder
```

### 2. Set Up a Virtual Environment (Recommended)

```bash
# Create venv
python -m venv venv

# Activate venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configuration (`.env` file)

Create a `.env` file in the root directory of the project and add your OpenAI API Key:

```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

---

## 💻 Usage

```bash
python transcribe.py --video "/path/to/video.mp4" [options]
```

### Options & Arguments

| Parameter | Shorthand | Description | Default |
| :--- | :--- | :--- | :--- |
| `--video` | `-v` | **[Required]** Path to the input video or audio file. | N/A |
| `--output` | `-o` | Directory or file path where transcription should be saved. | Current Directory |
| `--lang` | `-l` | The target ISO 639-1 language code (e.g. `en`, `pt`, `es`). | `pt` |
| `--test` | `-t` | Runs in **Test Mode** (transcribes only the first 30s of the video). | `False` |

### Examples

#### 1. Dry Run / Test Mode (Highly Recommended first step)
Extracts and transcribes only the first 30 seconds to make sure your API key works:
```bash
python transcribe.py -v "path/to/my-lecture.mp4" --test
```

#### 2. Transcribe a Full Video
Transcribes the whole video (splitting and joining automatically):
```bash
python transcribe.py -v "path/to/my-lecture.mp4"
```

#### 3. Customize Language and Output Directory
Save transcription file inside a custom folder and force English transcription:
```bash
python transcribe.py -v "my-lecture.mp4" -o "./transcripts/" -l "en"
```

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.
