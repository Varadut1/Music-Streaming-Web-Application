#declaring model classes to work with db tables and relations.
from .database import db
class Loggers(db.Model):
    __tablename__ = 'loggers'
    l_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    profile = db.Column(db.String)
    comment = db.relationship("Songs", secondary="comments")

class Admin(db.Model):
    __tablename__ = "admin"
    a_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    admin_name = db.Column(db.String, unique=True)
    password = db.Column(db.String)

class Genre(db.Model):
    __tablename__ ="genre"
    g_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    genrename = db.Column(db.String, unique=True)

class Songs(db.Model):
    __tablename__="songs"
    s_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True)
    lyrics = db.Column(db.String)
    rating = db.Column(db.Integer)
    doc = db.Column(db.String)
    singer = db.Column(db.String)
    g_id = db.Column(db.Integer, db.ForeignKey("genre.g_id"))
    l_id = db.Column(db.Integer, db.ForeignKey("loggers.l_id"))
    composer = db.relationship("Loggers", secondary="composer")
    
class Playlist(db.Model):
    __tablename__ = "playlist"
    p_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String)
    l_id = db.Column(db.Integer, db.ForeignKey("loggers.l_id"))
    songlist = db.relationship("Songs", secondary="loggersplaylist")

class LoggersPlaylist(db.Model):
    __tablename__ = "loggersplaylist"
    s_id = db.Column(db.Integer, db.ForeignKey("songs.s_id"), primary_key=True)
    p_id = db.Column(db.Integer, db.ForeignKey("playlist.p_id"), primary_key=True)


class Comments(db.Model):
    __tablename__ = "comments"
    c_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    comment = db.Column(db.String)
    liked = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    s_id = db.Column(db.Integer, db.ForeignKey("songs.l_id"))
    l_id = db.Column(db.Integer, db.ForeignKey("loggers.l_id"))

class Composer(db.Model):
    __tablename__ = "composer"
    l_id = db.Column(db.Integer, db.ForeignKey("loggers.l_id"), primary_key=True)
    s_id = db.Column(db.Integer, db.ForeignKey("songs.s_id"), primary_key=True)

class Played(db.Model):
    __tablename__ = "played"
    s_id = db.Column(db.Integer, db.ForeignKey("loggers.l_id"), primary_key=True)
    plays = db.Column(db.Integer)

class Album(db.Model):
    __tablename__ = "album"
    a_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True)
    By = db.Column(db.Integer)

class S_Album(db.Model):
    __tablename__ = "s_album"
    s_id = db.Column(db.Integer, db.ForeignKey("songs.s_id"), primary_key=True)
    a_id = db.Column(db.Integer, db.ForeignKey("album.a_id"), primary_key=True)

class Flag(db.Model):
    __tablename__ = "flag"
    f_id = db.Column(db.Integer, primary_key=True, autoincrement= True)
    s_id = db.Column(db.Integer, db.ForeignKey("songs.s_id"), primary_key=True)