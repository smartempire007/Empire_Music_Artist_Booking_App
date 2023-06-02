import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Connect to the database
DATABASE_URL = os.getenv('DATABASE_URL')

# IMPLEMENT DATABASE URL

# imported the database uri from .env file for security as DATABASE_URL instead of implementing the below standard
# SQLALCHEMY_DATABASE_URI =  'postgresql://postgres:password@localhost:5432/empire_music'
SQLALCHEMY_DATABASE_URI = DATABASE_URL
