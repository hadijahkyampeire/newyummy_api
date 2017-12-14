from flask import render_template, redirect
from flasgger import Swagger
from app import create_app

config_name = "development"
app = create_app(config_name)
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