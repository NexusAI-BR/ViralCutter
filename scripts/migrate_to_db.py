import os
import json
from database.manager import db
from database.models import Project, Segment

def migrate():
    print("Starting migration of existing projects to Database...")
    virals_dir = "VIRALS"
    
    if not os.path.exists(virals_dir):
        print("VIRALS directory not found. Nothing to migrate.")
        return

    projects = [d for d in os.listdir(virals_dir) if os.path.isdir(os.path.join(virals_dir, d))]
    
    for proj_name in projects:
        proj_path = os.path.join(virals_dir, proj_name)
        
        # Check if project already in DB
        existing = db.get_project_by_name(proj_name)
        if existing:
            print(f"Project '{proj_name}' already in database. Skipping.")
            continue
            
        print(f"Migrating project: {proj_name}")
        
        # Try to read process_config.json
        config_path = os.path.join(proj_path, "process_config.json")
        config_data = {}
        workflow = "1"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                workflow = config_data.get("workflow", "1")

        # Create project in DB
        proj_id = db.add_project(
            name=proj_name,
            path=proj_path,
            config=config_data,
            workflow=workflow
        )
        
        if proj_id:
            db.update_project_status(proj_id, "completed")
            
            # Try to migrate segments if viral_segments.txt exists
            segments_file = os.path.join(proj_path, "viral_segments.txt")
            if os.path.exists(segments_file):
                try:
                    with open(segments_file, 'r', encoding='utf-8') as f:
                        segs_json = json.load(f)
                        segments = segs_json.get("segments", [])
                        for s in segments:
                            db.add_segment(proj_id, s)
                    print(f"  -> Migrated {len(segments)} segments.")
                except Exception as e:
                    print(f"  -> Error migrating segments for {proj_name}: {e}")

    print("Migration completed!")

if __name__ == "__main__":
    migrate()
