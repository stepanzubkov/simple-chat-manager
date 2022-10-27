"""Handlers only for admins"""
from typing import Optional
from sqlalchemy.orm import Session
from vkbottle.bot import Blueprint, Message
from vkbottle.dispatch.rules.base import VBMLRule, RegexRule

from blueprints.public.services.admins import AdminsService
from db.base import engine
from db.models import Roles


bp = Blueprint("for admin commands")
bp.labeler.vbml_ignore_case = True


@bp.on.chat_message(
    VBMLRule(["бан", "кик", "забанить"])
    | RegexRule(r"^(бан|кик|забанить) \[id(\d+)\|.+\]$")
)
async def ban(message: Message, match: Optional[tuple] = None):
    """Kicks user by reply message or by mention"""
    member_id = int(match[1]) if match else message.reply_message.from_id

    admins = AdminsService(bp.api, message.peer_id)
    all_admins = await admins.get_main_admins() + await admins.get_secondary_admins()
    all_admin_ids = [admin.id for admin in all_admins]

    if message.from_id in all_admin_ids:
        if member_id not in all_admin_ids:
            await bp.api.messages.remove_chat_user(
                message.peer_id - 2000000000, member_id
            )
            await message.reply(
                "Пользователь успешно забанен. Пусть больше не возвращается."
            )

        else:
            await message.reply("Админа невозможно забанить!")


@bp.on.chat_message(text=["дать админку"])
async def give_admin_role(message: Message):
    members = await bp.api.messages.get_conversation_members(message.peer_id)
    admin_ids = [member.member_id for member in members.items if member.is_admin]
    if message.from_id in admin_ids:
        user_id = message.reply_message.from_id
        with Session(engine) as session:

            role = Roles(
                vk_id=user_id,
                conversation_id=message.peer_id,
                role="admin",
            )

            session.add(role)
            session.commit()

        user = (await bp.api.users.get(user_ids=user_id))[0]

        await message.reply(
            f"*id{user_id} ({user.first_name} {user.last_name}), теперь ты админ!"
        )


@bp.on.chat_message(regex=r"^дать админку \[id(\d+)\|.+\]$")
async def give_admin_role_by_mention(message: Message, match: tuple):
    member_id = int(match[0])

    members = await bp.api.messages.get_conversation_members(message.peer_id)
    admin_ids = [member.member_id for member in members.items if member.is_admin]
    if message.from_id in admin_ids:
        with Session(engine) as session:

            role = Roles(
                vk_id=member_id,
                conversation_id=message.peer_id,
                role="admin",
            )

            session.add(role)
            session.commit()

        user = (await bp.api.users.get(user_ids=member_id))[0]

        await message.reply(
            f"*id{member_id} ({user.first_name} {user.last_name}), теперь ты админ!"
        )


@bp.on.chat_message(text=["забрать админку"])
async def delete_admin_role(message: Message):
    members = await bp.api.messages.get_conversation_members(message.peer_id)
    admin_ids = [member.member_id for member in members.items if member.is_admin]
    if message.from_id in admin_ids:
        user_id = message.reply_message.from_id
        with Session(engine) as session:

            session.query(Roles).where(
                Roles.vk_id == user_id,
                Roles.conversation_id == message.peer_id,
            ).delete()
            session.commit()

        user = (await bp.api.users.get(user_ids=user_id))[0]

        await message.reply(
            f"*id{user_id} ({user.first_name} {user.last_name}), к сожалению, теперь ты не админ."
        )


@bp.on.chat_message(regex=r"^(забрать|отобрать|убрать) админку \[id(\d+)\|.+\]$")
async def delete_admin_role_by_mention(message: Message, match: tuple):
    member_id = int(match[1])

    members = await bp.api.messages.get_conversation_members(message.peer_id)
    admin_ids = [member.member_id for member in members.items if member.is_admin]
    if message.from_id in admin_ids:
        with Session(engine) as session:

            session.query(Roles).where(
                Roles.vk_id == member_id,
                Roles.conversation_id == message.peer_id,
            ).delete()
            session.commit()

        user = (await bp.api.users.get(user_ids=member_id))[0]

        await message.reply(
            f"*id{member_id} ({user.first_name} {user.last_name}), к сожалению, теперь ты не админ."
        )
