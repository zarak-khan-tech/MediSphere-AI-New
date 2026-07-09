"""
MediSphere AI - Appointment Booking Agent
Built by Zarak Khan
Handles doctor appointments with real slot availability checking.
"""

import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from utils.database import db
from config import Config
from utils.logger import logger


class AppointmentBookingAgent(BaseAgent):
    """
    Agent 2: Handles doctor appointments and scheduling.
    Checks real availability from database before booking.
    """
    
    def __init__(self):
        super().__init__(
            "AppointmentBookingAgent",
            "Books appointments with doctors across Quetta hospitals"
        )
        self.doctors = Config.DOCTORS
    
    def _extract_info(self, message: str) -> Dict[str, Any]:
        """Extract appointment info from message."""
        info = {}
        msg_lower = message.lower()
        
        # Doctor name
        for doctor in self.doctors:
            if doctor.lower() in msg_lower:
                info['doctor'] = doctor
                break
        
        # Department
        depts = ["cardiology", "pediatrics", "orthopedics", "general medicine", "ent", "gynecology"]
        for dept in depts:
            if dept in msg_lower:
                info['department'] = dept.title()
                break
        
        # Date
        date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', message)
        if date_match:
            d, m, y = date_match.groups()
            year = f"20{y}" if len(y) == 2 else y
            info['date'] = f"{year}-{m.zfill(2)}-{d.zfill(2)}"
        else:
            if 'tomorrow' in msg_lower:
                info['date'] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            elif 'today' in msg_lower:
                info['date'] = datetime.now().strftime("%Y-%m-%d")
        
        # Time preference
        time_match = re.search(r'(\d{1,2}):(\d{2})', message)
        if time_match:
            h, m = time_match.groups()
            info['preferred_time'] = f"{int(h):02d}:{m}"
        
        # Patient identification
        cnic_match = re.search(r'\b(\d{5}-?\d{7}-?\d)\b', message)
        if cnic_match:
            info['cnic'] = cnic_match.group(1).replace('-', '')
        
        pt_match = re.search(r'(PT-[A-Z0-9]{8})', message, re.IGNORECASE)
        if pt_match:
            info['patient_id'] = pt_match.group(1).upper()
        
        return info
    
    def _get_available_slots(self, doctor: str, date: str) -> List[str]:
        """Get available slots for a doctor on a specific date from database."""
        if doctor not in self.doctors:
            return []
        
        all_slots = self.doctors[doctor]["slots"]
        booked = db.get_appointments_by_date(date)
        booked_slots = [
            a["time_slot"] for a in booked 
            if a["doctor_name"] == doctor and a["status"] == "scheduled"
        ]
        return [s for s in all_slots if s not in booked_slots]
    
    def _check_availability(self, doctor_name: str, date: str) -> Dict[str, Any]:
        """Check if doctor has available slots."""
        if doctor_name not in self.doctors:
            all_docs = "\n".join([f"• {d}" for d in self.doctors.keys()])
            return {
                "available": False,
                "slots": [],
                "message": f"Doctor '{doctor_name}' not found.\n\nAvailable doctors:\n{all_docs}"
            }
        
        available = self._get_available_slots(doctor_name, date)
        doctor_info = self.doctors[doctor_name]
        
        if not available:
            return {
                "available": False,
                "slots": [],
                "message": (
                    f"Dr. {doctor_name} is FULLY BOOKED on {date}!\n\n"
                    f"Department: {doctor_info['department']}\n"
                    f"All slots taken: {', '.join(doctor_info['slots'])}\n\n"
                    f"Try another date or doctor."
                )
            }
        
        return {
            "available": True,
            "slots": available,
            "message": (
                f"Dr. {doctor_name} is AVAILABLE on {date}\n"
                f"Department: {doctor_info['department']}\n"
                f"Fee: Rs. {doctor_info['fee']}\n"
                f"Open slots: {', '.join(available)}"
            )
        }
    
    def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process appointment request.
        
        Returns:
            {
                status: "booked" | "no_slots" | "need_registration" | "need_doctor" | "availability",
                message: Human-readable response,
                appointment: dict (if booked)
            }
        """
        self._log_action("Processing appointment request")
        
        info = self._extract_info(message)
        msg_lower = message.lower()
        
        # Find patient
        patient = None
        session = context.get('session', {}) if context else {}
        
        if 'cnic' in info:
            patient = db.get_patient_by_cnic(info['cnic'])
        elif 'patient_id' in info:
            patient = db.get_patient_by_id(info['patient_id'])
        elif session.get('last_patient_id'):
            patient = db.get_patient_by_id(session['last_patient_id'])
        
        if not patient:
            return {
                "status": "need_registration",
                "message": "Please register first or provide your CNIC.\n\nType: 'register my name is [name], cnic [number], phone [number], age [number], [gender]'"
            }
        
        # Check if user is asking about availability only
        if any(w in msg_lower for w in ['available', 'free', 'slots', 'timing', 'schedule']):
            doctor_name = info.get('doctor')
            if not doctor_name:
                # List all doctors with availability
                date = info.get('date', datetime.now().strftime("%Y-%m-%d"))
                docs_status = []
                for doc, doc_info in self.doctors.items():
                    avail = self._get_available_slots(doc, date)
                    status = f"{len(avail)} slots free" if avail else "Fully booked"
                    docs_status.append(f"• {doc} ({doc_info['department']}) - {status}")
                
                return {
                    "status": "availability",
                    "message": f"Doctor Availability for {date}:\n\n" + "\n".join(docs_status)
                }
            
            date = info.get('date', datetime.now().strftime("%Y-%m-%d"))
            return self._check_availability(doctor_name, date)
        
        # Find doctor for booking
        doctor_name = info.get('doctor')
        if not doctor_name and info.get('department'):
            for doc_name, doc_info in self.doctors.items():
                if doc_info['department'].lower() == info['department'].lower():
                    doctor_name = doc_name
                    break
        
        if not doctor_name:
            docs_list = "\n".join([
                f"• {d} ({info['department']}) - Rs. {info['fee']} - Slots: {', '.join(info['slots'])}"
                for d, info in self.doctors.items()
            ])
            return {
                "status": "need_doctor",
                "message": f"Which doctor would you like?\n\nAvailable Doctors:\n{docs_list}\n\nType: 'Book appointment with Dr. [Name]'",
                "patient_id": patient['id']
            }
        
        # Default to today if no date
        date = info.get('date', datetime.now().strftime("%Y-%m-%d"))
        
        # Check availability
        availability = self._check_availability(doctor_name, date)
        if not availability["available"]:
            return {
                "status": "no_slots",
                "message": availability["message"]
            }
        
        # Select slot
        available_slots = availability["slots"]
        if 'preferred_time' in info and info['preferred_time'] in available_slots:
            selected_slot = info['preferred_time']
        else:
            selected_slot = available_slots[0]
        
        # Generate token
        today_apts = db.get_appointments_by_date(date)
        token_num = len([a for a in today_apts if a["doctor_name"] == doctor_name]) + 1
        
        # Create appointment
        apt_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
        apt_data = {
            "id": apt_id,
            "patient_id": patient['id'],
            "doctor_name": doctor_name,
            "department": self.doctors[doctor_name]['department'],
            "date": date,
            "time_slot": selected_slot,
            "status": "scheduled",
            "token_number": token_num
        }
        
        if db.add_appointment(apt_data):
            # Add to queue
            queue_data = {
                "id": f"Q-{uuid.uuid4().hex[:6].upper()}",
                "patient_id": patient['id'],
                "department": self.doctors[doctor_name]['department'],
                "doctor_name": doctor_name,
                "token_number": token_num,
                "estimated_wait": token_num * 15
            }
            db.add_to_queue(queue_data)
            
            self._log_action("Appointment booked", apt_id)
            return {
                "status": "booked",
                "message": (
                    f"Appointment Confirmed!\n\n"
                    f"ID: {apt_id}\n"
                    f"Patient: {patient['name']}\n"
                    f"Doctor: {doctor_name}\n"
                    f"Department: {self.doctors[doctor_name]['department']}\n"
                    f"Date: {date}\n"
                    f"Time: {selected_slot}\n"
                    f"Token: {token_num}\n"
                    f"Fee: Rs. {self.doctors[doctor_name]['fee']}\n\n"
                    f"Please arrive 15 minutes early with your CNIC!"
                ),
                "appointment": apt_data,
                "patient_id": patient['id']
            }
        else:
            return {
                "status": "error",
                "message": "Failed to book appointment. Please try again."
            }