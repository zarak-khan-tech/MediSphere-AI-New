"""
MediSphere AI - FAQ Guidance Agent
Built by Zarak Khan
Provides hospital information and guidance. NO medical diagnosis.
"""

from typing import Dict, Any

from agents.base_agent import BaseAgent
from config import Config
from utils.llm_client import llm
from utils.logger import logger


class FAQGuidanceAgent(BaseAgent):
    """
    Agent 3: FAQ and hospital guidance.
    Uses Grok LLM for natural responses when available.
    Falls back to hardcoded knowledge base.
    """
    
    def __init__(self):
        super().__init__(
            "FAQGuidanceAgent",
            "Provides hospital information, guidance, and general FAQs. Does NOT provide medical diagnosis."
        )
        self.knowledge = Config.FAQ_KNOWLEDGE
        self.disclaimer = Config.MEDICAL_DISCLAIMER
    
    def _classify_query(self, message: str) -> str:
        """Classify the FAQ query using keywords."""
        msg_lower = message.lower()
        
        # Check for medical diagnosis attempts
        medical_terms = [
            'fever', 'headache', 'pain', 'symptom', 'disease', 'cure', 'treatment',
            'diagnosis', 'prescribe', 'medicine', 'what should i take', 'stomach',
            'chest pain', 'infection', 'rash', 'cough', 'flu', 'medicine for',
            'i feel sick', 'not feeling well', 'what disease', 'what medicine'
        ]
        if any(term in msg_lower for term in medical_terms):
            return "medical_refusal"
        
        # Check each FAQ category
        for category, data in self.knowledge.items():
            if any(kw in msg_lower for kw in data["keywords"]):
                return category
        
        return "general"
    
    def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process FAQ request.
        
        Returns:
            {
                status: "answered" | "medical_refusal" | "general_guidance",
                message: Human-readable response,
                category: str
            }
        """
        self._log_action("Processing FAQ")
        
        category = self._classify_query(message)
        
        # Medical diagnosis refusal
        if category == "medical_refusal":
            return {
                "status": "guidance_only",
                "message": (
                    "I understand you're not feeling well, but I cannot diagnose or recommend treatment.\n\n"
                    "I can help you with:\n"
                    "• Finding the right doctor and department\n"
                    "• Booking an appointment\n"
                    "• Hospital timings and locations\n\n"
                    "For emergencies, call 1122 or visit our Emergency Department immediately."
                ),
                "suggested_action": "book_appointment",
                "category": "medical_refusal"
            }
        
        # Try Grok LLM for natural response
        if Config.USE_LLM and category in self.knowledge:
            hospital_context = self.knowledge[category]["response"]
            llm_response = llm.generate_faq_response(message, hospital_context)
            if llm_response:
                return {
                    "status": "answered",
                    "message": llm_response + self.disclaimer,
                    "category": category
                }
        
        # Fallback to hardcoded response
        if category in self.knowledge:
            return {
                "status": "answered",
                "message": self.knowledge[category]["response"] + self.disclaimer,
                "category": category
            }
        
        # General guidance
        return {
            "status": "general_guidance",
            "message": (
                "I can help you with:\n"
                "• Hospital timings & locations\n"
                "• Available departments & doctors\n"
                "• Fees & payment methods\n"
                "• Required documents\n"
                "• Emergency services\n"
                "• Insurance & Sehat Card\n"
                "• Pharmacy & visiting hours\n\n"
                "What would you like to know?"
            ) + self.disclaimer,
            "category": "general"
        }