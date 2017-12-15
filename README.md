
[![Build Status](https://travis-ci.org/hadijahkyampeire/newyummy_api.svg?branch=api)](https://travis-ci.org/hadijahkyampeire/newyummy_api)
[![Coverage Status](https://coveralls.io/repos/github/hadijahkyampeire/newyummy_api/badge.svg?branch=master)](https://coveralls.io/github/hadijahkyampeire/newyummy_api?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/930b41f7e96ab8f63f98/maintainability)](https://codeclimate.com/github/hadijahkyampeire/newyummy_api/maintainability)
<a href="https://www.python.org/dev/peps/pep-0008/">
<img class="notice-badge" src="https://img.shields.io/badge/code%20style-pep8-orange.svg" alt="Badge"/>
</a>
<a href="https://github.com/hadijahkyampeire/newyummy_api/blob/api/License.md">
<img class="notice-badge" src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="Badge"/>
</a>
# yummyrecipes_api
# Description
yummyrecipes_api is a RESTFul web api that let's users create accounts, login and create, view, edit and delete categories and recipes.

# API-Documentation
The api documentation can be found at http://127.0.0.1:5000/apidocs/#/
# Demo
The API demo is deployed on heroku at https://hadijahyummyrecipe-api.herokuapp.com/apidocs/#/
## Technologies used
* **[Python3](https://www.python.org/downloads/)** - A programming language that lets you work more quickly (The universe loves speed!).
* **[Flask](flask.pocoo.org/)** - A microframework for Python based on Werkzeug, Jinja 2 and good  environments
* **[PostgreSQL](https://www.postgresql.org/download/)** – Postgres database offers many [advantages](https://www.postgresql.org/about/advantages/) over others.
* Minor dependencies can be found in the requirements.txt file on the root folder.


## Installation / Usage
* If you wish to run your own build, first ensure you have python3 globally installed in your computer. If not, you can get python3 [here](https://www.python.org).
* After this, ensure you have installed virtualenv globally as well. If not, run this:
    ```
        $ pip install virtualenv
    ```
* Git clone this repo to your PC
    ```
        $ git clone git@https://github.com/hadijahkyampeire/newyummy_api
    ```


* #### Dependencies
    1. Cd into your the cloned repo as such:
        ```
        $ cd newyummy_api
        ```

    2. Create and fire up your virtual environment in python3:
        ```
        $ virtualenv -p python3 venv

        $ pip install autoenv
        ```
        Activate the virtual environment
        ```sh
        $ source env/bin/activate
        ```

* #### Environment Variables
    Create a .env file and add the following:
    ```
    source venv/bin/activate
    export SECRET="some-very-long-string-of-random-characters-CHANGE-TO-YOUR-LIKING"
    export APP_SETTINGS="development"
    export DATABASE_URL="postgresql://localhost/flask_api"
    ```

    Save the file. CD out of the directory and back in. `Autoenv` will automatically set the variables.
    We've now kept sensitive info from the outside world! 😄

* #### Install your requirements
    ```
    (venv)$ pip install -r requirements.txt
    ```

* #### Migrations
    On your psql console, create your database:
    ```
    > CREATE DATABASE flask_api;
    ```
    Then, make and apply your Migrations
    ```
    (venv)$ python manage.py db init

    (venv)$ python manage.py db migrate
    ```

    And finally, migrate your migrations to persist on the DB
    ```
    (venv)$ python manage.py db upgrade
    ```
## Database URI
    $ export DB_URL='postgresql://dbusername:dbpassword@localhost/dbname'
    ```
    Start the application by running
    ```sh
    $ python run.py 
    ```
## Functionality
  End points | Functionality | Access
  ------------------|------------------|--------------------
  auth/register|Post, create account|PUBLIC
  auth/login|post, login|PUBLIC 
  categories/|post, add category|PRIVATE
  categories/|Get, retrieve all categories| PRIVATE
  categories/id|Get, retrieve one category|PRIVATE
  categories/id|Put, Edit a category| PRIVATE
  categories/id|Delete, Delete a category| PRIVATE
  categories/id/recipes|post, add a recipe to a category|PRIVATE
  categories/id/recipes|Get, retrieve all recipes in a given category| PRIVATE
  categories/id/recipes/id|Get, retrieve a recipe in a given category|PRIVATE
  categories/id/recipes/id|Put, Edit a recipe in a given category| PRIVATE
  categories/id/recipes/id|Delete, Delete a recipe in a given category| PRIVATE
  -----------------|-----------------------|-------------------



   Test your setup using a client app like postman
