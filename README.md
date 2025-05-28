# 🎙️ Whiscribe (Audio → Text Converter)

**Whiscribe** is a lightweight, **CPU-only** speech-to-text app powered by **faster-whisper**.  
Run it from your browser with a single Python script (no GPU, no heavy stack).

---

## ✨ Features

- **CPU-Only** – works on any machine; CUDA/MPS not required.  
- **Minimal dependencies** – just `streamlit`, `faster-whisper`, `torch`.  
- **Model picker** – choose any faster-whisper model (*tiny* → *large-v3*).  
- **Advanced Settings** – tune VAD thresholds and beam size in the UI.  
- **100 MB upload limit** – large enough for most recordings.  
- MIT-licensed: fork, use and share freely.

---

## 🖥️ Requirements

| Requirement  | Notes                                         |
|--------------|-----------------------------------------------|
| Python 3.9+  | tested with both 3.9 and 3.12                 |
| pip packages | `faster-whisper`, `streamlit`, `torch`        |

---

## 🚀 Installation

```bash
# 1) Clone the repo
git clone https://github.com/sungurerdim/whiscribe.git
cd whiscribe

# 2) Create & activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3) Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4) Launch the app
streamlit run whiscribe.py
```

## ⚙️ Usage
- Upload an audio file (`opus`, `mp3`, `wav`, `flac`, `m4a`, `aac`, `mp4`, …) up to **100 MB**.  
- *(Optional)* open **Advanced Settings** to adjust VAD and beam-search parameters.  
- Click **“Transcribe”** and wait a few moments.  
- Copy the transcript or **Download Text** (`.txt`).  
- Click **Reset** to start over with another file.

## 📝 License
This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.  
© 2025 **Sungur Zahid Erdim**

## 🤝 Contributing
Bug reports and pull requests are welcome!

> **Note:** This script and README was prepared with assistance from ChatGPT.