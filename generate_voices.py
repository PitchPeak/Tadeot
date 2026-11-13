"""Erzeugt die Sprachdateien (MP3) für alle Sprüche aus lines.js.

Stimme: "Thorsten" (männlich, deutsch, Lizenz CC0) über Piper TTS, läuft komplett lokal.

Einmalig:
    pip install piper-tts
    ffmpeg muss installiert sein (für MP3)

Dann im Ordner tag-der-offenen-tuer:
    python generate_voices.py

Die Stimmmodelle (~190 MB) werden beim ersten Lauf nach ./.voices geladen (nicht im Git).
Unveränderte Texte (gleicher Text, gleiche Stimme) werden übersprungen; Dateien zu gelöschten Texten werden entfernt.
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
VOICE_DIR = HERE / ".voices"
AUDIO_DIR = HERE / "audio"
HF = "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE"

MODELS = {
    "thorsten-high": "thorsten/high/de_DE-thorsten-high",
    "thorsten-emotional": "thorsten_emotional/medium/de_DE-thorsten_emotional-medium",
}

# Stimme pro Rolle. Sprecher der emotionalen Variante (gemessene Tonhöhe):
# 0 amused 147 Hz, 1 angry 235, 2 disgusted 165, 3 drunk 151, 4 neutral 121,
# 5 sleepy 127, 6 surprised 127, 7 whisper. Über ~150 Hz klingt es schnell nicht mehr männlich.
# pitch < 1 macht die Stimme tiefer (Tempo bleibt gleich).
ROLE_VOICES = {
    "expert": {"model": "thorsten-high", "speaker": 0, "length_scale": 1.0, "pitch": 1.0},
    "critic": {"model": "thorsten-emotional", "speaker": 4, "length_scale": 1.0, "pitch": 1.0},
    "beginner": {"model": "thorsten-emotional", "speaker": 6, "length_scale": 0.95, "pitch": 1.0},
}

# Aussprache-Hilfen nur für die Sprachausgabe (die Sprechblase zeigt den Originaltext)
PRONOUNCE = {
    "Thinking Head": "Thinking Hedd",
    "QR-Code": "Kuh Er Code",
    "…": ",",
    "–": ",",
    "’": "'",
}


def audio_name(text: str, cfg: dict) -> str:
    # Stimmeinstellung gehört zum Namen: ändert sich die Stimme, wird neu erzeugt
    key = text + json.dumps(cfg, sort_keys=True) + json.dumps(PRONOUNCE, sort_keys=True)
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12] + ".mp3"


def tts_text(text: str) -> str:
    for a, b in PRONOUNCE.items():
        text = text.replace(a, b)
    # GROSSGESCHRIEBENE Betonung ("DICH") sonst als Buchstaben gesprochen
    return re.sub(r"\b[A-ZÄÖÜ]{2,}\b", lambda m: m.group(0).capitalize(), text)


def ensure_model(key: str) -> Path:
    VOICE_DIR.mkdir(exist_ok=True)
    base = MODELS[key]
    onnx = VOICE_DIR / (Path(base).name + ".onnx")
    for suffix in (".onnx", ".onnx.json"):
        target = onnx.with_name(Path(base).name + suffix)
        if not target.exists():
            print(f"Lade {target.name} …")
            urllib.request.urlretrieve(f"{HF}/{base}{suffix}", target)
    return onnx


def main() -> None:
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg fehlt (wird für MP3 benötigt).")
    src = (HERE / "lines.js").read_text(encoding="utf-8")
    lines = json.loads(src[src.index("{"): src.rindex("}") + 1])

    manifest: dict[str, dict[str, str]] = {}
    for role, groups in lines.items():
        cfg = ROLE_VOICES[role]
        model = ensure_model(cfg["model"])
        out_dir = AUDIO_DIR / role
        out_dir.mkdir(parents=True, exist_ok=True)
        manifest[role] = {}
        wanted = set()
        for text in dict.fromkeys(t for group in groups.values() for t in group):
            name = audio_name(text, cfg)
            wanted.add(name)
            manifest[role][text] = f"audio/{role}/{name}"
            target = out_dir / name
            if target.exists():
                continue
            print(f"[{role}] {text}")
            with tempfile.TemporaryDirectory() as tmp:
                txt, wav = Path(tmp) / "in.txt", Path(tmp) / "out.wav"
                txt.write_text(tts_text(text), encoding="utf-8")
                subprocess.run(
                    [sys.executable, "-m", "piper", "-m", str(model), "-i", str(txt), "-f", str(wav),
                     "-s", str(cfg["speaker"]), "--length-scale", str(cfg["length_scale"])],
                    check=True, capture_output=True,
                )
                p = cfg["pitch"]
                pitch_filter = ["-af", f"asetrate=22050*{p},aresample=22050,atempo={1 / p:.4f}"] if p != 1.0 else []
                subprocess.run(
                    ["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), *pitch_filter,
                     "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "64k", str(target)],
                    check=True,
                )
        for old in out_dir.glob("*.mp3"):
            if old.name not in wanted:
                old.unlink()

    (AUDIO_DIR / "manifest.js").write_text(
        "// Automatisch erzeugt von generate_voices.py – nicht von Hand bearbeiten.\n"
        "window.AUDIO = " + json.dumps(manifest, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print("Fertig:", sum(len(v) for v in manifest.values()), "Sprachdateien.")


if __name__ == "__main__":
    main()
