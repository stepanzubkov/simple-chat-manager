from config import VK_API_KEY
from vkbottle import load_blueprints_from_package
from vkbottle.bot import Bot


bot = Bot(
    token=VK_API_KEY,
)
bot.labeler.vbml_ignore_case = True

for bp in load_blueprints_from_package("blueprints"):
    bp.load(bot)


bot.run_forever()
