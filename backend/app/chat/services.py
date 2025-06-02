# backend/app/chat/services.py
"""
Chat service for handling PowerBI agent interactions
"""
import asyncio
from typing import Optional
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.database.models import User, Conversation, Message
from app.powerbi.agent import PowerBIAgentService

class ChatService:
    def __init__(self):
        self.powerbi_agent = PowerBIAgentService()

    async def process_message(
            self,
            user_id: str,
            message: str,
            conversation_id: Optional[int] = None
    ) -> dict:
        db = SessionLocal()
        try:
            # Get or create conversation
            if conversation_id:
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                ).first()
            else:
                # Create new conversation
                conversation = Conversation(
                    user_id=int(user_id),
                    title=message[:50] + "..." if len(message) > 50 else message
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)

            if not conversation:
                raise Exception("Conversation not found")

            # Save user message
            user_message = Message(
                conversation_id=conversation.id,
                content=message,
                is_user=True
            )
            db.add(user_message)
            db.commit()

            # Get response from PowerBI agent
            try:
                agent_response = await self.powerbi_agent.process_query(message)
            except Exception as e:
                agent_response = f"I'm sorry, I encountered an error processing your request: {str(e)}"

            # Save agent response
            agent_message = Message(
                conversation_id=conversation.id,
                content=agent_response,
                is_user=False
            )
            db.add(agent_message)
            db.commit()

            return {
                "conversation_id": conversation.id,
                "user_message": {
                    "id": user_message.id,
                    "content": user_message.content,
                    "is_user": True,
                    "created_at": user_message.created_at.isoformat()
                },
                "agent_message": {
                    "id": agent_message.id,
                    "content": agent_message.content,
                    "is_user": False,
                    "created_at": agent_message.created_at.isoformat()
                }
            }

        finally:
            db.close()