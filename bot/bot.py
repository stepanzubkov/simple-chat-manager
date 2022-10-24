from config import VK_API_KEY
from vkbottle.bot import Bot

from blueprints import bps


bot = Bot(
    token=VK_API_KEY,
)
bot.labeler.vbml_ignore_case = True

for bp in bps:
    bp.load(bot)


bot.run_forever()
