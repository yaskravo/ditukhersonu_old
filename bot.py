import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import json
import os

# Ініціалізація бота
bot = telebot.TeleBot('TELEGRAM_BOT_TOKEN')

# Шлях до файлу з даними користувачів
USER_DATA_FILE = 'user_data.json'

# Ініціалізація файлу з даними користувачів
def initialize_user_data_file():
    # Якщо файл не існує, створюємо його
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'w') as file:
            json.dump({}, file)

# Завантаження даних користувачів з файлу
def load_user_data():
    with open(USER_DATA_FILE, 'r') as file:
        return json.load(file)

# Збереження даних користувачів у файл
def save_user_data():
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users_data, file)

# Ініціалізація файлів
initialize_user_data_file()

# Завантаження даних користувачів
users_data = load_user_data()

# Головне меню
def send_main_menu(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('🇺🇦 Клік'), KeyboardButton('⭐️ Таблиця лідерів'), KeyboardButton('👥 Команда проєкту'))

    user_info = users_data.get(str(chat_id), {"nickname": "Невідомий", "account": 0, "channel": "Ніхто"})
    nickname = user_info["nickname"]
    account = user_info["account"]
    channel = user_info["channel"]
    money_sent = account * 0.002

    text = (
        f"👤 Нікнейм: {nickname}\n"
        f"👀 Рахунок: {account}\n"
        f"❤️ Грошей відправлено на допомогу дітям Херсонщини: {money_sent:.2f} грн\n"
        f"❤️‍🔥 Привів до проєкту: {channel}\n\n"
        "🇺🇦 Зберігаємо спокій та віримо в ЗСУ. (С) 2024 KristalMedia\n"
    )
    bot.send_message(chat_id, text, reply_markup=markup)

# Стартова команда
@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = str(message.chat.id)

    if chat_id in users_data:
        # Якщо користувач вже зареєстрований, надсилаємо головне меню
        send_main_menu(chat_id)
    else:
        # Якщо користувач новий, розпочинаємо процес реєстрації
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton('Так!'))
        bot.send_message(
            chat_id,
            "🖖 Вітаємо!\n\n"
            "Ditu.Khersonu — це благодійний проєкт, створений спільнотою українського інтернет-телебачення. "
            "Ваше завдання — натискати на кнопку, яка збільшує ваш внесок. З кожного кліку 0,002 грн надходить на допомогу дітям Херсонщини.\n\n"
            "Перед початком користування, будь ласка, ознайомтеся з нашою політикою конфіденційності — https://example.com/\n\n"
            "Ви погоджуєтеся з політикою конфіденційності?",
            reply_markup=markup
        )

@bot.message_handler(func=lambda message: message.text == 'Так!')
def agreement_handler(message):
    chat_id = str(message.chat.id)
    bot.send_message(chat_id, "😜 Розпочинаємо реєстрацію!\n\nВведіть нікнейм, який буде відображатися в таблиці лідерів.")

    # Зберігаємо стан реєстрації
    users_data[chat_id] = {"registration_step": "nickname"}
    save_user_data()

@bot.message_handler(func=lambda message: users_data.get(str(message.chat.id), {}).get("registration_step") == "nickname")
def nickname_handler(message):
    chat_id = str(message.chat.id)
    nickname = message.text

    users_data[chat_id] = {"nickname": nickname, "account": 0, "channel": "Ніхто"}
    save_user_data()

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Example1'), KeyboardButton('Example2'), KeyboardButton('Example3'), KeyboardButton('Пропустити'))
    bot.send_message(chat_id, "Який інтернет-канал запросив вас до проєкту?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['Example1', 'Example2', 'Example3', 'Пропустити'])
def channel_handler(message):
    chat_id = str(message.chat.id)
    channel = message.text

    if channel == 'Пропустити':
        bot.send_message(chat_id, "💔 Шкода..")
    else:
        bot.send_message(chat_id, f"❤️ Вас запросив \"{channel}\".")

    users_data[chat_id]["channel"] = channel
    save_user_data()
    send_main_menu(chat_id)

@bot.message_handler(func=lambda message: message.text == '🇺🇦 Клік')
def click_handler(message):
    chat_id = str(message.chat.id)

    if chat_id in users_data:
        users_data[chat_id]["account"] += 1
        save_user_data()
        bot.send_message(chat_id, "+1")
        send_main_menu(chat_id)

@bot.message_handler(func=lambda message: message.text == '⭐️ Таблиця лідерів')
def leaderboard_handler(message):
    chat_id = str(message.chat.id)

    sorted_users = sorted(
        users_data.items(),
        key=lambda x: x[1].get("account", 0) * 0.002,
        reverse=True
    )
    leaderboard_text = "🦸 Таблиця найбільших благодійників та рятівників діток Херсонської області\n\n"

    for idx, (user_id, user_info) in enumerate(sorted_users[:10], 1):
        account = user_info.get("account", 0) 
        nickname = user_info.get('nickname', 'Без імені')
        leaderboard_text += f"{idx}. {nickname}. Відправив {account * 0.002:.2f} гривень.\n"

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('⬅️ Повернутись назад'))
    bot.send_message(chat_id, leaderboard_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '⬅️ Повернутись назад')
def back_handler(message):
    chat_id = str(message.chat.id)
    send_main_menu(chat_id)

# Обробка натискання кнопки "👥 Команда проєкту"
@bot.message_handler(func=lambda message: message.text == '👥 Команда проєкту')
def team_handler(message):
    chat_id = str(message.chat.id)
    bot.send_message(
        chat_id,
        "This bot is based on the original project available at [https://github.com/yaskravo/ditukhersonu_old](https://github.com/yaskravo/ditukhersonu_old). All credit for the original creation goes to **yaskravo**."
    )
    send_main_menu(chat_id)

def admin_panel(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton('🔒 Видалити та заблокувати користувача'),
        KeyboardButton('✏️ Змінити нікнейм користувача')
    )
    markup.add(KeyboardButton('💰 Додати до рахунку користувача'), KeyboardButton('📰 Відправити новину'))
    bot.send_message(chat_id, "Адмін-панель", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if str(message.chat.id) == "YOUR_ID_TELEGRAM":
        admin_panel(message.chat.id)
    else:
        bot.send_message(message.chat.id, "У вас немає адмін прав.")

@bot.message_handler(func=lambda message: message.text == '🔒 Видалити та заблокувати користувача')
def delete_user_prompt(message):
    bot.send_message(message.chat.id, "Введіть нікнейм або ID користувача для блокування:")
    bot.register_next_step_handler(message, delete_user)

def delete_user(message):
    user_identifier = message.text
    if user_identifier in users_data:
        bot.send_message(message.chat.id, "Введіть причину блокування:")
        bot.register_next_step_handler(message, lambda msg: confirm_blocking(msg, user_identifier))
    else:
        bot.send_message(message.chat.id, "Користувача не знайдено!")

def confirm_blocking(message, user_identifier):
    reason = message.text
    bot.send_message(message.chat.id, f"Впевнені, що хочете заблокувати користувача? Причина: {reason}. Введіть 'Так' для підтвердження.")
    bot.register_next_step_handler(message, lambda msg: block_user(msg, user_identifier, reason))
def block_user(message, user_identifier, reason):
    if message.text.lower() == "так":
        del users_data[user_identifier]
        save_user_data()
        bot.send_message(user_identifier, f"На жаль, ви були заблоковані адміністратором. За {reason}.")
        bot.send_message(message.chat.id, "Користувач видалений та заблокований.")
    else:
        bot.send_message(message.chat.id, "Блокування скасовано.")
    admin_panel(message.chat.id)

@bot.message_handler(func=lambda message: message.text == '💰 Додати до рахунку користувача')
def add_account_prompt(message):
    bot.send_message(message.chat.id, "Введіть ID користувача для додавання до рахунку:")
    bot.register_next_step_handler(message, add_to_account)

def add_to_account(message):
    user_identifier = message.text
    if user_identifier in users_data:
        bot.send_message(message.chat.id, f"Введіть суму, яку бажаєте додати до рахунку користувача з ID {user_identifier}:")
        bot.register_next_step_handler(message, lambda msg: update_account(msg, user_identifier))
    else:
        bot.send_message(message.chat.id, "Користувача не знайдено!")

def update_account(message, user_identifier):
    try:
        addition = int(message.text)
        users_data[user_identifier]['account'] += addition
        save_user_data()
        bot.send_message(message.chat.id, f"Рахунок користувача з ID {user_identifier} змінено. Додано {addition} одиниць.")
        bot.send_message(user_identifier, f"🧐 Вам змінили рахунок на {addition} одиниць!\nВаш новий рахунок: {users_data[user_identifier]['account']}")
    except ValueError:
        bot.send_message(message.chat.id, "Будь ласка, введіть дійсне число для рахунку.")
    admin_panel(message.chat.id)

@bot.message_handler(func=lambda message: message.text == '✏️ Змінити нікнейм користувача')
def change_nickname_prompt(message):
    bot.send_message(message.chat.id, "Введіть нікнейм або ID користувача для зміни нікнейму:")
    bot.register_next_step_handler(message, change_nickname)

def change_nickname(message):
    user_identifier = message.text
    if user_identifier in users_data:
        bot.send_message(message.chat.id, f"Введіть новий нікнейм для користувача {user_identifier}:")
        bot.register_next_step_handler(message, lambda msg: update_nickname(msg, user_identifier))
    else:
        bot.send_message(message.chat.id, "Користувача не знайдено!")

def update_nickname(message, user_identifier):
    new_nickname = message.text
    old_nickname = users_data[user_identifier]['nickname']
    users_data[user_identifier]['nickname'] = new_nickname
    save_user_data()
    bot.send_message(user_identifier, f"⚠️ Адміністратор змінив ваш нікнейм!\nВаш старий нікнейм: {old_nickname}\nВаш новий нікнейм: {new_nickname}")
    bot.send_message(message.chat.id, f"Нікнейм користувача {old_nickname} змінено на {new_nickname}.")
    admin_panel(message.chat.id)

@bot.message_handler(func=lambda message: message.text == '📰 Відправити новину')
def send_news_prompt(message):
    bot.send_message(message.chat.id, "Введіть новину:")
    bot.register_next_step_handler(message, send_news)

def send_news(message):
    news = message.text
    for user_id in users_data:
        bot.send_message(user_id, f"{news}")
    bot.send_message(message.chat.id, "Новина успішно відправлена всім користувачам.")
    admin_panel(message.chat.id)

# Запуск бота
bot.polling(none_stop=True)
