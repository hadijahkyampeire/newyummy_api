from flask import Blueprint

category = Blueprint('categories', __name__)

from .import views