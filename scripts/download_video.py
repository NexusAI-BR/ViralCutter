import os
import re
import yt_dlp
import sys
import time
import shutil
import tempfile
from i18n.i18n import I18nAuto

i18n = I18nAuto()

def sanitize_filename(name):
    """Remove caracteres inválidos e emojis. No Windows, limitamos o tamanho."""
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    try:
        cleaned = cleaned.encode('cp1252', 'ignore').decode('cp1252')
    except:
        cleaned = cleaned.encode('ascii', 'ignore').decode('ascii')
    return cleaned.strip()[:100] # Limite de 100 caracteres para evitar caminhos muito longos

def progress_hook(d):
    if d['status'] == 'downloading':
        try:
            p = d.get('_percent_str', '').replace('%','')
            print(f"[download] {p}% - {d.get('_eta_str', 'N/A')} remaining", flush=True)
        except (KeyError, AttributeError, TypeError, ValueError) as e:
            print(f"[WARN] Failed to parse download progress: {e}")

def clean_temp_files(folder, base_name):
    if not os.path.exists(folder): return
    for f in os.listdir(folder):
        if base_name in f and (".temp" in f or ".part" in f or f.endswith(".ytdl")):
            try:
                os.remove(os.path.join(folder, f))
            except OSError as e:
                print(f"[WARN] Failed to remove temp file '{f}': {e}")

def _extract_sub_lang_from_name(filename):
    """
    Extract subtitle language code from yt-dlp output filename.
    Examples:
    - dl_video.pt.srt -> pt
    - dl_video.pt-BR.srt -> pt-br
    - dl_video.pt-orig.srt -> pt
    """
    name = filename.lower()
    match = re.search(r"dl_video\.([a-z]{2}(?:-[a-z]{2})?)(?:-orig)?\.srt$", name)
    if not match:
        return None
    return match.group(1).lower()

def download(url, base_root="VIRALS", download_subs=True, quality="best"):
    print(i18n("Extracting video information..."))
    title = None
    
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title')
    except Exception as e:
        print(i18n("Warning: Failed to extract info: {}").format(e))

    safe_title = sanitize_filename(title) if title else i18n("Unknown_Video")
    project_folder = os.path.abspath(os.path.join(base_root, safe_title))
    os.makedirs(project_folder, exist_ok=True)
    
    final_video_path = os.path.join(project_folder, "input.mp4")

    if os.path.exists(final_video_path) and os.path.getsize(final_video_path) > 1024:
        print(i18n("Using existing video file: {}").format(final_video_path))
        return final_video_path, project_folder

    # USAR PASTA TEMPORÁRIA DO SISTEMA PARA O DOWNLOAD
    # Isso evita problemas de trava de pasta e caminhos muito longos no Windows durante o merge
    with tempfile.TemporaryDirectory() as tmp_download_dir:
        temp_output_path = os.path.join(tmp_download_dir, "dl_video")
        
        quality_map = {
            "best": 'bestvideo+bestaudio/best',
            "1080p": 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            "720p": 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            "480p": 'bestvideo[height<=480]+bestaudio/best[height<=480]'
        }
        selected_format = quality_map.get(quality, 'bestvideo+bestaudio/best')

        ydl_opts_video = {
            'format': selected_format,
            'overwrites': True,
            'outtmpl': f"{temp_output_path}.%(ext)s",
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
            'quiet': False,
            'no_warnings': True,
            'force_ipv4': True,
        }

        print(i18n("Downloading video to safe temp area..."))
        try:
            with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                ydl.download([url])
        except Exception as e:
            if "sign in" in str(e).lower() or "confirm your age" in str(e).lower():
                print(i18n("Age restricted. Attempting with Chrome cookies..."))
                ydl_opts_video['cookiesfrombrowser'] = ('chrome',)
                try:
                    with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                        ydl.download([url])
                except Exception as e2:
                    print(i18n("Failed with cookies: {}. Fatal.").format(e2))
                    raise
            else:
                raise

        # Encontrar o vídeo baixado na pasta temp e mover para VIRALS
        downloaded_files = [f for f in os.listdir(tmp_download_dir) if f.startswith("dl_video") and f.endswith(".mp4")]
        if downloaded_files:
            source = os.path.join(tmp_download_dir, downloaded_files[0])
            print(i18n("Moving final video to project folder..."))
            try:
                # Usamos copy + remove em vez de rename/move para maior segurança no Windows entre drives
                shutil.copy2(source, final_video_path)
            except Exception as e_move:
                print(i18n("Error moving file: {}. Trying alternative...").format(e_move))
                # Fallback final se o shutil der erro de permissão (improvável no temp)
                time.sleep(2)
                shutil.move(source, final_video_path)

        # Download de legendas (também via TMP para segurança)
        if download_subs:
            print(i18n("\nFetching subtitles via temp area..."))
            ydl_opts_subs = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['pt.*', 'en.*', 'sp.*'],
                'outtmpl': f"{temp_output_path}.%(ext)s",
                'postprocessors': [{'key': 'FFmpegSubtitlesConvertor', 'format': 'srt'}],
                'quiet': True,
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts_subs) as ydl:
                    ydl.download([url])

                # Prefer PT subtitles. If PT is unavailable, skip external subtitles
                # so WhisperX transcribes directly from audio in the source language.
                subtitle_files = [f for f in os.listdir(tmp_download_dir) if f.startswith("dl_video") and f.endswith(".srt")]
                preferred_sub = None
                preferred_langs = ["pt-br", "pt"]

                for lang in preferred_langs:
                    for f in subtitle_files:
                        f_lang = _extract_sub_lang_from_name(f)
                        if f_lang == lang:
                            preferred_sub = f
                            break
                    if preferred_sub:
                        break

                if preferred_sub:
                    src_sub = os.path.join(tmp_download_dir, preferred_sub)
                    selected_lang = _extract_sub_lang_from_name(preferred_sub) or "pt"
                    dst_lang_sub = os.path.join(project_folder, f"input.{selected_lang}.srt")
                    dst_default_sub = os.path.join(project_folder, "input.srt")
                    shutil.move(src_sub, dst_lang_sub)
                    shutil.copy2(dst_lang_sub, dst_default_sub)
                    print(i18n("Subtitles ready. Selected language: {}").format(selected_lang))
                else:
                    print(i18n("No PT subtitles found. Skipping external subtitles to preserve original audio language context."))
            except Exception:
                print(i18n("Subtitles skipped (429 or missing). AI will transcribe locally."))

    return final_video_path, project_folder
