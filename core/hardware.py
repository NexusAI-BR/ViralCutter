import subprocess
import torch
import os

def check_ffmpeg_encoder(encoder_name):
    """Checks if the given encoder is available in FFmpeg."""
    try:
        # We use -encoders and search for the name
        result = subprocess.run(["ffmpeg", "-encoders"], capture_output=True, text=True, check=True)
        return encoder_name in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_best_hardware_config():
    """
    Detects the best available hardware for video encoding and ML.
    Prioritizes AMD (AMF) as requested by the user, then NVIDIA, then Intel.
    """
    config = {
        "video_encoder": "libx264",
        "video_preset": "ultrafast",
        "ml_device": "cpu",
        "compute_type": "float32",
        "description": "CPU (Generic)"
    }

    # 1. Check ML Device (Torch)
    if torch.cuda.is_available():
        config["ml_device"] = "cuda"
        config["compute_type"] = "float16"
        config["description"] = "NVIDIA GPU (CUDA)"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        config["ml_device"] = "mps"
        config["compute_type"] = "float32"
        config["description"] = "Apple Silicon (MPS)"
    
    # 2. Check Video Encoder (FFmpeg)
    # Order of preference based on user hardware (AMD RX 5700 XT)
    encoders = [
        ("h264_amf", "AMD Advanced Media Framework"),
        ("h264_nvenc", "NVIDIA NVENC"),
        ("h264_qsv", "Intel QuickSync"),
    ]

    for enc_name, label in encoders:
        if check_ffmpeg_encoder(enc_name):
            config["video_encoder"] = enc_name
            config["video_preset"] = "p1" if "nvenc" in enc_name else "speed" # Presets vary by encoder
            config["description"] += f" + {label}" if "CPU" not in config["description"] else label
            break

    return config

if __name__ == "__main__":
    cfg = get_best_hardware_config()
    print("--- Detected Hardware Configuration ---")
    for k, v in cfg.items():
        print(f"{k}: {v}")
