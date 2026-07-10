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
        
        # Handle empty results
        if not raw_results or record_count == 0:
            return self._handle_empty_results(query, tables_accessed)
        
        # Format results for LLM
        results_str = json.dumps(raw_results[:10], indent=2)  # Limit to 10 results
        
        # Build user prompt
        user_prompt = RESPONSE_USER_PROMPT_TEMPLATE.format(
            query=query,
            results=results_str,
            record_count=record_count,
            tables_accessed=", ".join(tables_accessed)
        )
        
        # Call LLM
        try:
            response = self.llm_client.chat_completion_json(
                system_prompt=RESPONSE_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.5,
                max_tokens=1024
            )
            
            return {
                "response_text": response.get("response_text", ""),
                "table_data": self._format_table_data(raw_results[:10]),  # Limit to 10
                "entities": response.get("entities", []),
                "follow_ups": response.get("follow_ups", [])
            }
        except Exception as e:
            # Fallback to raw data display on LLM failure
            return self._fallback_response(query, raw_results, str(e))
    
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
                "entities": response.get("entities", []),
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
    
    def _format_table_data(
        self,
        raw_results: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Format raw database results into table data format.
        
        Args:
            raw_results: Raw database results
            
        Returns:
            Formatted table data with firNo, crimeType, district, status
        """
        table_data = []
        
        for row in raw_results:
            # Extract common fields, handle missing keys gracefully
            fir_no = row.get("CrimeNo") or row.get("CaseNo") or row.get("ROWID", "N/A")
            crime_type = row.get("CrimeHeadName") or row.get("CrimeType") or "Unknown"
            district = row.get("DistrictName") or row.get("district") or "Unknown"
            status = row.get("CaseStatusName") or row.get("status") or "Unknown"
            
            table_data.append({
                "firNo": str(fir_no),
                "crimeType": str(crime_type),
                "district": str(district),
                "status": str(status)
            })
        
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
