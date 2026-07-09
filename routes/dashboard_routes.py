"""
MediSphere AI - Dashboard Routes
Built by Zarak Khan
Web page routes for the UI.
"""

from flask import Blueprint, render_template

from config import Config

dash_bp = Blueprint('dashboard', __name__)


@dash_bp.route('/')
def index():
    """Main chat interface."""
    return render_template('index.html', 
                         hospital_name=Config.HOSPITAL_NAME,
                         hospital_address=Config.HOSPITAL_ADDRESS,
                         hospital_phone=Config.HOSPITAL_PHONE)


@dash_bp.route('/dashboard')
def admin_dashboard():
    """Admin dashboard panel."""
    return render_template('dashboard.html',
                         hospital_name=Config.HOSPITAL_NAME,
                         doctors=Config.DOCTORS)