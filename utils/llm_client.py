"""
MediSphere AI - LLM Client
Built by Zarak Khan
Handles all communication with Grok API (xAI).
"""

import json
import requests
from typing import Dict, Optional, Any

from config import Config
from utils.logger import logger


class LLMClient:
    """
    Client for Grok API (xAI) with fallback to regex mode.
    """
    
    def __init__(self):
        self.api_key = Config.GROK_API_KEY
        self.api_url = Config.GROK_API_URL
        self.model = Config.GROK_MODEL
        self.available = Config.USE_LLM
        
        if self.available:
            logger.info(f"Grok LLM client initialized (model: {self.model})")
        else:
            logger.warning("Grok API key not found. Running in regex-only fallback mode.")
    
    def _call_api(self, messages: list, temperature: float = 0.1) -> Optional[str]:
        """
        Send request to Grok API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: 0.0 = strict, 1.0 = creative
            
        Returns:
            LLM response text or None if failed
        """
        if not self.available:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            logger.info("Grok API call successful")
            return content.strip()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Grok API request failed: {e}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"Grok API response parsing failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected LLM error: {e}")
            return None
    
    def classify_intent(self, message: str) -> Optional[str]:
        """
        Use Grok to classify user intent.
        
        Returns: 'registration', 'appointment', 'report', 'faq', or None
        """
        system_prompt = """You are an intent classifier for a hospital AI system.
Classify the user's message into EXACTLY ONE category:
- registration: User wants to register, sign up, create profile, or give personal info
- appointment: User wants to book, schedule, see a doctor, or check availability
- report: User wants to check lab results, blood test, x-ray, or medical report
- faq: User is asking about hospital info, timings, fees, location, departments

Reply with ONLY the category name, nothing else. One word only."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Classify: '{message}'"}
        ]
        
        result = self._call_api(messages, temperature=0.0)
        
        if result:
            result_lower = result.lower().strip()
            if "registration" in result_lower:
                return "registration"
            elif "appointment" in result_lower:
                return "appointment"
            elif "report" in result_lower:
                return "report"
            elif "faq" in result_lower:
                return "faq"
        
        return None
    
    def generate_faq_response(self, message: str, hospital_context: str) -> Optional[str]:
        """
        Use Grok to generate natural FAQ response.
        
        Args:
            message: User's question
            hospital_context: Hospital facts to ground the answer
            
        Returns:
            Natural language response or None
        """
        system_prompt = f"""You are a friendly, professional hospital receptionist for {Config.HOSPITAL_NAME}.
Use ONLY the following facts to answer. Be concise (2-3 sentences max).
If you don't know, say "Please contact the hospital directly."

FACTS:
{hospital_context}

RULES:
- Never give medical diagnosis or treatment advice
- Be warm and professional
- Use bullet points for lists
- Keep answers short and clear"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        return self._call_api(messages, temperature=0.3)
    
    def extract_entities(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Use Grok to extract structured info from message.
        
        Returns dict with name, cnic, phone, age, gender, doctor, date, etc.
        """
        system_prompt = """Extract patient information from the message.
Return ONLY a valid JSON object with these keys (use null if not found):
{
  "name": "patient's full name or null",
  "cnic": "13-digit Pakistani CNIC or null",
  "phone": "11-digit phone starting with 03 or null",
  "age": number or null,
  "gender": "Male" or "Female" or null,
  "doctor": "doctor name if mentioned or null",
  "department": "medical department if mentioned or null",
  "date": "YYYY-MM-DD if mentioned or null",
  "report_type": "blood_test, x_ray, urine, or null"
}

Return ONLY the JSON, no explanation."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Extract from: '{message}'"}
        ]
        
        result = self._call_api(messages, temperature=0.0)
        
        if result:
            try:
                # Find JSON in response
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    return json.loads(result[json_start:json_end])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse LLM JSON: {result}")
        
        return None


# Global LLM client instance
llm = LLMClient()