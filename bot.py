import json
import asyncio
from telegram.ext import Application, CommandHandler


asyncio.set_event_loop(asyncio.new_event_loop()) 

def load_goods():
    with open("data/goods.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data["items"]


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
    token = "BOT_TOKEN"

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("catalog", catalog))

    print("Бот запущен. Напиши /catalog в Telegram")
    app.run_polling()


if __name__ == "__main__":
    main()
