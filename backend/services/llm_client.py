"""
Catalyst Quick ML LLM client service for AI-powered query processing.
"""
import os
import json
from typing import Optional
from .token_manager import TokenManager


class CatalystLLMClient:
    """Client for interacting with Catalyst Quick ML LLM API for inference."""
    
    def __init__(self):
        """Initialize Catalyst LLM client with OAuth token manager."""
        # Catalyst Quick ML endpoint
        self.base_url = "https://api.catalyst.zoho.in/quickml/v1/project/46143000000022001/glm/chat"
        self.model = "crm-di-glm47b_30b_it"  # Default model from Catalyst
        self.org_id = os.getenv("CATALYST_ORG_ID", "60074849663")
        
        # Initialize OAuth token manager
        self.token_manager = TokenManager()
    
    def _get_headers(self) -> dict:
        """
        Get request headers with OAuth authorization.
        
        Returns:
            Headers dictionary with authorization
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"Zoho-oauthtoken {self.token_manager.get_access_token()}",
            "CATALYST-ORG": self.org_id
        }
    
    def chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Send a chat completion request to Catalyst Quick ML API.
        
        Args:
            system_prompt: System message defining the AI's role
            user_prompt: User message with the actual query
            json_mode: Whether to force JSON response format
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            
        Returns:
            The generated text response
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        }
        
        try:
            response = self.token_manager.make_authenticated_request(
                method="POST",
                url=self.base_url,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Catalyst LLM API request failed: {e}")
    
    def chat_completion_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> dict:
        """
        Send a chat completion request forcing JSON response.
        
        Args:
            system_prompt: System message defining the AI's role
            user_prompt: User message with the actual query
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Parsed JSON response as dictionary
        """
        response_text = self.chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response_text}")
