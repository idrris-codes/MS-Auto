import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from datetime import datetime, timedelta
import json
import os

TOKEN = '7221063293:AAE6HpSbMiUdjKziSXWsrd1YtwSwKWYkueQ'
CHANNEL_USERNAME = '@masirservice'
ADMIN_ID = 7826275748
ALLOWED_STATS_USERS = [ADMIN_ID]
DATA_FILE = 'bot_data.json'

bot = telebot.TeleBot(TOKEN)
languages_display = ['Русский', 'Тоҷикӣ', 'English']
language_codes = {'Русский': 'ru', 'Тоҷикӣ': 'tj', 'English': 'en'}

default_messages = {
    'start': {
        'ru': '🌍 Выберите язык:',
        'tj': '🌍 Забони худро интихоб кунед:',
        'en': '🌍 Choose your language:'
    },
    'subscribe': {
        'ru': '📢 Пожалуйста, подпишитесь на наш канал, чтобы продолжить!',
        'tj': '📢 Лутфан ба канали мо обуна шавед, то идома диҳед!',
        'en': '📢 Please subscribe to our channel to continue!'
    },
    'subscribed': {
        'ru': '✅ Спасибо! Вы подписаны. Вот меню:',
        'tj': '✅ Раҳмат! Шумо обуна шудед. Ин меню:',
        'en': '✅ Thanks! You are subscribed. Here is the menu:'
    },
    'not_subscribed': {
        'ru': '❌ Вы всё ещё не подписаны.\n🔄 Попробуйте ещё раз.',
        'tj': '❌ Шумо ҳанӯз обуна нашудаед.\n🔄 Боз кӯшиш кунед.',
        'en': "❌ You're still not subscribed.\n🔄 Try again."
    },
    'menu': {
        'ru': '🏠 Главное меню:',
        'tj': '🏠 Менюи асосӣ:',
        'en': '🏠 Main menu:'
    },
    'repair': {
        'ru': '🔧 Ремонт',
        'tj': '🔧 Таъмир',
        'en': '🔧 Repair'
    },
    'parts': {
        'ru': '⚙️ Запчасти',
        'tj': '⚙️ Қисмҳо',
        'en': '⚙️ Parts'
    },
    'pickup': {
        'ru': '📍 Пункты выдачи',
        'tj': '📍 Маконҳои гирифтани мол',
        'en': '📍 Pickup points'
    },
    'stats': {
        'ru': '📊 Статистика',
        'tj': '📊 Статистика',
        'en': '📊 Statistics'
    },
    'name': {
        'ru': '👤 Введите ваше имя:',
        'tj': '👤 Номи худро ворид кунед:',
        'en': '👤 Enter your name:'
    },
    'phone': {
        'ru': '📞 Введите ваш телефон:',
        'tj': '📞 Рақами телефонро ворид кунед:',
        'en': '📞 Enter your phone number:'
    },
    'car': {
        'ru': '🚗 Укажите марку, модель и год автомобиля:',
        'tj': '🚗 Марка, модел ва соли мошинро ворид кунед:',
        'en': '🚗 Enter your car make, model, and year:'
    },
    'comment': {
        'ru': '💬 Комментарий (если есть):',
        'tj': '💬 Шарҳ (агар бошад):',
        'en': '💬 Comment (if any):'
    },
    'submitted': {
        'ru': '📩 Ваша заявка отправлена!',
        'tj': '📩 Дархости шумо фиристода шуд!',
        'en': '📩 Your request has been submitted!'
    },
    'addresses': {
        'ru': '📍 Наш пункт выдачи:\n🏠 Республика Таджикистан, г. Душанбе, район Фирдавси,\nПроспект Гипрозем\n📌 Ориентир: рядом с баней «ПАРУС»\n🚪 Гараж №73 и Гараж №37',
        'tj': '📍 Макони гирифтани мол:\n🏠 Ҷумҳурии Тоҷикистон, ш. Душанбе, ноҳияи Фирдавсӣ,\nПроспекти Гипрозем\n📌 Ориентир: назди ҳаммоми «ПАРУС»\n🚪 Гаражи №73 ва гаражи №37',
        'en': '📍 Pickup point:\n🏠 Republic of Tajikistan, Dushanbe city, Firdavsi district,\nGiprozem Avenue\n📌 Landmark: near «PARUS» bathhouse\n🚪 Garage №73 and Garage №37'
    },
    'need_sub': {
        'ru': '⚠️ Для продолжения требуется подписка на канал!',
        'tj': '⚠️ Барои идома обуна ба канал лозим аст!',
        'en': '⚠️ Subscription to the channel is required to continue!'
    }
}

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data_store = json.load(f)
    except:
        data_store = {'submissions': {}, 'users': {}}
else:
    data_store = {'submissions': {}, 'users': {}}

def save_store():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_store, f, ensure_ascii=False, indent=2)

def get_lang(chat_id):
    u = data_store['users'].get(str(chat_id), {})
    return u.get('lang', 'ru')

def set_lang(chat_id, lang_code):
    data_store['users'].setdefault(str(chat_id), {})['lang'] = lang_code
    save_store()

def menu_keyboard(lang_code):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(default_messages['repair'][lang_code], default_messages['parts'][lang_code])
    kb.add(default_messages['pickup'][lang_code], default_messages['stats'][lang_code])
    return kb

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for l in languages_display:
        kb.add(l)
    bot.send_message(message.chat.id, default_messages['start']['ru'], reply_markup=kb)

@bot.message_handler(func=lambda m: m.text in languages_display)
def set_language(message):
    lang_code = language_codes.get(message.text, 'ru')
    set_lang(message.chat.id, lang_code)
    if not check_subscription(message.from_user.id):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton('🔗 Перейти в канал', url=f'https://t.me/{CHANNEL_USERNAME.lstrip("@")}'))
        kb.add(InlineKeyboardButton('✅ Подписался', callback_data='check_sub'))
        bot.send_message(message.chat.id, default_messages['subscribe'][lang_code], reply_markup=kb)
        return
    bot.send_message(message.chat.id, default_messages['menu'][lang_code], reply_markup=menu_keyboard(lang_code))

@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
def check_sub_callback(call):
    lang = get_lang(call.message.chat.id)
    if check_subscription(call.from_user.id):
        bot.send_message(call.message.chat.id, default_messages['subscribed'][lang], reply_markup=menu_keyboard(lang))
    else:
        bot.answer_callback_query(call.id, default_messages['not_subscribed'][lang])

service_texts = set([default_messages['repair']['ru'], default_messages['repair']['tj'], default_messages['repair']['en'],
                     default_messages['parts']['ru'], default_messages['parts']['tj'], default_messages['parts']['en']])

@bot.message_handler(func=lambda m: m.text in service_texts)
def choose_service(message):
    lang = get_lang(message.chat.id)
    if not check_subscription(message.from_user.id):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton('🔗 Перейти в канал', url=f'https://t.me/{CHANNEL_USERNAME.lstrip("@")}'))
        kb.add(InlineKeyboardButton('✅ Подписался', callback_data='check_sub'))
        bot.send_message(message.chat.id, default_messages['need_sub'][lang], reply_markup=kb)
        return
    data_store['users'].setdefault(str(message.chat.id), {})
    data_store['users'][str(message.chat.id)]['service'] = message.text
    save_store()
    bot.send_message(message.chat.id, default_messages['name'][lang])
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    lang = get_lang(message.chat.id)
    data_store['users'].setdefault(str(message.chat.id), {})
    data_store['users'][str(message.chat.id)]['name'] = message.text
    save_store()
    bot.send_message(message.chat.id, default_messages['phone'][lang])
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    lang = get_lang(message.chat.id)
    data_store['users'][str(message.chat.id)]['phone'] = message.text
    save_store()
    bot.send_message(message.chat.id, default_messages['car'][lang])
    bot.register_next_step_handler(message, get_car)

def get_car(message):
    lang = get_lang(message.chat.id)
    data_store['users'][str(message.chat.id)]['car'] = message.text
    save_store()
    bot.send_message(message.chat.id, default_messages['comment'][lang])
    bot.register_next_step_handler(message, get_comment)

def get_comment(message):
    lang = get_lang(message.chat.id)
    data_store['users'][str(message.chat.id)]['comment'] = message.text
    user_record = data_store['users'][str(message.chat.id)].copy()
    user_record['chat_id'] = message.chat.id
    user_record['username'] = message.from_user.username or ''
    user_record['timestamp'] = datetime.utcnow().isoformat()
    data_store['submissions'].setdefault(str(message.chat.id), [])
    data_store['submissions'][str(message.chat.id)].append(user_record)
    save_store()
    text_user = default_messages['submitted'][lang] + "\n\n"
    for k, v in user_record.items():
        if k in ['timestamp', 'chat_id', 'username']:
            continue
        text_user += f"{k.capitalize()}: {v}\n"
    bot.send_message(message.chat.id, text_user, reply_markup=menu_keyboard(lang))
    text_admin = f"📥 Новая заявка от @{user_record['username'] or 'без username'}\n\n"
    for k, v in user_record.items():
        if k == 'timestamp':
            continue
        text_admin += f"{k.capitalize()}: {v}\n"
    text_admin += f"\n👤 User ID: {message.chat.id}\n⏱ {user_record['timestamp']}"
    try:
        bot.send_message(ADMIN_ID, text_admin)
    except:
        pass

pickup_texts = set([default_messages['pickup']['ru'], default_messages['pickup']['tj'], default_messages['pickup']['en']])

@bot.message_handler(func=lambda m: m.text in pickup_texts)
def show_addresses(message):
    lang = get_lang(message.chat.id)
    bot.send_message(message.chat.id, default_messages['addresses'][lang])

stats_texts = set([default_messages['stats']['ru'], default_messages['stats']['tj'], default_messages['stats']['en']])

@bot.message_handler(func=lambda m: m.text in stats_texts)
def show_stats(message):
    if message.from_user.id not in ALLOWED_STATS_USERS:
        return
    lang = get_lang(message.chat.id)
    now = datetime.utcnow()
    today_count = 0
    week_count = 0
    for submissions in data_store['submissions'].values():
        for s in submissions:
            ts = s.get('timestamp')
            try:
                t = datetime.fromisoformat(ts)
            except:
                continue
            if t.date() == now.date():
                today_count += 1
            if t >= now - timedelta(days=7):
                week_count += 1
    bot.send_message(message.chat.id, f"{default_messages['stats'][lang]}\nСегодня: {today_count}\nЗа 7 дней: {week_count}")

@bot.message_handler(func=lambda m: True)
def fallback(message):
    chat_id = message.chat.id
    lang = get_lang(chat_id)
    if message.text in languages_display:
        return
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for l in languages_display:
        kb.add(l)
    bot.send_message(chat_id, default_messages['menu'][lang], reply_markup=kb)

bot.remove_webhook()
print("Webhook removed. Starting polling...")
bot.polling(none_stop=True)


if __name__ == '__main__':
    bot.remove_webhook()
    print("Bot started (polling)...")
    bot.polling(none_stop=True, interval=0, timeout=20)
