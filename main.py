from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_restful import Api
from flask import Flask 
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from application.controllers import set_routes

app = None
api = None

def create_app():
    app = Flask(__name__, template_folder="templates", static_url_path='/static')
    if os.getenv("ENV", "development") == "production":
        raise Exception('Not available')
    else:
        print("-----------Starting server-----------")
        app.config.from_object(LocalDevelopmentConfig)
        db.init_app(app)
        api = Api(app)
        app.app_context().push()
        set_routes(app)   
        return app, api
    

app, api = create_app()

from application.api import *
from application.models import *

api.add_resource(UserApi, "/v1/api/user", "/v1/api/user/<string:username>")      #adding apis to app for post and other requests
api.add_resource(AdminApi, "/v1/api/admin", "/v1/api/admin/<string:username>")
api.add_resource(GenreApi, "/v1/api/genre")
api.add_resource(PlaylistApi, "/v1/api/manage_playlist/<string:genrename>")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
