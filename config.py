"""
MediSphere AI - Configuration
Built by Zarak Khan
Centralized settings for the entire application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """All application settings in one place."""
    
    # Flask Settings
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "default-secret-key")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Grok API (xAI)
    GROK_API_KEY = os.getenv("GROK_API_KEY", "")
    GROK_API_URL = "https://api.x.ai/v1/chat/completions"
    GROK_MODEL = "grok-2-latest"
    
    # LLM Fallback
    USE_LLM = bool(GROK_API_KEY and GROK_API_KEY != "your_grok_api_key_here")
    
    # Hospital Info
    HOSPITAL_NAME = os.getenv("HOSPITAL_NAME", "Quetta City Hospital")
    HOSPITAL_ADDRESS = os.getenv("HOSPITAL_ADDRESS", "Jinnah Road, Quetta")
    HOSPITAL_PHONE = os.getenv("HOSPITAL_PHONE", "081-9201234")
    
    # Database
    DATABASE_PATH = "database/hospital.db"
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/medisphere.log"
    
    # Doctors Configuration
    DOCTORS = {
        "Dr. Ahmed Khan": {
            "department": "Cardiology",
            "specialization": "Heart Specialist",
            "slots": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
            "fee": 500,
            "experience": "15 years"
        },
        "Dr. Fatima Baloch": {
            "department": "Pediatrics",
            "specialization": "Child Specialist",
            "slots": ["09:30", "10:30", "11:30", "14:30", "15:30", "16:30"],
            "fee": 400,
            "experience": "10 years"
        },
        "Dr. Jamal Shah": {
            "department": "Orthopedics",
            "specialization": "Bone & Joint Specialist",
            "slots": ["10:00", "11:00", "12:00", "16:00", "17:00"],
            "fee": 600,
            "experience": "12 years"
        },
        "Dr. Sara Malik": {
            "department": "General Medicine",
            "specialization": "General Physician",
            "slots": ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00"],
            "fee": 300,
            "experience": "8 years"
        },
        "Dr. Rehman Kakar": {
            "department": "ENT",
            "specialization": "Ear, Nose, Throat",
            "slots": ["10:00", "11:00", "14:00", "15:00"],
            "fee": 450,
            "experience": "9 years"
        },
        "Dr. Nazia Ahmed": {
            "department": "Gynecology",
            "specialization": "Women's Health",
            "slots": ["09:00", "10:00", "11:00", "14:00", "15:00"],
            "fee": 500,
            "experience": "11 years"
        }
    }
    
    # FAQ Knowledge Base
    FAQ_KNOWLEDGE = {
        "timing": {
            "keywords": ["timing", "hours", "open", "close", "when", "time"],
            "response": (
                f"{HOSPITAL_NAME}:\n"
                "• OPD Hours: 9:00 AM - 5:00 PM (Monday-Saturday)\n"
                "• Emergency: 24/7\n"
                "• Pharmacy: 8:00 AM - 8:00 PM\n"
                "• Laboratory: 7:00 AM - 6:00 PM\n"
                "• Radiology: 8:00 AM - 5:00 PM"
            )
        },
        "location": {
            "keywords": ["location", "address", "where", "find", "reach", "located"],
            "response": (
                f"{HOSPITAL_NAME}:\n"
                f"📍 {HOSPITAL_ADDRESS}\n"
                "🚌 Bus Routes: 3, 7, 12 (Serena Stop)\n"
                "Branch 2 (Satellite Town): Sariab Road, Near Killi Geo\n"
                "Branch 3 (Brewery Road): Near Civil Secretariat"
            )
        },
        "departments": {
            "keywords": ["department", "specialist", "which doctor", "available", "services"],
            "response": (
                "Available Departments:\n"
                "• Cardiology (Dr. Ahmed Khan)\n"
                "• Pediatrics (Dr. Fatima Baloch)\n"
                "• Orthopedics (Dr. Jamal Shah)\n"
                "• General Medicine (Dr. Sara Malik)\n"
                "• ENT (Dr. Rehman Kakar)\n"
                "• Gynecology (Dr. Nazia Ahmed)\n"
                "• Emergency Medicine (24/7)\n"
                "• Radiology & Lab Services"
            )
        },
        "fees": {
            "keywords": ["fee", "cost", "price", "charges", "payment", "pay", "bill"],
            "response": (
                f"Fee Structure ({HOSPITAL_NAME}):\n"
                "• OPD Consultation: Rs. 300-600\n"
                "• Emergency Fee: Rs. 300\n"
                "• X-Ray: Rs. 800-1500\n"
                "• Blood Tests: Rs. 300-2000\n"
                "• Ultrasound: Rs. 1500-2500\n"
                "• Vaccination: Rs. 100-500\n"
                "💳 Payment: Cash, Card, JazzCash, EasyPaisa accepted"
            )
        },
        "documents": {
            "keywords": ["document", "bring", "cnic", "required", "need", "paper"],
            "response": (
                "Required Documents:\n"
                "• CNIC (mandatory for registration)\n"
                "• Previous medical records (if any)\n"
                "• Referral letter (if applicable)\n"
                "• Insurance card (if insured)\n"
                "For children: B-Form or Guardian's CNIC"
            )
        },
        "emergency": {
            "keywords": ["emergency", "urgent", "critical", "accident", "ambulance"],
            "response": (
                "🚨 Emergency Services (24/7):\n"
                f"• Emergency Hotline: {HOSPITAL_PHONE}\n"
                "• Ambulance: 1122 (Rescue 1122)\n"
                f"• Location: Emergency Gate, Main Campus ({HOSPITAL_ADDRESS})\n"
                "• No appointment needed for emergency\n"
                "• Trauma center and ICU available"
            )
        },
        "insurance": {
            "keywords": ["insurance", "sehat", "card", "sehhat", "coverage"],
            "response": (
                "Insurance & Sehat Card:\n"
                "• Sehat Sahulat Program accepted\n"
                "• State Life Insurance panel\n"
                "• Jubilee Insurance panel\n"
                "• EFU Health accepted\n"
                "Please bring your insurance card and CNIC. Coverage verification takes 10-15 minutes."
            )
        },
        "pharmacy": {
            "keywords": ["pharmacy", "medicine", "drug", "prescription", "medical store"],
            "response": (
                "Hospital Pharmacy:\n"
                "• Location: Ground Floor, Main Building\n"
                "• Hours: 8:00 AM - 8:00 PM\n"
                "• Generic medicines available\n"
                "• Outside prescriptions NOT accepted for narcotics\n"
                "• Home delivery available within Quetta city (Rs. 100 charge)"
            )
        },
        "visiting_hours": {
            "keywords": ["visit", "visiting", "meet patient", "ward", "room"],
            "response": (
                "Patient Visiting Hours:\n"
                "• General Wards: 4:00 PM - 7:00 PM\n"
                "• ICU: 5:00 PM - 6:00 PM (Close relatives only, 2 persons max)\n"
                "• Private Rooms: 10:00 AM - 8:00 PM\n"
                "• No visitors allowed in Operating Areas\n"
                "• Children under 12 not permitted in ICU"
            )
        },
        "blood_donation": {
            "keywords": ["blood", "donate", "donation", "transfusion"],
            "response": (
                "Blood Bank Services:\n"
                "• Location: Basement, Block C\n"
                "• Hours: 24/7 for emergencies, 9 AM - 5 PM for donations\n"
                "• Blood donation: Free health checkup included\n"
                "• All blood groups usually available\n"
                "• Contact: 081-9203456 for urgent blood requests"
            )
        },
        "vaccination": {
            "keywords": ["vaccine", "vaccination", "covid", "injection", "immunization"],
            "response": (
                "Vaccination Center:\n"
                "• Location: OPD Block, Room 105\n"
                "• Hours: 9:00 AM - 2:00 PM (Mon-Sat)\n"
                "• COVID-19 vaccines available\n"
                "• Childhood immunization (EPI schedule)\n"
                "• Travel vaccines (Hajj/Umrah, etc.)\n"
                "• Free for children under 5 years"
            )
        }
    }
    
    # Medical Disclaimer
    MEDICAL_DISCLAIMER = "\n\n⚠️ IMPORTANT: I cannot provide medical diagnosis or treatment advice. Please consult a qualified doctor at the hospital for any health concerns."