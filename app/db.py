import os

from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import asc, desc, func

USER_DETAILS_FOLDER = os.path.expanduser(r'~/Documents')


sqlite_filepath = os.path.join(USER_DETAILS_FOLDER, 'Data_Hunter_Archive.db')
engine = create_engine(f"sqlite:///{sqlite_filepath}")
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
