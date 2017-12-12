from flask import render_template
from flasgger import Swagger
from app import create_app

config_name = "development"
app = create_app(config_name)
swag= Swagger(app,
   template={
       "info": {
       "title": "Hadijahz YummyRecipes API",
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
    return render_template('index.html')

if __name__ == '__main__':
    app.run()