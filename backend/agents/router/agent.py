"""
Query router agent for classifying user intent and refining database queries.
"""
from typing import Optional, Dict, Any
from .prompts import ROUTER_SYSTEM_PROMPT, ROUTER_USER_PROMPT_TEMPLATE


class QueryRouterAgent:
    """Agent that classifies query route (general vs database) and refines queries."""
    
    def __init__(self, llm_client):
        """
        Initialize the query router agent.
        
        Args:
            llm_client: CatalystLLMClient instance for LLM inference
        """
        self.llm_client = llm_client
    
    def route_query(
        self,
        user_query: str,
        conversation_history: Optional[list[dict]] = None
    ) -> Dict[str, Any]:
        """
        Determine if query is general or database and refine it.
        
        Args:
            user_query: User's input query
            conversation_history: Optional list of previous conversation turns
            
        Returns:
            Dictionary with route, refined_query, explanation
        """
        # Build conversation context string
        context_str = ""
        if conversation_history:
            context_str = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in conversation_history[-5:]  # Last 5 messages
            ])
            
        user_prompt = ROUTER_USER_PROMPT_TEMPLATE.format(
            user_query=user_query,
            conversation_history=context_str if context_str else "No previous context."
        )
        
        try:
            response = self.llm_client.chat_completion_json(
                system_prompt=ROUTER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.1,  # Low temperature for classification and refinement
                max_tokens=512
            )
            
            # Ensure keys exist
            is_kannada = response.get("is_kannada", False)
            translated_query = response.get("translated_english_query", user_query).strip()
            route = response.get("route", "database").strip().lower()
            if route not in ["general", "database"]:
                route = "database"
                
            refined_query = response.get("refined_query", user_query).strip()
            explanation = response.get("explanation", "")
            
            return {
                "is_kannada": is_kannada,
                "translated_english_query": translated_query,
                "route": route,
                "refined_query": refined_query,
                "explanation": explanation
            }
        except Exception as e:
            print(f"[Warning] Routing agent failed: {e}. Defaulting to database route.")
            return {
                "is_kannada": False,
                "translated_english_query": user_query,
                "route": "database",
                "refined_query": user_query,
                "explanation": f"Routing failed due to error: {str(e)}"
            }
