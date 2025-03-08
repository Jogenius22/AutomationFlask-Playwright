import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))

# Path to data directory
DATA_DIR = os.path.join(basedir, 'data')

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Data file paths
ACCOUNTS_FILE = os.path.join(DATA_DIR, 'accounts.json')
CITIES_FILE = os.path.join(DATA_DIR, 'cities.json')
MESSAGES_FILE = os.path.join(DATA_DIR, 'messages.json')
SCHEDULES_FILE = os.path.join(DATA_DIR, 'schedules.json')
LOGS_FILE = os.path.join(DATA_DIR, 'logs.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')

# Initialize data files if they don't exist
def init_data_files():
    files = {
        ACCOUNTS_FILE: [],
        CITIES_FILE: [],
        MESSAGES_FILE: [],
        SCHEDULES_FILE: [],
        LOGS_FILE: [],
        SETTINGS_FILE: {
            "run_interval": 30,
            "max_posts_per_day": 10,
            "timeout_between_actions": 5,
            "enable_random_delays": True
        }
    }
    
    for file_path, default_data in files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump(default_data, f, indent=4)

# Initialize data files
init_data_files()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    CAPSOLVER_API_KEY = os.environ.get('CAPSOLVER_API_KEY') or 'CAP-F79C6D0E7A810348A201783E25287C6003CFB45BBDCB670F96E525E7C0132148'
    
    @staticmethod
    def init_app(app):
        # Create uploads directory if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 