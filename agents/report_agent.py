"""
MediSphere AI - Report & Queue Agent
Built by Zarak Khan
Handles lab reports, tokens, and queue management.
Generates dynamic, personalized reports.
"""

import re
import uuid
import random
from datetime import datetime
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from utils.database import db
from utils.logger import logger


class ReportQueueAgent(BaseAgent):
    """
    Agent 4: Manages lab reports, token status, and queue information.
    Generates different reports based on patient demographics.
    """
    
    def __init__(self):
        super().__init__(
            "ReportQueueAgent",
            "Manages lab report retrieval, token status, and queue information"
        )
    
    def _extract_ids(self, message: str) -> Dict[str, str]:
        """Extract IDs from message."""
        info = {}
        
        cnic_match = re.search(r'\b(\d{5}-?\d{7}-?\d)\b', message)
        if cnic_match:
            info['cnic'] = cnic_match.group(1).replace('-', '')
        
        pt_match = re.search(r'(PT-[A-Z0-9]{8})', message, re.IGNORECASE)
        if pt_match:
            info['patient_id'] = pt_match.group(1).upper()
        
        apt_match = re.search(r'(APT-[A-Z0-9]{8})', message, re.IGNORECASE)
        if apt_match:
            info['appointment_id'] = apt_match.group(1).upper()
        
        return info
    
    def _generate_report(self, patient: Dict, report_type: str = "blood_test") -> Dict[str, Any]:
        """
        Generate dynamic report based on patient age and gender.
        Different results for different patients!
        """
        age = patient.get("age", 30)
        gender = patient.get("gender", "Male")
        report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
        
        if report_type == "x_ray":
            findings = random.choice([
                "Normal chest X-ray. No active lung pathology.",
                "Mild congestion noted. Clinical correlation advised.",
                "Clear lung fields. Cardiac silhouette normal.",
                "Small calcified granuloma in right upper zone. Benign finding."
            ])
            return {
                "id": report_id,
                "type": "x_ray",
                "summary": f"Finding: {findings}\n\nImpression: {'Normal study' if 'Normal' in findings else 'Review needed'}",
                "download_url": f"https://hospital.quetta.pk/reports/{report_id}"
            }
        
        elif report_type == "urine":
            return {
                "id": report_id,
                "type": "urine",
                "summary": (
                    f"Color: {random.choice(['Yellow', 'Pale Yellow', 'Straw'])}\n"
                    f"pH: {round(random.uniform(5.0, 8.0), 1)}\n"
                    f"Glucose: Negative ✅\n"
                    f"Protein: {random.choice(['Negative', 'Trace'])}\n"
                    f"Ketones: Negative ✅"
                ),
                "download_url": f"https://hospital.quetta.pk/reports/{report_id}"
            }
        
        else:  # blood_test (default)
            # Different normal ranges based on gender
            if gender == "Female":
                hemoglobin = round(random.uniform(11.5, 15.5), 1)
            else:
                hemoglobin = round(random.uniform(13.0, 17.0), 1)
            
            # Age affects some values
            if age > 50:
                wbc = random.randint(4000, 10000)
                platelets = random.randint(140000, 350000)
            else:
                wbc = random.randint(4500, 11000)
                platelets = random.randint(150000, 400000)
            
            blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
            blood_group = random.choice(blood_groups)
            
            # Status indicator
            hb_status = "✅ Normal" if 12 <= hemoglobin <= 16 else "⚠️ Check with doctor"
            
            return {
                "id": report_id,
                "type": "blood_test",
                "summary": (
                    f"Blood Group: {blood_group}\n"
                    f"Hemoglobin: {hemoglobin} g/dL {hb_status}\n"
                    f"WBC Count: {wbc:,} /μL\n"
                    f"Platelets: {platelets:,} /μL\n"
                    f"RBC Count: {round(random.uniform(4.0, 6.0), 2)} million/μL"
                ),
                "download_url": f"https://hospital.quetta.pk/reports/{report_id}"
            }
    
    def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process report/queue request.
        
        Returns:
            {
                status: "report_ready" | "queue_status" | "need_id" | etc,
                message: Human-readable response,
                report: dict (if report generated)
            }
        """
        self._log_action("Processing report/queue request")
        
        msg_lower = message.lower()
        info = self._extract_ids(message)
        session = context.get('session', {}) if context else {}
        
        # Find patient
        patient = None
        if 'cnic' in info:
            patient = db.get_patient_by_cnic(info['cnic'])
        elif 'patient_id' in info:
            patient = db.get_patient_by_id(info['patient_id'])
        elif session.get('last_patient_id'):
            patient = db.get_patient_by_id(session['last_patient_id'])
        
        # REPORT QUERY
        if any(w in msg_lower for w in ["report", "lab", "test result", "blood test", "x-ray", "xray", "urine"]):
            if not patient:
                return {
                    "status": "need_id",
                    "message": "⚠️ Please provide your CNIC or Patient ID.\n\nExample: 'check my report for cnic 12345-1234567-8'"
                }
            
            # Determine report type
            report_type = "blood_test"
            if "x-ray" in msg_lower or "xray" in msg_lower or "chest" in msg_lower:
                report_type = "x_ray"
            elif "urine" in msg_lower:
                report_type = "urine"
            
            # Generate dynamic report
            report = self._generate_report(patient, report_type)
            
            # Save to database
            db.add_report({
                "id": report["id"],
                "patient_id": patient["id"],
                "report_type": report_type,
                "status": "ready",
                "generated_at": datetime.now().isoformat(),
                "results": report["summary"],
                "download_url": report["download_url"]
            })
            
            return {
                "status": "report_ready",
                "message": (
                    f"📄 Your {report_type.replace('_', ' ').title()} Report is Ready!\n\n"
                    f"Report ID: {report['id']}\n"
                    f"Patient: {patient['name']} (Age: {patient['age']}, {patient['gender']})\n"
                    f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
                    f"Results:\n{report['summary']}\n\n"
                    f"📥 Download: {report['download_url']}"
                ),
                "report": report
            }
        
        # TOKEN / QUEUE STATUS
        if any(w in msg_lower for w in ["token", "queue", "waiting", "turn", "my number"]):
            if not patient:
                return {
                    "status": "need_id",
                    "message": "⚠️ Please provide your CNIC or Patient ID to check queue status."
                }
            
            appointments = db.get_appointments_by_patient(patient["id"])
            active_apts = [a for a in appointments if a["status"] == "scheduled"]
            
            if not active_apts:
                return {
                    "status": "no_appointments",
                    "message": "📋 No active appointments found.\n\nType 'book appointment' to schedule one."
                }
            
            latest = active_apts[0]
            queue = db.get_queue_by_department(latest["department"])
            position = sum(1 for q in queue if q["token_number"] < latest["token_number"])
            
            return {
                "status": "queue_status",
                "message": (
                    f"🎫 Queue Status for {patient['name']}\n\n"
                    f"Token: {latest['token_number']}\n"
                    f"Department: {latest['department']}\n"
                    f"Doctor: {latest['doctor_name']}\n"
                    f"Time: {latest['time_slot']}\n"
                    f"Position: {position} patient(s) ahead\n"
                    f"Wait: ~{position * 15} minutes\n\n"
                    f"Please wait in the {latest['department']} area."
                ),
                "queue_info": {
                    "token": latest["token_number"],
                    "position": position,
                    "wait_time": position * 15
                }
            }
        
        # MY APPOINTMENTS
        if any(w in msg_lower for w in ["my appointments", "my bookings", "check appointment"]):
            if not patient:
                return {
                    "status": "need_id",
                    "message": "⚠️ Please provide your CNIC or Patient ID."
                }
            
            appointments = db.get_appointments_by_patient(patient["id"])
            if not appointments:
                return {
                    "status": "no_appointments",
                    "message": "📋 No appointments found.\n\nType 'book appointment' to schedule one."
                }
            
            apt_list = "\n".join([
                f"• {a['id']} | {a['doctor_name']} | {a['date']} {a['time_slot']} | {a['status']}"
                for a in appointments[:5]
            ])
            
            return {
                "status": "appointments_list",
                "message": f"📋 Your Appointments:\n\n{apt_list}"
            }
        
        # CANCEL APPOINTMENT
        if any(w in msg_lower for w in ["cancel", "remove appointment"]):
            if 'appointment_id' in info:
                if db.cancel_appointment(info['appointment_id']):
                    return {
                        "status": "cancelled",
                        "message": f"✅ Appointment {info['appointment_id']} has been cancelled."
                    }
                else:
                    return {
                        "status": "cancel_failed",
                        "message": "❌ Could not find that appointment ID. Please check and try again."
                    }
            
            return {
                "status": "need_details",
                "message": "Please provide your Appointment ID (APT-XXXX) to cancel."
            }
        
        # Default
        return {
            "status": "clarify",
            "message": (
                "🔬 I can help you with:\n"
                "• Check lab reports (blood, x-ray, urine)\n"
                "• Check token/queue status\n"
                "• View your appointments\n"
                "• Cancel appointments\n\n"
                "What would you like to do?"
            )
        }