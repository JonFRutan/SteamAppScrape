#Run 'poetry run python import.py' - that resolves these imports
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Table, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv

from datetime import datetime
from pathlib import Path
import json, pickle, os

#grab .env variables
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

Base = declarative_base()

#NOTE: schema.sql may be unnecessary, but I'm leaving it for now.

#defining database tables via SQLAlchemy. This only creates the tables if they do not exist.
#It does not alter anything that schema.sql has put in.
class GameTag(Base):
    __tablename__ = 'GameTag'
    game_tag_id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(Integer, ForeignKey('Game.app_id'))
    tag_id = Column(Integer, ForeignKey('Tag.tag_id'))

class Game(Base):
    __tablename__ = 'Game'
    app_id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text)
    release_date = Column(Date)
    tags = relationship('Tag', secondary='GameTag', back_populates='games')

class Tag(Base):
    __tablename__ = 'Tag'
    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True)
    games = relationship('Game', secondary='GameTag', back_populates='tags')

#NOTE: This will use a local .env file to connect to the database, check .env.sample.
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")

#you'll know if this fails, I was getting ~200 lines of error throws
engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}/{db_name}")
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

print("Connection successful...")
import_file = input("Enter filepath: ")

#NOTE: I haven't tested with a .pickle
if import_file.endswith('.json'):
    with open(import_file) as f:
        games = json.load(f)
elif import_file.endswith('.pickle'):
    with open(import_file, 'rb') as f:
        games = pickle.load(f)

for game_data in games:
    try:
        app_id = game_data['appID']
        title = game_data['title']
        description = game_data['description']
        release_date = datetime.strptime(game_data['release_date'], "%Y-%m-%d %H:%M:%S").date()
        tag_names = game_data['tags']

        game = session.query(Game).get(app_id)
        if not game:
            game = Game(app_id=app_id, title=title, description=description, release_date=release_date)
            session.add(game)
            print(f"[+] Added new game: {title} (AppID: {app_id})")
        else:
            print(f"[=] Game already exists: {title} (AppID: {app_id})")

        for name in tag_names:
            tag = session.query(Tag).filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
                session.add(tag)
                session.flush()
                print(f"    [+] Added new tag: {name}")

            if tag not in game.tags:
                game.tags.append(tag)
                print(f"        [+] Linked tag '{name}' to game '{title}'")

    except Exception as e:
        print(f"[!] Failed to process game '{game_data.get('title', 'Unknown')}': {e}")

#same as commit; in .sql
session.commit()
