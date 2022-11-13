"""Services for getting admins"""
from typing import List

from vkbottle import API
from vkbottle_types.codegen.objects import UsersUserFull
from sqlalchemy.orm import Session
from sqlalchemy import select

from db.base import engine
from db.models import Roles


class AdminsService:
    def __init__(self, api: API, peer_id: int):
        self._api = api
        self._peer_id = peer_id

    async def get_main_admins(self) -> List[UsersUserFull]:
        members = await self._api.messages.get_conversation_members(self._peer_id)
        admin_ids = [member.member_id for member in members.items if member.is_admin]
        admin_profiles = []
        for user in members.profiles:
            if user.id in admin_ids:
                admin_profiles.append(user)

        return admin_profiles

    async def get_secondary_admins(self) -> List[UsersUserFull]:
        session = Session(engine)
        secondary_admins = select(Roles).where(
            Roles.role == "admin",
            Roles.conversation_id == self._peer_id,
        )
        secondary_admin_ids = [
            admin.vk_id for admin in session.scalars(secondary_admins)
        ]

        users = await self._api.users.get(user_ids=secondary_admin_ids)
        return users
