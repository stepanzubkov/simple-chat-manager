from sqlalchemy import select
from sqlalchemy.orm import Session
from vkbottle.bot import Blueprint, Message

from db.base import engine
from db.models import Roles


bp = Blueprint("for admin commands")
bp.labeler.vbml_ignore_case = True


@bp.on.chat_message(text=["бан", "кик", "забанить"])
async def ban(message: Message):
    members = await bp.api.messages.get_conversation_members(message.peer_id)
    admin_ids = [member.member_id for member in members.items if member.is_admin]
    session = Session(engine)
    secondary_admins = select(Roles).where(Roles.role == "admin")
    secondary_admin_ids = [admin.vk_id for admin in session.scalars(secondary_admins)]

    if message.from_id in admin_ids or message.from_id in secondary_admin_ids:
        if message.reply_message.from_id not in secondary_admin_ids + admin_ids:
            await bp.api.messages.remove_chat_user(
                message.peer_id - 2000000000, message.reply_message.from_id
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


@bp.on.chat_message(text=["забрать админку"])
async def delete_admin_role(message: Message):
    members = await bp.api.messages.get_conversation_members(message.peer_id)
    admin_ids = [member.member_id for member in members.items if member.is_admin]
    if message.from_id in admin_ids:
        user_id = message.reply_message.from_id
        with Session(engine) as session:

            session.query(Roles).where(Roles.vk_id == user_id).delete()
            session.commit()

        user = (await bp.api.users.get(user_ids=user_id))[0]

        await message.reply(
            f"*id{user_id} ({user.first_name} {user.last_name}), к сожалению, теперь ты не админ."
        )
