"""
MediSphere AI - Patient Registration Agent
Built by Zarak Khan
Handles new patient registration and profile lookup.
"""

import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from utils.database import db
from utils.logger import logger


class PatientRegistrationAgent(BaseAgent):
    """
    Agent 1: Handles patient registration.
    Extracts info from natural language and validates Pakistani CNIC format.
    """
    
    def __init__(self):
        super().__init__(
            "PatientRegistrationAgent",
            "Handles new patient registration, profile updates, and patient lookup"
        )
    
    def _extract_info(self, message: str) -> Dict[str, Any]:
        """Extract patient info from natural language using regex."""
        info = {}
        msg_lower = message.lower()
        
        # Name extraction
        name_patterns = [
            r'name\s+(?:is\s+)?([A-Za-z]+(?:\s+[A-Za-z]+){0,2})',
            r'register\s+([A-Za-z]+(?:\s+[A-Za-z]+){0,2})',
            r'for\s+([A-Za-z]+(?:\s+[A-Za-z]+){0,2})(?:\s+(?:age|cnic|phone))'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, msg_lower)
            if match:
                name = match.group(1).strip().title()
                if name.lower() not in ['my', 'the', 'a', 'an', 'i', 'to', 'for']:
                    info['name'] = name
                    break
        
        # CNIC extraction (Pakistani format: 12345-1234567-8)
        cnic_match = re.search(r'\b(\d{5}-?\d{7}-?\d)\b', message)
        if cnic_match:
            info['cnic'] = cnic_match.group(1).replace('-', '')
        
        # Phone extraction
        phone_match = re.search(r'\b(03\d{9})\b', message)
        if phone_match:
            info['phone'] = phone_match.group(1)
        
        # Age extraction
        age_patterns = [
            r'age\s*[:=]?\s*(\d{1,3})',
            r'age\s+(\d{1,3})',
            r'(\d{1,3})\s*(?:years?|yrs?)',
            r'aged\s+(\d{1,3})'
        ]
        for pattern in age_patterns:
            age_match = re.search(pattern, msg_lower)
            if age_match:
                info['age'] = int(age_match.group(1))
                break
        
        # Gender extraction
        if 'male' in msg_lower or 'boy' in msg_lower or 'man' in msg_lower:
            info['gender'] = 'Male'
        elif 'female' in msg_lower or 'girl' in msg_lower or 'woman' in msg_lower:
            info['gender'] = 'Female'
        
        return info
    
    def _validate_cnic(self, cnic: str) -> bool:
        """Validate Pakistani CNIC format (13 digits)."""
        cnic_clean = cnic.replace('-', '')
        return len(cnic_clean) == 13 and cnic_clean.isdigit()
    
    def _validate_info(self, info: Dict) -> List[str]:
        """Check which required fields are missing."""
        required = ['name', 'cnic', 'phone', 'age', 'gender']
        return [f for f in required if f not in info]
    
    def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process registration request.
        
        Returns:
            {
                status: "registered" | "already_registered" | "incomplete" | "error",
                message: Human-readable response,
                patient_id: str (if registered),
                patient: dict (if found)
            }
        """
        self._log_action("Processing registration request")
        
        # Check if user wants to look up existing patient
        msg_lower = message.lower()
        if any(w in msg_lower for w in ['check', 'find', 'already registered', 'lookup']):
            cnic_match = re.search(r'\b(\d{5}-?\d{7}-?\d)\b', message)
            if cnic_match:
                cnic_clean = cnic_match.group(1).replace('-', '')
                patient = db.get_patient_by_cnic(cnic_clean)
                if patient:
                    return {
                        "status": "found",
                        "message": f"✅ Patient found!\n\nName: {patient['name']}\nPatient ID: {patient['id']}\nPhone: {patient['phone']}\nRegistered: {patient['registered_at'][:10]}",
                        "patient_id": patient['id'],
                        "patient": patient
                    }
                else:
                    return {
                        "status": "not_found",
                        "message": "❌ No patient found with this CNIC.\n\nWould you like to register as a new patient?"
                    }
        
        # Extract information from message
        info = self._extract_info(message)
        
        # Check for missing info
        missing = self._validate_info(info)
        if missing:
            return {
                "status": "incomplete",
                "message": f"⚠️ I need more information to complete registration.\n\nMissing: {', '.join(missing)}\n\nPlease provide your full name, CNIC (13 digits), phone number (03XXXXXXXXX), age, and gender.\n\nExample: 'Register Ali Khan, CNIC 12345-1234567-8, phone 03001234567, age 25, male'",
                "missing_fields": missing,
                "collected_so_far": info
            }
        
        # Validate CNIC format
        if not self._validate_cnic(info['cnic']):
            return {
                "status": "invalid_cnic",
                "message": "❌ Invalid CNIC format!\n\nPakistani CNIC must be exactly 13 digits.\nExample: 12345-1234567-8 or 1234512345678"
            }
        
        # Check if already registered
        cnic_clean = info['cnic'].replace('-', '')
        existing = db.get_patient_by_cnic(cnic_clean)
        if existing:
            return {
                "status": "already_registered",
                "message": f"⚠️ You are already registered!\n\nName: {existing['name']}\nPatient ID: {existing['id']}\nPhone: {existing['phone']}\n\nUse this Patient ID for appointments and reports.",
                "patient_id": existing['id'],
                "patient": existing
            }
        
        # Create new patient
        patient_id = f"PT-{uuid.uuid4().hex[:8].upper()}"
        patient_data = {
            "id": patient_id,
            "name": info['name'],
            "cnic": cnic_clean,
            "phone": info['phone'],
            "age": info['age'],
            "gender": info['gender'],
            "registered_at": datetime.now().isoformat()
        }
        
        if db.add_patient(patient_data):
            self._log_action("Patient registered", patient_id)
            return {
                "status": "registered",
                "message": (
                    f"✅ Registration Successful!\n\n"
                    f"🆔 Patient ID: {patient_id}\n"
                    f"👤 Name: {info['name']}\n"
                    f"🆔 CNIC: {cnic_clean}\n"
                    f"📱 Phone: {info['phone']}\n"
                    f"🎂 Age: {info['age']}\n"
                    f"⚧ Gender: {info['gender']}\n\n"
                    f"💾 Save your Patient ID! You'll need it for appointments and reports."
                ),
                "patient_id": patient_id
            }
        else:
            return {
                "status": "error",
                "message": "❌ Registration failed. This CNIC or phone number may already be registered."
            }