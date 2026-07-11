"""
Pydantic schemas for chat API request and response models.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class ChatQueryRequest(BaseModel):
    """Request model for chat query endpoint."""
    query: str
    session_id: str


class ChatTableRow(BaseModel):
    """Table row data for chat response."""
    firNo: str
    crimeType: str
    district: str
    status: str


class ChatEntity(BaseModel):
    """Entity extracted from query results."""
    name: str
    type: str
    detail: str


class ChatQueryResponse(BaseModel):
    """Response model for chat query endpoint."""
    message_id: str
    response_text: str
    table_data: List[ChatTableRow]
    sql_query: str
    scanned_records: int
    sources: List[str]
    entities: List[ChatEntity]
    follow_ups: List[str]
    timestamp: str


class ConversationItem(BaseModel):
    """Conversation history item."""
    session_id: str
    title: str
    created_at: str
    category: str


class ChatHistoryResponse(BaseModel):
    """Response model for chat history endpoint."""
    conversations: List[ConversationItem]


class NewConversationResponse(BaseModel):
    """Response model for new conversation endpoint."""
    session_id: str


class SessionMessage(BaseModel):
    """Single message within a session, returned by GET /messages."""
    role: str                          # 'user' | 'assistant'
    content: str
    sql_generated: Optional[str] = None
    created_at: str
    table_data_json: Optional[str] = None
    entities_json: Optional[str] = None
    follow_ups_json: Optional[str] = None
    sources_json: Optional[str] = None
    scanned_records: Optional[int] = None


class SessionMessagesResponse(BaseModel):
    """Response model for GET /api/chat/messages endpoint."""
    session_id: str
    messages: List[SessionMessage]
