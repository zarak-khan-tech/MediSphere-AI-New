"""
MediSphere AI - Main Application
Architected & Engineered by Zarak Khan

Flask application entry point with 3D UI.
"""

from flask import Flask
from config import Config
from routes.chat_routes import chat_bp
from routes.api_routes import api_bp
from routes.dashboard_routes import dash_bp
from utils.logger import logger

def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Register blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(dash_bp)
    
    logger.info("=" * 60)
    logger.info("MediSphere AI - Starting Up")
    logger.info("Architected & Engineered by Zarak Khan")
    logger.info("=" * 60)
    logger.info(f"Hospital: {Config.HOSPITAL_NAME}")
    logger.info(f"LLM Mode: {'Grok API' if Config.USE_LLM else 'Regex Fallback'}")
    logger.info(f"Doctors: {len(Config.DOCTORS)}")
    logger.info("=" * 60)
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print(" 🏥 MediSphere AI — Hospital Agent System")
    print(" 🚀 Architected & Engineered by Zarak Khan")
    print("=" * 60)
    print(f"\n 📍 Web Interface:    http://localhost:5000")
    print(f" 📊 Admin Dashboard:  http://localhost:5000/dashboard")
    print(f" 💬 Chat API:         http://localhost:5000/chat")
    print(f" 📈 Stats API:        http://localhost:5000/api/stats")
    print("\n" + "=" * 60)
    print(" Press CTRL+C to stop")
    print("=" * 60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )