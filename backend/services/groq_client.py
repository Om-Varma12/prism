"""
Groq LLM client service for AI-powered query processing.
"""
import os
from typing import Optional
from groq import Groq


class GroqClient:
    """Client for interacting with Groq API for LLM inference."""
    
    def __init__(self):
        """Initialize Groq client with API key from environment."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.client = Groq(api_key=api_key)
        self.model = "llama3-70b-70b-versatile"  # Default model
    
    def chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Send a chat completion request to Groq API.
        
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
        
        response_format = {"type": "json_object"} if json_mode else None
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format=response_format,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            # Retry once on rate limit or temporary errors
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format=response_format,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            except Exception as retry_error:
                raise RuntimeError(f"Groq API request failed: {retry_error}")
    
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
        import json
        
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
