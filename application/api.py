#here database is used for requesting and responsing of restful api
from flask import jsonify
from flask_restful import Resource, reqparse
from application.database import db
from application.models import *
from flask_restful import fields, marshal_with
from application.validation import *
from werkzeug.security import generate_password_hash, check_password_hash
# validation


output_fields_user = {
    "l_id": fields.Integer,
    "username": fields.String,
    "password": fields.String,
    "profile": fields.String,
}
create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('username')
create_user_parser.add_argument('password')
create_user_parser.add_argument('profile')


output_fields_admin = {
    "a_id": fields.Integer,
    "username": fields.String,
    "password": fields.String,
}
create_admin_parser = reqparse.RequestParser()
create_admin_parser.add_argument('username')
create_admin_parser.add_argument('password')


output_fields_genre = {
    "g_id":fields.Integer,
    "genrename":fields.String
}
create_genre_parser = reqparse.RequestParser()
create_genre_parser.add_argument("genrename")


output_fields_playlist = {
    "genrename":fields.String,
    "songlist":fields.List(fields.String)
}
create_playlist_parser = reqparse.RequestParser()
create_playlist_parser.add_argument("genrename")


class UserApi(Resource):
    @marshal_with(output_fields_user)   #returns json form of object tuple from requested table
    def get(self, username):
        logger = db.session.query(Loggers).filter(Loggers.username==username).first()
        if logger == None:
            print("No user fount")
        else:
            return logger
    
    @marshal_with(output_fields_user)
    def post(self):
        args = create_user_parser.parse_args()
        username = args.get("username", None)
        password = args.get("password", None)
        profile= args.get('profile', None)
        allnames = [i.username for i in db.session.query(Loggers).all()]
        print("got")
        if username in allnames:
            raise SimilarUserExists(error_code=410, error_message="You have entered user which exists in our database already, Please try with some other name!")
        else:
            newlogger = Loggers(username=username, password=generate_password_hash(password),profile=profile)
            db.session.add(newlogger)
            db.session.commit()
            return newlogger, 201
        
    @marshal_with(output_fields_user)
    def delete(self, username):
        logger = db.session.query(Loggers).filter(Loggers.username == username ).first()
        
        if(logger):
            db.session.delete(logger)
            db.session.commit()
            return logger, 200
        else:
            print("no user found")

    @marshal_with(output_fields_user)
    def put(self, username):
        logger = db.session.query(Loggers).filter(Loggers.username == username ).first()
        if(logger):
            args = create_user_parser.parse_args()
            username = args.get("username", None)
            password = args.get("password", None)
            profile= args.get('profile', None)
            logger.username = username
            logger.password = generate_password_hash(password)
            logger.profile = profile
            db.session.commit()
            return logger, 200
        else:
            print("no user found")






class AdminApi(Resource):
    @marshal_with(output_fields_admin)   #returns json form of object tuple from requested table
    def get(self, username):
        admin = db.session.query(Loggers).filter(Loggers.username==username).first()
        if admin == None:
            print("No user found")
        else:
            return admin
        
    @marshal_with(output_fields_admin)
    def post(self):
        args = create_user_parser.parse_args()
        username = args.get("username", None)
        password = args.get("password", None)
        profile= args.get('profile', None)
        allnames = [i.username for i in db.session.query(Loggers).all()]
        print("got")
        if username in allnames:
            raise Exception("Cant be same user")
        else:
            newlogger = Loggers(username=username, password=generate_password_hash(password),profile=profile)
            db.session.add(newlogger)
            db.session.commit()
            return newlogger, 201
        
    @marshal_with(output_fields_user)
    def delete(self, username):
        admin = db.session.query(Admin).filter(Admin.username == username ).first()
        if(admin):
            db.session.delete(admin)
            db.session.commit()
            return admin, 200
        else:
            print("no user found")

    @marshal_with(output_fields_user)
    def put(self, username):
        admin = db.session.query(Admin).filter(Admin.username == username ).first()
        if(admin):
            args = create_user_parser.parse_args()
            username = args.get("username", None)
            password = args.get("password", None)
            admin.username = username
            admin.password = generate_password_hash(password)
            db.session.commit()
            return admin, 200
        else:
            print("no user found")


class GenreApi(Resource):
    def get(self):
        genrelist = {str(i.g_id):i.genrename for i in db.session.query(Genre).all()}
        return genrelist

    def post(self):
        args = create_genre_parser.parse_args()
        genrename = args.get("genrename")
        newgenre = Genre(genrename=genrename)
        db.session.add(newgenre)
        db.session.commit()
        return { str(newgenre.g_id): genrename }
    


# idea is to put new playlist with names with songs for users in there profile with crud facility 
# while inserting insert correctr username and password 
#playlists table are created!
class PlaylistApi(Resource):
    @marshal_with(output_fields_playlist)
    def get(self, genrename):
        id = db.session.query(Genre).filter(Genre.genrename == genrename).first()
        if id!=None:
            songs = db.session.query(Songs).filter(Songs.g_id == id.g_id).all()
            songlist = [i.name for i in songs] if songs else []
            return {"genrename": str(genrename), "songlist": songlist}
        else:
            return {"Information":"Invalid genre found!"}
        
    # post for putting new playlist with genre
    # put for updating
    # delete  