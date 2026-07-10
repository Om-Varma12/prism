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
