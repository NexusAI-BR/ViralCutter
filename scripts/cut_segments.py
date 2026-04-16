import os
import json
import subprocess
from core.hardware import get_best_hardware_config
from . import cut_json

def cut(segments, project_folder="tmp", skip_video=False):
    """
    Cuts segments from the input video and transcription.
    segments: dict (the viral analysis response) or None (to load from viral_segments.txt)
    """
    hw = get_best_hardware_config()
    video_codec = hw["video_encoder"]
    video_preset = hw["video_preset"]
    print(f"[HW] Using encoder: {video_codec} ({hw['description']})")

    # Procurar input.mp4 ou input_video.mp4 no project_folder
    input_file = os.path.join(project_folder, "input.mp4")
    if not os.path.exists(input_file):
        input_file_legacy = os.path.join(project_folder, "input_video.mp4")
        if os.path.exists(input_file_legacy):
            input_file = input_file_legacy
        else:
            print(f"Error: Input file not found in {project_folder}")
            return

    # Preparar pastas
    cuts_folder = os.path.join(project_folder, "cuts")
    os.makedirs(cuts_folder, exist_ok=True)
    subs_folder = os.path.join(project_folder, "subs")
    os.makedirs(subs_folder, exist_ok=True)

    # Input JSON (Transcrição original)
    input_json_path = os.path.join(project_folder, "input.json")

    # Determinar fonte dos segmentos
    if segments is None:
        json_path = os.path.join(project_folder, 'viral_segments.txt')
        if not os.path.exists(json_path):
            print(f"Error: segments source not found in {project_folder}")
            return
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        # Se segments já for o dicionário
        data = segments

    segments_list = data.get("segments", [])
    if not segments_list:
        print("No segments found to cut.")
        return

    for i, segment in enumerate(segments_list):
        start_time = segment.get("start_time", 0)
        duration = segment.get("duration", 0)
        
        # Converter para float
        try:
            start_time_seconds = float(start_time)
            # Se for milisegundos (> 3600 e integer-like)
            if start_time_seconds > 10000 and isinstance(start_time, int):
                start_time_seconds /= 1000.0
        except:
            # Formato HH:MM:SS
            h, m, s = str(start_time).split(':')
            start_time_seconds = int(h) * 3600 + int(m) * 60 + float(s)

        try:
            duration_seconds = float(duration)
            if duration_seconds > 1000 and isinstance(duration, int):
                duration_seconds /= 1000.0
        except:
            duration_seconds = 0

        start_time_str = f"{start_time_seconds:.3f}"
        duration_str = f"{duration_seconds:.3f}"

        # Título amigável
        title = segment.get("title", f"Segment_{i}")
        safe_title = "".join([c for c in title if c.isalnum() or c in " _-"]).strip()
        safe_title = safe_title.replace(" ", "_")[:60]
        base_name = f"{i:03d}_{safe_title}"

        output_filename = f"{base_name}_original_scale.mp4"
        output_path = os.path.join(cuts_folder, output_filename)

        print(f"[{i+1}/{len(segments_list)}] Cutting: {title}")
        
        if not skip_video:
            command = [
                "ffmpeg", "-y", "-loglevel", "error", "-hide_banner",
                "-ss", start_time_str,
                "-i", input_file,
                "-t", duration_str,
                "-c:v", video_codec
            ]

            if video_codec == "h264_nvenc":
                command.extend(["-preset", "p1", "-b:v", "5M"])
            elif video_codec == "h264_amf":
                command.extend(["-usage", "transcoding", "-quality", "speed"])
            else:
                command.extend(["-preset", "ultrafast", "-crf", "23"])

            command.extend(["-c:a", "aac", "-b:a", "128k", output_path])

            try:
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error cutting segment {i}: {e}")
        
        # Sincronização de JSON (Corte da transcrição)
        end_time_seconds = start_time_seconds + duration_seconds
        json_output_path = os.path.join(subs_folder, f"{base_name}_processed.json")
        
        if os.path.exists(input_json_path):
            cut_json.cut_json_transcript(input_json_path, json_output_path, start_time_seconds, end_time_seconds)

    print(f"\n[DONE] {len(segments_list)} segments processed in {project_folder}")
