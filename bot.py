import json
import datetime
import os
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# =======================
# SQLite база
# =======================
conn = sqlite3.connect("bot.db")  # подключение к базе
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")

def create_client_if_not_exists(user_id, phone=None):
    cursor.execute("SELECT * FROM clients WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO clients (user_id, main_phone) VALUES (?, ?)",
            (user_id, phone)
        )
        conn.commit()

# таблица клиентов
cursor.execute("""
CREATE TABLE IF NOT EXISTS clients (
    user_id INTEGER PRIMARY KEY,
    main_phone TEXT,
    extra_phone TEXT
)
""")

# таблица заказов
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    pack TEXT,
    status TEXT DEFAULT 'new', -- new, active, completed, declined
    FOREIGN KEY(user_id) REFERENCES clients(user_id)
)
""")
conn.commit()

# =======================
# Функции для работы с базой
# =======================
def create_order(user_id, pack):
    cursor.execute(
        "INSERT INTO orders (user_id, pack, status) VALUES (?, ?, 'new')",
        (user_id, pack)
    )
    conn.commit()

# =======================
# Переменные окружения
# =======================
TOKEN = "8747058515:AAEXyeJVmm4V-xSQvOEXETzMuuHrPcv9DAA"      # токен от BotFather
ADMIN_ID = 1962562160 # твой Telegram ID

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# =======================
# Базы данных
# =======================
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

# =======================
# FSM для ввода данных
# =======================
class Form(StatesGroup):
    main_phone = State()
    extra_phone = State()
    address = State()
    wish = State()

# =======================
# Главное меню
# =======================
location_button = KeyboardButton("📍 Отправить геолокацию", request_location=True)
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add("📦 Выбрать комплект")
menu.add("📱 Основной номер")
menu.add("☎️ Дополнительный номер")
menu.add("🚚 Доставка", "🏠 Самовывоз")
menu.add(location_button)
menu.add("📝 Пожелания")
menu.add("📄 Отправить удостоверение")
menu.add("📋 Проверить заказ")
menu.add("✅ Оформить заказ")

# =======================
# Хендлеры
# =======================

# старт
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in orders:
        orders[user_id] = {}
    await message.answer("Здравствуйте, можете выбрать комплект 🚬", reply_markup=menu)

# выбор комплекта
@dp.message_handler(lambda m: m.text == "📦 Выбрать комплект")
async def choose_pack(message: types.Message):
    user_id = message.from_user.id
    if user_id not in orders:
        orders[user_id] = {}
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Легкий - 10000", "Средний - 13000", "Крепкий - 16000")
    await message.answer("Выберите комплект", reply_markup=kb)

@dp.message_handler(lambda m: m.text == "Легкий - 10000", state=None)
async def save_pack(message: types.Message):

    text = """
🔥 Легкий

В комплект входит:
• Кальян
• Табак легкий на 2 забивки
• Угли 6 шт
• Мундштуки
• Калауд
• Шипцы
• Плитка + 2000 тг

Цена: 10000 тг
"""

    await message.answer(text)
    user_id = message.from_user.id
    pack = message.text
    create_client_if_not_exists(user_id, phone=orders.get(user_id, {}).get("phone"))
    if user_id not in orders:
        orders[user_id] = {}
    orders[user_id]["pack"] = message.text
    create_order(user_id, pack)
    await message.answer("Комплект сохранён ✅", reply_markup=menu)

@dp.message_handler(lambda m: m.text == "Средний - 13000", state=None)
async def save_pack(message: types.Message):

    text = """
🔥 Средний

В комплект входит:
• Кальян
• Средний табак на 2 забивки
• Угли 6 шт
• Мундштуки
• Калауд
• Шипцы
• Плитка в комплекте

Цена: 13000 тг
"""

    await message.answer(text)
    user_id = message.from_user.id
    pack = message.text
    create_client_if_not_exists(user_id, phone=orders.get(user_id, {}).get("phone"))
    if user_id not in orders:
        orders[user_id] = {}
    orders[user_id]["pack"] = message.text
    create_order(user_id, pack)
    await message.answer("Комплект сохранён ✅", reply_markup=menu)

@dp.message_handler(lambda m: m.text == "Крепкий - 16000", state=None)
async def save_pack(message: types.Message):

    text = """
🔥 Крепкий

В комплект входит:
• Кальян
• Крепкий табак на 2 забивки
• Угли 6 шт
• Мундштуки
• Калауд
• Шипцы
• Плитка в комплекте

Цена: 16000 тг
"""

    await message.answer(text)
    user_id = message.from_user.id
    pack = message.text
    create_client_if_not_exists(user_id, phone=orders.get(user_id, {}).get("phone"))
    if user_id not in orders:
        orders[user_id] = {}
    orders[user_id]["pack"] = message.text
    create_order(user_id, pack)
    await message.answer("Комплект сохранён ✅", reply_markup=menu)

# основной номер
@dp.message_handler(lambda m: m.text == "📱 Основной номер")
async def main_phone(message: types.Message):
    await Form.main_phone.set()
    await message.answer("Введите основной номер телефона (обязательно)")

@dp.message_handler(state=Form.main_phone)
async def save_main_phone(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in orders:
        orders[user_id] = {}
    orders[user_id]["phone"] = message.text
    await message.answer("Основной номер сохранён ✅", reply_markup=menu)
    await state.finish()

# дополнительный номер
@dp.message_handler(lambda m: m.text == "☎️ Дополнительный номер")
async def extra_phone(message: types.Message):
    await Form.extra_phone.set()
    await message.answer("Введите дополнительный номер телефона")

@dp.message_handler(state=Form.extra_phone)
async def save_extra_phone(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in orders:
        orders[user_id] = {}
    orders[user_id]["extra_phone"] = message.text
    await message.answer("Дополнительный номер сохранён ✅", reply_markup=menu)
    await state.finish()

# доставка
@dp.message_handler(lambda m: m.text == "🚚 Доставка")
async def delivery(message: types.Message):
    user_id = message.from_user.id
    if user_id not in orders:
        orders[user_id] = {}
    orders[user_id]["delivery"] = "Доставка"
    await Form.address.set()
    await message.answer("Введите адрес доставки")

@dp.message_handler(state=Form.address)
async def save_address(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in orders:
        orders[user_id] = {}
    orders[user_id]["address"] = message.text
    await message.answer("Адрес сохранён ✅", reply_markup=menu)
    await state.finish()

# самовывоз
@dp.message_handler(lambda m: m.text == "🏠 Самовывоз")
async def pickup(message: types.Message):
    user_id = message.from_user.id
    if user_id not in orders:
        orders[user_id] = {}
    orders[user_id]["delivery"] = "Самовывоз"
    await message.answer("Самовывоз выбран ✅", reply_markup=menu)

# геолокация
@dp.message_handler(content_types=types.ContentType.LOCATION)
async def location(message: types.Message):
    user_id = message.from_user.id
    if user_id not in orders:
        orders[user_id] = {}
    orders[user_id]["location"] = message.location
    await message.answer("Геолокация получена 📍", reply_markup=menu)

# пожелания
@dp.message_handler(lambda m: m.text == "📝 Пожелания")
async def wish(message: types.Message):
    await Form.wish.set()
    await message.answer("Напишите ваши пожелания, предпочтения")

@dp.message_handler(state=Form.wish)
async def save_wish(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in orders:
        orders[user_id] = {}
    orders[user_id]["wish"] = message.text
    await message.answer("Пожелания сохранены ✅", reply_markup=menu)
    await state.finish()

# PDF удостоверение
@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def document(message: types.Message):
    user_id = message.from_user.id
    if user_id not in orders:
        orders[user_id] = {}
    if message.document.mime_type == "application/pdf" or message.document.file_name.endswith(".pdf"):
        orders[user_id]["doc"] = message.document.file_id
        await message.answer("PDF удостоверение получено ✅", reply_markup=menu)
    else:
        await message.answer("❌ Пожалуйста, отправьте удостоверение в PDF формате")
        
@dp.message_handler(lambda m: m.text == "📄 Отправить удостоверение")
async def send_pdf_instruction(message: types.Message):
    await message.answer("Пожалуйста, отправьте ваше удостоверение в PDF формате 📄")

# проверка заказа
@dp.message_handler(lambda m: m.text == "📋 Проверить заказ")
async def check(message: types.Message):
    user_id = message.from_user.id
    if user_id not in orders:
        orders[user_id] = {}
    data = orders[user_id]
    text = f"""
Ваш заказ:

Комплект: {data.get("pack")}
Основной номер: {data.get("phone")}
Доп. номер: {data.get("extra_phone")}
Способ получения: {data.get("delivery")}
Адрес: {data.get("address")}
Пожелания: {data.get("wish")}
"""
    await message.answer(text)

# оформление заказа
@dp.message_handler(lambda m: m.text == "✅ Оформить заказ")
async def finish(message: types.Message):
    user_id = message.from_user.id
    if user_id not in orders:
        orders[user_id] = {}
    data = orders[user_id]

    # обязательные поля
    if not data.get("pack"):
        await message.answer("Выберите комплект")
        return
    if not data.get("phone"):
        await message.answer("Введите основной номер")
        return
    if not data.get("doc"):
        await message.answer("Отправьте PDF удостоверение")
        return
    if not data.get("extra_phone"):
        await message.answer("Введите дополнительный номер")
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
    if "10000" in data["pack"]:
        price = 10000
    elif "13000" in data["pack"]:
        price = 13000
    elif "16000" in data["pack"]:
        price = 16000
    if data.get("delivery") == "Доставка":
        price += 2000

    # сообщение админу
    text = f"""
🔥 Новый заказ

Клиент: @{message.from_user.username}

Основной номер: {data.get("phone")}
Доп. номер: {data.get("extra_phone")}

Комплект: {data.get("pack")}
Способ получения: {data.get("delivery")}
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
    await message.answer("Заказ отправлен 🤝", reply_markup=menu)

# кнопки админа
@dp.callback_query_handler(lambda c: True)
async def admin_buttons(callback: types.CallbackQuery):
    action, user_id = callback.data.split("_")
    user_id = int(user_id)
    if action == "accept":
         # обновляем статус заказа в SQLite на active
        cursor.execute("""
            UPDATE orders SET status='active' 
            WHERE user_id=? AND status='new'
        """, (user_id,))
        conn.commit()
        await bot.send_message(user_id, "✅ Ваш заказ принят, в ближайшее время менеджер свяжется в вами!")
    elif action == "decline":
        cursor.execute("""
            UPDATE orders SET status='declined'
            WHERE user_id=? AND status='new'
        """, (user_id,))
        conn.commit()
        await bot.send_message(user_id, "❌ Заказ отклонён")
    elif action == "courier":
        await bot.send_message(user_id, "🚚 Курьер выехал")
    await callback.answer()

# =======================
# Хендлеры админа
# =======================

@dp.message_handler(commands=["admin"])
async def admin_menu(message: types.Message):
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этому меню")
        return
    
    # клавиатура для админа
    admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    admin_kb.add("📊 Активные заказы")
    admin_kb.add("📦 Завершить заказ")
    admin_kb.add("📈 Кол-во заказов клиента")
    
    await message.answer("👮‍♂️ Меню администратора:", reply_markup=admin_kb)

# показать все активные заказы
@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "📊 Активные заказы")
async def active_orders(message: types.Message):
    cursor.execute("""
        SELECT o.pack, c.main_phone, o.delivery_method, o.wishes
        FROM orders o
        JOIN clients c ON o.user_id = c.user_id
        WHERE o.status='active'
    """)
    orders_list = cursor.fetchall()
    if not orders_list:
        await message.answer("Активных заказов нет ❌")
        return
    text = "📋 Активные заказы:\n"
    for o in orders_list:
        text += f"\nID: {o[0]}\nОсновной: {o[1]}\nДоп.: {o[2]}\nКомплект: {o[3]}\n---"
    await message.answer(text)

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "📦 Завершить заказ")
async def finish_order_prompt(message: types.Message):
    # Показываем список активных заказов с кнопкой завершить
    cursor.execute("""
        SELECT o.pack, c.main_phone, o.delivery_method, o.wishes
        FROM orders o
        JOIN clients c ON o.user_id = c.user_id
        WHERE o.status='active'
    """)
    orders_list = cursor.fetchall()
    if not orders_list:
        await message.answer("Активных заказов нет ❌")
        return
    for o in orders_list:
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("✅ Завершить", callback_data=f"finish_{o[0]}"))
        await message.answer(f"ID: {o[0]}\nТелефон: {o[1]}\nКомплект: {o[2]}", reply_markup=kb)

# Хендлер кнопки
@dp.callback_query_handler(lambda c: c.data.startswith("finish_"))
async def finish_order_callback(callback: types.CallbackQuery):
    order_id = int(callback.data.split("_")[1])
    cursor.execute("UPDATE orders SET status='finished' WHERE id=?", (order_id,))
    conn.commit()
    await callback.answer("Заказ завершён ✅")
    await bot.send_message(callback.from_user.id, f"Заказ {order_id} завершён")

# запуск бота

executor.start_polling(dp)



























