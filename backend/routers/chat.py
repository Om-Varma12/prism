"""
Chat router for intelligent query processing.
"""
from fastapi import APIRouter, Depends, Request
from datetime import datetime
import uuid
from typing import Optional
import asyncio

from services.llm_client import CatalystLLMClient
from agents.text_to_sql.agent import TextToSQLAgent
from agents.response_structurer.agent import ResponseStructurer
from agents.title_generator.agent import TitleGenerator
from schemas.chat import (
    ChatQueryRequest,
    ChatQueryResponse,
    ChatHistoryResponse,
    ConversationItem,
    NewConversationResponse,
    SessionMessage,
    SessionMessagesResponse,
)
from core.database import get_zcql, get_stratus
from core.security import require_role
from fastapi.responses import StreamingResponse
import json


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


async def upload_pdf_to_stratus(
    pdf_buffer,
    session_id: str,
    stratus_instance,
    max_retries: int = 3,
    timeout: int = 30
) -> bool:
    """
    Upload PDF to Stratus bucket with retry logic.
    
    Args:
        pdf_buffer: BytesIO buffer containing PDF data
        session_id: Conversation session ID for filename
        stratus_instance: Stratus service instance
        max_retries: Maximum number of upload attempts
        timeout: Timeout in seconds for each upload attempt
    
    Returns:
        bool: True if upload succeeded, False otherwise
    """
    bucket_name = 'chat-pdfs'
    object_key = f'chat-{session_id}.pdf'
    
    # Prepare metadata
    metadata = {
        'conversation_id': session_id,
        'created_at': datetime.utcnow().isoformat(),
        'user_id': 'dev_user',
        'content_type': 'application/pdf'
    }
    
    # Upload options with overwrite enabled
    options = {
        'overwrite': 'true',
        'content_type': 'application/pdf',
        'meta_data': metadata
    }
    
    for attempt in range(max_retries):
        try:
            # Get bucket instance
            bucket = stratus_instance.bucket(bucket_name)
            
            # Reset buffer position before upload
            pdf_buffer.seek(0)
            
            # Upload with timeout
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    bucket.put_object,
                    object_key,
                    pdf_buffer,
                    options
                ),
                timeout=timeout
            )
            
            print(f"[Stratus Upload] Successfully uploaded {object_key} (attempt {attempt + 1})")
            return True
            
        except asyncio.TimeoutError:
            print(f"[Stratus Upload] Timeout on attempt {attempt + 1}/{max_retries}")
        except Exception as e:
            print(f"[Stratus Upload] Error on attempt {attempt + 1}/{max_retries}: {e}")
    
    print(f"[Stratus Upload] Failed after {max_retries} attempts")
    return False


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
    
    # Save to conversations table via ZCQL INSERT (avoids Table API permission issues)
    try:
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        user_conv_id = random.randint(1, 2147483647)
        asst_conv_id = random.randint(1, 2147483647)

        # Escape single quotes in content and JSON strings
        user_content = request.query.replace("'", "''")
        asst_content = structured_response["response_text"].replace("'", "''")
        sql_escaped = zcql_query.replace("'", "''") if zcql_query else ""
        
        # Convert response metadata to JSON strings and escape
        import json
        table_data_json = json.dumps(structured_response["table_data"]).replace("'", "''")
        entities_json = json.dumps(structured_response["entities"]).replace("'", "''")
        follow_ups_json = json.dumps(structured_response["follow_ups"]).replace("'", "''")
        sources_json = json.dumps(tables_accessed).replace("'", "''")
        scanned_records = len(flat_results)

        zcql.execute_query(f"""
            INSERT INTO conversations (conversation_id, user_id, session_id, role, content, sql_generated, created_at, table_data_json, entities_json, follow_ups_json, sources_json, scanned_records)
            VALUES ({user_conv_id}, 'dev_user', '{request.session_id}', 'user', '{user_content}', '{sql_escaped}', '{ts}', NULL, NULL, NULL, NULL, NULL)
        """)

        zcql.execute_query(f"""
            INSERT INTO conversations (conversation_id, user_id, session_id, role, content, sql_generated, created_at, table_data_json, entities_json, follow_ups_json, sources_json, scanned_records)
            VALUES ({asst_conv_id}, 'dev_user', '{request.session_id}', 'assistant', '{asst_content}', '{sql_escaped}', '{ts}', '{table_data_json}', '{entities_json}', '{follow_ups_json}', '{sources_json}', {scanned_records})
        """)
    except Exception as e:
        print(f"[Warning] Failed to save to conversations table: {e}")
    
    return response


@router.get("/history", response_model=ChatHistoryResponse)
async def chat_history(
    http_request: Request,
    zcql = Depends(get_zcql)
):
    """
    Get conversation history for the current user.
    
    Returns one item per unique session_id, titled by the first user message,
    grouped into Today / Previous 7 Days / Older categories.
    """
    try:
        # Fetch one row per session: the oldest user message (used as title)
        query = """
        SELECT session_id, content, created_at
        FROM conversations
        WHERE user_id = 'dev_user' AND role = 'user'
        ORDER BY created_at ASC
        """
        result = zcql.execute_query(query)
        rows = result if isinstance(result, list) else []

        # Deduplicate: keep only the first (oldest) row per session_id
        seen: dict = {}
        for row in rows:
            # ZCQL may wrap under table name key
            r = row.get("conversations", row)
            sid = r.get("session_id") or row.get("session_id", "")
            if sid and sid not in seen:
                seen[sid] = {
                    "session_id": sid,
                    "content": r.get("content") or row.get("content", "New Conversation"),
                    "created_at": r.get("created_at") or row.get("created_at", ""),
                }

        categorized = []
        now = datetime.utcnow()

        for sid, data in seen.items():
            raw_ts = data["created_at"]
            content = data["content"]
            try:
                # ZCQL returns datetimes like "2026-07-11 05:30:00" or ISO with T
                normalized = raw_ts.replace("T", " ").split("+")[0].split("Z")[0].strip()
                conv_date = datetime.strptime(normalized, "%Y-%m-%d %H:%M:%S")
                days_ago = (now - conv_date).days
                if days_ago == 0:
                    category = "Today"
                elif days_ago <= 7:
                    category = "Previous 7 Days"
                else:
                    category = "Older"
            except Exception:
                category = "Older"

            title = content[:50] if len(content) > 50 else content
            categorized.append(ConversationItem(
                session_id=sid,
                title=title,
                created_at=raw_ts,
                category=category,
            ))

        # Sort newest first within each category
        categorized.sort(key=lambda x: x.created_at, reverse=True)

        return ChatHistoryResponse(conversations=categorized)

    except Exception as e:
        print(f"[Warning] Failed to fetch conversation history: {e}")
        return ChatHistoryResponse(conversations=[])


@router.get("/messages", response_model=SessionMessagesResponse)
async def get_session_messages(
    session_id: str,
    zcql = Depends(get_zcql)
):
    """
    Return all messages for a given session_id in chronological order.
    Used by the frontend to restore a previous conversation.
    """
    try:
        escaped_sid = session_id.replace("'", "''")
        query = f"""
        SELECT role, content, sql_generated, created_at, table_data_json, entities_json, follow_ups_json, sources_json, scanned_records
        FROM conversations
        WHERE session_id = '{escaped_sid}' AND user_id = 'dev_user'
        ORDER BY created_at ASC
        """
        result = zcql.execute_query(query)
        rows = result if isinstance(result, list) else []

        messages = []
        for row in rows:
            # ZCQL may wrap under table name key
            r = row.get("conversations", row)
            messages.append(SessionMessage(
                role=r.get("role") or row.get("role", ""),
                content=r.get("content") or row.get("content", ""),
                sql_generated=r.get("sql_generated") or row.get("sql_generated"),
                created_at=r.get("created_at") or row.get("created_at", ""),
                table_data_json=r.get("table_data_json") or row.get("table_data_json"),
                entities_json=r.get("entities_json") or row.get("entities_json"),
                follow_ups_json=r.get("follow_ups_json") or row.get("follow_ups_json"),
                sources_json=r.get("sources_json") or row.get("sources_json"),
                scanned_records=r.get("scanned_records") or row.get("scanned_records"),
            ))

        return SessionMessagesResponse(session_id=session_id, messages=messages)

    except Exception as e:
        print(f"[Warning] Failed to fetch session messages: {e}")
        return SessionMessagesResponse(session_id=session_id, messages=[])


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


@router.get("/export-pdf")
async def export_chat_pdf(
    session_id: str,
    request: Request,
    zcql = Depends(get_zcql),
    stratus = Depends(get_stratus)
):
    """
    Export conversation to PDF with title, date/time, and all content except SQL.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from io import BytesIO
    
    try:
        # Fetch conversation messages
        escaped_sid = session_id.replace("'", "''")
        query = f"""
        SELECT role, content, sql_generated, created_at, table_data_json, entities_json, follow_ups_json, sources_json, scanned_records
        FROM conversations
        WHERE session_id = '{escaped_sid}' AND user_id = 'dev_user'
        ORDER BY created_at ASC
        """
        result = zcql.execute_query(query)
        rows = result if isinstance(result, list) else []
        
        if not rows:
            return {"error": "No messages found for this session"}
        
        # Format messages for title generation
        messages_for_title = []
        for row in rows:
            r = row.get("conversations", row)
            messages_for_title.append({
                "role": r.get("role") or row.get("role", ""),
                "content": r.get("content") or row.get("content", "")
            })
        
        # Generate title using LLM agent
        llm_client = CatalystLLMClient()
        title_generator = TitleGenerator(llm_client)
        title = title_generator.generate_title(messages_for_title)
        
        # Get conversation date/time (from first message)
        first_row = rows[0]
        r = first_row.get("conversations", first_row)
        created_at = r.get("created_at") or first_row.get("created_at", "")
        try:
            conv_date = datetime.strptime(created_at.replace('T', ' ').split('+')[0].split('Z')[0].strip(), "%Y-%m-%d %H:%M:%S")
            date_str = conv_date.strftime("%B %d, %Y at %I:%M %p")
        except:
            date_str = created_at
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#3B6FE8'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.gray,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1E2025'),
            spaceBefore=12,
            spaceAfter=6
        )
        
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2A2D35'),
            spaceAfter=12,
            leading=14
        )
        
        # Add title
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(f"Generated on {date_str}", date_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Add messages
        for row in rows:
            r = row.get("conversations", row)
            role = r.get("role") or row.get("role", "")
            content = r.get("content") or row.get("content", "")
            
            if role == 'user':
                story.append(Paragraph("<b>User:</b>", header_style))
            else:
                story.append(Paragraph("<b>Assistant:</b>", header_style))
            
            story.append(Paragraph(content, normal_style))
            
            # Add table data if available (assistant only)
            if role == 'assistant':
                table_data_json = r.get("table_data_json") or row.get("table_data_json")
                if table_data_json:
                    try:
                        table_data = json.loads(table_data_json)
                        if table_data:
                            story.append(Paragraph("<b>Results:</b>", header_style))
                            
                            # Create table
                            if table_data:
                                headers = list(table_data[0].keys())
                                data = [headers]
                                for row_data in table_data:
                                    data.append([str(row_data.get(h, '')) for h in headers])
                                
                                table = Table(data, colWidths=[1.5*inch]*len(headers))
                                table.setStyle(TableStyle([
                                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B3E47')),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ]))
                                story.append(table)
                                story.append(Spacer(1, 0.1*inch))
                    except Exception as e:
                        print(f"[PDF Export] Error parsing table data: {e}")
                
                # Add entities if available
                entities_json = r.get("entities_json") or row.get("entities_json")
                if entities_json:
                    try:
                        entities = json.loads(entities_json)
                        if entities:
                            story.append(Paragraph("<b>Mentioned Entities:</b>", header_style))
                            for entity in entities:
                                entity_text = f"• {entity.get('name', '')} ({entity.get('type', '')})"
                                story.append(Paragraph(entity_text, normal_style))
                            story.append(Spacer(1, 0.1*inch))
                    except Exception as e:
                        print(f"[PDF Export] Error parsing entities: {e}")
                
                # Add sources if available
                sources_json = r.get("sources_json") or row.get("sources_json")
                if sources_json:
                    try:
                        sources = json.loads(sources_json)
                        if sources:
                            story.append(Paragraph("<b>Data Sources:</b>", header_style))
                            for source in sources:
                                story.append(Paragraph(f"• {source}", normal_style))
                            story.append(Spacer(1, 0.1*inch))
                    except Exception as e:
                        print(f"[PDF Export] Error parsing sources: {e}")
            
            story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        
        # Upload PDF to Stratus in background (non-blocking)
        try:
            # Create a copy of the buffer for upload
            upload_buffer = BytesIO(buffer.getvalue())
            
            # Upload in background without blocking response
            asyncio.create_task(upload_pdf_to_stratus(
                pdf_buffer=upload_buffer,
                session_id=session_id,
                stratus_instance=stratus,
                max_retries=3,
                timeout=30
            ))
        except Exception as e:
            print(f"[Stratus Upload] Failed to initiate background upload: {e}")
            # Continue with PDF download response regardless
        
        # Return PDF as response
        buffer.seek(0)
        filename = f"chat_export_{session_id[:8]}.pdf"
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
        )
        
    except Exception as e:
        print(f"[PDF Export] Error: {e}")
        return {"error": f"Failed to generate PDF: {str(e)}"}


