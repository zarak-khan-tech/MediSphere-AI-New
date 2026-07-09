"""
MediSphere AI - API Routes
Built by Zarak Khan
REST API endpoints for dashboard data.
"""

from flask import Blueprint, request, jsonify

from utils.database import db
from config import Config
from utils.logger import logger

api_bp = Blueprint('api', __name__)


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics."""
    try:
        stats = db.get_stats()
        stats['doctors'] = len(Config.DOCTORS)
        stats['hospital_name'] = Config.HOSPITAL_NAME
        return jsonify({
            "status": "success",
            "data": stats
        })
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@api_bp.route('/patients', methods=['GET'])
def get_patients():
    """Get all patients."""
    try:
        patients = db.get_all_patients()
        return jsonify({
            "status": "success",
            "count": len(patients),
            "data": patients
        })
    except Exception as e:
        logger.error(f"Patients error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@api_bp.route('/appointments', methods=['GET'])
def get_appointments():
    """Get today's appointments."""
    try:
        appointments = db.get_todays_appointments()
        return jsonify({
            "status": "success",
            "count": len(appointments),
            "data": appointments
        })
    except Exception as e:
        logger.error(f"Appointments error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@api_bp.route('/queue', methods=['GET'])
def get_queue():
    """Get current queue status."""
    try:
        queue = db.get_all_queue()
        return jsonify({
            "status": "success",
            "count": len(queue),
            "data": queue
        })
    except Exception as e:
        logger.error(f"Queue error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@api_bp.route('/doctors', methods=['GET'])
def get_doctors():
    """Get all doctors configuration."""
    try:
        return jsonify({
            "status": "success",
            "count": len(Config.DOCTORS),
            "data": Config.DOCTORS
        })
    except Exception as e:
        logger.error(f"Doctors error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@api_bp.route('/register', methods=['POST'])
def direct_register():
    """Direct registration via API form."""
    try:
        data = request.get_json() or {}
        
        required = ['name', 'cnic', 'phone', 'age', 'gender']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                "status": "error",
                "message": f"Missing fields: {', '.join(missing)}"
            }), 400
        
        from agents.registration_agent import PatientRegistrationAgent
        agent = PatientRegistrationAgent()
        
        # Build message from form data
        message = f"register my name is {data['name']}, cnic {data['cnic']}, phone {data['phone']}, age {data['age']}, {data['gender']}"
        result = agent.process(message)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Direct register error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500