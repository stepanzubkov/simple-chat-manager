from typing import List
from vkbottle_types.codegen.objects import MessagesGetConversationMembers, UsersUserFull


def get_main_admins(members: MessagesGetConversationMembers) -> List[UsersUserFull]:
    admin_ids = [member.member_id for member in members.items if member.is_admin]
    admin_profiles = []
    for user in members.profiles:
        if user.id in admin_ids:
            admin_profiles.append(user)

    return admin_profiles
