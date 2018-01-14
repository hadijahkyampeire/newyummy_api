from flask import Blueprint

recipe=Blueprint('recipe',__name__)
from .import views