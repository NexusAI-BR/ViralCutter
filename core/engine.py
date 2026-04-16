import os
import time
import subprocess
from database.manager import db
from .hardware import get_best_hardware_config
from i18n.i18n import I18nAuto

i18n = I18nAuto()

class ViralCutterCore:
    def __init__(self, project_name=None, project_path=None):
        self.project_name = project_name
        self.project_path = project_path
        self.db_id = None
        self.hardware = get_best_hardware_config()
        
        if project_name:
            proj = db.get_project_by_name(project_name)
            if proj:
                self.db_id = proj.id
                self.project_path = proj.path
            else:
                self.initialize_project(project_name, project_path)

    def initialize_project(self, name, path, url=None, config=None, workflow="1"):
        self.project_name = name
        self.project_path = path
        self.db_id = db.add_project(
            name=name, 
            path=path,
            url=url,
            config=config,
            workflow=workflow
        )
        return self.db_id

    def log_status(self, status):
        if self.db_id:
            db.update_project_status(self.db_id, status)
            print(f"[CORE] Status updated: {status}")

    def get_ffmpeg_base_cmd(self):
        """Returns base FFmpeg command with optimal hardware config."""
        encoder = self.hardware["video_encoder"]
        preset = self.hardware["video_preset"]
        
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-hide_banner"]
        return cmd, encoder, preset

    def run_step(self, step_name, func, *args, **kwargs):
        """Wrapper to run a pipeline step with timing and logging."""
        start = time.time()
        # Map step names to readable statuses for filtering
        status_map = {
            "download": "downloading",
            "transcribe": "transcribing",
            "analysis": "analyzing",
            "cut": "cutting",
            "edit": "finalizing",
            "burn": "finalizing"
        }
        status_label = status_map.get(step_name, step_name)
        self.log_status(status_label)
        try:
            print(f"\n[CORE] Starting step: {step_name.upper()}...")
            result = func(*args, **kwargs)
            duration = time.time() - start
            print(f"[CORE] Step {step_name} completed in {duration:.2f}s")
            return result
        except Exception as e:
            self.log_status("error")
            print(f"[CORE] ERROR in {step_name}: {e}")
            raise e
