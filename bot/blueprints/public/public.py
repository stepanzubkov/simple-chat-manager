"""Public handlers"""

from pathlib import Path

import aiohttp
from sqlalchemy.orm import Session
from vkbottle import PhotoMessageUploader
from vkbottle.bot import Blueprint, Message

from services.admins import AdminsService
from db.models import ConversationRules
from db.base import engine
from db.crud.immunity import get_immunities
import config

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
    if not config.DOG_API_KEY:
        await message.answer("Сервис для получения картинок собак ещё не сконфигурирован.")
        return
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{config.DOG_API_PROVIDER_URL}v1/images/search?format=json&limit=1",
            headers={
                "x-api-key": config.DOG_API_KEY,
            },
        ) as response:

            if response.status != 200:
                await message.reply(f"Произошла ошибка с получением картинки собаки. Код ошибки: {response.status_code}")
                return

            async with session.get((await response.json())[0]["url"]) as image_response: 
                image = await image_response.read()

    with open("images/dog_temp.jpg", "wb") as temp:
        temp.write(image)

    photo_uploader = PhotoMessageUploader(api=bp.api)
    attachment = await photo_uploader.upload(str(Path("images/dog_temp.jpg").resolve()))
    await message.answer(attachment=attachment)


@bp.on.chat_message(text=["роли", "роли беседы"])
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

    message_text += "\nИммунитет:\n"
    immunities = await get_immunities(bp.api, message.peer_id)
    for immunity in immunities:
        message_text += f"*id{immunity.id} ({immunity.first_name} {immunity.last_name}) \n"

    await message.reply(message_text)


@bp.on.chat_message(text=["самобан", "самокик"])
async def self_ban(message: Message):
    """Bans author of message"""
    admins = AdminsService(bp.api, message.peer_id)
    all_admins = await admins.get_main_admins() + await admins.get_secondary_admins()
    all_admin_ids = [admin.id for admin in all_admins]
    if message.from_id not in all_admin_ids:
        await bp.api.messages.remove_chat_user(
            message.peer_id - 2000000000,
            message.from_id,
        )
        await message.reply("Прощай...")

    else:
        await message.reply("Самобан не разрешён для админов")


@bp.on.chat_message(text="правила")
async def get_rules(message: Message):
    session = Session(engine)
    rules = session.query(ConversationRules).filter_by(conversation_id=message.peer_id).first()
    if rules:
        await message.reply(f"Правила беседы: {rules.text}")
    else:
        await message.reply("Правила беседы ещё не установлены")
