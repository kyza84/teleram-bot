import json
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters 
from telegram import ReplyKeyboardMarkup


asyncio.set_event_loop(asyncio.new_event_loop()) 
CARTS = {}   # user_id: {item_id: qty}


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
        await show_cart(update, context)
        return

    if text == "Поиск":
        await update.message.reply_text("Поиск пока в разработке 🔍")
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


async def show_cart(update, context):
    user_id = update.message.from_user.id
    cart = CARTS.get(user_id, {})   

    if not cart:
        await update.message.reply_text("Ваша корзина пуста.")
        return

    items = load_goods()
    items_by_id = {it.get("id"): it for it in items}

    text = "Ваша корзина:\n\n"
    total = 0

    for item_id, qty in cart.items():
        it = items_by_id.get(item_id)
        if not it:
            continue
        name = it.get("type", "Товар")
        price = int(it.get("price", 0))
        line_sum = price * qty
        total += line_sum
        text += f"#{item_id} — {name} x {qty} = €{line_sum}\n"

    text += f"\nИтого: €{total}"
    await update.message.reply_text(text)


async def add_to_cart(update, context):
    # /add 1
    if not context.args:
        await update.message.reply_text("Укажите ID товара. Пример: /add 1")
        return

    try:
        item_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID Должен быть числом. Пример: /add 1")
        return
    items = load_goods()
    item = next((it for it in items if it.get("id") == item_id), None)

    if not item:  
        await update.message.reply_text(f"Товар с ID #{item_id} не найден.")
        return

    user_id = update.effective_user.id
    cart = CARTS.setdefault(user_id, {})

    curerent_qty = cart.get(item_id, 0)
    stock = item.get("stock", 0)

    if curerent_qty + 1 >= stock:
        await update.message.reply_text(f"Недостаточно товара на складе. Остаток: {stock}, в вашей корзине: {curerent_qty}")
        return

    cart[item_id] = curerent_qty + 1

    name = item.get("type", "Товар")
    await update.message. reply_text(
        f"Добавил в корзину: #{item_id} — {name}\n"
        f"Теперь в вашей корзине: {cart[item_id]}\n\n"
        f"Открыть корзину: /cart"
    )


def main():
    # ВСТАВЬ СВОЙ ТОКЕН СЮДА:
    token = "YOUR_BOT_TOKEN"

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("catalog", catalog))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cart", show_cart))
    app.add_handler(CommandHandler("add", add_to_cart))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_router))


    print("Бот запущен. Напиши /catalog в Telegram")
    app.run_polling()


if __name__ == "__main__":
    main()
