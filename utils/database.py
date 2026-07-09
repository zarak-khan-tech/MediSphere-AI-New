"""
MediSphere AI - Database Module
Built by Zarak Khan
Handles all SQLite database operations.
"""

import sqlite3
import json
import uuid
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

from config import Config
from utils.logger import logger


class Database:
    """
    Singleton database class for all hospital data operations.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.db_path = Config.DATABASE_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_database()
        self._initialized = True
        logger.info("Database initialized successfully")
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Create all tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Patients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    cnic TEXT UNIQUE NOT NULL,
                    phone TEXT UNIQUE NOT NULL,
                    age INTEGER NOT NULL,
                    gender TEXT NOT NULL,
                    address TEXT DEFAULT '',
                    city TEXT DEFAULT 'Quetta',
                    registered_at TEXT NOT NULL
                )
            """)
            # Create indexes for fast lookup
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cnic ON patients(cnic)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_phone ON patients(phone)")
            
            # Appointments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id TEXT PRIMARY KEY,
                    patient_id TEXT NOT NULL,
                    doctor_name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time_slot TEXT NOT NULL,
                    status TEXT DEFAULT 'scheduled',
                    token_number INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON appointments(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_apt ON appointments(patient_id)")
            
            # Reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id TEXT PRIMARY KEY,
                    patient_id TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    status TEXT DEFAULT 'ready',
                    generated_at TEXT NOT NULL,
                    results TEXT,
                    download_url TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_reports ON reports(patient_id)")
            
            # Queue table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS queue (
                    id TEXT PRIMARY KEY,
                    patient_id TEXT NOT NULL,
                    department TEXT NOT NULL,
                    doctor_name TEXT NOT NULL,
                    token_number INTEGER NOT NULL,
                    estimated_wait INTEGER DEFAULT 15,
                    status TEXT DEFAULT 'waiting',
                    issue_time TEXT NOT NULL,
                    counter INTEGER
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_queue_status ON queue(status)")
            
            # Sessions table (for conversation context)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT UNIQUE NOT NULL,
                    last_patient_id TEXT,
                    conversation_history TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    last_active TEXT NOT NULL
                )
            """)
            
            logger.info("All database tables created/verified")
    
    # ==================== PATIENT OPERATIONS ====================
    
    def add_patient(self, patient_data: Dict[str, Any]) -> bool:
        """Add a new patient to database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO patients (id, name, cnic, phone, age, gender, address, city, registered_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    patient_data['id'],
                    patient_data['name'],
                    patient_data['cnic'],
                    patient_data['phone'],
                    patient_data['age'],
                    patient_data['gender'],
                    patient_data.get('address', ''),
                    patient_data.get('city', 'Quetta'),
                    patient_data['registered_at']
                ))
                logger.info(f"Patient registered: {patient_data['id']}")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Duplicate patient: CNIC {patient_data.get('cnic')}")
            return False
        except Exception as e:
            logger.error(f"Failed to add patient: {e}")
            return False
    
    def get_patient_by_cnic(self, cnic: str) -> Optional[Dict]:
        """Find patient by CNIC (with or without dashes)."""
        cnic_clean = cnic.replace('-', '')
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients WHERE cnic = ?", (cnic_clean,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """Find patient by Patient ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_patient_by_phone(self, phone: str) -> Optional[Dict]:
        """Find patient by phone number."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients WHERE phone = ?", (phone,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_patients(self) -> List[Dict]:
        """Get all patients, newest first."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients ORDER BY registered_at DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== APPOINTMENT OPERATIONS ====================
    
    def add_appointment(self, apt_data: Dict[str, Any]) -> bool:
        """Add a new appointment."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO appointments (id, patient_id, doctor_name, department, date, time_slot, status, token_number, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    apt_data['id'],
                    apt_data['patient_id'],
                    apt_data['doctor_name'],
                    apt_data['department'],
                    apt_data['date'],
                    apt_data['time_slot'],
                    apt_data.get('status', 'scheduled'),
                    apt_data['token_number'],
                    apt_data.get('created_at', datetime.now().isoformat())
                ))
                logger.info(f"Appointment booked: {apt_data['id']}")
                return True
        except Exception as e:
            logger.error(f"Failed to add appointment: {e}")
            return False
    
    def get_appointments_by_date(self, date: str) -> List[Dict]:
        """Get all appointments for a specific date."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM appointments WHERE date = ?", (date,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_appointments_by_patient(self, patient_id: str) -> List[Dict]:
        """Get all appointments for a patient."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM appointments WHERE patient_id = ? ORDER BY date DESC, time_slot DESC",
                (patient_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_todays_appointments(self) -> List[Dict]:
        """Get today's appointments."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.get_appointments_by_date(today)
    
    def cancel_appointment(self, apt_id: str) -> bool:
        """Cancel an appointment."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE appointments SET status = 'cancelled' WHERE id = ?",
                    (apt_id,)
                )
                logger.info(f"Appointment cancelled: {apt_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to cancel appointment: {e}")
            return False
    
    # ==================== REPORT OPERATIONS ====================
    
    def add_report(self, report_data: Dict[str, Any]) -> bool:
        """Add a new lab report."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO reports (id, patient_id, report_type, status, generated_at, results, download_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    report_data['id'],
                    report_data['patient_id'],
                    report_data['report_type'],
                    report_data.get('status', 'ready'),
                    report_data['generated_at'],
                    report_data.get('results', ''),
                    report_data.get('download_url', '')
                ))
                logger.info(f"Report generated: {report_data['id']}")
                return True
        except Exception as e:
            logger.error(f"Failed to add report: {e}")
            return False
    
    def get_reports_by_patient(self, patient_id: str) -> List[Dict]:
        """Get all reports for a patient."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM reports WHERE patient_id = ? ORDER BY generated_at DESC",
                (patient_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== QUEUE OPERATIONS ====================
    
    def add_to_queue(self, queue_data: Dict[str, Any]) -> bool:
        """Add patient to queue."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO queue (id, patient_id, department, doctor_name, token_number, estimated_wait, status, issue_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    queue_data['id'],
                    queue_data['patient_id'],
                    queue_data['department'],
                    queue_data['doctor_name'],
                    queue_data['token_number'],
                    queue_data.get('estimated_wait', 15),
                    queue_data.get('status', 'waiting'),
                    queue_data.get('issue_time', datetime.now().isoformat())
                ))
                return True
        except Exception as e:
            logger.error(f"Failed to add to queue: {e}")
            return False
    
    def get_queue_by_department(self, department: str) -> List[Dict]:
        """Get queue for a department."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM queue WHERE department = ? AND status = 'waiting' ORDER BY issue_time",
                (department,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_queue(self) -> List[Dict]:
        """Get all active queue items."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM queue WHERE status = 'waiting' ORDER BY issue_time"
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== SESSION OPERATIONS ====================
    
    def get_or_create_session(self, user_id: str) -> Dict[str, Any]:
        """Get existing session or create new one."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                # Update last active
                cursor.execute(
                    "UPDATE sessions SET last_active = ? WHERE user_id = ?",
                    (datetime.now().isoformat(), user_id)
                )
                session = dict(row)
                session['conversation_history'] = json.loads(session.get('conversation_history', '[]'))
                return session
            
            # Create new session
            session_id = f"SES-{uuid.uuid4().hex[:8].upper()}"
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO sessions (id, user_id, conversation_history, created_at, last_active)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, user_id, '[]', now, now))
            
            return {
                'id': session_id,
                'user_id': user_id,
                'last_patient_id': None,
                'conversation_history': [],
                'created_at': now,
                'last_active': now
            }
    
    def update_session(self, user_id: str, last_patient_id: str = None, message: Dict = None):
        """Update session with new context."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if message:
                # Get current history
                cursor.execute(
                    "SELECT conversation_history FROM sessions WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                history = json.loads(row[0]) if row else []
                history.append(message)
                # Keep last 10 messages
                history = history[-10:]
                
                cursor.execute(
                    "UPDATE sessions SET conversation_history = ?, last_active = ? WHERE user_id = ?",
                    (json.dumps(history), datetime.now().isoformat(), user_id)
                )
            
            if last_patient_id:
                cursor.execute(
                    "UPDATE sessions SET last_patient_id = ? WHERE user_id = ?",
                    (last_patient_id, user_id)
                )
    
    # ==================== STATS ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM patients")
            total_patients = cursor.fetchone()[0]
            
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("SELECT COUNT(*) FROM appointments WHERE date = ?", (today,))
            today_appointments = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM reports WHERE status = 'ready'")
            pending_reports = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM queue WHERE status = 'waiting'")
            queue_count = cursor.fetchone()[0]
            
            return {
                'total_patients': total_patients,
                'today_appointments': today_appointments,
                'pending_reports': pending_reports,
                'queue_count': queue_count
            }


# Global database instance
db = Database()