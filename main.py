import os
import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@masirservice").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0") or 0)
STATS_USERS = {int(x) for x in os.getenv("STATS_USERS", str(ADMIN_ID)).replace(" ", "").split(",") if x.isdigit()}
DATA_FILE = Path(os.getenv("DATA_FILE", "bot_data.json"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Add BOT_TOKEN in Railway Variables.")
if not ADMIN_ID:
    raise RuntimeError("ADMIN_ID is missing. Add ADMIN_ID in Railway Variables.")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

LANGS = {
    "ru": "🇷🇺 Русский",
    "tj": "🇹🇯 Тоҷикӣ",
    "en": "🇬🇧 English"
}

LANG_BY_TEXT = {v: k for k, v in LANGS.items()}

T = {
    "choose_lang": {
        "ru": "🌍 <b>Выберите язык</b>\n\nПосле выбора языка бот откроет меню и проверит подписку на канал.",
        "tj": "🌍 <b>Забонро интихоб кунед</b>\n\nПас аз интихоб, бот менюро мекушояд ва обуна ба каналро месанҷад.",
        "en": "🌍 <b>Choose a language</b>\n\nAfter that, the bot will open the menu and check your channel subscription."
    },
    "subscribe": {
        "ru": "📢 <b>Остался один шаг</b>\n\nЧтобы оставить заявку и пользоваться ботом, подпишитесь на наш канал.",
        "tj": "📢 <b>Як қадам монд</b>\n\nБарои гузоштани дархост ва истифодаи бот, ба канали мо обуна шавед.",
        "en": "📢 <b>One step left</b>\n\nSubscribe to our channel to submit requests and use the bot."
    },
    "sub_ok": {
        "ru": "✅ <b>Готово!</b> Спасибо за подписку. Выберите нужный раздел:",
        "tj": "✅ <b>Тайёр!</b> Ташаккур барои обуна. Бахши лозимиро интихоб кунед:",
        "en": "✅ <b>Done!</b> Thanks for subscribing. Choose a section:"
    },
    "sub_bad": {
        "ru": "❌ Подписка пока не найдена. Подпишитесь на канал и нажмите кнопку проверки ещё раз.",
        "tj": "❌ Обуна ҳоло ёфт нашуд. Ба канал обуна шавед ва боз санҷед.",
        "en": "❌ Subscription was not found yet. Subscribe and check again."
    },
    "need_sub": {
        "ru": "⚠️ Для продолжения нужна подписка на канал.",
        "tj": "⚠️ Барои идома обуна ба канал лозим аст.",
        "en": "⚠️ Channel subscription is required to continue."
    },
    "menu": {
        "ru": "🏠 <b>Главное меню</b>\n\nВыберите услугу или нужный раздел ниже.",
        "tj": "🏠 <b>Менюи асосӣ</b>\n\nХизматрасонӣ ё бахши лозимиро интихоб кунед.",
        "en": "🏠 <b>Main menu</b>\n\nChoose a service or section below."
    },
    "repair": {"ru": "🔧 Ремонт", "tj": "🔧 Таъмир", "en": "🔧 Repair"},
    "parts": {"ru": "⚙️ Запчасти", "tj": "⚙️ Қисмҳо", "en": "⚙️ Parts"},
    "pickup": {"ru": "📍 Пункты выдачи", "tj": "📍 Нуқтаҳои гирифтани мол", "en": "📍 Pickup points"},
    "stats": {"ru": "📊 Статистика", "tj": "📊 Статистика", "en": "📊 Statistics"},
    "change_lang": {"ru": "🌍 Сменить язык", "tj": "🌍 Иваз кардани забон", "en": "🌍 Change language"},
    "cancel": {"ru": "❌ Отмена", "tj": "❌ Бекор кардан", "en": "❌ Cancel"},
    "back": {"ru": "⬅️ Назад", "tj": "⬅️ Ба қафо", "en": "⬅️ Back"},
    "name": {
        "ru": "👤 <b>Как вас зовут?</b>\n\nНапишите имя, чтобы менеджер мог правильно к вам обратиться.",
        "tj": "👤 <b>Номатон чист?</b>\n\nНомро нависед, то менеҷер дуруст муроҷиат кунад.",
        "en": "👤 <b>What is your name?</b>\n\nEnter your name so the manager can contact you properly."
    },
    "phone": {
        "ru": "📞 <b>Оставьте номер телефона</b>\n\nМожно отправить контакт кнопкой ниже или написать номер вручную.",
        "tj": "📞 <b>Рақами телефонро фиристед</b>\n\nМетавонед бо тугмаи поён контакт фиристед ё рақамро нависед.",
        "en": "📞 <b>Share your phone number</b>\n\nUse the button below or type the number manually."
    },
    "send_contact": {"ru": "📲 Отправить номер", "tj": "📲 Фиристодани рақам", "en": "📲 Share phone"},
    "car": {
        "ru": "🚗 <b>Укажите автомобиль</b>\n\nНапишите марку, модель и год. Например: Toyota Camry 2012.",
        "tj": "🚗 <b>Мошинро нишон диҳед</b>\n\nМарка, модел ва солро нависед. Масалан: Toyota Camry 2012.",
        "en": "🚗 <b>Enter your vehicle</b>\n\nWrite make, model and year. Example: Toyota Camry 2012."
    },
    "comment": {
        "ru": "💬 <b>Комментарий</b>\n\nОпишите проблему или нужную запчасть. Если комментария нет, напишите «-».",
        "tj": "💬 <b>Шарҳ</b>\n\nМушкилӣ ё қисми лозимиро нависед. Агар шарҳ набошад, «-» нависед.",
        "en": "💬 <b>Comment</b>\n\nDescribe the problem or required part. If there is no comment, type “-”."
    },
    "sent": {
        "ru": "✅ <b>Заявка отправлена</b>\n\nМенеджер свяжется с вами после обработки заявки.",
        "tj": "✅ <b>Дархост фиристода шуд</b>\n\nМенеҷер баъд аз баррасӣ бо шумо тамос мегирад.",
        "en": "✅ <b>Request sent</b>\n\nThe manager will contact you after processing it."
    },
    "cancelled": {
        "ru": "Заявка отменена. Вы вернулись в главное меню.",
        "tj": "Дархост бекор шуд. Шумо ба менюи асосӣ баргаштед.",
        "en": "Request cancelled. You are back in the main menu."
    },
    "unknown": {
        "ru": "Я не понял команду. Выберите действие через меню ниже.",
        "tj": "Ман фармонро нафаҳмидам. Амалро аз менюи поён интихоб кунед.",
        "en": "I did not understand the command. Choose an action from the menu below."
    },
    "addresses": {
        "ru": "📍 <b>Пункт выдачи Masir Service</b>\n\n🏠 Республика Таджикистан, г. Душанбе, район Фирдавси\n📌 Проспект Гипрозем, рядом с баней «ПАРУС»\n🚪 Гараж №73 и Гараж №37\n\nПеред приездом лучше заранее оставить заявку через бота.",
        "tj": "📍 <b>Нуқтаи гирифтани мол Masir Service</b>\n\n🏠 Ҷумҳурии Тоҷикистон, ш. Душанбе, ноҳияи Фирдавсӣ\n📌 Проспекти Гипрозем, назди ҳаммоми «ПАРУС»\n🚪 Гаражи №73 ва Гаражи №37\n\nПеш аз омадан беҳтар аст дар бот дархост гузоред.",
        "en": "📍 <b>Masir Service pickup point</b>\n\n🏠 Republic of Tajikistan, Dushanbe, Firdavsi district\n📌 Giprozem Avenue, near “PARUS” bathhouse\n🚪 Garage №73 and Garage №37\n\nIt is better to submit a request in the bot before arrival."
    }
}

SERVICE_KEYS = {"repair", "parts"}


def load_store():
    if not DATA_FILE.exists():
        return {"users": {}, "submissions": []}
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data.get("users"), dict):
            data["users"] = {}
        if not isinstance(data.get("submissions"), list):
            old = data.get("submissions", {})
            data["submissions"] = [x for v in old.values() for x in v] if isinstance(old, dict) else []
        return data
    except Exception:
        return {"users": {}, "submissions": []}


def save_store():
    tmp = DATA_FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)
    tmp.replace(DATA_FILE)


store = load_store()


def uid(message_or_call):
    return str(message_or_call.from_user.id)


def chat_id(message_or_call):
    return message_or_call.message.chat.id if hasattr(message_or_call, "message") else message_or_call.chat.id


def user(message_or_call):
    user_id = uid(message_or_call)
    store["users"].setdefault(user_id, {"lang": "ru", "state": "idle", "draft": {}})
    return store["users"][user_id]


def lang_of(message_or_call):
    return user(message_or_call).get("lang", "ru")


def tr(key, lang):
    return T[key].get(lang, T[key]["ru"])


def lang_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for text in LANGS.values():
        kb.add(text)
    return kb


def menu_keyboard(lang):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(tr("repair", lang), tr("parts", lang))
    kb.add(tr("pickup", lang), tr("change_lang", lang))
    if ADMIN_ID in STATS_USERS:
        kb.add(tr("stats", lang))
    return kb


def cancel_keyboard(lang, with_contact=False):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if with_contact:
        kb.add(KeyboardButton(tr("send_contact", lang), request_contact=True))
    kb.add(tr("cancel", lang))
    return kb


def sub_keyboard(lang):
    channel = CHANNEL_USERNAME.lstrip("@")
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔗 Telegram channel", url=f"https://t.me/{channel}"))
    kb.add(InlineKeyboardButton("✅ Check subscription", callback_data="check_sub"))
    return kb


def clean_text(value):
    return str(value or "").strip()[:700]


def service_key_by_text(text):
    for key in SERVICE_KEYS:
        if text in T[key].values():
            return key
    return None


def is_cancel(text):
    return text in T["cancel"].values() or text in T["back"].values()


def is_change_lang(text):
    return text in T["change_lang"].values()


def is_stats(text):
    return text in T["stats"].values()


def is_pickup(text):
    return text in T["pickup"].values()


def subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in {"member", "administrator", "creator"}
    except Exception:
        return False


def require_subscription(message):
    lang = lang_of(message)
    if subscribed(message.from_user.id):
        return True
    bot.send_message(message.chat.id, tr("need_sub", lang), reply_markup=sub_keyboard(lang))
    return False


def show_menu(chat, lang):
    bot.send_message(chat, tr("menu", lang), reply_markup=menu_keyboard(lang))


def reset_flow(user_data):
    user_data["state"] = "idle"
    user_data["draft"] = {}
    save_store()


def phone_from_message(message):
    if message.contact and message.contact.phone_number:
        return message.contact.phone_number
    text = clean_text(message.text)
    if re.fullmatch(r"[+\d][\d\s()\-]{5,30}", text):
        return text
    return text


def format_submission(data, lang):
    labels = {
        "ru": {"service": "Услуга", "name": "Имя", "phone": "Телефон", "car": "Автомобиль", "comment": "Комментарий"},
        "tj": {"service": "Хизмат", "name": "Ном", "phone": "Телефон", "car": "Мошин", "comment": "Шарҳ"},
        "en": {"service": "Service", "name": "Name", "phone": "Phone", "car": "Vehicle", "comment": "Comment"}
    }[lang]
    return "\n".join(f"<b>{labels[k]}:</b> {data.get(k, '-')}" for k in ["service", "name", "phone", "car", "comment"])


def send_admin_submission(message, item):
    username = f"@{message.from_user.username}" if message.from_user.username else "без username"
    text = (
        "📥 <b>Новая заявка Masir Service</b>\n\n"
        f"👤 <b>Пользователь:</b> {username}\n"
        f"🆔 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
        f"💬 <b>Chat ID:</b> <code>{message.chat.id}</code>\n"
        f"⏱ <b>Дата:</b> {item['created_at']} UTC\n\n"
        f"<b>Услуга:</b> {item['service']}\n"
        f"<b>Имя:</b> {item['name']}\n"
        f"<b>Телефон:</b> {item['phone']}\n"
        f"<b>Автомобиль:</b> {item['car']}\n"
        f"<b>Комментарий:</b> {item['comment']}"
    )
    bot.send_message(ADMIN_ID, text)


@bot.message_handler(commands=["start", "language"])
def start(message):
    data = user(message)
    data["state"] = "choosing_language"
    data.setdefault("lang", "ru")
    data["draft"] = {}
    save_store()
    bot.send_message(message.chat.id, tr("choose_lang", data["lang"]), reply_markup=lang_keyboard())


@bot.message_handler(commands=["menu"])
def menu_command(message):
    data = user(message)
    reset_flow(data)
    show_menu(message.chat.id, data.get("lang", "ru"))


@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    lang = lang_of(call)
    if subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "✅")
        reset_flow(user(call))
        bot.send_message(call.message.chat.id, tr("sub_ok", lang), reply_markup=menu_keyboard(lang))
    else:
        bot.answer_callback_query(call.id, tr("sub_bad", lang), show_alert=True)


@bot.message_handler(content_types=["text", "contact"])
def router(message):
    data = user(message)
    lang = data.get("lang", "ru")
    text = clean_text(message.text)

    if message.content_type == "text" and text in LANG_BY_TEXT:
        data["lang"] = LANG_BY_TEXT[text]
        data["state"] = "idle"
        data["draft"] = {}
        save_store()
        lang = data["lang"]
        if not subscribed(message.from_user.id):
            bot.send_message(message.chat.id, tr("subscribe", lang), reply_markup=sub_keyboard(lang))
            return
        bot.send_message(message.chat.id, tr("sub_ok", lang), reply_markup=menu_keyboard(lang))
        return

    if message.content_type == "text" and is_change_lang(text):
        data["state"] = "choosing_language"
        data["draft"] = {}
        save_store()
        bot.send_message(message.chat.id, tr("choose_lang", lang), reply_markup=lang_keyboard())
        return

    if message.content_type == "text" and is_cancel(text):
        reset_flow(data)
        bot.send_message(message.chat.id, tr("cancelled", lang), reply_markup=menu_keyboard(lang))
        return

    state = data.get("state", "idle")

    if state == "waiting_name":
        data["draft"]["name"] = clean_text(text)
        data["state"] = "waiting_phone"
        save_store()
        bot.send_message(message.chat.id, tr("phone", lang), reply_markup=cancel_keyboard(lang, with_contact=True))
        return

    if state == "waiting_phone":
        data["draft"]["phone"] = phone_from_message(message)
        data["state"] = "waiting_car"
        save_store()
        bot.send_message(message.chat.id, tr("car", lang), reply_markup=cancel_keyboard(lang))
        return

    if state == "waiting_car":
        data["draft"]["car"] = clean_text(text)
        data["state"] = "waiting_comment"
        save_store()
        bot.send_message(message.chat.id, tr("comment", lang), reply_markup=cancel_keyboard(lang))
        return

    if state == "waiting_comment":
        data["draft"]["comment"] = clean_text(text)
        item = {
            "id": int(time.time() * 1000),
            "user_id": message.from_user.id,
            "chat_id": message.chat.id,
            "username": message.from_user.username or "",
            "lang": lang,
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            **data["draft"]
        }
        store["submissions"].append(item)
        reset_flow(data)
        save_store()
        bot.send_message(message.chat.id, f"{tr('sent', lang)}\n\n{format_submission(item, lang)}", reply_markup=menu_keyboard(lang))
        try:
            send_admin_submission(message, item)
        except Exception:
            pass
        return

    if message.content_type == "text" and is_pickup(text):
        bot.send_message(message.chat.id, tr("addresses", lang), reply_markup=menu_keyboard(lang))
        return

    if message.content_type == "text" and is_stats(text):
        if message.from_user.id not in STATS_USERS:
            return
        now = datetime.now(timezone.utc)
        today = sum(1 for x in store["submissions"] if datetime.fromisoformat(x["created_at"]).date() == now.date())
        week = sum(1 for x in store["submissions"] if datetime.fromisoformat(x["created_at"]) >= now - timedelta(days=7))
        total = len(store["submissions"])
        bot.send_message(message.chat.id, f"📊 <b>Статистика</b>\n\nСегодня: {today}\nЗа 7 дней: {week}\nВсего: {total}", reply_markup=menu_keyboard(lang))
        return

    service_key = service_key_by_text(text) if message.content_type == "text" else None
    if service_key:
        if not require_subscription(message):
            return
        data["state"] = "waiting_name"
        data["draft"] = {"service": tr(service_key, lang)}
        save_store()
        bot.send_message(message.chat.id, tr("name", lang), reply_markup=cancel_keyboard(lang))
        return

    if state == "choosing_language":
        bot.send_message(message.chat.id, tr("choose_lang", lang), reply_markup=lang_keyboard())
        return

    bot.send_message(message.chat.id, tr("unknown", lang), reply_markup=menu_keyboard(lang))


if __name__ == "__main__":
    bot.remove_webhook()
    bot.infinity_polling(timeout=30, long_polling_timeout=30, skip_pending=True)
