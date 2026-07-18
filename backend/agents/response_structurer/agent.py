"""
Response structurer agent for converting raw query results to structured responses.
"""
from typing import Dict, Any, List
import json
from .prompts import (
    RESPONSE_SYSTEM_PROMPT,
    RESPONSE_USER_PROMPT_TEMPLATE,
    EMPTY_RESULTS_PROMPT_TEMPLATE
)


class ResponseStructurer:
    """Agent that structures raw database results into user-friendly responses."""
    
    def __init__(self, llm_client):
        """
        Initialize the response structurer agent.
        
        Args:
            llm_client: CatalystLLMClient instance for LLM inference
        """
        self.llm_client = llm_client
    
    def structure_response(
        self,
        query: str,
        raw_results: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Structure raw database results into a user-friendly response.
        
        Args:
            query: Original user query
            raw_results: Raw database query results
            metadata: Metadata including record_count, tables_accessed, sql_query
            
        Returns:
            Dictionary with response_text, table_data, entities, follow_ups
        """
        record_count = metadata.get("record_count", 0)
        tables_accessed = metadata.get("tables_accessed", [])
        sql_query = metadata.get("sql_query", "")
        
        # Detect aggregation/count-only result (no row-level data to table)
        is_aggregation = self._is_aggregation_result(raw_results)
        
        # Handle empty results
        if not raw_results or record_count == 0:
            return self._handle_empty_results(query, tables_accessed)
        
        # Format results for LLM (limit to 10 rows for prompt size)
        results_str = json.dumps(raw_results[:10], indent=2)
        
        # Build user prompt
        user_prompt = RESPONSE_USER_PROMPT_TEMPLATE.format(
            query=query,
            results=results_str,
            record_count=record_count,
        )
        
        # Call LLM for a clean natural-language response_text and follow_ups
        try:
            response = self.llm_client.chat_completion_json(
                system_prompt=RESPONSE_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.4,
                max_tokens=512
            )
            response_text = response.get("response_text", "")
            follow_ups = response.get("follow_ups", [])
        except Exception as e:
            response_text = f"Found {record_count} record(s) matching your query."
            follow_ups = ["Show more details", "Filter by district", "Sort by date"]
        
        # Build table data: skip table for pure aggregation results
        if is_aggregation:
            table_data = []
        else:
            table_data = self._format_table_data(raw_results[:50])
        
        return {
            "response_text": response_text,
            "table_data": table_data,
            "entities": [],
            "follow_ups": follow_ups,
        }
    
    def _clean_entities(self, raw_entities: Any) -> List[Dict[str, str]]:
        if not isinstance(raw_entities, list):
            return []
        cleaned = []
        for ent in raw_entities:
            if isinstance(ent, dict):
                name = ent.get("name") or ent.get("entity_name") or ent.get("value")
                type_val = ent.get("type") or ent.get("entity_type") or "Unknown"
                detail = ent.get("detail") or ent.get("description") or ent.get("info") or ""
                if name:
                    cleaned.append({
                        "name": str(name),
                        "type": str(type_val),
                        "detail": str(detail)
                    })
        return cleaned
    
    def _handle_empty_results(
        self,
        query: str,
        tables_accessed: List[str]
    ) -> Dict[str, Any]:
        """
        Handle case when no results are found.
        
        Args:
            query: Original user query
            tables_accessed: Tables that were queried
            
        Returns:
            Structured response with suggestions
        """
        user_prompt = EMPTY_RESULTS_PROMPT_TEMPLATE.format(
            query=query
        )
        
        try:
            response = self.llm_client.chat_completion_json(
                system_prompt=RESPONSE_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.5,
                max_tokens=512
            )
            
            return {
                "response_text": response.get("response_text", "No matching records found."),
                "table_data": [],
                "entities": self._clean_entities(response.get("entities", [])),
                "follow_ups": response.get("follow_ups", [
                    "Try broadening your search criteria",
                    "Check for alternative spellings",
                    "Ask about a different time period"
                ])
            }
        except Exception as e:
            return {
                "response_text": "No matching records found. Try rephrasing your query or broadening the search criteria.",
                "table_data": [],
                "entities": [],
                "follow_ups": [
                    "Try broadening your search criteria",
                    "Check for alternative spellings",
                    "Ask about a different time period"
                ]
            }
    
    def _is_aggregation_result(self, raw_results: List[Dict[str, Any]]) -> bool:
        """
        Detect if results contain aggregate function columns (COUNT, SUM, AVG, MIN, MAX).
        This includes pure aggregations (SELECT COUNT(*)) and GROUP BY results
        (SELECT COUNT(*), DistrictName ... GROUP BY ...).
        When ANY key is an aggregate function, the result is not row-level data
        and should not be rendered as a table.
        """
        if not raw_results:
            return False
        first_row = raw_results[0]
        keys = list(first_row.keys())
        if not keys:
            return False
        agg_keywords = ('COUNT', 'SUM', 'AVG', 'MIN', 'MAX')
        # If ANY key is an aggregate function, treat as aggregation — no table
        return any(any(kw in k.upper() for kw in agg_keywords) for k in keys if k)


    def _format_table_data(
        self,
        raw_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Format raw database results into a dynamic table for display.
        Preserves actual column names from the query instead of hardcoding FIR fields.
        
        Args:
            raw_results: Raw database results
            
        Returns:
            List of row dicts with cleaned, human-readable keys
        """
        if not raw_results:
            return []
        
        table_data = []
        for row in raw_results:
            cleaned_row = {}
            for key, value in row.items():
                # Clean up key: strip table prefix (e.g. "CaseMaster_CrimeNo" -> "CrimeNo")
                clean_key = key
                if '_' in key:
                    parts = key.split('_', 1)
                    # Only strip the prefix if the first part looks like a table name (Title case)
                    if parts[0] and parts[0][0].isupper():
                        clean_key = parts[1]
                cleaned_row[clean_key] = str(value) if value is not None else "N/A"
            if cleaned_row:
                table_data.append(cleaned_row)
        return table_data
    
    def _fallback_response(
        self,
        query: str,
        raw_results: List[Dict[str, Any]],
        error: str
    ) -> Dict[str, Any]:
        """
        Generate fallback response when LLM fails.
        
        Args:
            query: Original user query
            raw_results: Raw database results
            error: Error message from LLM
            
        Returns:
            Basic structured response with raw data
        """
        return {
            "response_text": f"Found {len(raw_results)} records matching your query. {error}",
            "table_data": self._format_table_data(raw_results[:10]),
            "entities": [],
            "follow_ups": [
                "Show more details",
                "Filter by district",
                "Sort by date"
            ]
        }
