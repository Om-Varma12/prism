"""
Text-to-SQL agent for converting natural language to ZCQL queries.
"""
from typing import Optional, Dict, Any
from .schema_context import SCHEMA_CONTEXT
from .prompts import SQL_SYSTEM_PROMPT, SQL_USER_PROMPT_TEMPLATE, SQL_RETRY_PROMPT_TEMPLATE
from .validator import validate_query, sanitize_query


class TextToSQLAgent:
    """Agent that converts natural language queries to ZCQL using LLM."""
    
    def __init__(self, llm_client):
        """
        Initialize the text-to-SQL agent.
        
        Args:
            llm_client: CatalystLLMClient instance for LLM inference
        """
        self.llm_client = llm_client
        self.schema_context = SCHEMA_CONTEXT
    
    def generate_query(
        self,
        user_query: str,
        conversation_history: Optional[list[dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate a ZCQL query from natural language.
        
        Args:
            user_query: Natural language query from user
            conversation_history: Optional list of previous conversation turns
            
        Returns:
            Dictionary with zcql_query, intent, entities, is_valid, error
        """
        # Build conversation context string
        context_str = ""
        if conversation_history:
            context_str = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in conversation_history[-5:]  # Last 5 messages
            ])
        
        # Build system prompt with schema context
        system_prompt = f"{SQL_SYSTEM_PROMPT}\n\n{self.schema_context}"
        
        # Build user prompt
        user_prompt = SQL_USER_PROMPT_TEMPLATE.format(
            user_query=user_query,
            conversation_context=context_str if context_str else "No previous context."
        )
        
        # Call LLM with JSON mode
        try:
            response = self.llm_client.chat_completion_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,  # Lower temperature for more deterministic SQL
                max_tokens=1024
            )
        except Exception as e:
            return {
                "zcql_query": "",
                "intent": f"Failed to generate query: {str(e)}",
                "entities": [],
                "is_valid": False,
                "error": str(e)
            }
        
        # Extract fields from response
        zcql_query = response.get("zcql_query", "").strip()
        intent = response.get("intent", "")
        entities = response.get("entities", [])
        confidence = response.get("confidence", 0.0)
        
        # Validate the generated query
        is_valid, error_message = validate_query(zcql_query)
        
        if not is_valid:
            # Retry once with error feedback
            retry_prompt = SQL_RETRY_PROMPT_TEMPLATE.format(
                error_message=error_message,
                user_query=user_query
            )
            
            try:
                retry_response = self.llm_client.chat_completion_json(
                    system_prompt=system_prompt,
                    user_prompt=retry_prompt,
                    temperature=0.3,
                    max_tokens=1024
                )
                
                zcql_query = retry_response.get("zcql_query", "").strip()
                intent = retry_response.get("intent", intent)
                entities = retry_response.get("entities", entities)
                confidence = retry_response.get("confidence", confidence)
                
                # Re-validate
                is_valid, error_message = validate_query(zcql_query)
                
                if not is_valid:
                    return {
                        "zcql_query": sanitize_query(zcql_query),
                        "intent": intent,
                        "entities": entities,
                        "is_valid": False,
                        "error": error_message
                    }
            except Exception as retry_error:
                return {
                    "zcql_query": sanitize_query(zcql_query),
                    "intent": intent,
                    "entities": entities,
                    "is_valid": False,
                    "error": f"Validation failed and retry error: {str(retry_error)}"
                }
        
        # Sanitize the valid query
        zcql_query = sanitize_query(zcql_query)
        
        return {
            "zcql_query": zcql_query,
            "intent": intent,
            "entities": entities,
            "is_valid": is_valid,
            "error": None if is_valid else error_message
        }
