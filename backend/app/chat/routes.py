# backend/app/chat/routes.py
"""
Chat routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.database.models import User, Conversation, Message
from app.auth.dependencies import get_current_user
from app.chat.models import ConversationResponse, ConversationCreate, MessageResponse

chat_router = APIRouter()

@chat_router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()

    return conversations

@chat_router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
        conversation_data: ConversationCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation

@chat_router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
        conversation_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation

@chat_router.delete("/conversations/{conversation_id}")
async def delete_conversation(
        conversation_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.delete(conversation)
    db.commit()

    return {"message": "Conversation deleted successfully"}


# Add this to your backend/app/chat/routes.py file

@chat_router.put("/conversations/{conversation_id}/title")
async def update_conversation_title(
        conversation_id: int,
        request: dict,  # expecting {"title": "new title"}
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Update conversation title"""

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    new_title = request.get("title")
    if not new_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required"
        )

    conversation.title = new_title
    conversation.updated_at = func.now()

    db.commit()
    db.refresh(conversation)

    return {
        "message": "Conversation title updated successfully",
        "conversation_id": conversation.id,
        "title": conversation.title
    }