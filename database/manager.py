import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base, Project, Segment, AppConfig

class DatabaseManager:
    def __init__(self, db_path='viralcutter.db'):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    def add_project(self, name, path, url=None, config=None, workflow="1"):
        session = self.get_session()
        try:
            project = Project(
                name=name,
                path=path,
                url=url,
                config=config,
                workflow=workflow
            )
            session.add(project)
            session.commit()
            return project.id
        except Exception as e:
            session.rollback()
            print(f"Error adding project: {e}")
            return None
        finally:
            self.Session.remove()

    def get_project_by_name(self, name):
        session = self.get_session()
        try:
            return session.query(Project).filter_by(name=name).first()
        finally:
            self.Session.remove()

    def list_projects(self, search_term=None, status_filter=None):
        session = self.get_session()
        try:
            query = session.query(Project)
            if search_term:
                query = query.filter(Project.name.like(f"%{search_term}%"))
            if status_filter and status_filter != "All":
                query = query.filter(Project.status == status_filter)
            return query.order_by(Project.created_at.desc()).all()
        finally:
            self.Session.remove()

    def delete_project(self, project_id):
        session = self.get_session()
        try:
            project = session.get(Project, project_id)
            if project:
                path = project.path
                session.delete(project)
                session.commit()
                return True, path
            return False, None
        except Exception as e:
            session.rollback()
            print(f"Error deleting project: {e}")
            return False, None
        finally:
            self.Session.remove()

    def add_segment(self, project_id, segment_data):
        session = self.get_session()
        try:
            segment = Segment(
                project_id=project_id,
                title=segment_data.get('title'),
                start_time=segment_data.get('start_time'),
                end_time=segment_data.get('end_time'),
                duration=segment_data.get('duration'),
                score=segment_data.get('score'),
                hook=segment_data.get('hook'),
                reasoning=segment_data.get('reasoning'),
                final_cut_path=segment_data.get('final_cut_path')
            )
            session.add(segment)
            session.commit()
            return segment.id
        except Exception as e:
            session.rollback()
            print(f"Error adding segment: {e}")
            return None
        finally:
            self.Session.remove()

    def update_project_status(self, project_id, status):
        session = self.get_session()
        try:
            project = session.get(Project, project_id)
            if project:
                project.status = status
                session.commit()
        finally:
            self.Session.remove()

# Singleton instance
db = DatabaseManager()
