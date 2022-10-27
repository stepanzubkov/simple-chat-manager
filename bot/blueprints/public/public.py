"""Public handlers"""

from pathlib import Path

import os
import random

from vkbottle import PhotoMessageUploader
from vkbottle.bot import Blueprint, Message

from blueprints.public.services.admins import AdminsService

bp = Blueprint("for public commands")
bp.labeler.vbml_ignore_case = True


@bp.on.chat_message(text=["бот"])
async def ping(message: Message):
    """Command for checking is bot launched"""

    await message.answer("На месте")


@bp.on.chat_message(text=["собака"])
async def dog_image(message: Message):
    """Sends dog image"""

    photo_uploader = PhotoMessageUploader(api=bp.api)
    attachment = await photo_uploader.upload(str(Path("images/dog.jpg").resolve()))
    await message.answer(attachment=attachment)


@bp.on.chat_message(text=["собака рандом", "собака случайная"])
async def dog_image_random(message: Message):
    """Sends random dog image from 13 images"""

    photo_uploader = PhotoMessageUploader(api=bp.api)

    dog_images_path = Path("images")
    dog_images = os.listdir(str(dog_images_path.resolve()))

    random_dog = random.choice(dog_images)
    attachment = await photo_uploader.upload(
        str((dog_images_path / random_dog).resolve())
    )
    await message.answer(attachment=attachment)


@bp.on.chat_message(text=["админы"])
async def list_admins(message: Message):
    """List main admins and secondary admins"""

    admins = AdminsService(bp.api, message.peer_id)

    message_text = "Главные админы:\n"
    main_admins = await admins.get_main_admins()
    for admin in main_admins:
        message_text += f"*id{admin.id} ({admin.first_name} {admin.last_name}) \n"

    message_text += "\nАдмины второго ранга:\n"
    secondary_admins = await admins.get_secondary_admins()
    for admin in secondary_admins:
        message_text += f"*id{admin.id} ({admin.first_name} {admin.last_name}) \n"

    await message.reply(message_text)
