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
            user_id: str,  # Keep as string initially
            message: str,
            conversation_id: Optional[int] = None
    ) -> dict:
        db = SessionLocal()
        try:
            print(f"🔄 Processing message:")
            print(f"   - User ID (raw): '{user_id}' (type: {type(user_id)})")
            print(f"   - Message: '{message}'")
            print(f"   - Conversation ID: {conversation_id}")

            # FIX: Safely convert user_id to int with proper error handling
            try:
                user_id_int = int(user_id)
            except ValueError as e:
                print(f"❌ Error converting user_id to int: {e}")
                raise Exception(f"Invalid user ID format: {user_id}")

            print(f"   - User ID (converted): {user_id_int}")

            # Get or create conversation
            if conversation_id:
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id_int  # Use converted int
                ).first()
            else:
                # Create new conversation
                conversation = Conversation(
                    user_id=user_id_int,  # Use converted int
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
                print(f"🤖 Calling PowerBI agent with message: '{message}'")
                agent_response = await self.powerbi_agent.process_query(message)
                print(f"✅ PowerBI agent response received")
            except Exception as e:
                print(f"❌ PowerBI agent error: {str(e)}")
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

        except Exception as e:
            print(f"❌ Error in process_message: {str(e)}")
            raise e
        finally:
            db.close()