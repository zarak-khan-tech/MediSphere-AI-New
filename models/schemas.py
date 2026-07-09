"""
MediSphere AI - Data Models
Built by Zarak Khan
Simple data structures for Patient, Appointment, Report, QueueTicket.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Patient:
    """Patient data model."""
    id: str
    name: str
    cnic: str
    phone: str
    age: int
    gender: str
    address: str = ""
    city: str = "Quetta"
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "cnic": self.cnic,
            "phone": self.phone,
            "age": self.age,
            "gender": self.gender,
            "address": self.address,
            "city": self.city,
            "registered_at": self.registered_at
        }


@dataclass
class Appointment:
    """Appointment data model."""
    id: str
    patient_id: str
    doctor_name: str
    department: str
    date: str
    time_slot: str
    status: str = "scheduled"
    token_number: int = 1
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "doctor_name": self.doctor_name,
            "department": self.department,
            "date": self.date,
            "time_slot": self.time_slot,
            "status": self.status,
            "token_number": self.token_number,
            "created_at": self.created_at
        }


@dataclass
class Report:
    """Lab report data model."""
    id: str
    patient_id: str
    report_type: str
    status: str = "ready"
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    results: str = ""
    download_url: str = ""
    
    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "report_type": self.report_type,
            "status": self.status,
            "generated_at": self.generated_at,
            "results": self.results,
            "download_url": self.download_url
        }


@dataclass
class QueueTicket:
    """Queue ticket data model."""
    id: str
    patient_id: str
    department: str
    doctor_name: str
    token_number: int
    estimated_wait: int = 15
    status: str = "waiting"
    issue_time: str = field(default_factory=lambda: datetime.now().isoformat())
    counter: Optional[int] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "department": self.department,
            "doctor_name": self.doctor_name,
            "token_number": self.token_number,
            "estimated_wait": self.estimated_wait,
            "status": self.status,
            "issue_time": self.issue_time,
            "counter": self.counter
        }