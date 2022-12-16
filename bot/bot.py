from config import VK_API_KEY
from vkbottle.bot import Bot

from blueprints.public.public import bp as public_bp
from blueprints.admin import bp as admin_bp


bot = Bot(
    token=VK_API_KEY,
)
bot.labeler.vbml_ignore_ = True

bps = [public_bp, admin_bp]
for bp in bps:
    bp.load(bot)


bot.run_forever()
