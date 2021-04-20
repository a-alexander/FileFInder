import datetime
import zipfile
from typing import Optional

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from .db import session, engine

import os
from datetime import datetime

Base = declarative_base()


def file_datetime_extractor(file_details, attr: str = 'st_ctime'):
    file_attr = int(getattr(file_details, attr))
    return datetime.fromtimestamp(file_attr)


def parse_date(date):
    if date is None:
        return '-'
    return date.strftime('%Y-%m-%d %H:%M:%S')


class File(Base):
    __tablename__ = "file_model"
    id = Column(Integer, primary_key=True)
    path = Column(String)
    file_name = Column(String)
    date_created = Column(DateTime)
    date_modified = Column(DateTime)
    last_accessed = Column(DateTime)
    size = Column(Float)
    file_type = Column(String)
    project_area_id = Column(Integer, ForeignKey('project_area_model.id'))

    @classmethod
    def create_from_path(cls, path: str, project_area_id: int) -> 'File':
        file_details = os.stat(path)
        return cls(path=path,
                   file_name=os.path.basename(path),
                   date_created=file_datetime_extractor(file_details, 'st_ctime'),
                   date_modified=file_datetime_extractor(file_details, 'st_mtime'),
                   last_accessed=file_datetime_extractor(file_details, 'st_atime'),
                   size=file_details.st_size / 1000,
                   file_type=path.split('.')[-1],
                   project_area_id=project_area_id)

    @staticmethod
    def parse_date(date):
        return date.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def created(self):
        return parse_date(self.date_created)

    @property
    def modified(self):
        return parse_date(self.date_modified)

    @property
    def accessed(self):
        return parse_date(self.last_accessed)


class ProjectArea(Base):
    __tablename__ = "project_area_model"
    id = Column(Integer, primary_key=True)
    path = Column(String)
    files = relationship("File", backref=backref("project_area"), cascade="all, delete-orphan")
    archived = Column(Boolean, default=False)
    last_archived = Column(DateTime, onupdate=datetime.utcnow)

    @property
    def last_archived_str(self):
        return parse_date(self.last_archived)

    def discover_files(self):
        """Populate the files for the project."""
        self.archived = False
        session.commit()
        for root, dirs, files in os.walk(self.path):
            for file in files:
                path = os.path.join(root, file)
                file_model = File.create_from_path(path, self.id)
                self.files.append(file_model)
        self.archived = True
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()


def available_paths() -> list[ProjectArea]:
    return session.query(ProjectArea).all()


def get_file_matches(project_areas: list[ProjectArea] = None,
                     phrase: Optional[str] = None,
                     ext: Optional[str] = None,
                     ignore_case: bool = True) -> list[File]:
    bare_query = session.query(File)
    if phrase:
        bare_query = bare_query.filter(File.file_name.like(f'%{phrase}%'))
    if ext:
        bare_query = bare_query.filter(File.file_type == ext)
    return bare_query.all()


Base.metadata.create_all(engine)


def zip_up_files(files: list[str], archive_name: str) -> str:
    archive_name = f'{archive_name}.zip'
    save_location = os.path.dirname(__file__)
    archive_path = os.path.join(save_location, archive_name)
    archive = zipfile.ZipFile(archive_path, 'w')
    no = 1
    for file in files:
        if not os.path.exists(file):
            continue
        new_name = f'{no}_{os.path.basename(file)}'
        archive.write(file, new_name, compress_type=zipfile.ZIP_DEFLATED)
        no += 1
    archive.close()
    return archive_path
