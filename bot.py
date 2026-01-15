import json
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters 
from telegram import ReplyKeyboardMarkup


asyncio.set_event_loop(asyncio.new_event_loop()) 

def load_goods():
    with open("data/goods.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data["items"]

async def start(update, context):
    keyboard = [
        ["Каталог", "Поиск"],
        ["Корзина"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Добро пожаловать в магазин! \nВыберите действие:",
        reply_markup=reply_markup
    )


async def menu_router(update, context):
    text = update.message.text

    if text == "Каталог":
        await catalog(update, context)
        return

        if text == "Корзина":
            await update.message.reply_text("Корзина пока в разработке ().")
            return

            if text == "Поиск":
                await update.message.reply_text("Поиск пока в разработке ().")
                return

    await update.message.reply_text("Не понял. Нажми кнопку в меню или /start.")


async def catalog(update, context):
    items = load_goods()

    if not items:
        await update.message.reply_text("Каталог пуст.")
        return

    text = " Каталог товаров:\n\n"
    for item in items:
        _id = item.get("id", "?")
        t = item.get("type", "без названия")
        pc = item.get("pricecategory", "—")
        price = item.get("price", "—")
        stock = item.get("stock", "—")
        text += f"#{_id} — {t} | {pc} | €{price} | остаток: {stock}\n"

    await update.message.reply_text(text)


def main():
    # ВСТАВЬ СВОЙ ТОКЕН СЮДА:
    token = "BOT_TOKEN_HERE"

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("catalog", catalog))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_router))


    print("Бот запущен. Напиши /catalog в Telegram")
    app.run_polling()


if __name__ == "__main__":
    main()
