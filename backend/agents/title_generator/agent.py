"""
Chat title generation agent.
"""
from typing import List, Dict
from services.llm_client import CatalystLLMClient
from .prompts import TITLE_SYSTEM_PROMPT, TITLE_USER_PROMPT_TEMPLATE


class TitleGenerator:
    """Agent for generating conversation titles using LLM."""
    
    def __init__(self, llm_client: CatalystLLMClient):
        self.llm_client = llm_client
    
    def generate_title(self, conversation_messages: List[Dict]) -> str:
        """
        Generate a title for the conversation based on the messages.
        
        Args:
            conversation_messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Generated title string
        """
        if not conversation_messages:
            return "New Conversation"
        
        # Format conversation for the prompt
        formatted_messages = []
        for msg in conversation_messages:
            role = msg.get('role', 'user').upper()
            content = msg.get('content', '')
            formatted_messages.append(f"{role}: {content}")
        
        conversation_text = "\n".join(formatted_messages)
        
        # Build user prompt
        user_prompt = TITLE_USER_PROMPT_TEMPLATE.format(
            conversation_messages=conversation_text
        )
        
        try:
            # Call LLM to generate title
            title = self.llm_client.chat_completion(
                system_prompt=TITLE_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.3,  # Lower temperature for more focused output
                max_tokens=50    # Short output for title
            )
            
            # Clean up the title
            title = title.strip()
            # Remove any quotes if present
            title = title.strip('"\'')
            
            return title if title else "Conversation"
            
        except Exception as e:
            print(f"[TitleGenerator] Error generating title: {e}")
            # Fallback to first user message truncated
            first_user_msg = next(
                (msg.get('content', '') for msg in conversation_messages if msg.get('role') == 'user'),
                ''
            )
            if first_user_msg:
                return first_user_msg[:50] + ('...' if len(first_user_msg) > 50 else '')
            return "Conversation"
