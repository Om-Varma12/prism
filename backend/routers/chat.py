"""
Chat router for intelligent query processing.
"""
from fastapi import APIRouter, Depends, Request
from datetime import datetime
import uuid
from typing import Optional

from services.llm_client import CatalystLLMClient
from agents.text_to_sql.agent import TextToSQLAgent
from agents.response_structurer.agent import ResponseStructurer
from schemas.chat import (
    ChatQueryRequest,
    ChatQueryResponse,
    ChatHistoryResponse,
    ConversationItem,
    NewConversationResponse
)
from core.database import get_zcql, get_datastore
from core.security import require_role


router = APIRouter(prefix="/api/chat", tags=["chat"])


def flatten_zcql_results(results: list) -> list:
    """
    Flatten nested ZCQL result structure.
    
    Args:
        results: Raw ZCQL query results
        
    Returns:
        Flattened list of dictionaries
    """
    if not results:
        return []
    
    # ZCQL returns results as list of dicts, but nested structure may vary
    # Handle common nested patterns
    flattened = []
    for row in results:
        if isinstance(row, dict):
            # Flatten nested dict if needed
            flat_row = {}
            for key, value in row.items():
                if isinstance(value, dict):
                    # Extract values from nested dict
                    for nested_key, nested_value in value.items():
                        flat_row[f"{key}_{nested_key}"] = nested_value
                        # Keep un-prefixed key for direct column name lookup
                        if nested_key not in flat_row:
                            flat_row[nested_key] = nested_value
                else:
                    flat_row[key] = value
            flattened.append(flat_row)
        else:
            flattened.append({"value": row})
    
    return flattened


@router.post("/query", response_model=ChatQueryResponse)
async def chat_query(
    request: ChatQueryRequest,
    http_request: Request,
    zcql = Depends(get_zcql)
):
    """
    Main chat query endpoint.
    
    Processes natural language query through the agent pipeline:
    1. Text-to-SQL agent generates ZCQL
    2. Execute ZCQL against database
    3. Response structurer formats results
    4. Return structured response
    """
    import re
    import random
    
    # Initialize agents
    llm_client = CatalystLLMClient()
    text_to_sql_agent = TextToSQLAgent(llm_client)
    response_structurer = ResponseStructurer(llm_client)
    
    # Fetch conversation history for context
    history_rows = []
    try:
        history_query = f"""
        SELECT role, content FROM conversations 
        WHERE session_id = '{request.session_id}' 
        ORDER BY created_at ASC 
        LIMIT 10
        """
        history_result = zcql.execute_query(history_query)
        # Flatten results
        for r in (history_result if isinstance(history_result, list) else []):
            conv_data = r.get("conversations", r)
            history_rows.append({
                "role": conv_data.get("role"),
                "content": conv_data.get("content")
            })
    except Exception as e:
        print(f"[Warning] Failed to fetch conversation context: {e}")
    
    # Generate SQL query
    sql_result = text_to_sql_agent.generate_query(
        user_query=request.query,
        conversation_history=history_rows
    )
    
    if not sql_result["is_valid"] or not sql_result["zcql_query"]:
        # Return error response if SQL generation failed
        return ChatQueryResponse(
            message_id=str(uuid.uuid4()),
            response_text=f"Unable to generate query: {sql_result.get('error', 'Unknown error')}",
            table_data=[],
            sql_query=sql_result.get("zcql_query", ""),
            scanned_records=0,
            sources=[],
            entities=[],
            follow_ups=["Try rephrasing your question", "Ask about a different topic"],
            timestamp=datetime.utcnow().isoformat()
        )
    
    zcql_query = sql_result["zcql_query"]
    
    # Execute ZCQL query
    try:
        query_result = zcql.execute_query(zcql_query)
        raw_results = query_result if isinstance(query_result, list) else []
    except Exception as e:
        # Handle ZCQL execution error
        return ChatQueryResponse(
            message_id=str(uuid.uuid4()),
            response_text=f"Query execution failed: {str(e)}",
            table_data=[],
            sql_query=zcql_query,
            scanned_records=0,
            sources=[],
            entities=[],
            follow_ups=["Try rephrasing your question", "Ask about a different topic"],
            timestamp=datetime.utcnow().isoformat()
        )
    
    # Flatten results
    flat_results = flatten_zcql_results(raw_results)
    
    # Extract tables accessed from ZCQL query
    tables_accessed = []
    if zcql_query:
        # Match table names after FROM or JOIN
        tables = re.findall(r'FROM\s+(\w+)|JOIN\s+(\w+)', zcql_query, re.IGNORECASE)
        for table_tuple in tables:
            t = table_tuple[0] or table_tuple[1]
            if t and t not in tables_accessed:
                tables_accessed.append(t)
    if not tables_accessed:
        tables_accessed = ["CaseMaster"]
    
    # Extract metadata
    metadata = {
        "record_count": len(flat_results),
        "tables_accessed": tables_accessed,
        "sql_query": zcql_query
    }
    
    # Structure response
    structured_response = response_structurer.structure_response(
        query=request.query,
        raw_results=flat_results,
        metadata=metadata
    )
    
    # Build final response
    response = ChatQueryResponse(
        message_id=str(uuid.uuid4()),
        response_text=structured_response["response_text"],
        table_data=structured_response["table_data"],
        sql_query=zcql_query,
        scanned_records=len(flat_results),
        sources=tables_accessed,
        entities=structured_response["entities"],
        follow_ups=structured_response["follow_ups"],
        timestamp=datetime.utcnow().isoformat()
    )
    
    # Save to conversations table (optional - try/except)
    try:
        datastore = get_datastore(http_request)
        table = datastore.table("conversations")
        
        # Save user message
        table.insert({
            "conversation_id": random.randint(1, 2147483647),
            "user_id": "dev_user",  # TODO: Get from auth
            "session_id": request.session_id,
            "role": "user",
            "content": request.query,
            "sql_generated": zcql_query,
            "created_at": datetime.utcnow().isoformat()
        })
        
        # Save assistant response
        table.insert({
            "conversation_id": random.randint(1, 2147483647),
            "user_id": "dev_user",
            "session_id": request.session_id,
            "role": "assistant",
            "content": structured_response["response_text"],
            "sql_generated": zcql_query,
            "created_at": datetime.utcnow().isoformat()
        })
    except Exception as e:
        # Log warning but don't fail the request
        print(f"[Warning] Failed to save to conversations table: {e}")
    
    return response


@router.get("/history", response_model=ChatHistoryResponse)
async def chat_history(
    http_request: Request,
    zcql = Depends(get_zcql)
):
    """
    Get conversation history for the current user.
    
    Groups conversations by session_id and categorizes by date.
    """
    try:
        # Query conversations table
        query = """
        SELECT session_id, MIN(content) as first_message, MIN(created_at) as created_at
        FROM conversations
        WHERE user_id = 'dev_user'
        GROUP BY session_id
        ORDER BY created_at DESC
        """
        
        result = zcql.execute_query(query)
        conversations = result if isinstance(result, list) else []
        
        # Categorize by date
        categorized = []
        now = datetime.utcnow()
        
        for conv in conversations:
            created_at = conv.get("created_at", "")
            first_message = conv.get("first_message", "New Conversation")
            session_id = conv.get("session_id", "")
            
            # Parse date and categorize
            try:
                conv_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                days_ago = (now - conv_date).days
                
                if days_ago == 0:
                    category = "Today"
                elif days_ago <= 7:
                    category = "Previous 7 Days"
                else:
                    category = "Older"
            except:
                category = "Older"
            
            categorized.append(ConversationItem(
                session_id=session_id,
                title=first_message[:50] if len(first_message) > 50 else first_message,
                created_at=created_at,
                category=category
            ))
        
        return ChatHistoryResponse(conversations=categorized)
    
    except Exception as e:
        # Return empty history on error
        print(f"[Warning] Failed to fetch conversation history: {e}")
        return ChatHistoryResponse(conversations=[])


@router.post("/new", response_model=NewConversationResponse)
async def new_conversation():
    """
    Create a new conversation session.
    
    Generates a new UUID for the session_id.
    """
    return NewConversationResponse(session_id=str(uuid.uuid4()))


@router.get("/db-status")
async def db_status(zcql = Depends(get_zcql)):
    """Diagnostic endpoint to count rows in core tables."""
    status = {}
    tables = ['CaseMaster', 'Victim', 'Unit', 'CrimeSubHead', 'Accused', 'District', 'CaseStatusMaster']
    for table in tables:
        try:
            res = zcql.execute_query(f"SELECT COUNT(ROWID) as count FROM {table}")
            status[table] = res[0].get('count', 0) if res else 0
        except Exception as e:
            status[table] = f"Error: {str(e)}"
    return status


@router.get("/debug-query")
async def debug_query(zcql = Depends(get_zcql)):
    """Diagnose ZCQL join issues by dumping raw values."""
    diagnostics = {}
    
    # 1. Dump all Victims
    try:
        res = zcql.execute_query("SELECT ROWID, VictimName, CaseMasterID FROM Victim LIMIT 50")
        diagnostics["Victims_Table"] = res
    except Exception as e:
        diagnostics["Victims_Table_Error"] = str(e)
        
    # 2. Dump all CaseMaster rows
    try:
        res = zcql.execute_query("SELECT ROWID, CaseMasterID, CrimeNo, PoliceStationID, CrimeMinorHeadID FROM CaseMaster LIMIT 50")
        diagnostics["CaseMaster_Table"] = res
    except Exception as e:
        diagnostics["CaseMaster_Table_Error"] = str(e)
        
    # 3. Check specific Unit ROWID
    try:
        res = zcql.execute_query("SELECT ROWID, UnitName FROM Unit WHERE ROWID = '46143000000055049'")
        diagnostics["Unit_Check_46143000000055049"] = res
    except Exception as e:
        diagnostics["Unit_Check_Error"] = str(e)

    # 4. Check specific CrimeSubHead ROWID
    try:
        res = zcql.execute_query("SELECT ROWID, CrimeHeadName FROM CrimeSubHead WHERE ROWID = '46143000000055176'")
        diagnostics["CrimeSubHead_Check_46143000000055176"] = res
    except Exception as e:
        diagnostics["CrimeSubHead_Check_Error"] = str(e)
        
    # 5. Test join between CaseMaster and Victim
    try:
        query = "SELECT CaseMaster.CrimeNo, Victim.VictimName FROM CaseMaster INNER JOIN Victim ON CaseMaster.ROWID = Victim.CaseMasterID"
        res = zcql.execute_query(query)
        diagnostics["CaseMaster_Victim_Join"] = res
    except Exception as e:
        diagnostics["CaseMaster_Victim_Join_Error"] = str(e)
        
    # 6. Test 3-table join WITHOUT WHERE (does it return rows at all?)
    try:
        query = """
        SELECT CaseMaster.CrimeNo, Victim.VictimName, Unit.UnitName
        FROM CaseMaster
        INNER JOIN Victim ON CaseMaster.ROWID = Victim.CaseMasterID
        INNER JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
        LIMIT 5
        """
        res = zcql.execute_query(query)
        diagnostics["Join_3Table_No_Where"] = res
    except Exception as e:
        diagnostics["Join_3Table_No_Where_Error"] = str(e)

    # 7. Test 3-table join with WHERE on CaseMaster column (not Victim)
    try:
        query = """
        SELECT CaseMaster.CrimeNo, Victim.VictimName, Unit.UnitName
        FROM CaseMaster
        INNER JOIN Victim ON CaseMaster.ROWID = Victim.CaseMasterID
        INNER JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
        WHERE CaseMaster.CrimeNo = '104430100120240002'
        """
        res = zcql.execute_query(query)
        diagnostics["Join_3Table_Where_On_CaseMaster"] = res
    except Exception as e:
        diagnostics["Join_3Table_Where_On_CaseMaster_Error"] = str(e)

    # 8. Test 3-table join with WHERE on Victim column
    try:
        query = """
        SELECT CaseMaster.CrimeNo, Victim.VictimName, Unit.UnitName
        FROM CaseMaster
        INNER JOIN Victim ON CaseMaster.ROWID = Victim.CaseMasterID
        INNER JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
        WHERE Victim.VictimName LIKE '*Lakshmi*'
        """
        res = zcql.execute_query(query)
        diagnostics["Join_3Table_Where_On_Victim"] = res
    except Exception as e:
        diagnostics["Join_3Table_Where_On_Victim_Error"] = str(e)

    # 9. Test LEFT JOIN instead of INNER JOIN with Unit
    try:
        query = """
        SELECT CaseMaster.CrimeNo, Victim.VictimName, Unit.UnitName
        FROM CaseMaster
        INNER JOIN Victim ON CaseMaster.ROWID = Victim.CaseMasterID
        LEFT JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
        WHERE Victim.VictimName LIKE '*Lakshmi*'
        """
        res = zcql.execute_query(query)
        diagnostics["Join_Left_Unit_Where_Victim"] = res
    except Exception as e:
        diagnostics["Join_Left_Unit_Where_Victim_Error"] = str(e)

    # 10. Just victim name no join
    try:
        query = "SELECT ROWID, VictimName, CaseMasterID FROM Victim WHERE VictimName LIKE '*Lakshmi*'"
        res = zcql.execute_query(query)
        diagnostics["Victim_Where_Only"] = res
    except Exception as e:
        diagnostics["Victim_Where_Only_Error"] = str(e)

    return diagnostics


