"""
General chat agent for conversational queries and elaborations.
"""
from typing import Optional, Dict, Any
from .prompts import GENERAL_CHAT_SYSTEM_PROMPT, GENERAL_CHAT_USER_PROMPT_TEMPLATE


class GeneralChatAgent:
    """Agent that handles general conversational queries and elaborations based on history."""
    
    def __init__(self, llm_client):
        """
        Initialize the general chat agent.
        
        Args:
            llm_client: CatalystLLMClient instance for LLM inference
        """
        self.llm_client = llm_client
        
    def generate_response(
        self,
        user_query: str,
        conversation_history: Optional[list[dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate a conversational response based on history.
        
        Args:
            user_query: User's input query
            conversation_history: Optional list of previous conversation turns
            
        Returns:
            Dictionary with response_text, follow_ups
        """
        # Build conversation context string
        context_str = ""
        if conversation_history:
            context_str = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in conversation_history[-10:]  # Last 10 messages for more context
            ])
            
        user_prompt = GENERAL_CHAT_USER_PROMPT_TEMPLATE.format(
            user_query=user_query,
            conversation_history=context_str if context_str else "No previous context."
        )
        
        try:
            response = self.llm_client.chat_completion_json(
                system_prompt=GENERAL_CHAT_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.5,
                max_tokens=1024
            )
            
            response_text = response.get("response_text", "Hello! How can I assist you with the PRISM database today?")
            follow_ups = response.get("follow_ups", ["Show active cases", "Search by crime head", "Analyze district trends"])
            
            return {
                "response_text": response_text,
                "follow_ups": follow_ups
            }
        except Exception as e:
            print(f"[Warning] General chat agent failed: {e}")
            return {
                "response_text": f"I'm here to help, but I encountered an issue generating a response: {str(e)}",
                "follow_ups": ["Show active cases", "Search by crime head"]
            }
