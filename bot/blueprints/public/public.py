from pathlib import Path

import os
import random

from sqlalchemy.orm import Session
from sqlalchemy import select
from vkbottle import PhotoMessageUploader
from vkbottle.bot import Blueprint, Message

from .utils import get_main_admins

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
    message_id = message.conversation_message_id
    await bp.api.messages.delete(
        peer_id=message.peer_id,
        cmids=message_id,
        delete_for_all=True,
    )


@bp.on.chat_message(text=["собака рандом"])
async def dog_image_random(message: Message):
    photo_uploader = PhotoMessageUploader(api=bp.api)
    dog_images_path = Path("images")
    dog_images = os.listdir(str(dog_images_path.resolve()))
    random_dog = random.choice(dog_images)
    attachment = await photo_uploader.upload(
        str((dog_images_path / random_dog).resolve())
    )
    await message.answer(attachment=attachment)
    message_id = message.conversation_message_id
    await bp.api.messages.delete(
        peer_id=message.peer_id,
        cmids=message_id,
        delete_for_all=True,
    )


@bp.on.chat_message(text=["админы"])
async def list_admins(message: Message):
    response = "Главные админы:\n"
    members = await bp.api.messages.get_conversation_members(message.peer_id)
    for admin in get_main_admins(members):
        response += f"*id{admin.id} ({admin.first_name} {admin.last_name})"

    session = Session(engine)
    response += "\nАдмины второго ранга: \n"
    secondary_admins = select(Roles).where(
        Roles.role == "admin",
        Roles.conversation_id == message.peer_id,
    )
    secondary_admin_ids = [admin.vk_id for admin in session.scalars(secondary_admins)]

    users = await bp.api.users.get(user_ids=secondary_admin_ids)
    for user in users:
        response += f"*id{user.id} ({user.first_name} {user.last_name}) \n"

    await message.reply(response)
