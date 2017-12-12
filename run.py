from flask import render_template
from flasgger import Swagger
from app import create_app

config_name = "development"
app = create_app(config_name)
swag= Swagger(app,
   template={
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