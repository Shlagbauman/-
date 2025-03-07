import telebot
from datetime import datetime, timedelta
import sqlite3
from telebot import types

TOKEN ="TOKEN"

bot = telebot.TeleBot(TOKEN)

def database():
    conn = sqlite3.connect('events.db', check_same_thread=False)
    cur = conn.cursor()
    '''
    Создает базу данных SQLite с таблицами
    Эти 3 таблицы:
    У users:
        chat_id (INTEGER PRIMARY KEY): id чата пользователя.
        username (TEXT): Имя пользователя.
    У events:
            - event_id (INTEGER PRIMARY KEY AUTOINCREMENT): id мероприятия.
            - chat_id (INTEGER): id чата пользователя.
            - title (TEXT): Название мероприятия.
            - date (TEXT): Дата в формате ДД-ММ-ГГГГ.
            - type (TEXT): Тип мероприятия (например, День Рождения).
            - tags (TEXT): Хэштеги, связанные с мероприятием.
    У notes:
            - note_id (INTEGER PRIMARY KEY AUTOINCREMENT): id заметки.
            - chat_id (INTEGER): id чата пользователя.
            - content (TEXT): Содержимое заметки.
            - created_at (TEXT DEFAULT CURRENT_TIMESTAMP): Время создания заметки.
            - updated_at (TEXT DEFAULT CURRENT_TIMESTAMP): Время последнего обновления заметки.
            '''
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            username TEXT
        );
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            title TEXT,
            date TEXT,
            type TEXT,
            tags TEXT,
            FOREIGN KEY(chat_id) REFERENCES users(chat_id)
        );
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            note_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            content TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(chat_id) REFERENCES users(chat_id)
        );
    ''')

    conn.commit()
    return conn, cur

conn, cur = database()

def registration(chat_id, username):
    """
    Регистрирует нового пользователя в базе данных.

    На входе:
        chat_id (int): id чата пользователя.
        username (str): Имя пользователя.

    Возвращает:
        True или False
    """
    try:
        cur.execute("INSERT INTO users (chat_id, username) VALUES (?, ?)", (chat_id, username))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

@bot.message_handler(commands=['start'])
def welcome(message):
    """
        Обрабатывает команду /start .
        Параметры:
                сообщение от пользователя
        """
    chat_id = message.chat.id
    username = message.from_user.username or message.from_user.first_name

    if not registration(chat_id, username):
        bot.reply_to(message, "Вы уже зарегистрированы.")
    else:
        bot.reply_to(message, f"👋 Привет, {username}! Вы успешно зарегистрированы.")
    menu(message)

def menu(message):
    """
        Отображает главное меню
        Параметры:
                сообщение от пользователя
        """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        types.KeyboardButton(text="📅 Мероприятия"),
        types.KeyboardButton(text="📝 Заметки")
    ]
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, "Что вы хотите сделать?", reply_markup=keyboard)

def show_events_menu(message):
    """
        Отображает меню для работы с мероприятиями.
        Параметры:
                сообщение от пользователя
        """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        types.KeyboardButton(text="➕ Добавить мероприятие"),
        types.KeyboardButton(text="👀 Просмотреть мероприятия"),
        types.KeyboardButton(text="⬅️ Назад")
    ]
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, "Выберите действие с мероприятиями:", reply_markup=keyboard)

def show_notes_menu(message):
    """
        Отображает меню для работы с заметками.
        Параметры:
                сообщение от пользователя
        """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        types.KeyboardButton(text="➕ Создать заметку"),
        types.KeyboardButton(text="👀 Просмотреть заметки"),
        types.KeyboardButton(text="⬅️ Назад")
    ]
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, "Выберите действие с заметками:", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text == "➕ Добавить мероприятие")
def add_event(message):
    """
       Запрашивает у пользователя название мероприятия для добавления.
        Параметры:
                сообщение от пользователя
       """
    msg = bot.send_message(message.chat.id, "Введите название мероприятия:")
    bot.register_next_step_handler(msg, process_event_title)

def process_event_title(message):
    """
        Обрабатывает введённое пользователем название мероприятия и запрашивает дату.
            Параметры:
                сообщение от пользователя
        """
    title = message.text.strip()
    if not title:
        msg = bot.send_message(message.chat.id, "❌ Название не может быть пустым. Введите название мероприятия:")
        bot.register_next_step_handler(msg, process_event_title)
        return
    msg = bot.send_message(message.chat.id, "📅 Введите дату мероприятия в формате ДД-ММ-ГГГГ:")
    bot.register_next_step_handler(msg, process_event_date, title)

def process_event_date(message, title):
    """
        Обрабатывает введённую пользователем дату мероприятия и запрашивает тип мероприятия.

        Параметры:
            message (telebot.types.Message): Объект сообщения от пользователя.
            title (str): Название мероприятия.
        """
    date_str = message.text.strip()
    try:
        event_date = datetime.strptime(date_str, "%d-%m-%Y").date()
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Дата введена неверно. Попробуйте еще раз (ДД-ММ-ГГГГ):")
        bot.register_next_step_handler(msg, process_event_date, title)
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [
        types.KeyboardButton(text="🎂 День Рождения"),
        types.KeyboardButton(text="💍 Годовщина"),
        types.KeyboardButton(text="⏰ Дедлайн"),
        types.KeyboardButton(text="➕ Прочее")
    ]
    keyboard.add(*buttons)
    msg = bot.send_message(message.chat.id, "Выберите тип мероприятия:", reply_markup=keyboard)
    bot.register_next_step_handler(msg, process_event_type, title, event_date)

def process_event_type(message, title, event_date):
    """
        Обрабатывает выбранный пользователем тип мероприятия и запрашивает хэштеги.

        Параметры:
            message (telebot.types.Message): Объект сообщения от пользователя.
            title (str): Название мероприятия.
            event_date (datetime.date): Дата мероприятия.
        """
    event_type_text = message.text.strip()
    type_mapping = {
        "🎂 День Рождения": "День Рождения",
        "💍 Годовщина": "Годовщина",
        "⏰ Дедлайн": "Дедлайн",
        "➕ Прочее": "Прочее"
    }
    event_type = type_mapping.get(event_type_text)
    if not event_type:
        bot.send_message(message.chat.id, "❌ Неверный выбор. Попробуйте снова.")
        show_events_menu(message)
        return

    msg = bot.send_message(message.chat.id, "🔖 Введите хэштеги через запятую (например, #деньрождения, #семья):")
    bot.register_next_step_handler(msg, process_event_tags, title, event_date, event_type)

def process_event_tags(message, title, event_date, event_type):
    """
        Сохраняет введённые пользователем хэштеги и добавляет мероприятие в базу данных.

        Параметры:
            message (telebot.types.Message): Объект сообщения от пользователя.
            title (str): Название мероприятия.
            event_date (datetime.date): Дата мероприятия.
            event_type (str): Тип мероприятия.
        """
    tags = message.text.strip()
    chat_id = message.chat.id

    cur.execute("INSERT INTO events (chat_id, title, date, type, tags) VALUES (?,?,?,?,?)",
                (chat_id, title, event_date.strftime("%d-%m-%Y"), event_type, tags))
    conn.commit()

    bot.send_message(message.chat.id, "✅ Мероприятие добавлено!")

    menu(message)

@bot.message_handler(func=lambda m: m.text == "👀 Просмотреть мероприятия")
def view_events(message):
    """
        Отображает все мероприятия, запланированные пользователем, с возможностью удаления.

        Параметры:
            message (telebot.types.Message): Объект сообщения от пользователя.
        """
    chat_id = message.chat.id
    cur.execute("SELECT event_id, title, date, type, tags FROM events WHERE chat_id = ?", (chat_id,))
    rows = cur.fetchall()

    if len(rows) == 0:
        bot.send_message(chat_id, "📭 У вас нет запланированных мероприятий.")
    else:
        for row in rows:
            event_id, title, date, event_type, tags = row
            response = f"**{title}**\n📅 Дата: {date}\n📌 Тип: {event_type}\n🔖 Хэштеги: {tags}"
            keyboard = types.InlineKeyboardMarkup()
            delete_button = types.InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_event_{event_id}")
            keyboard.add(delete_button)
            bot.send_message(chat_id, response, parse_mode="Markdown", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_event_"))
def delete_event_callback(call):
    """
        Отображает все мероприятия, запланированные пользователем, с возможностью удаления.

        Параметры:
            message (telebot.types.Message): Объект сообщения от пользователя.
        """
    chat_id = call.message.chat.id
    event_id = int(call.data.split("_")[-1])

    cur.execute("SELECT title, date FROM events WHERE event_id = ? AND chat_id = ?", (event_id, chat_id))
    event = cur.fetchone()
    if not event:
        bot.answer_callback_query(call.id, "❌ Мероприятие не найдено или уже удалено.")
        return

    title, date_str = event
    try:
        event_date = datetime.strptime(date_str, "%d-%m-%Y").date()
    except ValueError:
        bot.answer_callback_query(call.id, "❌ Некорректная дата мероприятия.")
        return

    cur.execute("DELETE FROM events WHERE event_id = ? AND chat_id = ?", (event_id, chat_id))
    conn.commit()

    bot.delete_message(chat_id, call.message.message_id)

    bot.send_message(chat_id, f"✅ Мероприятие '{title}' удалено.")

    bot.answer_callback_query(call.id, "Мероприятие удалено.")

@bot.message_handler(func=lambda m: m.text == "➕ Создать заметку")
def create_note(message):
    """
        Запрашивает у пользователя текст новой заметки.

        Параметры:
            message (telebot.types.Message): Объект сообщения от пользователя.
        """
    msg = bot.send_message(message.chat.id, "📝 Введите текст заметки:")
    bot.register_next_step_handler(msg, save_note)

def save_note(message):
    """
        Сохраняет введённую пользователем заметку в базе данных.

        Параметры:
            message (telebot.types.Message): Объект сообщения от пользователя.
        """
    content = message.text.strip()
    chat_id = message.chat.id

    if not content:
        msg = bot.send_message(chat_id, "❌ Заметка не может быть пустой. введите текст заметки:")
        bot.register_next_step_handler(msg, save_note)
        return

    cur.execute("INSERT INTO notes (chat_id, content) VALUES (?, ?)", (chat_id, content))
    conn.commit()

    bot.send_message(chat_id, "✅ Заметка создана!")

    menu(message)

@bot.message_handler(func=lambda m: m.text == "👀 Просмотреть заметки")
def view_notes(message):
    """
        Отображает все заметки, созданные пользователем, с возможностью удаления.

        Параметры:
            message (telebot.types.Message): Объект сообщения от пользователя.
        """
    chat_id = message.chat.id
    cur.execute("SELECT note_id, content FROM notes WHERE chat_id = ?", (chat_id,))
    rows = cur.fetchall()

    if len(rows) == 0:
        bot.send_message(chat_id, "📭 У вас нет заметок.")
    else:
        for row in rows:
            note_id, content = row
            response = f"**Заметка {note_id}:**\n{content}"
            keyboard = types.InlineKeyboardMarkup()
            delete_button = types.InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_note_{note_id}")
            keyboard.add(delete_button)
            bot.send_message(chat_id, response, parse_mode="Markdown", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_note_"))
def delete_note_callback(call):
    """
        Обрабатывает нажатие кнопки удаления заметки.

        Параметры:
            call (telebot.types.CallbackQuery): Объект колбэка от пользователя.
        """
    chat_id = call.message.chat.id
    note_id = int(call.data.split("_")[-1])

    cur.execute("SELECT content FROM notes WHERE note_id = ? AND chat_id = ?", (note_id, chat_id))
    note = cur.fetchone()
    if not note:
        bot.answer_callback_query(call.id, "❌ Заметка не найдена или уже удалена.")
        return

    cur.execute("DELETE FROM notes WHERE note_id = ? AND chat_id = ?", (note_id, chat_id))
    conn.commit()

    bot.delete_message(chat_id, call.message.message_id)

    bot.send_message(chat_id, f"✅ Заметка {note_id} удалена.")

    bot.answer_callback_query(call.id, "Заметка удалена.")

@bot.message_handler(func=lambda m: m.text in ["📅 Мероприятия", "📝 Заметки", "⬅️ Назад"])
def MenuActions(message):
    """
        Обрабатывает действия пользователя в главном меню.

        Параметры:
            message (telebot.types.Message): Объект сообщения от пользователя.
        """
    text = message.text

    if text == "📅 Мероприятия":
        show_events_menu(message)
    elif text == "📝 Заметки":
        show_notes_menu(message)
    elif text == "⬅️ Назад":
        menu(message)

if __name__ == '__main__':
    print("📡 Бот запущен...")
    bot.infinity_polling()
