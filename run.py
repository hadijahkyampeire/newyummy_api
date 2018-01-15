import os

from flask import render_template, redirect, jsonify
from flasgger import Swagger
from app import create_app

config_name = os.getenv('APP_SETTINGS')
app = create_app(config_name)

@app.errorhandler(405)
def url_not_found(error):
    return jsonify({'message':'Requested method not allowed'}), 405

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({'message':'page not found, check the url'}), 404

@app.errorhandler(500)
def internal_error(error):
    return "500 error"

swag= Swagger(app,
   template={
       "info": {
       "title": "Hadijahz YummyRecipes API Version 1",
       "description": "API that creates and logs in a user so as to manipulate yummyrecipes. Find source code and guidelines on 'https://github.com/hadijahkyampeire/newyummy_api'"},
       "securityDefinitions":{
           "TokenHeader": {
               "type": "apiKey",
               "name": "Authorization",
               "in": "header"
               
           }
       }
   })
@app.route("/")
def main():
    return redirect('/apidocs')

if __name__ == '__main__':
    app.run()