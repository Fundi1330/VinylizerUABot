from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Bot, LabeledPrice
from bot.config import config

# the callback data is stored like this "duration of the subscription(in months), price"
keyboard = []
plans: dict = config.get('plans', None)

if plans is None:
    raise ValueError('"plans" should be set in config')

async def generate_premium_invoice_keyboard(bot: Bot):
    for plan in plans:
        title = f"Купити преміум на {plan['length']} місяць"
        link = await bot.create_invoice_link(
            title=title,
            description='Test',
            payload=config.get('payload'),
            currency='XTR',
            prices=[LabeledPrice(title, plan['price'])]
        )
        keyboard.append(
            [InlineKeyboardButton(title + f" за {plan['price']}⭐", url=link)],
        )

    return InlineKeyboardMarkup(keyboard)