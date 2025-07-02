# backend/app/chat/services.py
"""
Chat service for handling PowerBI agent interactions - FIXED VERSION
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

            # Verify user exists
            user = db.query(User).filter(User.id == user_id_int).first()
            if not user:
                raise Exception(f"User with ID {user_id_int} not found")

            # Get or create conversation
            conversation = None
            if conversation_id:
                # Try to find existing conversation
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id_int
                ).first()

                if not conversation:
                    print(f"⚠️  Conversation {conversation_id} not found for user {user_id_int}")
                    # Create new conversation instead of failing
                    conversation = Conversation(
                        user_id=user_id_int,
                        title=message[:50] + "..." if len(message) > 50 else message
                    )
                    db.add(conversation)
                    db.commit()
                    db.refresh(conversation)
                    print(f"✅ Created new conversation {conversation.id} for user {user_id_int}")

            if not conversation:
                # Create new conversation
                conversation = Conversation(
                    user_id=user_id_int,
                    title=message[:50] + "..." if len(message) > 50 else message
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
                print(f"✅ Created new conversation {conversation.id} for user {user_id_int}")

            # Save user message
            user_message = Message(
                conversation_id=conversation.id,
                content=message,
                is_user=True
            )
            db.add(user_message)
            db.commit()
            db.refresh(user_message)
            print(f"✅ Saved user message {user_message.id}")

            # Get response from PowerBI agent
            try:
                print(f"🤖 Calling PowerBI agent with message: '{message}'")
                agent_response = await self.powerbi_agent.process_query(message)
                print(f"✅ PowerBI agent response received: {agent_response[:100]}...")
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
            db.refresh(agent_message)
            print(f"✅ Saved agent message {agent_message.id}")

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
            # Return a more user-friendly error response instead of raising
            return {
                "conversation_id": conversation_id,
                "user_message": {
                    "id": None,
                    "content": message,
                    "is_user": True,
                    "created_at": None
                },
                "agent_message": {
                    "id": None,
                    "content": f"I'm sorry, I encountered an error: {str(e)}",
                    "is_user": False,
                    "created_at": None
                }
            }
        finally:
            db.close()