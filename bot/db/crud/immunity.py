from sqlalchemy.orm import Session
from vkbottle_types.codegen.objects import UsersUserFull
from vkbottle import API

from db.models import Roles
from db.base import engine

def give_immunity(vk_id: int, conversation_id: int) -> None:
    """Gives immunity role by vk_id in conversation"""
    with Session(engine) as session:
        immunity = Roles(
            vk_id=vk_id,
            conversation_id=conversation_id,
            role="immunity",
        )

        session.add(immunity)
        session.commit()


def delete_immunity(vk_id: int, conversation_id: int) -> None:
    """Deletes immunity role in conversation"""
    with Session(engine) as session:
        session.query(Roles).filter_by(
            conversation_id=conversation_id,
            vk_id=vk_id,
            role="immunity",
        ).delete()
        session.commit()


def check_immunity(vk_id: int, conversation_id: int) -> bool:
    """Checks that user has an immunity in conversation"""
    with Session(engine) as session:
        immunity = session.query(Roles).filter_by(
            conversation_id=conversation_id,
            vk_id=vk_id,
            role="immunity",
        ).first()

        return bool(immunity)


async def get_immunities(api: API, conversation_id: int) -> list[UsersUserFull]:
    """Returns all immunity roles in conversation"""
    with Session(engine) as session:
        immunities = session.query(Roles).filter_by(
            conversation_id=conversation_id,
            role="immunity",
        ).all()

        immunity_ids = [
            immunity.vk_id for immunity in immunities
        ]

        users = await api.users.get(user_ids=immunity_ids)
        return users
