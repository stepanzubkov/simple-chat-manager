"""Handlers only for admins"""
from typing import Optional
import re

from sqlalchemy.orm import Session
from vkbottle.bot import Blueprint, Message
from vkbottle.dispatch.rules.base import VBMLRule, RegexRule

from blueprints.public.services.admins import AdminsService
from db.base import engine
from db.models import Roles, ConversationRules

bp = Blueprint("for admin commands")


@bp.on.chat_message(
    VBMLRule(["бан", "кик", "забанить"])
    | RegexRule(re.compile(r"^(бан|кик|забанить) \[id(\d+)\|.+\]$", re.IGNORECASE))
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


@bp.on.chat_message(
    VBMLRule(["дать админку", "выдать админку"])
    | RegexRule(re.compile(r"^(дать|выдать) админку \[id(\d+)\|.+\]$", re.IGNORECASE))
)
async def give_admin_role(message: Message, match: tuple = None):
    """Gives admin role by reply message or by mention"""
    member_id = int(match[1]) if match else message.reply_message.from_id

    admins = AdminsService(bp.api, message.peer_id)
    main_admins = await admins.get_main_admins()
    main_admin_ids = [admin.id for admin in main_admins]
    if message.from_id in main_admin_ids:
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


@bp.on.chat_message(
    VBMLRule(["забрать админку", "отобрать админку", "убрать админку"])
    | RegexRule(
        re.compile(
            r"^(забрать|отобрать|убрать) админку \[id(\d+)\|.+\]$", re.IGNORECASE
        )
    )
)
async def delete_admin_role(message: Message, match: tuple = None):
    """Deletes admin role by reply message or by mention"""
    member_id = int(match[1]) if match else message.reply_message.from_id

    admins = AdminsService(bp.api, message.peer_id)
    main_admins = await admins.get_main_admins()
    main_admin_ids = [admin.id for admin in main_admins]
    if message.from_id in main_admin_ids:
        with Session(engine) as session:
            admin_role = session.query(Roles).where(
                Roles.vk_id == member_id,
                Roles.conversation_id == message.peer_id,
                Roles.role == "admin",
            )
            if admin_role.count() > 0:
                admin_role.delete()
                session.commit()
                user = (await bp.api.users.get(user_ids=member_id))[0]

                await message.reply(
                    f"*id{member_id} ({user.first_name} {user.last_name}), к сожалению, теперь ты не админ."
                )
            else:
                await message.reply("У пользователя не было админки")

@bp.on.chat_message(text="новые правила <new_rules>")
async def new_rules(message: Message, new_rules: str):
    admins = AdminsService(bp.api, message.peer_id)
    all_admins = await admins.get_main_admins() + await admins.get_secondary_admins()
    all_admin_ids = [admin.id for admin in all_admins]
    if message.from_id in all_admin_ids:
        session = Session(engine)
        rules = session.query(ConversationRules).filter_by(conversation_id=message.peer_id).first()
        if rules:
            rules.text = new_rules

            await message.reply("Правила беседы обновлены")
        else:
            rules = ConversationRules(conversation_id=message.peer_id, text=new_rules)
            session.add(rules)

            await message.reply("Правила беседы установлены")

        
        session.commit()
        session.close()

