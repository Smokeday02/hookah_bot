import json
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "8747058515:AAEXyeJVmm4V-xSQvOEXETzMuuHrPcv9DAA"
ADMIN_ID = 1962562160

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

orders = {}
clients = {}

# загрузка базы клиентов
try:
    with open("clients.json", "r") as f:
        clients = json.load(f)
except:
    clients = {}

def save_clients():
    with open("clients.json", "w") as f:
        json.dump(clients, f)

# главное меню
location_button = KeyboardButton("📍 Отправить геолокацию", request_location=True)

menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add("📦 Выбрать комплект")
menu.add("📱 Основной номер")
menu.add("☎️ Доп номер")
menu.add("🚚 Доставка", "🏠 Самовывоз")
menu.add(location_button)
menu.add("📝 Пожелания")
menu.add("📄 Отправить удостоверение")
menu.add("📋 Проверить заказ")
menu.add("✅ Оформить заказ")

# старт
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    orders[message.from_user.id] = {}
    await message.answer(
        "Добро пожаловать в аренду кальянов 🚬",
        reply_markup=menu
    )

# выбор комплекта
@dp.message_handler(lambda m: m.text == "📦 Выбрать комплект")
async def choose_pack(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Стандарт - 7000")
    kb.add("Премиум - 10000")
    kb.add("VIP - 15000")
    kb.add("⬅ Назад")
    await message.answer("Выберите комплект", reply_markup=kb)

@dp.message_handler(lambda m: "7000" in m.text or "10000" in m.text or "15000" in m.text)
async def save_pack(message: types.Message):
    orders[message.from_user.id]["pack"] = message.text
    await message.answer("Комплект сохранён ✅", reply_markup=menu)

# основной номер
@dp.message_handler(lambda m: m.text == "📱 Основной номер")
async def main_phone(message: types.Message):
    await message.answer("Введите основной номер телефона")

@dp.message_handler(lambda m: m.text.startswith("8") or m.text.startswith("+"))
async def save_phone(message: types.Message):
    orders[message.from_user.id]["phone"] = message.text
    await message.answer("Номер сохранён ✅", reply_markup=menu)

# дополнительный номер
@dp.message_handler(lambda m: m.text == "☎️ Доп номер")
async def extra_phone(message: types.Message):
    await message.answer("Введите дополнительный номер")

@dp.message_handler()
async def save_extra(message: types.Message):
    user_id = message.from_user.id
    if "phone" in orders[user_id] and "extra_phone" not in orders[user_id]:
        orders[user_id]["extra_phone"] = message.text
        await message.answer("Доп номер сохранён", reply_markup=menu)

# доставка
@dp.message_handler(lambda m: m.text == "🚚 Доставка")
async def delivery(message: types.Message):
    orders[message.from_user.id]["delivery"] = "Доставка"
    await message.answer("Введите адрес доставки")

# самовывоз
@dp.message_handler(lambda m: m.text == "🏠 Самовывоз")
async def pickup(message: types.Message):
    orders[message.from_user.id]["delivery"] = "Самовывоз"
    await message.answer("Самовывоз выбран", reply_markup=menu)

# сохранение адреса
@dp.message_handler()
async def save_address(message: types.Message):
    user_id = message.from_user.id
    if orders[user_id].get("delivery") == "Доставка" and "address" not in orders[user_id]:
        orders[user_id]["address"] = message.text
        await message.answer("Адрес сохранён", reply_markup=menu)

# геолокация
@dp.message_handler(content_types=types.ContentType.LOCATION)
async def location(message: types.Message):
    orders[message.from_user.id]["location"] = message.location
    await message.answer("Геолокация получена 📍", reply_markup=menu)

# пожелания
@dp.message_handler(lambda m: m.text == "📝 Пожелания")
async def wish(message: types.Message):
    await message.answer("Напишите пожелания")

@dp.message_handler()
async def save_wish(message: types.Message):
    user_id = message.from_user.id
    if "wish" not in orders[user_id]:
        orders[user_id]["wish"] = message.text
        await message.answer("Пожелания сохранены", reply_markup=menu)

# удостоверение
@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def document(message: types.Message):
    if message.document.mime_type == "application/pdf":
        orders[message.from_user.id]["doc"] = message.document.file_id
        await message.answer("PDF удостоверение получено ✅", reply_markup=menu)
    else:
        await message.answer("Пожалуйста отправьте удостоверение в PDF")

# проверка заказа
@dp.message_handler(lambda m: m.text == "📋 Проверить заказ")
async def check(message: types.Message):
    data = orders.get(message.from_user.id)
    text = f"""
Ваш заказ:

Комплект: {data.get("pack")}
Телефон: {data.get("phone")}
Доп номер: {data.get("extra_phone")}
Способ: {data.get("delivery")}
Адрес: {data.get("address")}
Пожелания: {data.get("wish")}
"""
    await message.answer(text)

# оформление
@dp.message_handler(lambda m: m.text == "✅ Оформить заказ")
async def finish(message: types.Message):
    user_id = message.from_user.id
    data = orders.get(user_id)

    if not data.get("pack"):
        await message.answer("Выберите комплект")
        return
    if not data.get("phone"):
        await message.answer("Введите основной номер")
        return
    if not data.get("doc"):
        await message.answer("Отправьте PDF удостоверение")
        return

    # база клиентов
    today = str(datetime.date.today())
    if str(user_id) not in clients:
        clients[str(user_id)] = {"phone": data["phone"], "orders": 1, "last_order": today}
    else:
        clients[str(user_id)]["orders"] += 1
        clients[str(user_id)]["last_order"] = today
    save_clients()

    # цена
    price = 0
    if "7000" in data["pack"]:
        price = 7000
    elif "10000" in data["pack"]:
        price = 10000
    elif "15000" in data["pack"]:
        price = 15000
    if data.get("delivery") == "Доставка":
        price += 2000

    text = f"""
🔥 Новый заказ

Клиент: @{message.from_user.username}

Телефон: {data.get("phone")}
Доп номер: {data.get("extra_phone")}

Комплект: {data.get("pack")}
Способ: {data.get("delivery")}
Адрес: {data.get("address")}

Пожелания:
{data.get("wish")}

Итого: {price} тг
"""
    admin_kb = InlineKeyboardMarkup()
    admin_kb.add(
        InlineKeyboardButton("✅ Принять", callback_data=f"accept_{user_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"decline_{user_id}")
    )
    admin_kb.add(
        InlineKeyboardButton("🚚 Курьер выехал", callback_data=f"courier_{user_id}")
    )

    await bot.send_message(ADMIN_ID, text, reply_markup=admin_kb)
    if "location" in data:
        await bot.send_location(ADMIN_ID, data["location"].latitude, data["location"].longitude)
    await bot.send_document(ADMIN_ID, data["doc"])
    await message.answer("Заказ отправлен 🤝")

# кнопки админа
@dp.callback_query_handler(lambda c: True)
async def admin_buttons(callback: types.CallbackQuery):
    action, user_id = callback.data.split("_")
    user_id = int(user_id)
    if action == "accept":
        await bot.send_message(user_id, "✅ Ваш заказ принят")
    elif action == "decline":
        await bot.send_message(user_id, "❌ Заказ отклонён")
    elif action == "courier":
        await bot.send_message(user_id, "🚚 Курьер выехал")
    await callback.answer()

executor.start_polling(dp)