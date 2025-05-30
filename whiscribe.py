# -----------------------------------------------------------------------------
# 🎙️ Whiscribe (Audio → Text Converter)
# Copyright (c) 2025  Sungur Zahid Erdim
#
# This software is licensed under the MIT License.
# For the full license text, see the LICENSE file in this repository.
# -----------------------------------------------------------------------------

import io, os, time, psutil
from typing import Optional

import streamlit as st
import torch
from faster_whisper import WhisperModel

# ---- torch.classes patch: prevents Streamlit watcher error --------------
torch.classes.__path__ = []
torch.classes.__path__ = [os.path.join(torch.__path__[0],
                                       getattr(torch.classes, "__file__", ""))]

# ────────── utility functions ────────────────────────────────────────────
def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

@st.cache_resource(ttl=3600, max_entries=1, show_spinner="📦 Downloading model…")
def load_model(size: str, cache_dir: Optional[str] = None) -> WhisperModel:
    return WhisperModel(
        size,
        device="cpu",
        compute_type="int8",
        download_root=cache_dir or None,
        local_files_only=False,
        cpu_threads=min(1, psutil.cpu_count(logical=True)-1)
    )

def transcribe_bytes(buf: bytes,
                     model: WhisperModel,
                     vad_min_ms: int,
                     vad_max_s: int,
                     vad_threshold: float,
                     beam_size: int):
    t0 = time.time()
    segments, _ = model.transcribe(
        io.BytesIO(buf),
        language=None,
        vad_filter=True,
        vad_parameters={
            "threshold": vad_threshold,
            "min_speech_duration_ms": vad_min_ms,
            "max_speech_duration_s": vad_max_s,
        },
        beam_size=beam_size,
    )
    text = " ".join(s.text.strip() for s in segments if s.text.strip())
    return text, time.time() - t0

# ────────── page config & state ──────────────────────────────────────────
PAGE_TITLE = "Whiscribe (Audio → Text Converter)"
st.set_page_config(page_title=PAGE_TITLE, page_icon="🎙️", layout="wide")

st.session_state.setdefault("uploader_key", 0)
st.session_state.setdefault("file_bytes", None)
st.session_state.setdefault("transcript", "")
st.session_state.setdefault("elapsed", 0.0)

# ────────── header ───────────────────────────────────────────────────────
st.title(PAGE_TITLE)
st.divider()

# ────────── sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    model_size = st.selectbox(
        "Model",
        [
            "Systran/faster-whisper-tiny",
            "Systran/faster-whisper-base",
            "Systran/faster-whisper-small",
            "Systran/faster-whisper-medium",
            "Systran/faster-whisper-large-v3",
            "Systran/faster-distil-whisper-large-v3",
        ],
        index=2,
    )

    st.markdown("---")
    st.caption("🔧 Advanced Settings")

    default_cache = os.path.join(os.path.dirname(__file__), ".cache")
    cache_dir = st.text_input(
        "Model cache folder",
        value="",
        placeholder="e.g. /path/to/cache",
        help=("Optional folder to cache downloaded models. "
              "Leave empty for default `.cache` in the current directory."),
    )

    if not cache_dir:
        cache_dir = default_cache
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)
    st.write(f"Using cache: `{cache_dir}`")

    vad_min = st.number_input(
        "Min. speech (ms)",
        100, 1000, 250, 50,
        help=("Minimum segment length to be considered speech (in ms). "
              "Lower values catch shorter/softer utterances."),
    )

    vad_max = st.number_input(
        "Max. speech (s)",
        5, 60, 30, 1,
        help=("Maximum segment length allowed to be treated as a single "
              "speech chunk (in seconds)."),
    )

    vad_thr = st.slider(
        "VAD threshold", 0.0, 1.0, 0.15, 0.01,
        help=("Threshold used for voice-activity detection. "
              "Lower catches quiet speech, higher reduces noise."),
    )

    beam_sz = st.slider(
        "Beam size", 1, 10, 5, 1,
        help=("Number of alternatives considered in beam search. "
              "Higher is usually more accurate but slower."),
    )

# ────────── file upload ──────────────────────────────────────────────────
st.subheader("📁 Upload File")
MAX_FILE_SIZE = 100 * 1024 * 1024   # 100 MB

def _save_uploaded():
    fu = st.session_state[f"fu_{st.session_state.uploader_key}"]
    if fu:
        if fu.size > MAX_FILE_SIZE:
            st.error("🚫 File exceeds 100 MB limit.")
            st.session_state.file_bytes = None
        else:
            st.session_state.file_bytes = fu.getvalue()

st.file_uploader(
    "Select an audio file (≤ 100 MB)",
    type=["opus", "mp3", "wav", "flac", "m4a", "aac", "mp4",
      "ogg", "webm", "mov", "3gp", "aiff", "aif"],
    key=f"fu_{st.session_state.uploader_key}",
    on_change=_save_uploaded,
)

# ────────── main flow ────────────────────────────────────────────────────
if not st.session_state.transcript:
    if st.button("🚀 Transcribe", use_container_width=True):
        if not st.session_state.file_bytes:
            st.warning("📭 Please upload a file first.")
        else:
            with st.spinner("🔍 Transcribing…"):
                try:
                    model = load_model(model_size, cache_dir)
                    txt, elapsed = transcribe_bytes(
                        st.session_state.file_bytes,
                        model,
                        vad_min, vad_max, vad_thr, beam_sz,
                    )
                    
                    if not txt.strip(): txt = " ___ Couldn't detect any speech. Please check your file and try again. ___ "

                    st.session_state.transcript = txt
                    st.session_state.elapsed = elapsed
                    safe_rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
else:
    st.success(f"✅ Completed · {st.session_state.elapsed:.2f} s")
    st.code(
        st.session_state.transcript,
        language=None,
        line_numbers=True,
        wrap_lines=True,
    )
    st.download_button(
        "💾 Download Text",
        st.session_state.transcript,
        file_name="transcript.txt",
    )

    def _clear():
        st.session_state.update(
            uploader_key=st.session_state.uploader_key + 1,
            file_bytes=None,
            transcript="",
            elapsed=0.0,
        )
    st.button("🧹 Reset", on_click=_clear, use_container_width=True)
