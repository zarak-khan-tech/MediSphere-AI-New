"""
MediSphere AI - Base Agent
Built by Zarak Khan
All agents inherit from this base class.
"""

from typing import Dict, Any
from utils.logger import logger


class BaseAgent:
    """
    Base class for all hospital agents.
    Every agent must implement the process() method.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        logger.info(f"Agent initialized: {name}")
    
    def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        Args:
            message: The user's message
            context: Optional context (session, patient info, etc.)
            
        Returns:
            Dict with status, message, and any additional data
        """
        raise NotImplementedError("Each agent must implement process()")
    
    def _log_action(self, action: str, details: str = ""):
        """Log what the agent is doing."""
        logger.info(f"[{self.name}] {action} {details}")