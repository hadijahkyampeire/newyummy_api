from flask_api import FlaskAPI
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response


# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
    from .models import Category, User, Recipe
    app = FlaskAPI(__name__, instance_relative_config=True)
    CORS(app)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)
    from .categories import category
    app.register_blueprint(category)
    from .recipes import recipe
    app.register_blueprint(recipe)

    return app
