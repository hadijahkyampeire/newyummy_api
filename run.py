
from app import create_app

config_name = "development"
app = create_app(config_name)
@app.route("/")
def main():
    return 'Hello Welcome to Hadijahz yummy recipe Api, Go ahead and use the existing URL !'

if __name__ == '__main__':
    app.run()