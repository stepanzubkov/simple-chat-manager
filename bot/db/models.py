from sqlalchemy import Column, Integer, String

from db.base import Base


class Roles(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer)
    conversation_id = Column(Integer)
    role = Column(String(30))
