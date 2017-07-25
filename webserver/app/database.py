from app import app
from sqlalchemy import and_
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import load_only
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()

class Entry(Base):
    __tablename__ = 'entry'

    timestamp = Column(Integer, primary_key=True)
    count = Column(Integer, nullable=False)
    type = Column(String(250), nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.as_dict())


engine = create_engine(app.config['DB_LOCATION'])
_current_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def initialize():
    """
    Initialize database. Called upon application start.
    """
    Base.metadata.create_all(bind=engine)


def add(entity):
    """
    Save/persist given entity.
    """
    _current_session.add(entity)
    _current_session.commit()
    return entity.timestamp


def merge(entity):
    """
    Merge given entitiy.
    """
    _current_session.merge(entity)
    _current_session.commit()
    return entity.timestamp


def add_many(entities):
    """
    Save/persist given entities.
    """
    timestamps = []
    for entity in entities:
        _current_session.add(entity)
        timestamps.append(entity.timestamp)
    _current_session.commit()
    return timestamps


def merge_many(entities):
    """
    Merge given entities.
    """
    timestamps = []
    for entity in entities:
        _current_session.merge(entity)
        timestamps.append(entity.id)
    _current_session.commit()
    return timestamps


def all(cls):
    """
    Find all objects of class cls.
    """
    all_objs = _current_session.query(cls).all()
    return all_objs


def find_entry_by_timestamp(timestamp):
    """
    Find one user by matching username.
    """
    try:
        one = _current_session.query(Entry).filter(Entry.timestamp == timestamp).one()
    except NoResultFound:
        one = None
    return one


def find_entries_by_entry_type(type):
    """
    Find all exercise entries with matching type.
    """
    all_objs = _current_session.query(Entry).filter(Entry.type == type).all()
    return all_objs
