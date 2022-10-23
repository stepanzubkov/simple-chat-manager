from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import select
from vkbottle import PhotoMessageUploader
from vkbottle.bot import Blueprint, Message

from db.base import engine
from db.models import Roles

bp = Blueprint("for public commands")
bp.labeler.vbml_ignore_case = True


@bp.on.chat_message(text=["бот"])
async def ping(message: Message):
    await message.answer("На месте")


@bp.on.chat_message(text=["собака"])
async def dog_image(message: Message):
    photo_uploader = PhotoMessageUploader(api=bp.api)
    attachment = await photo_uploader.upload(str(Path("images/dog.jpg").resolve()))
    await message.answer(attachment=attachment)
    message_id = message.get_message_id()
    await bp.api.messages.delete(
        peer_id=message.peer_id,
        message_ids=message_id,
        delete_for_all=True,
    )


@bp.on.chat_message(text=["админы"])
async def list_admins(message: Message):
    response = "Главные админы:\n"
    members = await bp.api.messages.get_conversation_members(message.peer_id)
    for member in members.items:
        if member.is_admin:
            response += (
                f"*id{member.member_id} ({member.first_name} {member.last_name}) \n"
            )

    session = Session(engine)
    response += "\nАдмины второго ранга: \n"
    secondary_admins = select(Roles).where(Roles.role == "admin")
    secondary_admin_ids = [admin.vk_id for admin in session.scalars(secondary_admins)]

    users = await bp.api.users.get(user_ids=secondary_admin_ids)
    for user in users:
        response += f"*id{user.id} ({user.first_name} {user.last_name}) \n"

    await message.reply(response)
