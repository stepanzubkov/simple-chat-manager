from sqlalchemy import Column, Integer, String, Text

from db.base import Base


class Roles(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer)
    conversation_id = Column(Integer)
    role = Column(String(30))


class ConversationRules(Base):
    __tablename__ = "conversation_rules"
    
    id= Column(Integer, primary_key=True) 
    conversation_id = Column(Integer)
    text = Column(Text, nullable=True)
