from jwtauthtest.database import Base
from sqlalchemy import Column, Integer, String, Text, Enum, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
import enum, datetime

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(200), nullable=False)

    entries = relationship("Entry")
    fields = relationship("Field")

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User {{ username: {self.username}, password: {self.password} }}'


class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    # Title optional, otherwise generated from text. topic-modeled, or BERT summary, etc?
    title = Column(String(128))
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Static fields (not user-generated)
    incognito_therapist = Column(Boolean)
    incognito_ml = Column(Boolean)

    field_entries = relationship("FieldEntry")
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, title, text):
        self.title = title
        self.text = text

    # TODO look into https://stackoverflow.com/questions/7102754/jsonify-a-sqlalchemy-result-set-in-flask
    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'text': self.text
        }


class FieldType(enum.Enum):
    # medication changes / substance intake
    # exercise, sleep, diet, weight
    numeric = 1

    # happiness score
    fivestar = 2

    # periods
    bool = 3

    # think of more
    # weather_api?
    # mood words (happy, sad, anxious, wired, bored, ..)


class Field(Base):
    """Entries that change over time. Uses:
    * Charts
    * Effects of sentiment, topics on entries
    * Global trends (exercise -> 73% happiness)
    """
    __tablename__ = 'fields'

    id = Column(Integer, primary_key=True)
    type = Column(Enum(FieldType))
    name = Column(String(128))
    # attributes = dict()

    user_id = Column(Integer, ForeignKey('users.id'))


class FieldEntry(Base):
    __tablename__ = 'field_entries'

    id = Column(Integer, primary_key=True)
    value = Column(Float)  # TODO Can everything be a number? reconsider

    entry_id = Column(Integer, ForeignKey('entries.id'))
    field_id = Column(Integer, ForeignKey('fields.id'))
