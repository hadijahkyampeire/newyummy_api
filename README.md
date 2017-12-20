
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
*see the API Documentation by following this [url](http://127.0.0.1:5000/apidocs/#/)*
# Demo
The API demo is deployed on heroku at https://hadijahyummyrecipe-api.herokuapp.com/apidocs/#/

## Requirements(Building Blocks)
- `Python3` - A programming language that lets us work more quickly (The universe loves speed!).
- `Flask` - A microframework for Python based on Werkzeug, Jinja 2 and good intentions
- `Virtualenv` - A tool to create isolated virtual environment
- `PostgreSQL` – Postgres database offers many advantages over others.
- `Psycopg2` – A Python adapter for Postgres.
- `Flask-SQLAlchemy` – A Flask extension that provides support for SQLAlchemy.
- `Flask-Migrate` – Offers SQLAlchemy database migrations for Flask apps using Alembic.

## Installation
First clone this repository
```
$ git clone @https://github.com/hadijahkyampeire/newyummy_api
$ cd Yummy-Recipe-RestAPI
```
Create virtual environment and install it
```
$ virtualenv --python=python3 venv
$ source /venv/bin/activate
```
Then install all the necessary dependencies by
```
pip install -r requirements.txt
```

## Set environment varibles and setup database
### On windows
You need to create a test database for tests to run
postgres# CREATE DATABASE test_db
At the terminal or console type
```
set APP_SETTINGS=development
set DATABASE_URL_DEV=postgresql://postgres:@localhost/flask_api
psql -U postgres
postgres# CREATE DATABASE yummy_api
```
### On linux/Ubuntu or Mac
At the terminal or console type
```
export APP_SETTINGS=development
export DATABASE_URL=postgresql://postgres:@localhost/flask_api
psql -U postgres
postgres# CREATE ROLE postgres
postgres# CREATE DATABASE flask_api
```

## Initialize the database and create database tables
```
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
```

## Run the server
At the terminal or console type
```
python run.py
```
## Testing and knowing coverage
To run tests run this command at the console/terminal
```
nosetests or
python manage.py test
```
To run tests with coverage run this command at the console/terminal
```
python manage.py test_cov or
nosetests -v --with-coverages
```
## Functionality
  End points | Functionality | Access
  ------------------|------------------|--------------------
  /api/v1/auth/register|Post, create account|PUBLIC
  /api/v1/auth/login|post, login|PUBLIC 
  /api/v1/auth/reset_password|post, logout|PUBLIC 
  /api/v1/auth/logout|post, logout|PUBLIC 
  /api/v1/categories/|post, add category|PRIVATE
  /api/v1/categories/|Get, retrieve all categories| PRIVATE
  /api/v1/categories/id|Get, retrieve one category|PRIVATE
  /api/v1/categories/id|Put, Edit a category| PRIVATE
  /api/v1/categories/id|Delete, Delete a category| PRIVATE
  /api/v1/categories/id/recipes|post, add a recipe to a category|PRIVATE
  /api/v1/categories/id/recipes|Get, retrieve all recipes in a given category| PRIVATE
  /api/v1/categories/id/recipes/id|Get, retrieve a recipe in a given category|PRIVATE
  /api/v1/categories/id/recipes/id|Put, Edit a recipe in a given category| PRIVATE
  /api/v1/categories/id/recipes/id|Delete, Delete a recipe in a given category| PRIVATE
  -----------------|-----------------------|-------------------



   Test your setup using a client app like postman
