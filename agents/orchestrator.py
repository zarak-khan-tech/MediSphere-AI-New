"""
MediSphere AI - Master Orchestrator
Built by Zarak Khan
Routes user messages to the correct sub-agent using intent classification.
"""

import re
from typing import Dict, Any

from agents.registration_agent import PatientRegistrationAgent
from agents.appointment_agent import AppointmentBookingAgent
from agents.faq_agent import FAQGuidanceAgent
from agents.report_agent import ReportQueueAgent
from utils.llm_client import llm
from utils.database import db
from utils.logger import logger


class MasterOrchestrator:
    """
    The brain of the system. Decides which agent handles each message.
    Uses Grok LLM for intent classification when available, falls back to regex.
    """
    
    def __init__(self):
        self.reg_agent = PatientRegistrationAgent()
        self.apt_agent = AppointmentBookingAgent()
        self.faq_agent = FAQGuidanceAgent()
        self.report_agent = ReportQueueAgent()
        logger.info("Master Orchestrator initialized")
    
    def _classify_intent_regex(self, message: str) -> str:
        """
        Fast regex-based intent classification.
        Used as primary method or fallback when LLM is unavailable.
        """
        msg_lower = message.lower()
        
        # Priority 1: Report/Queue keywords (check BEFORE cnic)
        report_keywords = [
            "report", "lab", "test result", "blood test", "x-ray", "xray",
            "token", "queue", "waiting", "my turn", "my appointments",
            "cancel", "urine", "check my report"
        ]
        if any(kw in msg_lower for kw in report_keywords):
            return "report"
        
        # Priority 2: Appointment keywords
        appointment_keywords = [
            "appointment", "book", "schedule", "doctor", "consultation",
            "see a doctor", "visit doctor", "token for", "available",
            "slots", "dr.", "dr "
        ]
        if any(kw in msg_lower for kw in appointment_keywords):
            return "appointment"
        
        # Priority 3: Registration keywords
        registration_keywords = [
            "register", "new patient", "sign up", "my name is", "admission",
            "i am", "cnic"  # cnic alone might be registration
        ]
        if any(kw in msg_lower for kw in registration_keywords):
            # But check if it's actually a report query with cnic
            if "report" not in msg_lower and "token" not in msg_lower:
                return "registration"
        
        # Default: FAQ
        return "faq"
    
    def _classify_intent_llm(self, message: str) -> str:
        """Use Grok LLM for intent classification."""
        result = llm.classify_intent(message)
        return result if result else self._classify_intent_regex(message)
    
    def process(self, message: str, user_id: str = "anonymous") -> Dict[str, Any]:
        """
        Main entry point. Routes message to correct agent.
        
        Args:
            message: User's message
            user_id: Unique user identifier
            
        Returns:
            {
                intent: str,
                agent: str,
                response: dict
            }
        """
        logger.info(f"Processing message from {user_id}: {message[:50]}...")
        
        # Get or create session
        session = db.get_or_create_session(user_id)
        
        # Classify intent (LLM first, then regex fallback)
        if llm.available:
            intent = self._classify_intent_llm(message)
            logger.info(f"Intent classified by LLM: {intent}")
        else:
            intent = self._classify_intent_regex(message)
            logger.info(f"Intent classified by regex: {intent}")
        
        # Build context with session data
        context = {
            "user_id": user_id,
            "session": session
        }
        
        # Route to appropriate agent
        if intent == "registration":
            response = self.reg_agent.process(message, context)
        elif intent == "appointment":
            response = self.apt_agent.process(message, context)
        elif intent == "report":
            response = self.report_agent.process(message, context)
        else:
            response = self.faq_agent.process(message, context)
        
        # Update session if patient was registered or found
        if response.get("patient_id"):
            db.update_session(user_id, last_patient_id=response["patient_id"])
        
        # Log conversation
        db.update_session(user_id, message={
            "role": "user",
            "content": message,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        db.update_session(user_id, message={
            "role": "assistant",
            "content": response.get("message", "")[:100],
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        
        # Map intent to agent name
        agent_names = {
            "registration": "PatientRegistrationAgent",
            "appointment": "AppointmentBookingAgent",
            "report": "ReportQueueAgent",
            "faq": "FAQGuidanceAgent"
        }
        
        return {
            "intent": intent,
            "agent": agent_names.get(intent, "MasterOrchestrator"),
            "response": response
        }


# Global orchestrator instance
orchestrator = MasterOrchestrator()