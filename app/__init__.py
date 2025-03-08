from flask import Flask
from config import config
from datetime import datetime

def create_app(config_name='default'):
    """Application factory function to create and configure the Flask app"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Register blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Add context processor for common template variables
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    return app 