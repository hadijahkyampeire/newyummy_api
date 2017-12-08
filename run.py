from flask import render_template
from app import create_app

config_name = "development"
app = create_app(config_name)
@app.route("/")
def main():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()