import json, datetime, os

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

main_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("📞Записаться", callback_data="register")],
    [InlineKeyboardButton("📋Мои записи", callback_data="check_record")],
    [InlineKeyboardButton("💰Прайс", callback_data="price")],
    [InlineKeyboardButton("📍Контакты", callback_data="contacts")],
    [InlineKeyboardButton("ℹ️О салоне", callback_data="information")]
])
register_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("✂️Стрижки", callback_data="haircut")],
    [InlineKeyboardButton("🧔‍Борода", callback_data="beard")],
    [InlineKeyboardButton("✨Дополнительные услуги", callback_data="additional_services")],
    [InlineKeyboardButton("🔥Популярные комплексы", callback_data="popular_complexes")],
    [InlineKeyboardButton("⬅ Назад", callback_data="back_all")]
])
haircut_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Мужская стрижка — 1 500 ₽", callback_data="haircut1")],
    [InlineKeyboardButton("Стрижка + укладка — 1 800 ₽", callback_data="haircut2")],
    [InlineKeyboardButton("Стрижка машинкой — 900 ₽", callback_data="haircut3")],
    [InlineKeyboardButton("Стрижка для пенсионеров - 500₽", callback_data="haircut4")],
    [InlineKeyboardButton("⬅ Назад", callback_data="back_register")]
])
beard_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Оформление бороды — 900 ₽", callback_data="beard1")],
    [InlineKeyboardButton("Стрижка бороды + моделирование — 1 200 ₽", callback_data="beard2")],
    [InlineKeyboardButton("⬅ Назад", callback_data="back_register")]
])
additional_services_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Укладка — 700 ₽", callback_data="additional1")],
    [InlineKeyboardButton("Камуфляж седины — 1 500 ₽", callback_data="additional2")],
    [InlineKeyboardButton("Уход за лицом — 1 000 ₽", callback_data="additional3")],
    [InlineKeyboardButton("⬅ Назад", callback_data="back_register")]
])
popular_complexes_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Стрижка + укладка — 1 800 ₽", callback_data="popular1")],
    [InlineKeyboardButton("Стрижка + борода — 2 500 ₽", callback_data="popular2")],
    [InlineKeyboardButton("Стрижка + борода + укладка —  3 000 ₽", callback_data="popular3")],
    [InlineKeyboardButton("⬅ Назад", callback_data="back_register")]
])
my_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("👀 Посмотреть запись", callback_data="watch")],
    [InlineKeyboardButton("✏️ Изменить запись", callback_data="change")],
    [InlineKeyboardButton("❌ Отменить запись", callback_data="cancel_record")],
    [InlineKeyboardButton("⬅ Назад", callback_data="back_all")]
])
confirm_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            "✅ Подтвердить",
            callback_data="confirm_record"
        )
    ],
    [
        InlineKeyboardButton(
            "❌ Отменить",
            callback_data="cancel_record"
        )
    ]
])
back_register_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("⬅ Назад", callback_data="back_register")]
])
back_all_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("⬅ Назад", callback_data="back_all")]
])
masters_callback = {
    "staff1": "Мария",
    "staff2": "Алексей",
    "staff3": "Евгений"
}
masters = {
    "Мария": [
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00"
    ],

    "Алексей": [
        "10:00",
        "11:00",
        "12:00",
        "13:00"
    ],

    "Евгений": [
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00"
    ]
}
months = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря"
}

def format_date(date):
    return f"{date.day} {months[date.month]}"
def back_keyboard(callback):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅ Назад",
                callback_data=callback
            )
        ]
    ])
def create_staff_keyboard(back_button):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👤 Мария", callback_data="staff1")
        ],
        [
            InlineKeyboardButton("👤 Алексей", callback_data="staff2")
        ],
        [
            InlineKeyboardButton("👤 Евгений", callback_data="staff3")
        ],
        [
            InlineKeyboardButton("⬅ Назад", callback_data=back_button)
        ]
    ])
def create_time_keyboard(master,date):
    records = load_records()
    busy_times = []
    for record in records:
        if (
            record["master"] == master
            and record["date"] == date
        ):
            busy_times.append(record["time"])
    keyboard = []

    for time in masters[master]:
        if time in busy_times:
            continue

        keyboard.append([
            InlineKeyboardButton(
                time,
                callback_data=f"time_{time}"
            )
        ])
    if len(keyboard) == 0:
        keyboard.append([
            InlineKeyboardButton(
                "❌ Нет свободного времени",
                callback_data="no_time"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅ Назад",
            callback_data="back_staff"
        )
    ])

    return InlineKeyboardMarkup(keyboard)
def create_date_keyboard():
    keyboard = []

    months = {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноября",
        12: "декабря"
    }

    today = datetime.date.today()

    for i in range(7):
        date = today + datetime.timedelta(days=i)
        date_text = f"{date.day} {months[date.month]}"
        keyboard.append([
            InlineKeyboardButton(
                date_text,
                callback_data=f"date_{date}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton(
            "⬅ Назад",
            callback_data="back_staff"
        )
    ])
    return InlineKeyboardMarkup(keyboard)
def load_records():
    with open("records.json", "r", encoding="utf-8") as file:
        return json.load(file)
def save_records(records):
    with open("records.json", "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=4)

data = load_records()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("barber.jpg", "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=(
                "🦊 Добро пожаловать в FF Barbershop!\n\n"
                "Здесь вы можете записаться к барберу, "
                "ознакомиться с услугами и ценами, "
                "узнать адрес и график работы.\n\n"
                "Выберите нужный раздел ниже."
            ),
            reply_markup=main_keyboard
        )
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "register":
        await query.edit_message_caption(
            "🔍Выбрать услугу:",
            reply_markup=register_keyboard
        )
    elif query.data == "haircut":
        await query.edit_message_caption(
            "🔍Выбрать услугу:", reply_markup=haircut_keyboard)
    elif query.data == "beard":
        await query.edit_message_caption(
            "🔍Выбрать услугу:", reply_markup=beard_keyboard)
    elif query.data == "additional_services":
        await query.edit_message_caption(
            "🔍Выбрать услугу:", reply_markup=additional_services_keyboard)
    elif query.data == "popular_complexes":
        await query.edit_message_caption(
            "🔍Выбрать услугу:", reply_markup=popular_complexes_keyboard)
    elif query.data == "check_record":
        await query.edit_message_caption(
            "🔍Выбрать услугу:", reply_markup=my_keyboard)
    elif query.data in masters_callback:

        context.user_data["master"] = masters_callback[query.data]

        await query.edit_message_caption(
            "📅 Выберите дату:",
            reply_markup=create_date_keyboard()
        )
    elif query.data.startswith("date_"):

        selected_date = query.data.replace("date_", "")

        context.user_data["date"] = selected_date

        master = context.user_data["master"]
        date = context.user_data["date"]

        await query.edit_message_caption(
            "⏰ Выберите время:",
            reply_markup=create_time_keyboard(master,date)
        )
    elif query.data.startswith("time_"):

        time = query.data.replace("time_", "")

        context.user_data["time"] = time

        date = datetime.datetime.strptime(

            context.user_data["date"],

            "%Y-%m-%d"

        ).date()

        await query.edit_message_caption(
            "Введите ваше имя:"
        )
    elif query.data in ["haircut1", "haircut2", "haircut3", "haircut4"]:
        await query.edit_message_caption(
            "🔍Выбрать мастера:", reply_markup=create_staff_keyboard("back_haircut"))
    elif query.data in ["beard1", "beard2"]:
        await query.edit_message_caption(
            "🔍Выбрать мастера:", reply_markup=create_staff_keyboard("back_beard"))
    elif query.data in ["additional1", "additional2", "additional3"]:
        await query.edit_message_caption(
            "🔍Выбрать мастера:", reply_markup=create_staff_keyboard("back_additional_services"))
    elif query.data in ["popular1", "popular2", "popular3"]:
        await query.edit_message_caption(
            "🔍Выбрать мастера:", reply_markup=create_staff_keyboard("back_popular_complexes"))
    elif query.data == "price":
        await query.edit_message_caption(
            "💰 Прайс FF Barbershop\n\n"

            "✂️ Стрижки:\n\n"
            "👦 Мужская стрижка — 1 500 ₽\n"
            "💇 Стрижка + укладка — 1 800 ₽\n"
            "🧔 Стрижка машинкой — 900 ₽\n"
            "👴 Стрижка для пенсионеров — 1 000 ₽\n\n"

            "🧔 Борода:\n\n"
            "🪒 Оформление бороды — 900 ₽\n"
            "🔥 Стрижка бороды + моделирование — 1 200 ₽\n"
            "💈 Комплекс (стрижка + борода) — 2 500 ₽\n\n"

            "✨ Дополнительные услуги:\n\n"
            "🧴 Укладка — 700 ₽\n"
            "🧖 Камуфляж седины — 1 500 ₽\n"
            "💆 Уход за лицом — 1 000 ₽\n\n"

            "⭐ Популярные комплексы:\n\n"
            "🥇 Стандарт:\n"
            "Стрижка + укладка\n"
            "1 800 ₽\n\n"

            "🥈 Барбер-комплекс:\n"
            "Стрижка + борода + укладка\n"
            "3 000 ₽\n\n"

            "🦊 FF Barbershop — стиль начинается с деталей!"
            , reply_markup=back_all_keyboard)
    elif query.data == "contacts":
        await query.edit_message_caption(
            "📍 FF Barbershop\n\n"
            "Адрес:\n"
            "г.Москва, ул.Тверская, д.24\n\n"

            "🕒 График работы:\n"
            "Пн–Вс: 10:00 — 18:00\n\n"

            "📞 Телефон:\n"
            "+7(999)123 - 45 - 67\n\n"

            "📱 Telegram:\n"
            "@FF_Barbershop\n\n"

            "Будем рады видеть вас"
            , reply_markup=back_all_keyboard)
    elif query.data == "information":
        await query.edit_message_caption(
            "🦊 FF Barbershop!\n\n"
            "FF Barbershop — это мужская парикмахерская, где классический стиль сочетается с современными "
            "техниками.\n\n"
            "Наши мастера помогут подобрать идеальную стрижку, оформить бороду и создать образ, который "
            "подчеркнет ваш стиль.\n\n"
            "Мы используем профессиональную косметику и уделяем внимание каждой детали, "
            "чтобы каждый клиент получил качественный сервис и комфортную атмосферу.\n\n"
            "✂️ Стрижки\n"
            "🧔формление бороды\n"
            "💈Укладка\n"
            "☕Уютная атмосфера\n\n"
            "Ждем вас в FF Barbershop!"
            , reply_markup=back_all_keyboard)
    elif query.data == "watch":
        records = load_records()
        user_id = query.from_user.id
        for record in records:
            if record["user_id"] == user_id:
                await query.edit_message_caption(
                    "📋 Ваша запись:\n\n"
                    f"👤 Мастер: {record['master']}\n"
                    f"📅 Дата: {record['date']}\n"
                    f"⏰ Время: {record['time']}\n"
                    f"📞 Телефон: {record['phone']}"
                )
                break
        else:
            await query.edit_message_caption(
                "❌ У вас нет активной записи.", reply_markup=my_keyboard
            )
    elif query.data == "change":
        records = load_records()
        user_id = query.from_user.id
        found = False
        for record in records:
            if record["user_id"] == user_id:
                found = True
                break
        if found:
            context.user_data["editing"] = True
            await query.edit_message_caption(
                "✏️ Редактирование записи.\n\n"
                "Старая запись удалена.\n"
                "Теперь создайте новую запись.\n\n"
                "Выберите услугу:",
                reply_markup=register_keyboard
            )
        else:
            await query.edit_message_caption(
                "❌ У вас нет записи для изменения.",
                reply_markup=my_keyboard
            )
    elif query.data == "back_haircut":
        await query.edit_message_caption(
            "🔍 Выбрать услугу:",
            reply_markup=haircut_keyboard
        )
    elif query.data == "back_beard":
        await query.edit_message_caption(
            "🔍 Выбрать услугу:",
            reply_markup=beard_keyboard
        )
    elif query.data == "back_additional_services":
        await query.edit_message_caption(
            "🔍 Выбрать услугу:",
            reply_markup=additional_services_keyboard
        )
    elif query.data == "back_popular_complexes":
        await query.edit_message_caption(
            "🔍 Выбрать услугу:",
            reply_markup=popular_complexes_keyboard
        )
    elif query.data == "back_register":
        await query.edit_message_caption(
            "🔍Выбрать услугу:", reply_markup=register_keyboard
        )
    elif query.data == "back_staff":
        await query.edit_message_caption(
            "🔍 Выберите мастера:",
            reply_markup=create_staff_keyboard("back_register")
        )
    elif query.data == "back_all":
        await query.edit_message_caption(
            "🦊 Добро пожаловать в FF Barbershop!\n\n"
            "Здесь вы можете записаться к барберу, "
            "ознакомиться с услугами и ценами, посмотреть наши работы, "
            "узнать адрес и график работы.\n\n"
            "Выберите нужный раздел ниже.", reply_markup=main_keyboard)
    elif query.data == "no_time":
        await query.answer(
            "У этого мастера нет свободного времени.",
            show_alert=True
        )
    elif query.data == "confirm_record":
        records = load_records()
        if context.user_data.get("editing"):
            user_id = query.from_user.id
            records = [
                record for record in records
                if record["user_id"] != user_id
            ]
            context.user_data.pop("editing")
        record = {
            "user_id": query.from_user.id,
            "master": context.user_data["master"],
            "date": context.user_data["date"],
            "time": context.user_data["time"],
            "name": context.user_data["name"],
            "phone": context.user_data["phone"]
        }
        records.append(record)
        save_records(records)
        context.user_data.clear()

        await query.edit_message_text(
            "🎉 Запись успешно создана!"
        )
    elif query.data == "cancel_record":
        records = load_records()
        user_id = query.from_user.id
        found = False
        new_records = []
        for record in records:
            if record["user_id"] == user_id:
                found = True
            else:
                new_records.append(record)
        if found:
            save_records(new_records)
            context.user_data.clear()
            with open("barber.jpg", "rb") as photo:
                await query.message.reply_photo(
                    photo=photo,
                    caption="❌ Запись отменена.\n\nВыберите раздел:",
                    reply_markup=main_keyboard
                )
            await query.delete_message()
        else:
            await query.edit_message_caption(
                "❌ У вас нет активной записи.",
                reply_markup=my_keyboard
            )
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "time" in context.user_data and "name" not in context.user_data:
        name = update.message.text
        context.user_data["name"] = name
        await update.message.reply_text(
            "📞 Введите ваш номер телефона:"
        )
    elif "name" in context.user_data and "phone" not in context.user_data:
        phone = update.message.text
        context.user_data["phone"] = phone
        date = datetime.datetime.strptime(
            context.user_data["date"],
            "%Y-%m-%d"
        ).date()
        await update.message.reply_text(
            f"✅ Проверьте запись:\n\n"
            f"👤 Мастер: {context.user_data['master']}\n"
            f"📅 Дата: {format_date(date)}\n"
            f"⏰ Время: {context.user_data['time']}\n"
            f"👨 Имя: {context.user_data['name']}\n"
            f"📞 Телефон: {context.user_data['phone']}\n\n"
            f"Всё верно?",
            reply_markup=confirm_keyboard
        )
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, message))
app.run_polling()
