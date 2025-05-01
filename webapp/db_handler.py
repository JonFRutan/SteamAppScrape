# Run 'poetry run python import.py' - that resolves these imports
#module imports
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Table, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

#local imports
import scrape as sc

Base = declarative_base()

def configure(cnx):
    """Called a single time from app.py for the database engine"""
    global Session
    Session.configure(bind=cnx)

# defining database tables via SQLAlchemy. This only creates the tables if they do not exist.
# It does not alter anything that schema.sql has put in.

#defining Tables
class User(Base):
    __tablename__ = 'User'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(100))

class Library(Base):
    __tablename__ = 'Library'
    library_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('User.user_id'))
    app_id = Column(Integer, ForeignKey('Game.app_id'))

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

#functions
def from_data(cnx, game_data):
    """Insert a game from it's scraped json. Requires a database connection."""
    Session = sessionmaker(bind=cnx)
    session = Session()
    Base.metadata.create_all(cnx)

    try:
        app_id = game_data['appID']
        title = game_data['title']
        description = game_data['description']
        release_date = game_data['release_date'].date()
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

    session.commit()
    session.close()

def import_user_and_library(cnx, user_info):
    """Imports a user via their ID, simultaneously importing any unrecognized games and tagging them"""
    Session = sessionmaker(bind=cnx)
    session = Session()
    Base.metadata.create_all(cnx)

    steam_id = int(user_info['steam_id'])
    username = user_info['username']
    user = session.query(User).filter_by(user_id=steam_id).first()
    if not user:
        user = User(user_id=steam_id, username=username)
        session.add(user)
        session.commit()
        print(f"[+] Added user: {username} (SteamID: {steam_id})")
    else:
        print(f"[=] User already exists: {username} (SteamID: {steam_id})")
    
    for game_data in user_info['games']:
        app_id = game_data['appid']
        game = session.query(Game).filter_by(app_id=app_id).first()
        if not game:
            print(f"[-] Game {app_id} not found. Scraping and inserting...")
            scraped_game = sc.scrape(app_id)
            if scraped_game:
                insert_game(session, scraped_game)
                session.expire_all()
                game = session.query(Game).filter_by(app_id=app_id).first()
        
        if not game:
            print(f"[!] Game {app_id} still missing after scraping. Skipping link.")
            continue

        link = session.query(Library).filter_by(user_id=steam_id, app_id=app_id).first()
        if not link:
            new_link = Library(user_id=steam_id, app_id=app_id)
            session.add(new_link)
            print(f"[+] Linked {username} to {game.title} (AppID {app_id})")
        else:
            print(f"[=] Link already exists for {username} and {game.title} (AppID {app_id})")

    session.commit()
    session.close()

def insert_game(session, game_data):
    """Insert a game using scraped data."""
    try:
        app_id = game_data['appID']
        title = game_data['title']
        description = game_data['description']
        release_date = game_data['release_date'].date()
        tag_names = game_data['tags']

        game = session.query(Game).get(app_id)
        if not game:
            game = Game(app_id=app_id, title=title, description=description, release_date=release_date)
            session.add(game)

        for name in tag_names:
            tag = session.query(Tag).filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
                session.add(tag)
                session.flush()

            if tag not in game.tags:
                game.tags.append(tag)

        session.commit()
    except Exception as e:
        print(f"[!] Error inserting game: {e}")
        session.rollback()
    finally:
        session.close()

def update_game(cnx, appid, new_title=None, new_description=None):
    Session = sessionmaker(bind=cnx)
    session = Session()
    try:
        game = session.query(Game).filter_by(app_id=appid).first()
        if not game:
            return f"Game with AppID {appid} not found."
        if new_title:
            game.title = new_title
        if new_description:
            game.description = new_description

        session.commit()
        return f"Game {appid} updated."
    except Exception as e:
        return f"Error updating game: {e}"
    finally:
        session.close()

def delete_game(cnx, appid):
    Session = sessionmaker(bind=cnx)
    session = Session()
    try:
        game = session.query(Game).filter_by(app_id=appid).first()
        if not game:
            return f"Game with AppID {appid} not found."
        session.delete(game)
        session.commit()
        return f"Game {appid} deleted."
    except Exception as e:
        session.rollback()
        return f"Error deleting game: {e}, rolling back..."
    finally:
        session.close()