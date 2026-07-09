"""
MediSphere AI - Routes Package
Built by Zarak Khan
"""

from routes.chat_routes import chat_bp
from routes.api_routes import api_bp
from routes.dashboard_routes import dash_bp

__all__ = ['chat_bp', 'api_bp', 'dash_bp']