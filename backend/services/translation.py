"""
Translation service for translating between English and Kannada using QuickML LLM.
"""
from typing import Dict, Any
from services.llm_client import CatalystLLMClient


class TranslationService:
    """Service to handle translation between English and Kannada."""
    
    def __init__(self, llm_client: CatalystLLMClient = None):
        """Initialize the translation service."""
        self.llm_client = llm_client or CatalystLLMClient()
        
    def translate_to_kannada(self, text: str) -> str:
        """
        Translate English text to natural, grammatically correct Kannada (in Kannada script).
        
        Args:
            text: English text to translate
            
        Returns:
            Translated Kannada text
        """
        if not text or not text.strip():
            return text
            
        system_prompt = (
            "You are a professional translator. Translate the given English text into natural, "
            "grammatically correct Kannada (in Kannada script). Return ONLY the translated Kannada text. "
            "Do not add any explanations, notes, or extra characters."
        )
        
        user_prompt = f"English text:\n{text}\n\nKannada translation:"
        
        try:
            translated = self.llm_client.chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=2048
            )
            return translated.strip()
        except Exception as e:
            print(f"[Warning] Translation to Kannada failed: {e}")
            return text
            
    def translate_to_english(self, text: str) -> str:
        """
        Translate Kannada text (Kannada script or transliterated Kannada) to English.
        
        Args:
            text: Kannada text to translate
            
        Returns:
            Translated English text
        """
        if not text or not text.strip():
            return text
            
        system_prompt = (
            "You are a professional translator. Translate the given Kannada input (which may be in "
            "Kannada script or transliterated Kannada / Manglish) into plain, refined English with its "
            "proper meaning. Return ONLY the translated English text. Do not add any explanations, "
            "notes, or extra characters."
        )
        
        user_prompt = f"Kannada input:\n{text}\n\nEnglish translation:"
        
        try:
            translated = self.llm_client.chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=2048
            )
            return translated.strip()
        except Exception as e:
            print(f"[Warning] Translation to English failed: {e}")
            return text
