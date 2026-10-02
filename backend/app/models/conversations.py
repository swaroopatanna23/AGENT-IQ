from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class ConversationModel(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    title = Column(String(255), default="New Analysis Session")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")
    dataset = relationship("Dataset", back_populates="conversations")
    queries = relationship("QueryModel", back_populates="conversation", cascade="all, delete-orphan")
    messages = relationship("ConversationMessageModel", back_populates="conversation", cascade="all, delete-orphan")

class ConversationMessageModel(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender = Column(String(20), nullable=False)  # user, agent
    content = Column(Text, nullable=False)
    language = Column(String(20), default="en")
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("ConversationModel", back_populates="messages")
