import json
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
import os
from dotenv import load_dotenv
load_dotenv()
from telegram.ext import Application, CommandHandler, MessageHandler, filters 
from telegram import ReplyKeyboardMarkup


asyncio.set_event_loop(asyncio.new_event_loop()) 
CARTS = {}  # user_id: {item_id: qty}

def load_goods():
    with open("data/goods.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    goods = {}
    for item in data["items"]:
        item_id = int(item["id"])
        goods[item_id] = item

    return goods


GOODS = load_goods()


async def start(update, context):
    keyboard = [
        ["Каталог", "Поиск"],
        ["Корзина"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Привет! Выбирай:", reply_markup=reply_markup)



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
    items = GOODS  # словарь {id: item}

    text = "Каталог товаров:\n"
    for item_id, item in items.items():
        _id = item.get("id", "?")
        name = item.get("type", item.get("name", "Товар"))
        price = item.get("price", 0)
        stock = item.get("stock", 0)
        text += f"#{item_id} — {name} | €{price} | остаток:{stock}\n"

    await update.message.reply_text(text)



async def show_cart(update, context):
    user_id = update.effective_user.id
    cart = CARTS.get(user_id, {})

    if not cart:
        await update.message.reply_text("Ваша корзина пуста.")
        return



    text = "Ваша корзина:\n\n"
    total = 0

    for item_id, qty in cart.items():
        it = GOODS.get(item_id)
        if not it:
            continue

        name = it.get("type", it.get("name", "Товар"))
        price = int(it.get("price", 0))
        line_sum = price * qty
        total += line_sum

        text += f"#{item_id} — {name} × {qty} = €{line_sum}\n"

    text += f"\nИтог: €{total}"
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

    item = GOODS.get(item_id)

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


async def remove_from_cart(update, context):
     if not context.args:
        await update.message.reply_text("Напиши так: /remove 1")
        return

     try:
        item_id = int(context.args[0])
     except ValueError:
        await update.message.reply_text("ID должен быть числом. Пример: /remove 1")
        return

     user_id = update.effective_user.id
     cart = CARTS.setdefault(user_id, {})

     if item_id not in cart:
        await update.message.reply_text("Этого товара нет в корзине.")
        return


     cart[item_id] -= 1
     if cart[item_id] <= 0:
        del cart[item_id]

     if not cart:
        CARTS.pop(user_id, None)

        await update.message.reply_text("- Убрал 1 штуку. Посмотреть: /cart")


async def clear_cart(update, context):
    user_id = update.effective_user.id
    CARTS.pop(user_id, None)
    await update.message.reply_text("Корзина очищена. Посмотреть: /cart")


async def on_menu_button(update, context):
    q = update.callback_query
    await q.answer()

    if q.data == "menu:home":
        await q.edit_message_text("Привет! Выбирай:", reply_markup=kb_main())
        return

    if q.data == "menu:catalog":
        # используем структуру goods
        text = "Каталог товаров:"
        return

    if q.data == "menu:cart":
        # вызываем show_cart
        await show_cart(update, context)
        return



async def on_cart_button(update, context):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id

    # формат cart:add:1
    parts = q.data.split(":")
    Action == parts[1]

    if action == "add":
        item_id = int(parts[2])
        # переиспользуем add_to_cart логику
        # минилогика тут 
        cart = CARTS.setdefault(user_id, {})
        if item_ not in GOODS:
            await q.edit_message_text(f"Товар #{item_id} не найден.", reply_markup=kb_cart_actions(False))
            return

    
    if action == "clear":
        CARTS.pop(user_id, None)
        await q.edit_message_text("Корзина очищена.", reply_markup=kb_cart_actions(False))
        return


async def on_pay_button(update, context):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("Sorry, оформление заказа пока не реализовано.", reply_markup=kb_main())
    



def kb_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Каталог", callback_data="meny:catalog")]
        [InlineKeyboardButton("Корзина", callback_data="menu:cart")]
    ])

def kb_catalog(goods: dict):
    rows = []
    for item_id, item in goods.items():
        name = item.get("name",f"Товар #{item_id}")
        price = item.get("price","?")
        stock = item.get("stock", item.get("остаток", item.get("left", ""))) #на всякий 
        label = f"+ #{item_id} {name} (€{price})"
        rows.append([InlineKeyboardButton(label, callback_data=f"cart:add:{item_id}")])

    rows.append([InlineKeyboardButton("Корзина", callback_data="menu:cart")])
    rows.append([InlineKeyboardButton("Меню", callback_data="menu:home")])
    return InlineKeyboardMarkup(rows)

    def kb_actions(has_items: bool):
        rows = []
        if has_items:
            rows.append([InlineKeyboardButton("Очистить", callback_data="cart:clear")])
        rows.append([InlineKeyboardButton("Оформить (позже)", callback_data="pay:checkout")])
        rows.append([InlineKeyboardButton("Меню", callback_data="menu:home")])
        return InlineKeyboardMarkup(rows)




def main():
    token = os.getenv("BOT_TOKEN")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("catalog", catalog))
    app.add_handler(CommandHandler("cart", show_cart))
    app.add_handler(CommandHandler("add", add_to_cart))
    app.add_handler(CommandHandler("remove", remove_from_cart))
    app.add_handler(CommandHandler("clear", clear_cart))
    app.add_handler(CallbackQueryHandler(on_menu_button, pattern=r"^menu:"))
    app.add_handler(CallbackQueryHandler(on_cart_button, pattern=r"^cart:"))
    app.add_handler(CallbackQueryHandler(on_pay_button, pattern=r"^pay:"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_router))

    print("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()

    
