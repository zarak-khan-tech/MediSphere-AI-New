"""
MediSphere AI - Chat Routes
Built by Zarak Khan
API endpoints for chat functionality.
"""

from flask import Blueprint, request, jsonify

from agents.orchestrator import orchestrator
from utils.logger import logger

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint.
    
    Request JSON: {"message": "user message", "user_id": "optional"}
    Response JSON: {"agent": "AgentName", "message": "response", "status": "status"}
    """
    try:
        data = request.get_json() or {}
        message = data.get('message', '').strip()
        user_id = data.get('user_id', 'anonymous')
        
        if not message:
            return jsonify({
                "status": "error",
                "message": "No message provided"
            }), 400
        
        logger.info(f"Chat request from {user_id}")
        
        # Process through orchestrator
        result = orchestrator.process(message, user_id)
        
        return jsonify({
            "status": result['response'].get('status', 'success'),
            "agent": result['agent'],
            "intent": result['intent'],
            "message": result['response'].get('message', ''),
            "patient_id": result['response'].get('patient_id'),
            "data": {k: v for k, v in result['response'].items() 
                     if k not in ['message', 'status', 'patient_id']}
        })
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({
            "status": "error",
            "message": "An error occurred. Please try again."
        }), 500


@chat_bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "MediSphere AI",
        "version": "2.0"
    })